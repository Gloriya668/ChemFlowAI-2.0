import copy,html,io,json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse,HTMLResponse,Response
from pydantic import BaseModel,Field,ValidationError
from typing import Literal
from . import engine
from .case_variant import case_key,result_key
from .store import ROOT,LOCK,read_json,load,save,list_projects,delete_project
from .models import ProjectSpec,SimulationIR
from .skills import execute_skill,REGISTRY
from .adapters import SimulatorUnavailable,SnapshotMismatch
app=FastAPI(title='ChemFlow AI',version='0.1.0')
from .finance import FinanceRequest, cases as finance_cases, calculate as finance_calculate

@app.get('/api/finance/cases')
def financial_cases():
    return finance_cases()

@app.post('/api/finance/calculate')
def financial_calculation(body: FinanceRequest):
    return finance_calculate(body)

class CreateTask(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    dataset:Literal['pdh','pyridine','custom']
    mode:Literal['reference','blind']='blind'
    backend:Literal['reference_replay','dwsim','external_mcp']='dwsim'
class StepAction(BaseModel):
    review_ack:bool=False
    note:str=''
    model:str|None=None
    route:str|None=None
class SpecUpdate(BaseModel):
    spec:ProjectSpec
    invalidate:bool=False
class TextInput(BaseModel):
    text:str=Field(max_length=100000)
    spec:ProjectSpec|None=None

def get(pid):
    try:
        p=load(pid)
        migrated=False
        if p.get('mode')=='demo':
            p['mode']='reference';migrated=True
        from .design_basis import migrate_input
        if migrate_input(p):migrated=True
        if migrated:save(p)
        return p
    except (ValueError,FileNotFoundError):raise HTTPException(404,'Project not found')
def checked(fn):
    try:return fn()
    except HTTPException:raise
    except SimulatorUnavailable as e:raise HTTPException(503,str(e))
    except SnapshotMismatch as e:raise HTTPException(409,str(e))
    except (ValueError,ValidationError,KeyError,TypeError) as e:raise HTTPException(422,str(e))
def current(p,step):
    engine.ensure(p,step)
    if p['max_step']!=step or step in p['completed']:raise ValueError('修改已完成阶段需要先明确重新打开并使下游失效')
def summary(p):return {k:p[k] for k in ['id','name','dataset','mode','backend','max_step','completed','status','revision']}
def view(p,step):
    engine.ensure(p,step);d=copy.deepcopy(p)
    for key,minstep in [('model',3),('route',4),('ir',5),('result',5),('review',5),('optimization',7),('tea',8),('validation',9)]:
        if step<minstep:d[key]=None
    d['inspector']=execute_skill(engine.SKILLS[step-1],step,{'spec':p['spec'],'review':d.get('review') or {}})
    if d.get('result',{} ) and d['result']['backend']=='DWSIM':
        d['inspector'].update(observation='DWSIM 已返回真实求解结果',evidence=d['result']['notes'],risk='需核对模型适用性及守恒；收敛不代表工程有效性。')
    d['models']=engine.models(p) if step>=3 else []
    from .evidence import evidence
    d['evidence']=evidence(p['dataset']) if p['backend']=='reference_replay' and step>=6 and case_key(p['spec'])!='pyridine525' else None
    equipment_path=ROOT/'data/equipment_parameters.json'
    d['equipment_parameters']=read_json(equipment_path).get(result_key(p)) if p['backend']=='reference_replay' and step>=5 and equipment_path.exists() else None
    d['route_insights']=[]
    if p['backend']=='reference_replay' and step>=4 and p['dataset']!='custom':
        for rid in (['route_a','route_b','route_c'] if p['dataset']=='pdh' else ['pyridine']):
            r=read_json(ROOT/'data/replay'/f'{result_key(p,rid)}.json')
            heat=[e['duty']['value'] for e in r['energy'] if '压缩' not in e['id']]
            power=[e['duty']['value'] for e in r['energy'] if '压缩' in e['id']]
            d['route_insights'].append({'id':rid,'units':len(r['topology']['units']),'streams':len(r['streams']),'heat':sum(max(0,x) for x in heat) if heat else None,'power':sum(power) if power else None})
    from .design_basis import completion
    d['design_basis']=completion(p['spec'])
    d['step']=step;d['workflow_state']=engine.STEP_IDS[p['max_step']-1];return d
@app.get('/api/health')
def health():
    import hashlib
    return {'status':'ok','build':'2026-10-10-v3','instance_id':hashlib.sha256(str(ROOT.resolve()).lower().encode()).hexdigest(),
            'agent':'ENGINEERING_AGENT','llm_transport':'REAL_HTTP','default_simulator':'dwsim',
            'simulators':{'dwsim':{'status_endpoint':'/api/dwsim/status'},
                          'reference_replay':{'purpose':'EXPLICIT_ARCHIVE_REVIEW_ONLY'}}}
@app.get('/api/catalog')
def catalog():return read_json(ROOT/'data/catalog.json')
@app.get('/api/property-data/{dataset}')
def property_data(dataset:str):
    from .properties import catalog
    return checked(lambda:catalog(dataset))
@app.get('/api/projects/{pid}/reference-basis')
def reference_basis(pid:str):
    from .design_basis import load_input
    p=get(pid);s=load_input(case_key(p['spec']));s['project_id']=p['id']
    if p['dataset']=='pdh':
        for t in s['target_products']:
            top=t.get('product_role')=='TOP'
            t['name']='丙烯 / C3H6' if top else '丙烷 / C3H8'
            t['purity']={'value':0.996 if top else 0.975,'unit':'mol/mol','source_type':'IMPORTED_INPUT','source_name':'离线包内已有产品目标','version':'1','status':'REFERENCE'}
    return s
@app.get('/api/projects/{pid}/vle')
def get_vle(pid:str):
    from .properties import vle_for
    p=get(pid);engine.ensure(p,2);return vle_for(p)
@app.put('/api/projects/{pid}/vle')
def put_vle(pid:str,body:dict):
    from .properties import validate_vle,vle_for
    with LOCK:
        def run():
            p=get(pid);current(p,2);record=validate_vle(body,p['spec']);p['vle_data']=[record]
            engine.event(p,'实验 VLE 已保存；实验记录与关联生成曲线分别标注');save(p);return vle_for(p)
        return checked(run)
@app.get('/api/projects')
def projects():return [summary(p) for p in list_projects()]
@app.post('/api/projects')
def create_task(body:CreateTask):
    with LOCK:return checked(lambda:summary(engine.create(**body.model_dump())))
@app.get('/api/projects/{pid}')
def project(pid:str):return summary(get(pid))
@app.delete('/api/projects/{pid}')
def remove_project(pid:str):
    with LOCK:
        get(pid)
        delete_project(pid)
        return {'id':pid,'deleted':True}

@app.get('/api/projects/{pid}/steps/{step}')
def project_view(pid:str,step:int):return checked(lambda:view(get(pid),step))
@app.put('/api/projects/{pid}/spec')
def change_spec(pid:str,body:SpecUpdate):
    with LOCK:return checked(lambda:summary(engine.update_spec(get(pid),body.spec.model_dump(),body.invalidate)))
@app.post('/api/projects/{pid}/intake')
def intake(pid:str,body:TextInput):
    def run():
        p=get(pid);s=body.spec.model_dump() if body.spec else p['spec']
        if s['dataset']!=p['dataset']:raise ValueError('Dataset mismatch')
        return engine.parse_intake(body.text,s)
    return checked(run)
@app.post('/api/projects/{pid}/design-basis/validate')
def validate_basis(pid:str,body:SpecUpdate):
    from .design_basis import completion
    p=get(pid)
    if body.spec.dataset!=p['dataset']:raise HTTPException(422,'Dataset mismatch')
    return completion(body.spec)
@app.post('/api/projects/{pid}/reopen/{step}')
def reopen(pid:str,step:int,body:dict):
    with LOCK:
        def run():
            p=get(pid);engine.ensure(p,step)
            if not body.get('invalidate'):raise ValueError('INVALIDATION_REQUIRED')
            engine.invalidate_from(p,step);engine.event(p,f'Reopened Step {step}; downstream invalidated');save(p);return summary(p)
        return checked(run)
@app.post('/api/projects/{pid}/steps/{step}/confirm')
def confirm(pid:str,step:int,body:StepAction):
    with LOCK:return checked(lambda:summary(engine.confirm(get(pid),step,body.model_dump())))
@app.post('/api/projects/{pid}/simulate')
def simulate(pid:str):
    if get(pid)['backend']=='dwsim':
        from .agent import simulate_checked
        return checked(lambda:view(simulate_checked(pid,get(pid)['revision']),5))
    with LOCK:
        def run():
            p=get(pid);current(p,5);return view(engine.run_simulation(p),5)
        return checked(run)
@app.get('/api/projects/{pid}/routes/{route}')
def route(pid:str,route:str):
    def run():
        p=get(pid);engine.ensure(p,4);return engine.load_ir(p,route)
    return checked(run)
class RouteChoice(BaseModel):
    route:str
    revision:int
    invalidate:bool=False

@app.get('/api/projects/{pid}/routes/{route}/preview')
def route_preview(pid:str,route:str):
    def run():
        p=copy.deepcopy(get(pid));engine.ensure(p,4)
        p['ir']=engine.load_ir(p,route);p['route']=route;p['max_step']=max(5,p['max_step']);p['result']=None
        warning=None
        if p['backend']=='reference_replay':
            try:engine.run_simulation(p,persist=False)
            except SnapshotMismatch as exc:warning=str(exc)
        return {'topology':p['ir'],'svg':canvas_svg(p),'result':p['result'],'warning':warning}
    return checked(run)

@app.put('/api/projects/{pid}/route-choice')
def choose_route(pid:str,body:RouteChoice):
    with LOCK:
        def run():
            p=get(pid);engine.ensure(p,4)
            if p['revision']!=body.revision:raise HTTPException(409,'项目已更新，请刷新页面后重新选择')
            ir=engine.load_ir(p,body.route)
            if p.get('route')==body.route:return summary(p)
            if (p['max_step']>4 or 4 in p['completed']) and not body.invalidate:
                raise HTTPException(409,'更换方案需要确认后续结果失效')
            engine.invalidate_from(p,4)
            p['route']=body.route;p['ir']=ir;p.pop('reference_load_error',None)
            engine.event(p,'重新选择流程方案：'+ir['title']+'；等待路线确认')
            save(p);return summary(p)
        return checked(run)

@app.post('/api/projects/{pid}/optimization')
def optimization(pid:str,body:dict):
    with LOCK:
        def run():p=get(pid);current(p,7);return view(engine.optimize(p,body),7)
        return checked(run)
@app.get('/api/projects/{pid}/comparison')
def comparison(pid:str):
    def run():
        p=get(pid);engine.ensure(p,7)
        if p['backend']!='reference_replay':return []
        ids=['route_a','route_b','route_c'] if p['dataset']=='pdh' else ['pyridine'] if p['dataset']=='pyridine' else [];out=[]
        for rid in ids:
            r=read_json(ROOT/'data/replay'/f'{result_key(p,rid)}.json');entries=r['energy'];heat=[e for e in entries if '压缩' not in e['id']];power=[e for e in entries if '压缩' in e['id']]
            def metric(es):return {'value':sum(max(e['duty']['value'],0) for e in es) if es else None,'unit':'kW','source_type':'CALCULATED','source_name':'Engineering archive duty aggregation','version':'1','status':'REFERENCE','formula':'sum(positive reported duties); missing equipment not zero','parents':[e['duty'] for e in es]}
            out.append({'id':rid,'title':r['topology']['title'],'thermal':metric(heat),'power':metric(power),'status':'REFERENCE_COMPARISON','energy':entries})
        return out
    return checked(run)
@app.post('/api/projects/{pid}/tea')
def evaluate_tea(pid:str,body:dict):
    with LOCK:
        def run():p=get(pid);current(p,8);return view(engine.tea(p,body),8)
        return checked(run)
@app.get('/api/projects/{pid}/canvas')
def canvas(pid:str):return checked(lambda:Response(canvas_svg(get(pid)),media_type='image/svg+xml'))
def canvas_svg(p):
    engine.ensure(p,5)
    if not p['route']:raise ValueError('No route selected')
    ns={'s':'http://www.w3.org/2000/svg'};ET.register_namespace('',ns['s']);svg=ET.fromstring((ROOT/'data/assets'/f"{result_key(p)}.svg").read_text(encoding='utf-8'));result=p.get('result')
    for g in svg.findall('.//s:g[@class="stream-label"]',ns):
        stream=g.get('data-stream-id');r=result['streams'].get(stream) if result else None
        for text in g.findall('s:text',ns):
            k=text.get('data-key')
            if not k:continue
            key={'massflow':'mass_flow'}.get(k,k);v=r[key]['value'] if r else None;text.text='—' if v is None else (f'{v:,.2f}' if key=='mass_flow' else f'{v:.2f} '+('°C' if key=='temperature' else 'bar'))
        g.set('data-validation','ANOMALY' if r and r['temperature']['status']=='ANOMALY' else ('REFERENCE' if r else 'PENDING'))
    return ET.tostring(svg,encoding='unicode')
def report_text(p):
    if p['status']!='COMPLETE':raise ValueError('Report available after completed Step 09')
    from .evidence import evidence
    from .properties import vle_for
    p=copy.deepcopy(p);p['source_evidence']=evidence(p['dataset']) if p['backend']=='reference_replay' and case_key(p['spec'])!='pyridine525' else {'notes':p['result']['notes']};p['vle']=vle_for(p);p['equipment_parameters']=read_json(ROOT/'data/equipment_parameters.json').get(result_key(p)) if p['backend']=='reference_replay' else None
    return '# ChemFlow AI 工程验证报告\n\n'+p['name']+'\n\nBackend: '+p['backend']+'\n\nWorkflow Integration: '+p['validation']['workflow_integration']+'\n\nIndependent Numerical Validation: '+p['validation']['independent_numerical_validation']+'\n\n'+('DWSIM 实际求解结果。收敛不等于通过独立实验验证，详见求解记录。' if p['result']['backend']=='DWSIM' else '参考结果回放，未进行独立模拟。')+'\n\n'+json.dumps({k:p[k] for k in ['spec','model','route','ir','review','optimization','tea','validation','approvals','events','source_evidence','vle','equipment_parameters']},ensure_ascii=False,indent=2)
@app.get('/api/projects/{pid}/report')
def report(pid:str):
    def run():
        p=get(pid);text=report_text(p);content='<!doctype html><meta charset="utf-8"><title>ChemFlow AI Report</title><style>body{font:15px system-ui;max-width:1100px;margin:40px auto;background:#f6f8fa;color:#163345}pre{white-space:pre-wrap;overflow-wrap:anywhere}svg{width:100%;height:auto}@media print{button{display:none}}</style><h1>ChemFlow AI · 工程验证报告</h1><p>Workflow Complete · Independent Numerical Validation: NOT ASSESSED</p>'+canvas_svg(p)+'<pre>'+html.escape(text)+'</pre>'
        return HTMLResponse(content,headers={'Content-Disposition':'attachment; filename="ChemFlow-report.html"'})
    return checked(run)
@app.get('/api/projects/{pid}/package')
def package(pid:str):
    def run():
        p=get(pid);report=report_text(p);out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            from .evidence import evidence
            from .properties import vle_for,catalog
            for name,value in [('equipment_parameters',read_json(ROOT/'data/equipment_parameters.json').get(result_key(p)) if p['backend']=='reference_replay' else None),('source_evidence',evidence(p['dataset']) if p['backend']=='reference_replay' and case_key(p['spec'])!='pyridine525' else {'notes':p['result']['notes']}),('vle',vle_for(p)),('property_parameters',catalog(p['dataset']))]:
                z.writestr(name+'.json',json.dumps(value,ensure_ascii=False,indent=2))
            for filename,key in [('design_basis','spec'),('simulation_ir','ir'),('simulation_result','result'),('energy_review','review'),('optimization','optimization'),('tea_environment','tea'),('validation','validation'),('human_approvals','approvals'),('provenance_events','events')]:z.writestr(filename+'.json',json.dumps(p[key],ensure_ascii=False,indent=2))
            from .agent import history
            z.writestr('agent_runs.json',json.dumps(history(pid),ensure_ascii=False,indent=2))
            from .dwsim_solver import runs_for_project
            z.writestr('solver_runs.json',json.dumps(runs_for_project(pid),ensure_ascii=False,indent=2))
            z.writestr('flowsheet.svg',canvas_svg(p));z.writestr('report.md',report);z.writestr('model_route_decision.json',json.dumps({'model':p['model'],'route':p['route'],'model_validation':'NOT_INDEPENDENTLY_VALIDATED'},ensure_ascii=False))
        return Response(out.getvalue(),media_type='application/zip',headers={'Content-Disposition':'attachment; filename="ChemFlow-delivery.zip"'})
    return checked(run)
from .equipment_estimate import EstimateInputs,estimate as equipment_estimate
from .drawings import DrawingRequest,drawing

@app.get('/api/projects/{pid}/drawing-defaults')
def engineering_drawing_defaults(pid: str, unit: str):
    from .drawing_defaults import equipment_defaults
    p=get(pid);engine.ensure(p,5)
    return equipment_defaults(p,unit)

@app.post('/api/projects/{pid}/drawing')
def engineering_drawing(pid:str,request:DrawingRequest):
    def run():
        p=get(pid)
        engine.ensure(p,5)
        return Response(drawing(p,request),media_type='image/svg+xml')
    return checked(run)

@app.post('/api/projects/{pid}/equipment-estimate')
def equipment_estimate_preview(pid:str,inputs:EstimateInputs):
    def run():
        p=get(pid)
        engine.ensure(p,6)
        if p['dataset']!='pdh':raise ValueError('当前估算仅适用于三个丙烷/丙烯参考示例')
        return equipment_estimate(inputs)
    return checked(run)

class ChatMessage(BaseModel):
    role:Literal['user','assistant']
    content:str=Field(min_length=1,max_length=12000)

class ChatRequest(BaseModel):
    message:str=Field(min_length=1,max_length=12000)
    history:list[ChatMessage]=Field(default_factory=list,max_length=12)
    step:int=Field(default=1,ge=1,le=9)

@app.get('/api/llm/status')
def llm_status():
    from .llm import status
    return status()

@app.get('/api/knowledge/status')
def knowledge_status():
    from .knowledge import status
    return status()

@app.get('/api/knowledge/search')
def knowledge_search(q:str=Query(min_length=1,max_length=2000),limit:int=Query(default=5,ge=1,le=20)):
    from .knowledge import search
    return {'query':q,'results':search(q,limit)}

@app.post('/api/llm/test')
def llm_test():
    from .llm import complete
    return complete([{'role':'user','content':'请简短回复：连接成功。'}])

@app.post('/api/projects/{pid}/ai/chat')
def llm_chat(pid:str,body:ChatRequest):
    from .llm import chat
    if not body.message.strip():raise HTTPException(422,'请输入问题。')
    return checked(lambda:chat(view(get(pid),body.step),body.message,[m.model_dump() for m in body.history]))

class AgentRequest(BaseModel):
    message:str=Field(min_length=1,max_length=12000)
    step:int=Field(ge=1,le=9)
    allow_simulation:bool=False

@app.get('/api/dwsim/status')
def dwsim_status():
    from .dwsim_mcp import status
    return checked(status)

@app.post('/api/dwsim/test')
def dwsim_test():
    from .dwsim_mcp import probe
    return checked(probe)

@app.get('/api/projects/{pid}/dwsim/runs')
def dwsim_runs(pid:str):
    from .dwsim_solver import runs_for_project
    get(pid)
    return checked(lambda:runs_for_project(pid))

@app.get('/api/projects/{pid}/dwsim/registration')
def dwsim_registration(pid:str):
    from .dwsim_solver import registration
    return checked(lambda:registration(get(pid)))

@app.get('/api/projects/{pid}/agent/runs')
def agent_runs(pid:str):
    from .agent import history
    get(pid)
    return checked(lambda:history(pid))

@app.post('/api/projects/{pid}/agent/runs',status_code=202)
def start_agent(pid:str,body:AgentRequest):
    from .agent import start
    get(pid)
    return checked(lambda:start(pid,body.message,body.step,body.allow_simulation))

@app.get('/api/projects/{pid}/agent/runs/{rid}')
def agent_run(pid:str,rid:str):
    from .agent import read
    get(pid)
    try:return checked(lambda:read(pid,rid))
    except FileNotFoundError:raise HTTPException(404,'Agent task not found')

@app.post('/api/projects/{pid}/agent/runs/{rid}/cancel')
def cancel_agent(pid:str,rid:str):
    from .agent import cancel
    get(pid)
    try:return checked(lambda:cancel(pid,rid))
    except FileNotFoundError:raise HTTPException(404,'Agent task not found')

from .learning_custom import router as learning_router
app.include_router(learning_router)
from .learning_study import router as study_router
app.include_router(study_router)

@app.get('/{path:path}')
def frontend(path:str):
    root=ROOT/'frontend/dist';file=(root/path).resolve()
    if not file.is_relative_to(root.resolve()):raise HTTPException(404)
    if file.is_file():return FileResponse(file)
    if path.startswith(('api/','data/','backend/','config/','runtime/')):raise HTTPException(404)
    if (root/'index.html').exists():return FileResponse(root/'index.html')
    return HTMLResponse('Frontend not built. Run npm run build.',status_code=503)

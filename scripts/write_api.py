from pathlib import Path
P=Path(r'E:\CodexOutputs\ChemFlowAI')
(P/'backend/app.py').write_text(r'''import copy,html,io,json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse,HTMLResponse,Response
from pydantic import BaseModel,Field,ValidationError
from typing import Literal
from . import engine
from .store import ROOT,LOCK,read_json,load,save,list_projects
from .models import ProjectSpec,SimulationIR
from .skills import execute_skill,REGISTRY
from .adapters import SimulatorUnavailable,SnapshotMismatch
app=FastAPI(title='ChemFlow AI',version='0.1.0')
class CreateTask(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    dataset:Literal['pdh','pyridine']
    mode:Literal['demo','blind']='demo'
    backend:Literal['reference_replay','dwsim','aspen_mcp']='reference_replay'
class StepAction(BaseModel):
    review_ack:bool=False
    note:str=''
    model:str|None=None
    route:str|None=None
class SpecUpdate(BaseModel):
    spec:ProjectSpec
    invalidate:bool=False
class TextInput(BaseModel):text:str=Field(max_length=100000)

def get(pid):
    try:return load(pid)
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
    d['models']=engine.models(p) if step>=3 else []
    d['step']=step;return d
@app.get('/api/health')
def health():return {'status':'ok','network':'offline-first','agent':'RULE_ENGINE','simulators':read_json(ROOT/'config/simulators.json')}
@app.get('/api/catalog')
def catalog():return read_json(ROOT/'data/catalog.json')
@app.get('/api/projects')
def projects():return [summary(p) for p in list_projects()]
@app.post('/api/projects')
def create_task(body:CreateTask):
    with LOCK:return checked(lambda:summary(engine.create(**body.model_dump())))
@app.get('/api/projects/{pid}')
def project(pid:str):return summary(get(pid))
@app.get('/api/projects/{pid}/steps/{step}')
def project_view(pid:str,step:int):return checked(lambda:view(get(pid),step))
@app.put('/api/projects/{pid}/spec')
def change_spec(pid:str,body:SpecUpdate):
    with LOCK:return checked(lambda:summary(engine.update_spec(get(pid),body.spec.model_dump(),body.invalidate)))
@app.post('/api/projects/{pid}/intake')
def intake(pid:str,body:TextInput):return checked(lambda:engine.parse_intake(body.text,get(pid)['spec']))
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
    with LOCK:
        def run():
            p=get(pid);current(p,5);return view(engine.run_simulation(p),5)
        return checked(run)
@app.get('/api/projects/{pid}/routes/{route}')
def route(pid:str,route:str):
    def run():
        p=get(pid);engine.ensure(p,4);return engine.load_ir(p,route)
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
        if p['mode']=='blind':raise ValueError('参考比较不用于盲验证')
        ids=['route_a','route_b','route_c'] if p['dataset']=='pdh' else ['pyridine'];out=[]
        for rid in ids:
            r=read_json(ROOT/'data/replay'/f'{rid}.json');entries=r['energy'];heat=[e for e in entries if '压缩' not in e['id']];power=[e for e in entries if '压缩' in e['id']]
            def metric(es):return {'value':sum(max(e['duty']['value'],0) for e in es) if es else None,'unit':'kW','source_type':'CALCULATED','source_name':'Aspen reference duty aggregation','version':'1','status':'REFERENCE','formula':'sum(positive reported duties); missing equipment not zero','parents':[e['duty'] for e in es]}
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
    ns={'s':'http://www.w3.org/2000/svg'};ET.register_namespace('',ns['s']);svg=ET.fromstring((ROOT/'data/assets'/f"{p['route']}.svg").read_text(encoding='utf-8'));result=p.get('result')
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
    return '# ChemFlow AI 工程验证报告\n\n'+p['name']+'\n\nBackend: '+p['backend']+'\n\nWorkflow Integration: '+p['validation']['workflow_integration']+'\n\nIndependent Numerical Validation: '+p['validation']['independent_numerical_validation']+'\n\nThis result is replayed from an existing Aspen reference dataset for workflow integration testing. It does not represent a new independent ChemFlow simulation.\n\n'+json.dumps({k:p[k] for k in ['spec','model','route','ir','review','optimization','tea','validation','approvals','events']},ensure_ascii=False,indent=2)
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
            for filename,key in [('design_basis','spec'),('simulation_ir','ir'),('simulation_result','result'),('energy_review','review'),('optimization','optimization'),('tea_environment','tea'),('validation','validation'),('human_approvals','approvals'),('provenance_events','events')]:z.writestr(filename+'.json',json.dumps(p[key],ensure_ascii=False,indent=2))
            z.writestr('flowsheet.svg',canvas_svg(p));z.writestr('report.md',report);z.writestr('model_route_decision.json',json.dumps({'model':p['model'],'route':p['route'],'model_validation':'NOT_INDEPENDENTLY_VALIDATED'},ensure_ascii=False))
        return Response(out.getvalue(),media_type='application/zip',headers={'Content-Disposition':'attachment; filename="ChemFlow-delivery.zip"'})
    return checked(run)
@app.get('/{path:path}')
def frontend(path:str):
    root=ROOT/'frontend/dist';file=(root/path).resolve()
    if not file.is_relative_to(root.resolve()):raise HTTPException(404)
    if file.is_file():return FileResponse(file)
    if path.startswith(('api/','data/','backend/','config/','runtime/')):raise HTTPException(404)
    if (root/'index.html').exists():return FileResponse(root/'index.html')
    return HTMLResponse('Frontend not built. Run npm run build.',status_code=503)
''',encoding='utf-8')
(P/'frontend/tsconfig.json').write_text('''{"compilerOptions":{"target":"ES2022","lib":["ES2022","DOM","DOM.Iterable"],"module":"ESNext","moduleResolution":"Bundler","jsx":"react-jsx","strict":true,"esModuleInterop":true,"skipLibCheck":true,"noEmit":true},"include":["src"]}''',encoding='utf-8')
(P/'frontend/vite.config.ts').write_text("import {defineConfig} from 'vite'; import tailwindcss from '@tailwindcss/vite'; export default defineConfig({plugins:[tailwindcss()],server:{proxy:{'/api':'http://127.0.0.1:8765'}},build:{chunkSizeWarningLimit:700}});",encoding='utf-8')
(P/'frontend/index.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#070B14"><title>ChemFlow AI｜智模拟·绿化工</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>',encoding='utf-8')
print('API endpoints and frontend configuration created.')

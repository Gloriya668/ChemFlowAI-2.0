from pathlib import Path
P=Path(r'E:\CodexOutputs\ChemFlowAI')
def w(n,s):(P/n).write_text(s,encoding='utf-8')
w('backend/models.py',r'''from typing import Any,Literal
from pydantic import BaseModel,Field,ConfigDict,model_validator
import math
class ProvenanceRecord(BaseModel):
    value: float|str|None = None
    unit: str=''
    source_type: Literal['USER_INPUT','ASPEN_REFERENCE','LITERATURE','DATABASE','RULE','LLM','SIMULATOR','CALCULATED']
    source_name: str
    version: str='1'
    locator: str=''
    status: str='UNVERIFIED'
    formula: str|None=None
    parents: list[dict]=Field(default_factory=list)
    @model_validator(mode='after')
    def finite(self):
        if isinstance(self.value,float) and not math.isfinite(self.value):raise ValueError('Finite engineering values required')
        if self.source_type=='LLM' and isinstance(self.value,(float,int)):raise ValueError('LLM cannot author engineering numerical values')
        return self
class ComponentSpec(BaseModel):
    id:str
    name:str
    source_type:str
    source_name:str
class FeedSpec(BaseModel):
    stream_id:str
    temperature:ProvenanceRecord
    pressure:ProvenanceRecord
    mass_flow:ProvenanceRecord
    composition:dict[str,ProvenanceRecord]=Field(default_factory=dict)
class ReactionSpec(BaseModel):
    equation:str
    source_type:str
    source_name:str
class ProductTarget(BaseModel):
    name:str
    purity:ProvenanceRecord|None=None
    source_type:str
    source_name:str
class ConstraintSpec(BaseModel):
    model_config=ConfigDict(extra='allow')
class UtilitySpec(ConstraintSpec):pass
class ProjectSpec(BaseModel):
    model_config=ConfigDict(extra='forbid')
    project_id:str=''
    dataset:Literal['pdh','pyridine']
    components:list[ComponentSpec]
    feeds:list[FeedSpec]
    reaction:ReactionSpec
    target_products:list[ProductTarget]
    capacity:ProvenanceRecord|None=None
    constraints:dict=Field(default_factory=dict)
    utilities:dict=Field(default_factory=dict)
    source:dict
class PropertyData(BaseModel):
    component_id:str
    critical_temperature:ProvenanceRecord|None=None
    critical_pressure:ProvenanceRecord|None=None
    interaction_parameters_status:str='MISSING'
class PropertyMethodCandidate(BaseModel):
    id:str
    reason:str
    risk:str
    status:str='NEEDS_HUMAN_REVIEW'
    source_type:str='RULE'
class UnitOperation(BaseModel):
    id:str
    type:str
    label:str
    parameters:dict=Field(default_factory=dict)
class MaterialStream(BaseModel):
    stream_id:str
    from_unit:str|None=None
    to_unit:str|None=None
class EnergyStream(BaseModel):
    id:str
    from_unit:str|None=None
    to_unit:str|None=None
    duty:ProvenanceRecord|None=None
class Connection(MaterialStream):pass
class SimulationIR(BaseModel):
    route_id:str
    title:str
    components:list[ComponentSpec]=Field(default_factory=list)
    property_method:str=''
    units:list[UnitOperation]
    streams:list[MaterialStream]
    connections:list[Connection]
    energy_streams:list[EnergyStream]=Field(default_factory=list)
    source:dict
    @model_validator(mode='after')
    def graph(self):
        ids=[u.id for u in self.units];ss=[s.stream_id for s in self.streams]
        if len(set(ids))!=len(ids) or len(set(ss))!=len(ss):raise ValueError('Duplicate graph IDs')
        if set(c.stream_id for c in self.connections)!=set(ss):raise ValueError('Connection/stream set mismatch')
        if len(self.connections)!=len(ss):raise ValueError('Duplicate connections')
        for c in self.connections:
            if not c.from_unit and not c.to_unit:raise ValueError('Disconnected stream')
            for k in [c.from_unit,c.to_unit]:
                if k and k not in ids:raise ValueError('Unknown equipment reference')
        return self
class StreamResult(BaseModel):
    stream_id:str
    temperature:ProvenanceRecord
    pressure:ProvenanceRecord
    mass_flow:ProvenanceRecord
    phase:ProvenanceRecord
    vapor_fraction:ProvenanceRecord|None=None
    composition:dict[str,ProvenanceRecord]=Field(default_factory=dict)
class EquipmentResult(BaseModel):
    id:str
    duty:ProvenanceRecord|None=None
class EnergyResult(BaseModel):
    entries:list[EquipmentResult]
    balance_status:str='NOT_ASSESSED'
class SimulationResult(BaseModel):
    route_id:str
    backend:str
    solver_status:str
    converged:bool|None
    streams:dict[str,StreamResult]
    energy:list[EquipmentResult]
    topology:dict
    source:str
    notes:list[str]
class OptimizationCandidate(BaseModel):
    id:str
    variables:dict[str,ProvenanceRecord]=Field(default_factory=dict)
    objectives:dict[str,ProvenanceRecord|None]=Field(default_factory=dict)
    status:str='NOT_SOLVED'
class EconomicResult(BaseModel):
    status:str
    metrics:dict[str,ProvenanceRecord|None]
    missing_inputs:list[str]
class EnvironmentalResult(EconomicResult):pass
class ValidationResult(BaseModel):
    workflow_integration:str
    independent_numerical_validation:str
    checks:list[dict]
    thresholds:dict
class SkillResult(BaseModel):
    skill:str
    step:int
    status:str
    observation:str
    evidence:list[str]
    risk:str
    recommendation:str
    action_required:str
''')
w('backend/store.py',r'''from pathlib import Path
import json,os,threading,uuid
ROOT=Path(__file__).resolve().parents[1]
PROJECTS=Path(os.environ.get('CHEMFLOW_PROJECTS',ROOT/'runtime/projects'))
PROJECTS.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock()
def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def path_for(pid):
    try:uuid.UUID(pid)
    except ValueError:raise ValueError('Invalid project id')
    return PROJECTS/(pid+'.json')
def load(pid):return read_json(path_for(pid))
def save(p):
    with LOCK:
        path=path_for(p['id']);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(p,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,path)
def list_projects():return [read_json(f) for f in sorted(PROJECTS.glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True)]
''')
w('backend/skills.py',r'''from .store import ROOT,read_json
from .models import ProjectSpec,SkillResult
REGISTRY=read_json(ROOT/'config/skills.json')
def execute_skill(name,step,context):
    entry=next((s for s in REGISTRY if s['name']==name),None)
    if not entry or step not in entry['steps']:raise ValueError('WRONG_STEP')
    spec=ProjectSpec.model_validate(context['spec']);evidence=[];risk='没有连接独立求解器。'
    if name=='chemflow-intake':
        errors=check_spec(spec);obs='设计基准已结构化' if not errors else '设计输入需要补充';evidence=errors or [f'{len(spec.feeds)} 股进料均有可追溯温度、压力和质量流量。']
        risk='目标纯度、公用工程及部分工程约束尚未定义；不可作为实际设计交付。'
    elif name=='chemflow-property-modeling':
        obs='仅进行输入校核和物性方法规则筛选';evidence=['输入表不含独立纯组分临界参数、完整 BIP 和实验 VLE。','PR/SRK/PRSV 用于烃类候选；NRTL 用于极性非理想候选（待验证）。'];risk='模型推荐不等于物性验证。'
    elif name=='chemflow-process-synthesis':
        obs='保留已审核流程拓扑，生成模拟器无关 IR';evidence=['路线来源：已有用户流程资产；不是数值结果驱动生成。'];risk='吡啶采用与数据一致的开循环存档，不包含旧图未匹配回流。'
    elif name=='chemflow-simulation-review':
        obs='审核 Adapter 输出及质量守恒';evidence=context.get('review',{}).get('issues',[]) or ['结果加载前不提供收敛判断。'];risk='REPLAY_NOT_SOLVED 不代表实际求解收敛；异常原值不修改。'
    elif name=='chemflow-optimization-tea':
        obs='保存优化问题并检查评价输入';evidence=['无优化器时仅参考比较；不绘制伪造最优前沿。','价格、小时、基年、币种和方法缺失时不计算。'];risk='参考方案跨模拟运行，边界可能不一致；不是优化结论。'
    else:
        obs='复核工作流与数据映射';evidence=['Ground Truth 仅此步骤的 Evaluator 可读取。'];risk='同源回放不能证明独立数值精度。'
    return SkillResult(skill=name,step=step,status='NEEDS_HUMAN_REVIEW',observation=obs,evidence=evidence,risk=risk,recommendation='检查来源并完成当前阶段工程复核。',action_required='人工确认后继续').model_dump()
def check_spec(spec):
    errors=[]
    if not spec.feeds or not spec.components:errors.append('必须提供组分与进料')
    for f in spec.feeds:
        for k,u in [('temperature','C'),('pressure','bar'),('mass_flow','kg/h')]:
            q=getattr(f,k)
            if not isinstance(q.value,(int,float)):errors.append(f'{f.stream_id}.{k} 缺失数值')
            elif k=='temperature' and q.value< -273.15:errors.append('温度低于绝对零度')
            elif k in ('pressure','mass_flow') and q.value<=0:errors.append(f'{f.stream_id}.{k} 必须大于零')
            if q.unit!=u:errors.append(f'{f.stream_id}.{k} 单位应为 {u}')
    return errors
''')
w('backend/adapters.py',r'''from abc import ABC,abstractmethod
from typing import Literal
from pydantic import BaseModel
from .store import ROOT,read_json
from .models import SimulationIR,SimulationResult
class SimulatorUnavailable(Exception):pass
class SnapshotMismatch(Exception):pass
class TypedSimulatorCommand(BaseModel):
    operation:Literal['load_model','set_feed','set_unit_parameter','solve','get_streams','get_duties']
    unit_id:str|None=None
    stream_id:str|None=None
    parameter:Literal['temperature','pressure','mass_flow','reflux_ratio','feed_stage','compressor_ratio']|None=None
    value:float|None=None
class SimulatorAdapter(ABC):
    @abstractmethod
    def run(self,spec,ir:SimulationIR)->SimulationResult:...
class ReferenceReplayAdapter(SimulatorAdapter):
    def run(self,spec,ir):
        original=read_json(ROOT/'data/validation'/spec['dataset']/'input.json')
        def key(s):return [(f['stream_id'],f['temperature']['value'],f['pressure']['value'],f['mass_flow']['value'],{k:q['value'] for k,q in f['composition'].items()}) for f in s['feeds']]
        if key(spec)!=key(original) or spec['reaction']!=original['reaction'] or spec['components']!=original['components'] or spec['constraints']!=original['constraints'] or spec['utilities']!=original['utilities']:
            raise SnapshotMismatch('进料或工程基准已改变，不能将历史回放作为新结果。请恢复标准输入，或接入真实模拟器。')
        result=SimulationResult.model_validate(read_json(ROOT/'data/replay'/f'{ir.route_id}.json'))
        return result
class DWSIMAdapter(SimulatorAdapter):
    def run(self,spec,ir):raise SimulatorUnavailable('SIMULATOR NOT CONNECTED: DWSIM API/MCP 尚未配置')
class AspenMCPAdapter(SimulatorAdapter):
    def run(self,spec,ir):raise SimulatorUnavailable('SIMULATOR NOT CONNECTED: Aspen MCP typed tools 尚未连接')
    def execute(self,command:TypedSimulatorCommand):raise SimulatorUnavailable('请配置受支持 typed-tool 实现；禁止原始 COM path')
def adapter(mode,backend):
    if mode=='blind' and backend=='reference_replay':raise SimulatorUnavailable('Blind Validation 禁止使用 Reference Replay')
    return {'reference_replay':ReferenceReplayAdapter,'dwsim':DWSIMAdapter,'aspen_mcp':AspenMCPAdapter}[backend]()
''')
w('backend/evaluator.py',r'''from .store import ROOT,read_json
from .models import ValidationResult
class GoldenEvaluator:
    def evaluate(self,project):
        if project['max_step']!=9:raise ValueError('Ground Truth access requires Step 09')
        result=project.get('result')
        if not result:raise ValueError('No simulation result')
        route=project['route'];base=ROOT/'data/validation'/('pyridine' if route=='pyridine' else 'pdh/'+route)
        golden=read_json(base/'ground_truth.json');t=read_json(ROOT/'config/validation_thresholds.json');checks=[]
        def add(label,status,details):checks.append({'label':label,'status':status,'details':details})
        actual=set(result['streams']);expected=set(golden['streams']);add('Data Mapping','PASS' if actual==expected else 'FAIL',f'{len(actual)} / {len(expected)} stream IDs')
        def graph(x):return (sorted((u['id'],u['type']) for u in x['units']),sorted((c['stream_id'],c['from_unit'] or '',c['to_unit'] or '') for c in x['connections']))
        add('Topology Match','PASS' if graph(project['ir'])==graph(golden['topology']) else 'FAIL','设备类型、流股与连接逐项比较')
        for key,limit in [('temperature',t['temperature_abs_C']),('pressure',t['pressure_abs_bar']),('mass_flow',t['mass_flow_relative'])]:
            errors=[]
            for name in expected&actual:
                a=result['streams'][name][key]['value'];b=golden['streams'][name][key]['value']
                if a is None or b is None:continue
                errors.append(abs(a-b)/(max(abs(b),1e-12) if key=='mass_flow' else 1))
            error=max(errors,default=None);add(key+' mapping','PASS' if error is not None and error<=limit and actual==expected else 'FAIL',{'max_error':error,'threshold':limit,'interpretation':'同源回放字段映射检查，非独立模拟精度'})
        balance=material_balance(result);add('Material Balance','PASS' if balance['relative_error']<=t['material_balance_relative'] else 'WARN',balance)
        energy=result['energy'];ge=golden['energy'];ok=len(energy)==len(ge)
        for a,b in zip(energy,ge):ok=ok and a['id']==b['id'] and abs(a['duty']['value']-b['duty']['value'])<=max(abs(b['duty']['value']),1)*t['energy_relative']
        add('Energy Mapping','PASS' if energy and ok else ('NOT_ASSESSED' if not energy else 'FAIL'),'无能量数据时不计算误差；不等价于能量衡算闭合')
        add('State Machine','PASS' if project['completed']==list(range(1,9)) else 'FAIL','服务端已确认步骤 1–8')
        add('Ground Truth Loading','PASS',str(base.relative_to(ROOT)))
        add('Process Visualization','PASS' if (ROOT/'data/assets'/f'{route}.svg').exists() else 'FAIL','复用动画 SVG；点击与映射由 E2E 验证')
        is_replay=result['backend']=='REFERENCE_REPLAY'
        return ValidationResult(workflow_integration='PASS' if not any(c['status']=='FAIL' for c in checks) else 'FAIL',independent_numerical_validation='NOT_ASSESSED' if is_replay else ('PASS' if all(c['status'] not in ('FAIL','WARN') for c in checks) else 'NEEDS_REVIEW'),checks=checks,thresholds=t).model_dump()
def material_balance(result):
    ins=[c['stream_id'] for c in result['topology']['connections'] if not c['from_unit']];outs=[c['stream_id'] for c in result['topology']['connections'] if not c['to_unit']]
    total_in=sum(result['streams'][i]['mass_flow']['value'] for i in ins);total_out=sum(result['streams'][i]['mass_flow']['value'] for i in outs)
    return {'input_kg_h':total_in,'output_kg_h':total_out,'residual_kg_h':total_out-total_in,'relative_error':abs(total_out-total_in)/max(total_in,1e-12),'source_type':'CALCULATED','source_name':'外部进出料质量流量之差','formula':'abs(sum(out)-sum(in))/sum(in)','input_streams':ins,'output_streams':outs}
''')
w('backend/engine.py',r'''import copy,datetime,json,re,uuid
from .store import ROOT,read_json,save
from .models import ProjectSpec,SimulationIR
from .skills import check_spec,execute_skill
from .adapters import adapter
from .evaluator import material_balance
STEP_NAMES=['需求与设计基准','物性与数据校核','模型选择与验证','路线与分离筛选','流程搭建与收敛','能量与设备分析','参数与方案优化','经济与环境评价','复核与成果交付']
SKILLS=['chemflow-intake','chemflow-property-modeling','chemflow-property-modeling','chemflow-process-synthesis','chemflow-simulation-review','chemflow-simulation-review','chemflow-optimization-tea','chemflow-optimization-tea','chemflow-validation']
def event(p,message):p['events'].append({'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'message':message});p['revision']+=1

def create(name,dataset,mode,backend):
    p={'id':str(uuid.uuid4()),'name':name,'dataset':dataset,'mode':mode,'backend':backend,'max_step':1,'completed':[],'status':'IN_PROGRESS','revision':0,'route':None,'model':None,'ir':None,'result':None,'review':None,'optimization':None,'tea':None,'validation':None,'approvals':{},'events':[]}
    p['spec']=read_json(ROOT/'data/validation'/dataset/'input.json');p['spec']['project_id']=p['id'];ProjectSpec.model_validate(p['spec']);event(p,'Created validation task; input-only context');save(p);return p

def ensure(p,step):
    if step<1 or step>9 or step>p['max_step']:raise ValueError('LOCKED_STEP: 请按顺序完成当前工程确认')
def input_key(spec):
    s=copy.deepcopy(spec);s.pop('project_id',None);return json.dumps(s,sort_keys=True,ensure_ascii=False)
def update_spec(p,spec,invalidate):
    spec=ProjectSpec.model_validate(spec).model_dump();spec['project_id']=p['id']
    if spec['dataset']!=p['dataset']:raise ValueError('项目体系不可在设计编辑中替换，请创建新任务')
    if input_key(spec)==input_key(p['spec']):return p
    if p['completed'] and not invalidate:raise ValueError('INVALIDATION_REQUIRED')
    p['spec']=spec;invalidate_from(p,1);event(p,'Design basis changed; all downstream states invalidated');save(p);return p

def invalidate_from(p,step):
    p['completed']=[s for s in p['completed'] if s<step];p['max_step']=step;p['status']='IN_PROGRESS';p['approvals']={k:v for k,v in p['approvals'].items() if int(k)<step}
    fields={3:['model'],4:['route','ir'],5:['result','review'],7:['optimization'],8:['tea'],9:['validation']}
    for threshold,names in fields.items():
        if step<=threshold:
            for name in names:p[name]=None

def load_ir(p,route):
    allowed=['route_a','route_b','route_c'] if p['dataset']=='pdh' else ['pyridine']
    if route not in allowed:raise ValueError('Route incompatible with dataset')
    base=ROOT/'data/validation'/('pyridine' if route=='pyridine' else 'pdh/'+route)
    ir=read_json(base/'topology.json');ir['components']=p['spec']['components'];ir['property_method']=p['model'];return SimulationIR.model_validate(ir).model_dump()
def models(p):
    if p['dataset']=='pdh':return [{'id':m,'reason':'烃类与氢气体系的状态方程候选','risk':'需检验氢气、低温分离及所用 T/P 范围；未进行实验 VLE 验证','status':'NEEDS_HUMAN_REVIEW','source_type':'RULE'} for m in ['PR','SRK','PRSV']]
    return [{'id':m,'reason':'含氨、水及极性有机物的非理想混合体系候选','risk':'需确认 BIP、气相模型和适用范围；未知参数不补造','status':'NEEDS_HUMAN_REVIEW','source_type':'RULE'} for m in ['NRTL','UNIQUAC']]
def run_simulation(p):
    ensure(p,5)
    if not p['ir']:raise ValueError('No approved SimulationIR')
    result=adapter(p['mode'],p['backend']).run(p['spec'],SimulationIR.model_validate(p['ir'])).model_dump()
    p['result']=result;issues=[]
    for n,s in result['streams'].items():
        if s['temperature']['status']=='ANOMALY':issues.append(n+': SOURCE ANOMALY，异常低温原值未修改')
    balance=material_balance(result)
    if balance['relative_error']>read_json(ROOT/'config/validation_thresholds.json')['material_balance_relative']:issues.append('外部质量衡算超出阈值，需审核源结果边界')
    if p['dataset']=='pyridine':issues.append('PY-R/B2 存档计算警告')
    p['review']={'status':'NEEDS_HUMAN_REVIEW' if issues else 'REPLAY_LOADED','issues':issues,'balance':balance,'solver_status':result['solver_status'],'converged':None,'energy_balance':'NOT_ASSESSED'}
    event(p,'Reference fixture loaded; no independent solver executed');save(p);return p

def confirm(p,step,data):
    ensure(p,step)
    if step!=p['max_step']:raise ValueError('请先修改并明确使下游失效，而不是重复确认历史步骤')
    if not data.get('review_ack'):raise ValueError('HUMAN_REVIEW_REQUIRED')
    if step==1:
        errors=check_spec(ProjectSpec.model_validate(p['spec']))
        if errors:raise ValueError('; '.join(errors))
    elif step==3:
        selected=data.get('model')
        if selected not in [m['id'] for m in models(p)]:raise ValueError('请选择模型')
        p['model']=selected
    elif step==4:
        p['ir']=load_ir(p,data.get('route'));p['route']=p['ir']['route_id']
    elif step==5:
        if not p['result']:raise ValueError('请先加载或运行模拟器')
        if p['review']['issues'] and not data.get('note','').strip():raise ValueError('异常结果需填写人工复核备注')
    elif step==7:
        if not p['optimization'] or not p['optimization'].get('candidate_selected'):raise ValueError('请保存优化问题，并选择当前参考基线作为后续评价对象')
    elif step==8:
        if not p['tea']:raise ValueError('请运行评价输入检查，即使结果为 NOT_CALCULATED')
    elif step==9:
        from .evaluator import GoldenEvaluator
        p['validation']=GoldenEvaluator().evaluate(p)
        if p['validation']['workflow_integration']=='FAIL':raise ValueError('Workflow validation failed; cannot complete')
    p['approvals'][str(step)]={'confirmed':True,'note':data.get('note',''),'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_model':p.get('model') if step==3 else None}
    p['completed'].append(step);p['max_step']=min(9,step+1);p['status']='COMPLETE' if step==9 else 'IN_PROGRESS';event(p,f'Step {step:02d} confirmed: {STEP_NAMES[step-1]}');save(p);return p

def parse_intake(text,spec):
    s=copy.deepcopy(spec);found=[]
    if text.strip().startswith('{'):
        candidate=json.loads(text);return {'spec':ProjectSpec.model_validate(candidate).model_dump(),'recognized':['JSON ProjectSpec'],'unparsed':[]}
    feed=s['feeds'][0]
    for key,unit,pattern,mult in [('temperature','C',r'(?:温度|temperature)\s*[:：=]?\s*(-?\d+(?:\.\d+)?)\s*(?:°?C|℃)',1),('pressure','bar',r'(?:压力|pressure)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*bar',1),('pressure','bar',r'(?:压力|pressure)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*kPa',.01),('mass_flow','kg/h',r'(?:流量|flow)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*kg/h',1)]:
        m=re.search(pattern,text,re.I)
        if m:feed[key]={'value':float(m[1])*mult,'unit':unit,'source_type':'USER_INPUT','source_name':'自然语言输入','version':'1','locator':m[0],'status':'UNVERIFIED'};found.append(key)
    return {'spec':ProjectSpec.model_validate(s).model_dump(),'recognized':found,'unparsed':['规则解析只支持明确带单位的温度/压力/流量；其余内容需人工填写，未推断。']}

def optimize(p,body):
    ensure(p,7)
    variables=body.get('variables',{})
    allowed={'column_pressure':(0.01,100),'reflux_ratio':(0.1,100),'feed_stage':(1,300),'compressor_ratio':(1,10),'split_fraction':(0,1)}
    import math
    for k,v in variables.items():
        if k not in allowed or not isinstance(v,(float,int)) or not math.isfinite(v) or not allowed[k][0]<=v<=allowed[k][1]:raise ValueError('Invalid optimization variable/bound')
    p['optimization']={'status':'OPTIMIZATION_PREVIEW','variables':{k:{'value':v,'unit':{'column_pressure':'bar','feed_stage':'stage'}.get(k,'ratio'),'source_type':'USER_INPUT','source_name':'优化问题设置','version':'1','status':'NOT_SOLVED'} for k,v in variables.items()},'bounds':body.get('bounds',{}),'constraints':['满足产品目标（待输入）','在真实模拟器中收敛'],'objectives':['min thermal_duty','min electrical_duty'],'candidate_selected':p['route'] if body.get('select_baseline') else None,'candidate_status':'REFERENCE_BASELINE','message':'参数未运行新模拟，图中参考点不随滑块伪变化'}
    p['tea']=None;p['validation']=None;event(p,'Optimization problem saved; no optimizer executed');save(p);return p

def tea(p,body):
    ensure(p,8)
    required=['basis_year','currency','hours','feed_price','product_price','utility_price','method'];missing=[k for k in required if body.get(k) in (None,'')]
    metrics={k:None for k in ['CAPEX','OPEX','Unit Product Cost','NPV','IRR','Payback','Carbon','Water','Resource Recovery','Annual Utility Cost','Annual Feed Cost','Annual Product Revenue']}
    import math
    for k in ['hours','feed_price','product_price','utility_price','carbon_factor']:
        if body.get(k) not in (None,'') and (not isinstance(body[k],(int,float)) or not math.isfinite(body[k]) or body[k]<0):raise ValueError('Invalid non-negative finite TEA input: '+k)
    if body.get('hours') and body['hours']>8784:raise ValueError('Operating hours exceed a year')
    if body.get('basis_year') not in (None,'') and (not isinstance(body['basis_year'],int) or not 1900<=body['basis_year']<=2200):raise ValueError('Invalid basis year')
    if not missing:
        if body['method']!='UTILITY_ONLY':raise ValueError('Only transparent UTILITY_ONLY accounting is implemented')
        duties=p['result']['energy'];positive=sum(max(e['duty']['value'],0) for e in duties);currency=body['currency'];hours=body['hours']
        def calc(v,unit,formula,parents):return {'value':v,'unit':unit,'source_type':'CALCULATED','source_name':'确定性年度化核算','version':'1','status':'PARTIAL','formula':formula,'parents':parents}
        if duties:metrics['Annual Utility Cost']=calc(positive*hours*body['utility_price'],currency+'/year','sum(positive reference kW) × hours × uniform utility price',[e['duty'] for e in duties]+[{'source_type':'USER_INPUT','source_name':'TEA form','value':body}])
        inflow=sum(f['mass_flow']['value'] for f in p['spec']['feeds']);metrics['Annual Feed Cost']=calc(inflow*hours*body['feed_price'],currency+'/year','sum(feed kg/h) × hours × uniform feed price',[f['mass_flow'] for f in p['spec']['feeds']]+[{'source_type':'USER_INPUT','source_name':'TEA form','value':body}])
        product=p['result']['streams']['4' if p['dataset']=='pyridine' else 'PRO-D']['mass_flow'];metrics['Annual Product Revenue']=calc(product['value']*hours*body['product_price'],currency+'/year','gross product stream kg/h × hours × price; not pure-product revenue',[product,{'source_type':'USER_INPUT','source_name':'TEA form','value':body}])
        if duties and body.get('carbon_factor') is not None:metrics['Carbon']=calc(positive*hours*body['carbon_factor'],'kgCO2e/year','positive duty kW × hours × user uniform factor (boundary partial)',[{'source_type':'USER_INPUT','source_name':'TEA form','value':body}]+[e['duty'] for e in duties])
    p['tea']={'status':'NOT_CALCULATED' if missing else 'PARTIAL_CALCULATION','inputs':body,'metrics':metrics,'missing_inputs':missing,'limitations':['CAPEX/OPEX/NPV/IRR/回收期缺少完整方法和投资现金流，不计算。','年度公用工程仅使用已有正 duty；未包含冷却费用、维护、人工和未报告设备。','统一单价/排放因子为用户假设，不代表全厂生命周期核算。']}
    event(p,'TEA prerequisites checked; missing economics remain NOT_CALCULATED');save(p);return p
''')
print('Backend domain schemas, skill tools, adapters, state machine and evaluator created.')

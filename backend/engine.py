import copy,datetime,json,re,uuid
from .store import ROOT,read_json,save
from .models import ProjectSpec,SimulationIR
from .skills import check_spec,execute_skill
from .adapters import adapter
from .evaluator import material_balance
from .case_variant import case_key, result_key
STEP_NAMES=['需求与设计基准','物性与数据校核','模型选择与验证','路线与分离筛选','流程搭建与收敛','能量与设备分析','参数与方案优化','经济与环境评价','复核与成果交付']
STEP_IDS=['STEP_01_DESIGN_BASIS','STEP_02_PROPERTY_VALIDATION','STEP_03_MODEL_SELECTION','STEP_04_ROUTE_SCREENING','STEP_05_SIMULATION','STEP_06_ENERGY_EQUIPMENT','STEP_07_OPTIMIZATION','STEP_08_TEA_ENVIRONMENT','STEP_09_VALIDATION_DELIVERY']
SKILLS=['chemflow-intake','chemflow-property-modeling','chemflow-property-modeling','chemflow-process-synthesis','chemflow-simulation-review','chemflow-simulation-review','chemflow-optimization-tea','chemflow-optimization-tea','chemflow-validation']
def event(p,message):p['events'].append({'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'message':message});p['revision']+=1

def create(name,dataset,mode,backend):
    p={'id':str(uuid.uuid4()),'name':name,'dataset':dataset,'mode':mode,'backend':backend,'max_step':1,'completed':[],'status':'IN_PROGRESS','revision':0,'route':None,'model':None,'ir':None,'result':None,'review':None,'optimization':None,'tea':None,'validation':None,'approvals':{},'events':[]}
    from .design_basis import load_input
    p['input_schema_version']=8
    p['spec']=load_input('pyridine525' if dataset=='pyridine' else dataset);p['spec']['project_id']=p['id']
    # Keep the reference result archive server-side; new tasks start with empty user-entered fields.
    for f in p['spec'].get('feeds',[]):
        for key in ('temperature','pressure','mass_flow','molar_flow'):
            q=f.get(key)
            if q:
                q.update({'value':None,'source_type':'USER_INPUT','source_name':'人工输入','status':'UNVERIFIED','locator':''})
    p['spec']['reaction'].update({'equation':'','source_type':'USER_INPUT','source_name':'人工输入'})
    for target in p['spec'].get('target_products',[])+p['spec'].get('byproducts',[]):
        target.update({'name':'','purity':None,'source_type':'USER_INPUT','source_name':'人工输入'})
    p['input_schema_version']=8
    ProjectSpec.model_validate(p['spec']);event(p,'Created task with empty user input fields');save(p);return p

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
    if p['dataset']=='custom':raise ValueError('自定义工程尚无已确认的流程拓扑数据')
    allowed=['route_a','route_b','route_c'] if p['dataset']=='pdh' else ['pyridine']
    if route not in allowed:raise ValueError('Route incompatible with dataset')
    base=ROOT/'data/validation'/(case_key(p['spec']) if route=='pyridine' else 'pdh/'+route)
    ir=read_json(base/'topology.json');ir['components']=p['spec']['components'];ir['property_method']=p['model'];return SimulationIR.model_validate(ir).model_dump()
def models(p):
    from .recommendations import models as candidates
    return candidates(p)

def run_simulation(p,persist=True):
    ensure(p,5)
    if p['dataset']=='custom':raise ValueError('该自定义工程尚未配置求解器与可追溯流程结果，不能载入其他案例数据')
    if not p['ir']:raise ValueError('No approved SimulationIR')
    result=adapter(p['mode'],p['backend']).run(p['spec'],SimulationIR.model_validate(p['ir'])).model_dump()
    if p['dataset']=='pdh' and p['backend']=='reference_replay':
        archive=read_json(ROOT/'data/reference_data/pdh_workbook.json')
        route_data=archive['routes'].get(p['route'])
        if route_data:
            result['workbook_streams']=route_data['streams']
            result['workbook_energy']=route_data['energy']
            result['workbook_source']={'source_file':archive['source_file'],'sha256':archive['sha256'],'flow_sheet':route_data['flow_sheet'],'energy_sheet':route_data['energy_sheet']}
            by_id={}
            for item in route_data['streams']:
                by_id.setdefault(item['stream_id'],item)
            for stream_id,stream in result['streams'].items():
                src=by_id.get(stream_id)
                if not src:continue
                for prop in src['properties']:
                    rec=prop['source'];field={'value':prop['value'],'unit':prop['unit'],'source_type':'IMPORTED_INPUT','source_name':archive['source_file'],'version':archive['sha256'][:16],'locator':f"{rec['sheet']}!{rec['cell']}",'status':'REFERENCE'}
                    if prop['property']=='molar_flow':stream['molar_flow']=field
                    else:stream.setdefault('workbook_properties',{})[prop['property']]=field
                stream['workbook_composition']={c['component_id']:{'value':c['value'],'unit':c['unit'],'source_type':'IMPORTED_INPUT','source_name':archive['source_file'],'version':archive['sha256'][:16],'locator':f"{c['source']['sheet']}!{c['source']['cell']}",'status':'REFERENCE'} for c in src['composition']}
    p.pop('reference_load_error',None)
    p['result']=result;issues=[]
    for n,s in result['streams'].items():
        if s['temperature']['status']=='ANOMALY':issues.append(n+': SOURCE ANOMALY，异常低温原值未修改')
    balance=material_balance(result)
    if balance['relative_error']>read_json(ROOT/'config/validation_thresholds.json')['material_balance_relative']:issues.append('外部质量衡算超出阈值，需审核源结果边界')
    if p['dataset']=='pyridine':issues.extend(result['notes'] if case_key(p['spec'])=='pyridine525' else ['PY-R/B2 源模型计算警告'])
    p['review']={'status':'NEEDS_HUMAN_REVIEW' if issues else ('SOLVED' if result['backend']=='DWSIM' else 'REPLAY_LOADED'),'issues':issues,'balance':balance,'solver_status':result['solver_status'],'converged':result['converged'],'energy_balance':'NOT_ASSESSED'}
    event(p,('DWSIM simulation solved: '+result['source']) if result['backend']=='DWSIM' else 'Reference fixture loaded; no independent solver executed')
    if persist:save(p)
    return p

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
        if not p['result']:raise ValueError('请先载入工程参考结果，或运行已连接的专业模拟器')
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
    p['completed'].append(step);p['max_step']=min(9,step+1);p['status']='COMPLETE' if step==9 else 'IN_PROGRESS';event(p,f'Step {step:02d} confirmed: {STEP_NAMES[step-1]}')
    if step==4 and p['mode']=='reference' and p['backend']=='reference_replay':
        from .adapters import SnapshotMismatch
        try:run_simulation(p)
        except SnapshotMismatch as exc:
            p['reference_load_error']=str(exc);event(p,'参考数据未自动加载：设计基准与归档不同')
    save(p);return p

def parse_intake(text,spec):
    from .intake import parse
    return parse(text,spec)


def optimize(p,body):
    ensure(p,7)
    variables=body.get('variables',{})
    allowed={'column_pressure','reflux_ratio','feed_stage','compressor_ratio','split_fraction','stage_count','entrainer_flow'}
    import math
    for k,v in variables.items():
        if k not in allowed or isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<=0 or (k in ('feed_stage','stage_count') and not float(v).is_integer()) or (k=='split_fraction' and v>1) or (k=='compressor_ratio' and v<1):raise ValueError('Invalid optimization variable value')
    if variables.get('feed_stage',0)>variables.get('stage_count',float('inf')):raise ValueError('进料板位置不得大于塔板数')
    unit_id=body.get('unit_id','')
    if variables and unit_id not in {u['id'] for u in p['ir']['units']}:raise ValueError('请选择优化变量所属的设备')
    p['optimization']={'status':'OPTIMIZATION_PREVIEW','unit_id':unit_id,'variables':{k:{'value':v,'unit':{'column_pressure':'bar','feed_stage':'stage','stage_count':'stage','entrainer_flow':'kmol/h'}.get(k,'ratio'),'source_type':'USER_INPUT','source_name':'优化问题设置','version':'1','status':'NOT_SOLVED'} for k,v in variables.items()},'bounds':body.get('bounds',{}),'constraints':['满足 Step1 已确认产品摩尔分率目标','在真实模拟器中收敛'],'objectives':['min thermal_duty','min electrical_duty'],'candidate_selected':p['route'] if body.get('select_baseline') else None,'candidate_status':'SIMULATED_BASELINE' if p['backend']=='dwsim' else 'REFERENCE_BASELINE','message':'参数未运行新模拟，图中参考点不随滑块伪变化'}
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
        product=p['result']['streams'][('PY' if case_key(p['spec'])=='pyridine525' else '4') if p['dataset']=='pyridine' else 'PRO-D']['mass_flow'];metrics['Annual Product Revenue']=calc(product['value']*hours*body['product_price'],currency+'/year','gross product stream kg/h × hours × price; not pure-product revenue',[product,{'source_type':'USER_INPUT','source_name':'TEA form','value':body}])
        if duties and body.get('carbon_factor') is not None:metrics['Carbon']=calc(positive*hours*body['carbon_factor'],'kgCO2e/year','positive duty kW × hours × user uniform factor (boundary partial)',[{'source_type':'USER_INPUT','source_name':'TEA form','value':body}]+[e['duty'] for e in duties])
    p['tea']={'status':'NOT_CALCULATED' if missing else 'PARTIAL_CALCULATION','inputs':body,'metrics':metrics,'missing_inputs':missing,'limitations':['CAPEX/OPEX/NPV/IRR/回收期缺少完整方法和投资现金流，不计算。','年度公用工程仅使用已有正 duty；未包含冷却费用、维护、人工和未报告设备。','统一单价/排放因子为用户假设，不代表全厂生命周期核算。']}
    event(p,'TEA prerequisites checked; missing economics remain NOT_CALCULATED');save(p);return p

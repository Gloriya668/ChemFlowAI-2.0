from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'frontend/src/pages/Steps.tsx';s=p.read_text()
s="import {ModelWorkspace,RouteWorkspace} from '../components/DecisionWorkspace';\nimport {EvidencePanel} from '../components/EvidencePanel';\n"+s
a=s.index(' if(step===3)return');b=s.index(" if(step===4&&",a)
s=s[:a]+" if(step===3)return <ModelWorkspace p={p} model={model} setModel={setModel} canEdit={canEdit}/>;\n"+s[b:]
a=s.index(' if(step===4){');b=s.index(' if(step===5&&',a)
s=s[:a]+" if(step===4)return <RouteWorkspace p={p} route={route} setRoute={setRoute} canEdit={canEdit} run={run}/>;\n"+s[b:]
for step in range(6,10):s=s.replace(f' if(step==={step})return <>',f' if(step==={step})return <><EvidencePanel p={{p}} step={{{step}}}/>')
old='已收到投资费用、产品成本、收入、财务分析及吡啶经济分析资料。当前文件涉及不同装置/产品，部分报告的封面与正文范围不一致；在确认哪些表格属于本工程前，不导入其中的投资、价格、成本、回收期或收益数字。请补充本项目对应的权威文件及基准年、币种和产能口径。'
s=s.replace(old,'资料中的经济数值、页码和冲突已列在上方。下表用于独立填写本次核算假设，缺失项不会按零计算。请先统一年运行小时、价格版本和核算边界。')
s=s.replace("const [vars,setVars]=useState<Record<string,number>>({});","const [vars,setVars]=useState<Record<string,number>>({});const [unitId,setUnitId]=useState(p.optimization?.unit_id||'');")
a=s.index('{Object.keys(vars).length?');b=s.index('<button className="full-width"',a)
s=s[:a]+'''<label>变量所属设备<select aria-label="优化设备" value={unitId} disabled={!canEdit} onChange={e=>{setUnitId(e.target.value);setVars({})}}><option value="">请选择设备</option>{p.ir.units.map((u:any)=><option value={u.id} key={u.id}>{u.id} · {u.type}</option>)}</select></label><div className="form-grid two" style={{margin:'14px 0'}}>{[['column_pressure','操作压力 / bar'],['reflux_ratio','回流比 / mol·mol⁻¹'],['stage_count','塔板数'],['feed_stage','进料板'],['compressor_ratio','压比'],['entrainer_flow','共沸剂流量 / kmol·h⁻¹']].map(([key,label])=><label key={key}>{label}<input type="number" min="0" step={key.includes('stage')?'1':'any'} disabled={!canEdit||!unitId} value={vars[key]??''} onChange={e=>{const v={...vars};if(e.target.value==='')delete v[key];else v[key]=Number(e.target.value);setVars(v)}}/></label>)}</div><Notice>可依据上方资料输入候选参数；这里只保存设备参数，不冒充已运行的优化结果。搜索边界和求解器仍需补充。</Notice>'''+s[b:]
s=s.replace("variables:vars,bounds:","variables:vars,unit_id:unitId,bounds:")
p.write_text(s,encoding='utf-8')
# Store device scope and dimensionally correct units.
p=R/'backend/engine.py';s=p.read_text();s=s.replace("'status':'OPTIMIZATION_PREVIEW','variables'","'status':'OPTIMIZATION_PREVIEW','unit_id':unit_id,'variables'")
s=s.replace("{'column_pressure':'bar','feed_stage':'stage'}","{'column_pressure':'bar','feed_stage':'stage','stage_count':'stage','entrainer_flow':'kmol/h'}")
s=s.replace("'满足产品目标（待输入）'","'满足 Step1 已确认产品摩尔分率目标'")
# Reference result loading on entering Step5; mismatch stays explicit.
old="event(p,f'Step {step:02d} confirmed: {STEP_NAMES[step-1]}');save(p);return p"
new="""event(p,f'Step {step:02d} confirmed: {STEP_NAMES[step-1]}')
    if step==4 and p['mode']=='reference' and p['backend']=='reference_replay':
        from .adapters import SnapshotMismatch
        try:run_simulation(p)
        except SnapshotMismatch as exc:
            p['reference_load_error']=str(exc);event(p,'参考数据未自动加载：设计基准与归档不同')
    save(p);return p"""
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=R/'frontend/src/pages/Steps.tsx';s=p.read_text();s=s.replace(' if(step===5)return <>',' if(step===5)return <>{p.reference_load_error&&<Notice tone="red">{p.reference_load_error}</Notice>}');p.write_text(s,encoding='utf-8')
# VLE evidence no longer describes all data as missing.
p=R/'backend/skills.py';s=p.read_text().replace('输入表不含独立纯组分临界参数、完整 BIP 和实验 VLE。','已接入有来源的物性常数与二元参数；C3 实验 VLE 来自 NIST ThermoML，覆盖率与适用范围见物性工作区。');p.write_text(s,encoding='utf-8')
print('Integrated decisions, evidence and scoped optimization')

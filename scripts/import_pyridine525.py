"""Reproducible import of the supplied closed-loop case. No solver is executed."""
import copy, csv, hashlib, json, re, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
with zipfile.ZipFile(source) as z:
    candidates = [n for n in z.namelist() if n.lower().endswith('.bkp')]
    assert len(candidates) == 1
    raw = z.read(candidates[0])
text = raw.decode('gb18030', errors='replace')
summary = text.split('$_SUMMARY_FILE', 1)[1].split('$_ADS_FILE', 1)[0]
sha = hashlib.sha256(source.read_bytes()).hexdigest()
components = ['THFA','NH3','Pyridine','Water','H2','n-Hexane','Methanol','3-Methylpyridine','2-Aminopyridine']
def record(value, unit, locator, status='REFERENCE'):
    return dict(value=value,unit=unit,source_type='IMPORTED_INPUT',source_name=source.name,version=sha[:16],locator=locator,status=status)
def tokens(body):
    return re.sub(r'<[^>]+>', '', body).split()
def number(s):
    return None if s == '*' else float(s.replace('D','E'))
def dsets(category, name):
    return re.findall(r'DSET '+category+r' (\S+) '+name+r' @\S+\s*\((.*?)\)', summary, re.S)
streams = {}
for sid, body in dsets('STREAM MATERIAL', 'RES_STR'):
    v = list(map(number, tokens(body)))
    assert len(v) == 6 and all(x is not None for x in v)
    loc = 'SUMMARY/STREAM/'+sid+'/RES_STR'
    streams[sid] = dict(stream_id=sid,component_ids=components,temperature=record(v[0],'C',loc,'ANOMALY' if v[0]<-200 else 'REFERENCE'),pressure=record(v[1],'bar',loc),mass_flow=record(v[2],'kg/h',loc),molar_flow=record(v[4],'kmol/h',loc),vapor_fraction=record(v[5],'mol/mol',loc),composition={})
connections = []; enthalpy = {}
for sid, body in dsets('STREAM MATERIAL','STR_MAIN'):
    t = tokens(body); assert t[3] == 'NRTL'
    connections.append(dict(stream_id=sid,from_unit=None if t[0]=='*' else t[0],to_unit=None if t[1]=='*' else t[1]))
    streams[sid]['phase'] = record(t[2],'','SUMMARY/STREAM/'+sid+'/STR_MAIN')
    # STR_MAIN: four identifiers, four arrays of nine component properties,
    # then mole/mass/volume flow, T/P, phase fractions and three enthalpy fields.
    values = list(map(number,t[4:])); assert len(values)>46
    for c, value in zip(components,values[9:18]):
        streams[sid]['composition'][c] = record(value,'mol/mol','SUMMARY/STREAM/'+sid+'/STR_MAIN/MOLEFRAC/'+c)
    assert abs(sum(q['value'] for q in streams[sid]['composition'].values())-1)<1e-6
    enthalpy[sid] = values[46]
assert len(streams)==14 and len(connections)==14
definitions = [('PY-R','RYIELD','REACTOR','产率反应器'),('SPR','FLASH2','FLASH','气液闪蒸分离器'),('2AP-SPR','RADFRAC','TOWER','2-氨基吡啶分离塔'),('3-PY-SPR','RADFRAC','TOWER','3-甲基吡啶分离塔'),('PY-SPR','MIXER','MIXER','循环溶剂混合器'),('MIXER','RADFRAC','TOWER','吡啶精制塔'),('DECANTER','DECANTER','DECANTER','液液分相器')]
units=[]; equipment=[]
for uid, model, kind, label in definitions:
    m=re.search(r'\?\s*BLOCK\s+'+model+r'\s+"?'+re.escape(uid)+r'"?\s*\?(.*?)(?=\?\s*(?:BLOCK|STREAM|CONVERGENCE|REPORT|FLOWSHEET)|\$_)',text,re.S)
    assert m, uid
    body=m.group(1); rows=[]; params={}
    for key, title, unit in [('TEMP','温度','C'),('PRES','压力','bar'),('NSTAGE','理论级数（含端级）','stage'),('FEED-STAGE','进料级','stage'),('BASIS-RR','摩尔回流比','mol/mol'),('BASIS-B','塔底摩尔流量','kmol/h'),('L2-CUTOFF','第二液相截断值','')]:
        hit=re.search(r'(?<![\w-])'+key+r'\s*=\s*([\d.]+)(?:\s*<([^>]+)>\s*<([^>]+)>)?',body)
        if hit:
            value=float(hit[1]); actual_unit='kPa' if key=='PRES' and hit[3]=='10' else unit
            rows.append(dict(label=title,key=key,value=value,unit=actual_unit,context=model,raw=hit[0]))
            params[key]=record(value,actual_unit,'INPUT/BLOCK/'+uid+'/'+key)
    # RadFrac top pressure uses PRES1, not PRES.
    hit=re.search(r'PRES1\s*=\s*([\d.]+)\s*<20>\s*<(\d+)>',body)
    if hit:
        value=float(hit[1]); unit='kPa' if hit[2]=='10' else 'bar'
        rows.append(dict(label='塔顶压力',key='PRES1',value=value,unit=unit,context=model,raw=hit[0]));params['PRES1']=record(value,unit,'INPUT/BLOCK/'+uid+'/PRES1')
    if model=='RADFRAC':rows.append(dict(label='冷凝器形式',key='CONDENSER',value='TOTAL / 全凝器',unit='',context=model,raw='CONDENSER = TOTAL'))
    if model=='RYIELD':
        for cid,y in re.findall(r'CID\s*=\s*"?([\w-]+)"?\s+SSID\s*=\s*MIXED\s+MOLE-YIELD\s*=\s*([\d.]+)',body):
            rows.append(dict(label='产率权重 '+cid,key='MOLE-YIELD',value=float(y),unit='相对权重',context=model,raw=f'{cid}: {y}',note='源模型归一化以维持质量平衡；不是百分比或实际产物流量。'))
    if model=='DECANTER':rows.append(dict(label='第二液相关键组分',key='L2-COMPS',value='Water',unit='',context=model,raw='L2-COMPS = ( WATER )'))
    equipment.append(dict(id=uid,label=label,model=model,locator='INPUT/BLOCK/'+uid,rows=rows,note='设备位号保留原定义，设备类型按模型识别。'))
    units.append(dict(id=uid,type=kind,label=label,parameters=params))
topology=dict(route_id='pyridine',title='四氢糠醇制吡啶 · 分相与溶剂循环',units=units,streams=connections,connections=connections,energy_streams=[],source=dict(file=source.name,sha256=sha,variant='pyridine525'))
notes=['PY-R：指定产率已归一化以维持质量平衡。','MIXER（精制塔）：进料压力低于进料级压力（0.1 bar → 1 bar），需核查增压设备。','A-S2、A-S3 温度低于 −200°C，保留源值并待复核。','已导入源模型结果；本工作台未执行独立求解。']
# METCBAR inherits MET enthalpy-flow unit (13), selector 3 = CAL/SEC.
# Unit conversion follows Summary File Toolkit unit table; retain original values.
energy=[]
for uid,body in dsets('BLOCK RADFRAC','RESD'):
    for i,label in enumerate(['冷凝器','再沸器']):
        rawq=number(tokens(body)[i]); q=record(rawq*0.004184,'kW','SUMMARY/BLOCK/'+uid+'/RESD/'+str(i))
        q.update(source_type='CALCULATED',formula='cal/s × 4.184 / 1000 = kW',parents=[record(rawq,'cal/s','SUMMARY/BLOCK/'+uid+'/RESD/'+str(i))])
        energy.append(dict(id=uid+' '+label,duty=q))
for uid,model,kind,label in definitions:
    if model=='RADFRAC':continue
    ins=[c['stream_id'] for c in connections if c['to_unit']==uid];outs=[c['stream_id'] for c in connections if c['from_unit']==uid]
    q=record((sum(enthalpy[s] for s in outs)-sum(enthalpy[s] for s in ins))*0.004184,'kW','SUMMARY/STREAM/STR_MAIN/HFLMX')
    q.update(source_type='CALCULATED',formula='(sum(outlet enthalpy flow)-sum(inlet enthalpy flow)) × 0.004184; from imported stream results',parents=[record(enthalpy[s],'cal/s',s+'/HFLMX') for s in ins+outs])
    energy.append(dict(id=uid+' 净热负荷（焓差）',duty=q))
result=dict(route_id='pyridine',backend='REFERENCE_REPLAY',solver_status='SOURCE_RESULTS_WITH_WARNINGS',converged=None,streams=streams,energy=energy,topology=topology,source=source.name,notes=notes)
spec=json.loads((ROOT/'data/validation/pyridine/input.json').read_text(encoding='utf-8'))
spec['feeds']=[{k:copy.deepcopy(streams[s][k]) for k in ['stream_id','component_ids','temperature','pressure','mass_flow','molar_flow','composition']} for s in ['THFA','NH3']]
spec['reaction']=dict(equation='THFA + NH3 → 吡啶、水、氢气及含氮副产物（RYIELD 产率模型）',source_type='IMPORTED_INPUT',source_name=source.name)
spec['source']=dict(source_type='IMPORTED_INPUT',source_name=source.name,version=sha[:16],variant='pyridine525',sha256=sha,request_text='四氢糠醇与氨制吡啶，分相及溶剂回流',property_method='NRTL',recycle_initial_molar_flow=176,recycle_stream_id='RE')
spec['target_products']=[dict(name='Pyridine',purity=None,source_type='IMPORTED_INPUT',source_name=source.name)]
def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
dump(ROOT/'data/validation/pyridine525/input.json',spec)
dump(ROOT/'data/validation/pyridine525/topology.json',topology)
dump(ROOT/'data/validation/pyridine525/ground_truth.json',result)
dump(ROOT/'data/replay/pyridine525.json',result)
ep=ROOT/'data/equipment_parameters.json';all_eq=json.loads(ep.read_text(encoding='utf-8'))
all_eq['pyridine525']=dict(file='四氢糠醇闭循环工艺',sha256=sha,notice='7 个单元；MIXER 为精制塔，PY-SPR 为混合器。循环 RE 不计入外部进料。',units=equipment);dump(ep,all_eq)
out=ROOT/'outputs/pyridine525';out.mkdir(parents=True,exist_ok=True)
dump(out/'equipment.json',equipment);dump(out/'streams.json',streams)
with (out/'streams.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['stream','from','to','T_C','P_bar','kg_h','kmol_h','vapor_fraction']+components)
    for c in connections:
        s=streams[c['stream_id']];w.writerow([s['stream_id'],c['from_unit'],c['to_unit']]+[s[k]['value'] for k in ['temperature','pressure','mass_flow','molar_flow','vapor_fraction']]+[s['composition'][k]['value'] for k in components])
print(json.dumps(dict(units=len(units),streams=len(streams),energy=len(energy),product_kg_h=streams['PY']['mass_flow']['value'],purity=streams['PY']['composition']['Pyridine']['value'],equipment_rows={x['id']:len(x['rows']) for x in equipment})))

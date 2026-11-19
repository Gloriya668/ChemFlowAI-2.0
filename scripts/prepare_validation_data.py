"""Read original Excel only at preparation time. No frontend benchmark files."""
from pathlib import Path
import ast,copy,hashlib,json,re,xml.etree.ElementTree as ET
import xlrd,openpyxl
ROOT=Path(__file__).resolve().parents[1]
ASSETS=Path(r'E:\CodexOutputs\Aspen流程可视化')
PDH=Path(r'E:\Desktop\丙烯丙烷数据最最最最终版.xls');PYR=Path(r'E:\Desktop\四氢糠醇_所有流股结果.xlsx')
def dump(path,obj):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def val(value,unit,filename,sheet,cell,status='REFERENCE'):
 return {'value':value,'unit':unit,'source_type':'ASPEN_REFERENCE','source_name':filename.name,'version':hashlib.sha256(filename.read_bytes()).hexdigest()[:16],'locator':sheet+'!'+cell,'status':status}
def col(c):return openpyxl.utils.get_column_letter(c+1)
def normalize_unit(value,unit,target):
 factors={('kPa','bar'):.01,('MPa','bar'):10,('kg/s','kg/h'):3600,('kg/hr','kg/h'):1,('cal/sec','kW'):.004184,('Gcal/day','kW'):4184000/86400}
 if unit==target:return value
 if (unit,target)==('K','C'):return value-273.15
 if (unit,target) not in factors:raise ValueError('Unsupported unit conversion')
 return value*factors[(unit,target)]
def read_topologies():
 tree=ast.parse((ASSETS/'build.py').read_text(encoding='utf-8-sig'));body=[]
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name in ('node','edge'):body.append(n)
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('D','common','ce') for t in n.targets):body.append(n)
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='D':body.append(n)
 env={};exec(compile(ast.Module(body=body,type_ignores=[]),'<trusted-existing-asset-topology>','exec'),env)
 return env['D']
def main():
 specs=read_topologies();wb=xlrd.open_workbook(str(PDH));routes={}
 maps={
 'route_a':{'FEED':(None,'REACTOR'),'REACT':('REACTOR','COOLER'),'COOL-OUT':('COOLER','FLASH'),'H2':('FLASH',None),'HEAT-IN':('FLASH','HEATER'),'HEAT-OUT':('HEATER','COLUMN'),'PRO-D':('COLUMN',None),'PRO-B':('COLUMN',None)},
 'route_b':{'FEED':(None,'REACTOR'),'REACT':('REACTOR','COOLER1'),'COO-OUT':('COOLER1','FLASH1'),'H2':('FLASH1',None),'HEAT-IN':('FLASH1','HEATER'),'HEAT-OUT':('HEATER','HPD'),'COMP-IN':('HPD','COMPR'),'COMP-OUT':('COMPR','REBOILER'),'REB-IN':('HPD','REBOILER'),'REB-OUT':('REBOILER','ASSI-REB'),'FLA-IN':('ASSI-REB','FLASH2'),'FLA-OUT':('FLASH2','HPD'),'PRO-B':('FLASH2',None),'VALVE-IN':('REBOILER','VALVE'),'COOL-IN':('VALVE','COOLER2'),'COOL-OUT':('COOLER2','SPLITTER'),'REFLUX':('SPLITTER','HPD'),'PRO-D':('SPLITTER',None)},
 'route_c':{'FEED':(None,'REACTOR'),'REACT':('REACTOR','COOLER'),'COOL-OUT':('COOLER','FLASH'),'H2':('FLASH',None),'HEAT-IN':('FLASH','HEATER'),'HEAT-OUT':('HEATER','STRIP'),'COMP-IN':('STRIP','COMP'),'COMP-OUT':('COMP','RECT'),'REFLUX':('VALVE','STRIP'),'VALVE-IN':('RECT','VALVE'),'PRO-D':('RECT',None),'PRO-B':('STRIP',None)},
 'pyridine':{'NH3':(None,'PY-R'),'THFA':(None,'PY-R'),'A-R':('PY-R','2AP-SPR'),'H2':('2AP-SPR',None),'A-S1':('2AP-SPR','SPR'),'A-S2':('SPR','3-PY-SPR'),'2AP':('SPR',None),'A-S3':('3-PY-SPR','B4'),'3-PY':('3-PY-SPR',None),'1':(None,'B4'),'6':('B4','B2'),'3':('B2',None),'4':('B2',None)}}
 route_indices={'route_a':0,'route_b':2,'route_c':1,'pyridine':3}
 needles={'route_a':'1-普通精馏 物流','route_b':'2-热泵精馏 物流','route_c':'3-内部热耦合精馏 物流结果（耦合后）'}
 for route,needle in needles.items():
  sh=next(s for s in wb.sheets() if s.name.startswith(needle));rows=[sh.row_values(i) for i in range(sh.nrows)];streams={}
  for base in [0,rows[0].index('结果')+1]:
   keys={rows[i][base]:i for i in range(len(rows)) if rows[i][base]}
   for c in range(base+2,sh.ncols):
    name=rows[0][c]
    if not name or name=='结果':break
    if name in streams:continue
    def cell(label,unit):
     r=keys.get(label)
     return val(rows[r][c] if r is not None and isinstance(rows[r][c],(int,float)) else None,unit,PDH,sh.name,f'{col(c)}{r+1}' if r is not None else 'N/A')
    vapor=cell('摩尔汽相分率','fraction');phase=rows[keys['相态']][c]
    if not phase:phase='两相' if vapor['value'] is not None and 0<vapor['value']<1 else '未知'
    compositions={}
    for ri,row in enumerate(rows):
     if isinstance(row[base],str) and row[base] in ('PROPA-01','PROPY-01','HYDRO-01') and isinstance(row[c],(int,float)):
      compositions[row[base]]=val(row[c],'fraction',PDH,sh.name,f'{col(c)}{ri+1}')
    streams[name]={'stream_id':name,'temperature':cell('温度','C'),'pressure':cell('压力','bar'),'mass_flow':cell('质量流量','kg/h'),'phase':val(phase,'',PDH,sh.name,f'{col(c)}{keys["相态"]+1}'),'vapor_fraction':vapor,'composition':compositions}
  energy=[]
  prefix={'route_a':'1-普通精馏 能量','route_b':'2-热泵精馏 能量','route_c':'3-内部热耦合精馏 耦合后能耗'}[route]
  es=next(s for s in wb.sheets() if s.name.startswith(prefix));group='设备'
  for ri in range(es.nrows):
   row=es.row_values(ri)
   if row[0] and len(row)>1 and row[1]=='':group=str(row[0])
   if row[0] in ('热负荷','负荷','压缩机功率') and isinstance(row[1],(int,float)):
    unit=row[2];raw=val(row[1],unit,PDH,es.name,f'B{ri+1}');v=copy.deepcopy(raw)
    if unit!='kW':v.update(value=normalize_unit(row[1],unit,'kW'),unit='kW',source_type='CALCULATED',formula=('cal/s × 0.004184' if unit=='cal/sec' else 'Gcal/day × 1e9 × 4.184 / 86400 / 1000'),parents=[raw])
    energy.append({'id':('压缩机功率' if row[0]=='压缩机功率' else group),'duty':v})
   for ci in range(3,len(row)-2):
    if isinstance(row[ci],str) and any(t in row[ci] for t in ('辅助再沸器负荷','压缩机负荷')) and isinstance(row[ci+1],(int,float)) and row[ci+2]=='kW':energy.append({'id':row[ci],'duty':val(row[ci+1],'kW',PDH,es.name,f'{col(ci+1)}{ri+1}')})
  routes[route]={'streams':{k:streams[k] for k in maps[route]},'energy':energy,'source':PDH.name,'notes':['仅回放存档，未新求解。','不同段结果存在质量不闭合，不自动校正。']}
 pw=openpyxl.load_workbook(PYR,data_only=True);sh=pw['流股总表'];streams={}
 for c in range(3,16):
  name=str(sh.cell(1,c).value)
  def pc(r,u):return val(sh.cell(r,c).value,u,PYR,sh.title,f'{openpyxl.utils.get_column_letter(c)}{r}','ANOMALY' if r==9 and name in ('A-S2','A-S3') else 'REFERENCE')
  streams[name]={'stream_id':name,'temperature':pc(9,'C'),'pressure':pc(10,'bar'),'mass_flow':pc(7,'kg/h'),'phase':pc(4,''),'vapor_fraction':pc(11,'fraction'),'composition':{}}
 for rownum,r in enumerate(pw['组分结果'].iter_rows(min_row=2,values_only=True),start=2):
  name=str(r[0]);streams[name]['composition'][r[1]]=val(r[6],'mass fraction',PYR,'组分结果',f'G{rownum}')
 routes['pyridine']={'streams':streams,'energy':[],'source':PYR.name,'notes':['开循环结果，不含分相器与回流。','A-S2/A-S3 为异常低温原值。','PY-R/B2 存档存在警告；未重新求解。']}
 ns={'s':'http://www.w3.org/2000/svg'};ET.register_namespace('',ns['s'])
 html=(ASSETS/'Aspen流程动画.html').read_text(encoding='utf-8');svgs=re.findall(r'<svg\b.*?</svg>',html,re.S)
 for route,result in routes.items():
  title,slug,nodes,edges=specs[route_indices[route]]
  topology={'route_id':route,'title':title,'units':[{'id':n[0],'type':n[1].upper(),'label':n[4],'parameters':{}} for n in nodes],'streams':[{'stream_id':e[0],'from_unit':maps[route][e[0]][0],'to_unit':maps[route][e[0]][1]} for e in edges],'connections':[{'stream_id':n,'from_unit':v[0],'to_unit':v[1]} for n,v in maps[route].items()],'energy_streams':[],'source':{'source_type':'USER_INPUT','source_name':'既有已审核流程可视化资产','version':'2026-10-06'}}
  result.update(route_id=route,backend='REFERENCE_REPLAY',solver_status='REPLAY_NOT_SOLVED',converged=None,topology=topology)
  base=f'data/validation/pdh/{route}' if route!='pyridine' else 'data/validation/pyridine'
  dump(base+'/topology.json',topology);dump(base+'/ground_truth.json',result);dump('data/replay/'+route+'.json',result)
  svg=ET.fromstring(svgs[route_indices[route]])
  for i,g in enumerate(svg.findall('.//s:g[@class="stream-label"]',ns)):
   g.set('data-stream-id',edges[i][0]);g.set('role','button');g.set('tabindex','0');g.set('aria-label','流股 '+edges[i][0])
   for t in list(g):
    if t.tag.endswith('title'):g.remove(t)
    elif t.get('data-key'):t.text='—'
  for i,g in enumerate(svg.findall('.//s:g[@class="equipment"]',ns)):
   g.set('data-equipment-id',nodes[i][0]);g.set('role','button');g.set('tabindex','0');g.set('aria-label','设备 '+nodes[i][0])
  for i,path in enumerate(svg.findall('.//s:path',ns)):
   pid=path.get('id','')
   match=re.search(r'-p(\d+)$',pid)
   if match:path.set('data-stream-id',edges[int(match.group(1))][0]);path.set('class','stream-pipe')
  for t in svg.findall('s:text',ns):
   if t.get('y')=='1380':t.text='Engineering visualization · 结构示意 / 原始数值由当前结果绑定'
  (ROOT/'data/assets'/f'{route}.svg').write_text(ET.tostring(svg,encoding='unicode'),encoding='utf-8')
 def feed(s):return {k:copy.deepcopy(s[k]) for k in ('stream_id','temperature','pressure','mass_flow','composition')}
 def spec(dataset,feeds,components,reaction,targets):return {'project_id':'','dataset':dataset,'components':[{'id':c,'name':c,'source_type':'USER_INPUT','source_name':'任务定义'} for c in components],'feeds':feeds,'reaction':{'equation':reaction,'source_type':'USER_INPUT','source_name':'任务定义'},'target_products':[{'name':t,'purity':None,'source_type':'USER_INPUT','source_name':'任务定义'} for t in targets],'capacity':None,'constraints':{},'utilities':{},'source':{'source_type':'ASPEN_REFERENCE','source_name':'仅进料输入；非下游标准答案','version':'1'}}
 pdh=spec('pdh',[feed(routes['route_a']['streams']['FEED'])],['C3H8','C3H6','H2'],'C3H8 → C3H6 + H2',['Propylene'])
 pyr=spec('pyridine',[feed(streams[k]) for k in ['THFA','NH3','1']],['THFA','NH3','Pyridine','Water','H2','n-Hexane','Methanol','3-Methylpyridine','2-Aminopyridine'],'THFA + NH3 → pyridine-related products（反应系数需工程确认）',['Pyridine'])
 dump('data/validation/pdh/input.json',pdh);dump('data/validation/pyridine/input.json',pyr)
 dump('data/catalog.json',{'datasets':[{'id':'pdh','title':'丙烷脱氢工程验证','description':'反应与 C3 分离 · 三条路线','routes':['route_a','route_b','route_c']},{'id':'pyridine','title':'四氢糠醇制吡啶工程验证','description':'多级分离 · 开循环存档','routes':['pyridine']}],'routes':[{'id':r,'title':specs[route_indices[r]][0]} for r in routes]})
 dump('data/preprocessing_manifest.json',{'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [PDH,PYR]],'asset_source':str(ASSETS),'counts':{r:len(x['streams']) for r,x in routes.items()},'replay_lineage':'same archived Aspen source as evaluator benchmark; not independent'})
 print('Prepared original Excel -> inputs, isolated benchmarks, replay fixtures and sanitized animated SVGs.')
if __name__=='__main__':main()

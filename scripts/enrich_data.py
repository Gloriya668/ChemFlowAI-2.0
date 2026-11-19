"""Reproducible extraction of supplied archives and downloaded public data."""
import json, hashlib, re, csv, itertools, shutil
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT.parent/'source_review'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
base='https://raw.githubusercontent.com/DanWBR/dwsim/windows/DWSIM.Thermodynamics/Assets/'
names={'Propane':('C3H8','丙烷'),'Propylene':('C3H6','丙烯'),'Hydrogen':('H2','氢气'),'Water':('Water','水'),'Ammonia':('NH3','氨'),'Pyridine':('Pyridine','吡啶'),'N-hexane':('n-Hexane','正己烷'),'Methanol':('Methanol','甲醇')}
comps={};ids={}
for filename in ['chemsep1.xml','chemsep2.xml']:
 for c in ET.parse(SRC/'web'/filename).findall('compound'):
  name=c.find('CompoundID').get('value')
  if name not in names:continue
  id,cn=names[name];get=lambda k: c.find(k).get('value')
  ids[get('LibraryIndex')]=id
  comps[id]={'id':id,'name':cn,'english':name,'cas':get('CAS'),'mw':float(get('MolecularWeight')),'tc':float(get('CriticalTemperature')),'pc':float(get('CriticalPressure'))/1e5,'omega':float(get('AcentricityFactor')),'source':'ChemSep v8.3 / DWSIM 官方仓库','url':base+'Databases/'+filename,'locator':'CompoundID='+name,'status':'DATABASE','note':'数据库推荐常数；Pc 由 Pa ÷ 100000 转为 bar，不代表本体系实验验证。'}
for id,cn,cas,mw in [('THFA','四氢糠醇','97-99-4',102.1317),('3-Methylpyridine','3-甲基吡啶','108-99-6',93.1265),('2-Aminopyridine','2-氨基吡啶','504-29-0',94.1145)]:
 comps[id]={'id':id,'name':cn,'english':id,'cas':cas,'mw':mw,'tc':None,'pc':None,'omega':None,'status':'PARTIAL','source':'NIST Chemistry WebBook（身份与分子量）','url':'https://webbook.nist.gov/cgi/cbook.cgi?ID=C'+cas.replace('-','')+'&Units=SI','note':'本次检索未取得可靠 Tc、Pc、ω；待补参数或有验证的估算。'}
pairs=[]
for file,model in [('pr_ip.dat','PR'),('nrtl.dat','NRTL')]:
 for n,line in enumerate((SRC/'web'/file).read_text().splitlines(),1):
  v=line.split(';')
  if len(v)<4 or v[0] not in ids or v[1] not in ids:continue
  a,b=ids[v[0]],ids[v[1]]
  if model=='PR' and not {a,b}<={'C3H8','C3H6','H2'}:continue
  if model=='NRTL' and ({a,b}&{'C3H8','C3H6'}):continue
  params={'kij':float(v[2])} if model=='PR' else {'Aij':float(v[2]),'Aji':float(v[3]),'alpha':float(v[4])}
  comment=v[3] if model=='PR' else v[5]
  pairs.append({'i':a,'j':b,'model':model,'parameters':params,'unit':'dimensionless' if model=='PR' else 'Aij/Aji: cal/mol; alpha: dimensionless','convention':'aij=(1-kij)√(ai·aj)' if model=='PR' else 'τij=Aij/(R·T), R=1.987204 cal/(mol·K); i/j 顺序不可互换','range':comment,'source':'ChemSep / DECHEMA 参数集，经 DWSIM 官方仓库分发','url':base+file,'locator':f'{file}: line {n}','status':'LITERATURE_PARAMETER','note':'保留多条拟合参数及其温压范围；不得跨模型或无条件外推。'})
vle=read(SRC/'web/vle.json');datasets=vle['PureOrMixtureData']
def vals(dataset):
 return {(tuple(sorted((v['nVarNumber'],v['nVarValue']) for v in r['VariableValue']))):r['PropertyValue'][0] for r in dataset['NumValues']}
ys=vals(datasets[3]);points=[]
for key,p in vals(datasets[2]).items():
 v=dict(key);y=ys[key];points.append({'T':v[2],'P':p['nPropValue']/100,'x':v[1],'y':y['nPropValue'],'uP':p['CombinedUncertainty']['nCombExpandUncertValue']/100,'uy':y['CombinedUncertainty']['nCombExpandUncertValue']})
experimental={'id':'nist-c3-2006','kind':'binary_pxy','components':['C3H6','C3H8'],'basis':'C3H6 mole fraction','source':'Ho et al. (2006), Fluid Phase Equilibria 245, 63–70 / NIST ThermoML','url':'https://trc.nist.gov/ThermoML/10.1016/j.fluid.2006.03.009.html','status':'EXPERIMENTAL','points':points,'note':'90 组实测 P–x–y，6 个温度；连线仅辅助阅读，不表示本平台已拟合模型。压力及气相摩尔分率不确定度保留于数据中。'}
propane_exp={'id':'nist-propane-2006','kind':'propane_pt','components':['C3H8'],'basis':'pure propane','source':experimental['source'],'url':experimental['url'],'status':'EXPERIMENTAL','points':[{'T':dict(k)[1],'P':v['nPropValue']/100} for k,v in vals(datasets[1]).items()]}
for dataset,cs in [('pdh',['C3H8','C3H6','H2']),('pyridine',['THFA','NH3','Pyridine','Water','H2','n-Hexane','Methanol','3-Methylpyridine','2-Aminopyridine'])]:
 ps=[p for p in pairs if p['i'] in cs and p['j'] in cs]; covered={frozenset((p['i'],p['j'])) for p in ps}
 obj={'components':{c:comps[c] for c in cs},'binary_data':{'pairs':ps,'covered_pairs':len(covered),'total_pairs':len(cs)*(len(cs)-1)//2,'missing_pairs':[' / '.join(p) for p in itertools.combinations(cs,2) if frozenset(p) not in covered]},'vle':[experimental,propane_exp] if dataset=='pdh' else [],'checked_at':'2026-10-08','source_status':'公开数据已导入；完整性与适用性分别核对'}
 write(ROOT/'data'/f'properties_{dataset}.json',obj)
write(ROOT/'data/property_data.json',{d:read(ROOT/'data'/f'properties_{d}.json') for d in ['pdh','pyridine']})
license_dir=ROOT/'docs/licenses';license_dir.mkdir(exist_ok=True)
shutil.copyfile(SRC/'web/Artistic_license_2_0.txt',license_dir/'ChemSep-Artistic-2.0.txt')
(license_dir/'DATA-NOTICE.txt').write_text('ChemSep v8.3 pure component data: Copyright Harry Kooijman and Ross Taylor (2021), Artistic License 2.0.\nInteraction parameter excerpts: ChemSep / DECHEMA, copyright 1992 Harry Kooijman and Ross Taylor; distributed in DWSIM Assets. See source URLs and row locators in data/property_data.json.\nNIST ThermoML data: Ho et al. (2006), DOI 10.1016/j.fluid.2006.03.009.\nSelected numerical records are redistributed with attribution; source material remains unchanged outside this project.\n',encoding='utf-8')
# Source-specific molar feeds from supplied presentation; never relabel a mass purity as a mole purity.
p=read(ROOT/'data/validation/pyridine/input.json')
for f in p['feeds']:
 f['molar_flow']={'value':{'THFA':25,'NH3':25,'1':176}[f['stream_id']],'unit':'kmol/h','source_type':'IMPORTED_INPUT','source_name':'吡啶课程答辩资料','locator':'slide 18' if f['stream_id']!='1' else 'slide 21','version':'2025-05','status':'REFERENCE'}
for d in ['pdh','pyridine']:
 s=p if d=='pyridine' else read(ROOT/'data/validation/pdh/input.json')
 for t in s['target_products']+s.get('byproducts',[]):
  if t.get('purity') and t['purity']['unit'] not in ['mol/mol','mole fraction']:t['purity']=None
 s['source']['request_text']='丙烷脱氢制丙烯' if d=='pdh' else '四氢糠醇与氨制吡啶'
 write(ROOT/'data/validation'/d/'input.json',s)
# Cross-check the user's new visualization CSV against all 51 archived streams.
route_map={'普通精馏':'route_a','热泵精馏':'route_b','内部热耦合精馏':'route_c','四氢糠醇':'pyridine'}
rows=list(csv.DictReader((SRC/'visualization/流股参数与来源.csv').open(encoding='utf-8-sig')))
audit=[]
for row in rows:
 name=row['流程'];rid=next((v for k,v in route_map.items() if k in name),None)
 if not rid:audit.append({'flow':name,'status':'UNMAPPED'});continue
 r=read(ROOT/'data/replay'/f'{rid}.json');s=r['streams'].get(row['流股名称'])
 errors={} if s else {'stream':'missing'}
 if s:
  for field,col in [('temperature','温度'),('pressure','压力'),('mass_flow','质量流量')]:
   if abs(s[field]['value']-float(row[col]))>1e-6:errors[field]=[s[field]['value'],float(row[col])]
 audit.append({'route':rid,'stream':row['流股名称'],'status':'MATCH' if not errors else 'CONFLICT','errors':errors,'locator':row['来源工作表']+'!'+row['源单元格（温度/压力/流量）']})
write(ROOT/'data/visualization_audit.json',audit)
print('Properties',len(comps),'BIP rows',len(pairs),'VLE',len(points),'visual streams',len(audit),'conflicts',[a for a in audit if a['status']!='MATCH'])

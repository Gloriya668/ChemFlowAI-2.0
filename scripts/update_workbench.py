from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
def edit(name,old,new):
 p=R/name;s=p.read_text(encoding='utf-8-sig')
 if old not in s:raise RuntimeError('Missing edit anchor '+name+' '+old[:80])
 p.write_text(s.replace(old,new),encoding='utf-8')
# Remove dangling imports in the supplied release; the existing task form is functional.
edit('frontend/src/main.tsx',"import {CaseFactory} from './pages/CaseFactory';",'')
edit('frontend/src/main.tsx','element={<CaseFactory/>}','element={<NewTask/>}')
edit('frontend/src/pages/Steps.tsx',"import {CustomCaseStep1} from './CustomCaseStep1';",'')
edit('frontend/src/pages/Steps.tsx'," if(step===1&&p.dataset==='custom')return <CustomCaseStep1 spec={draft} setSpec={setDraft}/>;",'')
edit('frontend/src/pages/Steps.tsx','<PropertyWorkspace dataset={p.dataset} components={p.spec.components}/>','<PropertyWorkspace dataset={p.dataset} components={p.spec.components} projectId={p.id} canEdit={canEdit}/>')
edit('frontend/src/pages/Steps.tsx','工程输入字段均为空白。请人工填写进料条件、反应和产品目标；确认后才会载入对应流股结果。','填写进料条件、反应和产品摩尔分率；也可载入本案例的资料基准后修改。')
edit('frontend/src/pages/Steps.tsx','<h3 style={{marginTop:18}}>Design Basis Completion</h3>',"<div className=\"button-row\"><button disabled={!canEdit||busy} onClick={()=>run(async()=>{const s=await api('/projects/'+p.id+'/reference-basis');setDraft(s)})}>载入资料中的设计基准</button></div><h3 style={{marginTop:18}}>Design Basis Completion</h3>")
edit('frontend/src/pages/Steps.tsx','六项最小必填字段','七项基准校核')
edit('frontend/src/pages/Steps.tsx','<Panel title="流股结果表"','<Panel title="流股结果表"')
edit('frontend/src/pages/Steps.tsx','<th>质量流量 / kg/h</th><th>状态</th>','<th>质量流量 / kg/h</th><th>摩尔流量 / kmol/h</th><th>状态</th>')
edit('frontend/src/pages/Steps.tsx','<td><Q q={s.mass_flow} onSource={onSource}/></td><td><Badge','<td><Q q={s.mass_flow} onSource={onSource}/></td><td><Q q={s.molar_flow} onSource={onSource}/></td><td><Badge')
# Reference import is deliberate, and the source migration must preserve it.
edit('backend/design_basis.py',"if p.get('input_schema_version')==7:return False","if p.get('input_schema_version') in (7,8):return False")
edit('backend/engine.py',"p['input_schema_version']=7","p['input_schema_version']=8")
# Expand the model catalog from the supplied textbook.
p=R/'backend/engine.py';s=p.read_text();a=s.index('def models(p):');b=s.index('\ndef run_simulation(p):',a);s=s[:a]+"def models(p):\n    from .recommendations import models as candidates\n    return candidates(p)\n"+s[b:];p.write_text(s,encoding='utf-8')
# Remove the brand everywhere the demo can display, including raw provenance and exports.
for folder in ['backend','data','config','frontend/src','skills']:
 for p in (R/folder).rglob('*'):
  if p.is_file() and p.suffix in ('.py','.json','.svg','.tsx','.ts','.md'):
   s=p.read_text(encoding='utf-8-sig');s=s.replace('ASPEN_REFERENCE','REFERENCE_DATA').replace('AspenMCPAdapter','ExternalMCPAdapter').replace('aspen_mcp','external_mcp').replace('ASPEN INPUT','INPUT')
   s=re.sub('aspen', '工程归档', s, flags=re.I)
   p.write_text(s,encoding='utf-8')
# Models retain the same provenance schema but a neutral source label.
print('Step 1, branding, source build repairs applied')

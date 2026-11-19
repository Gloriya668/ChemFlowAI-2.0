from pathlib import Path
import json,re
P=Path(r'E:\CodexOutputs\ChemFlowAI')
f=P/'backend/engine.py';s=f.read_text(encoding='utf-8');s=s.replace("SKILLS=['chemflow-intake'", "STEP_IDS=['STEP_01_DESIGN_BASIS','STEP_02_PROPERTY_VALIDATION','STEP_03_MODEL_SELECTION','STEP_04_ROUTE_SCREENING','STEP_05_SIMULATION','STEP_06_ENERGY_EQUIPMENT','STEP_07_OPTIMIZATION','STEP_08_TEA_ENVIRONMENT','STEP_09_VALIDATION_DELIVERY']\nSKILLS=['chemflow-intake'");f.write_text(s,encoding='utf-8')
f=P/'backend/app.py';s=f.read_text(encoding='utf-8').replace("d['step']=step;return d", "d['step']=step;d['workflow_state']=engine.STEP_IDS[p['max_step']-1];return d");f.write_text(s,encoding='utf-8')
f=P/'requirements.txt';s=f.read_text(encoding='utf-8');f.write_text(s+'PyYAML==6.0.3\n' if 'PyYAML' not in s else s,encoding='utf-8')
f=P/'backend/skills.py';s=f.read_text(encoding='utf-8');s=s.replace("if not spec.feeds or not spec.components:errors.append('必须提供组分与进料')", "if not spec.feeds or not spec.components:errors.append('必须提供组分与进料')\n    if len({f.stream_id for f in spec.feeds})!=len(spec.feeds):errors.append('进料标识重复')\n    for target in spec.target_products:\n        if target.purity and (not isinstance(target.purity.value,(int,float)) or not 0<=target.purity.value<=1):errors.append('目标纯度应为 0–1 分率')");f.write_text(s,encoding='utf-8')
# Export the backend-owned schema used for API and file intake.
import sys;sys.path.insert(0,str(P))
from backend.models import ProjectSpec,SimulationIR,SimulationResult,SkillResult
for name,model in [('ProjectSpec',ProjectSpec),('SimulationIR',SimulationIR),('SimulationResult',SimulationResult),('SkillResult',SkillResult)]:
 (P/'config'/f'{name}.schema.json').write_text(json.dumps(model.model_json_schema(),ensure_ascii=False,indent=2),encoding='utf-8')
refs=[]
for f in (P/'reference').rglob('code.html'):
 text=f.read_text(encoding='utf-8');headings=re.findall(r'<h[12][^>]*>(.*?)</h[12]>',text,re.S);headings=[re.sub('<[^>]+>','',h).strip() for h in headings]
 refs.append(f'- {f.parent.name}: '+ '; '.join(headings[:3]) +f'；HTML {len(text)} 字符；只作布局参考。')
with (P/'docs/ASSET_AUDIT.md').open('a',encoding='utf-8') as f:f.write('\n## 全部 Stitch 页面清单\n'+'\n'.join(refs)+'\n')
print('State IDs, shared JSON schemas, intake guards and full Stitch page index saved.')

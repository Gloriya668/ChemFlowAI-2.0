from pathlib import Path
P=Path(r'E:\CodexOutputs\ChemFlowAI')
f=P/'scripts/prepare_validation_data.py';s=f.read_text(encoding='utf-8-sig')
s=s.replace("('kg/hr','kg/h'):1}","('kg/hr','kg/h'):1,('cal/sec','kW'):.004184,('Gcal/day','kW'):4184000/86400}")
s=s.replace("if row[0] in ('热负荷','负荷')", "if row[0] in ('热负荷','负荷','压缩机功率')")
s=s.replace("if unit=='cal/sec':v.update(value=row[1]*.004184,unit='kW',source_type='CALCULATED',formula='cal/s × 0.004184',parents=[raw])", "if unit!='kW':v.update(value=normalize_unit(row[1],unit,'kW'),unit='kW',source_type='CALCULATED',formula=('cal/s × 0.004184' if unit=='cal/sec' else 'Gcal/day × 1e9 × 4.184 / 86400 / 1000'),parents=[raw])")
s=s.replace("energy.append({'id':group,'duty':v})", "energy.append({'id':('压缩机功率' if row[0]=='压缩机功率' else group),'duty':v})")
s=s.replace("for r in pw['组分结果'].iter_rows(min_row=2,values_only=True):", "for rownum,r in enumerate(pw['组分结果'].iter_rows(min_row=2,values_only=True),start=2):")
s=s.replace("f'G{list(streams).index(name)*9+2 if name in streams else 0}'", "f'G{rownum}'")
f.write_text(s,encoding='utf-8')
f=P/'frontend/src/pages/Steps.tsx';s=f.read_text(encoding='utf-8').replace('绝对压力 / bar','压力 / bar（原表单位）');f.write_text(s,encoding='utf-8')
f=P/'backend/skills.py';s=f.read_text(encoding='utf-8');s=s.replace("evidence=context.get('review',{}).get('issues',[]) or ['结果加载前不提供收敛判断。']", "evidence=context.get('review',{}).get('issues',[]) or (['参考结果已加载；外部质量差已计算。独立求解仍未执行。'] if context.get('review') else ['结果加载前不提供收敛判断。'])")
s=s.replace("return SkillResult(skill=name", "from .knowledge import retrieve\n    evidence += [r['citation']+': '+r['excerpt'] for r in retrieve(name,obs,limit=1)]\n    return SkillResult(skill=name")
f.write_text(s,encoding='utf-8')
(P/'backend/knowledge.py').write_text('''from pathlib import Path
from .store import ROOT

def retrieve(skill_name,query,limit=2):
    """Deterministic local reference retrieval. Never indexes benchmark or replay files."""
    if skill_name not in {p.name for p in (ROOT/'skills').iterdir() if p.is_dir()}:return []
    files=list((ROOT/'skills'/skill_name/'references').glob('*.md'));tokens=set(query.lower().split());ranked=[]
    for f in files:
        text=f.read_text(encoding='utf-8');lines=[l for l in text.splitlines() if l and not l.startswith('#')]
        score=sum(t in text.lower() for t in tokens)
        ranked.append((score,{'citation':str(f.relative_to(ROOT)).replace('\\\\','/'),'source_type':'RULE','excerpt':' '.join(lines[:2]),'version':'1'}))
    return [r for _,r in sorted(ranked,key=lambda x:x[0],reverse=True)[:limit]]
''',encoding='utf-8')
f=P/'backend/adapters.py';s=f.read_text(encoding='utf-8').replace('from pydantic import BaseModel','from pydantic import BaseModel,ConfigDict').replace('class TypedSimulatorCommand(BaseModel):','class TypedSimulatorCommand(BaseModel):\n    model_config=ConfigDict(extra="forbid")');f.write_text(s,encoding='utf-8')
f=P/'tests/test_engine.py';s=f.read_text(encoding='utf-8-sig');s+='''

def test_energy_units_and_power():
    a=store.read_json(store.ROOT/'data/replay/route_a.json');c=store.read_json(store.ROOT/'data/replay/route_c.json')
    reboiler=next(x['duty'] for x in a['energy'] if x['id']=='再沸器')
    assert reboiler['unit']=='kW'
    assert reboiler['value']==pytest.approx(61.9943162976*4184000/86400)
    assert reboiler['parents'][0]['unit']=='Gcal/day'
    assert next(x['duty']['value'] for x in c['energy'] if x['id']=='压缩机功率')==349.053702

def test_local_retrieval_and_typed_commands():
    from backend.knowledge import retrieve
    from backend.adapters import TypedSimulatorCommand
    results=retrieve('chemflow-property-modeling','NRTL property')
    assert results and all('skills/' in r['citation'].replace('\\\\','/') and 'ground_truth' not in str(r) for r in results)
    with pytest.raises(ValueError):TypedSimulatorCommand(operation='solve',com_path='arbitrary')
''';f.write_text(s,encoding='utf-8')
print('Unit normalization, compressor data, provenance row references and local retrieval patched.')

import copy
import pytest
from backend import engine,store
from backend.adapters import ReferenceReplayAdapter,SnapshotMismatch
from backend.models import SimulationIR,SimulationResult
from backend.app import view,canvas_svg
from backend.drawings import process
from backend.evaluator import material_balance
from backend.case_variant import case_key

def test_closed_loop_source_mapping():
 r=store.read_json(store.ROOT/'data/replay/pyridine525.json')
 validated=SimulationResult.model_validate(r).model_dump()
 assert len(r['streams'])==14 and len(r['topology']['units'])==7
 assert validated['streams']['PY']['molar_flow']['value']==20
 b=material_balance(r)
 assert b['input_kg_h']==pytest.approx(2979.094)
 assert b['residual_kg_h']==pytest.approx(.242203)
 assert 'RE' not in b['input_streams']+b['output_streams']
 assert r['streams']['PY']['composition']['Pyridine']['value']==pytest.approx(.997837895)
 assert r['streams']['A-S2']['temperature']['status']=='ANOMALY'
 units={u['id']:u for u in r['topology']['units']}
 assert units['MIXER']['type']=='TOWER' and units['PY-SPR']['type']=='MIXER'
 assert units['3-PY-SPR']['parameters']['BASIS-RR']['value']==3
 assert r['energy'][0]['duty']['value']==pytest.approx(-1904014.96*.004184)

def test_closed_loop_workflow_and_legacy_isolation(tmp_path,monkeypatch):
 monkeypatch.setattr(store,'PROJECTS',tmp_path)
 p=engine.create('Source integration test','pyridine','reference','reference_replay')
 assert case_key(p['spec'])=='pyridine525'
 spec=store.read_json(store.ROOT/'data/validation/pyridine525/input.json')
 engine.update_spec(p,spec,False)
 for step in range(1,5):engine.confirm(p,step,dict(review_ack=True,note='Automated fixture checks only',model='NRTL',route='pyridine'))
 engine.run_simulation(p)
 assert p['result']['solver_status']=='SOURCE_RESULTS_WITH_WARNINGS'
 assert p['result']['converged'] is None
 assert len(view(p,5)['equipment_parameters']['units'])==7
 assert 'DECANTER' in canvas_svg(p)
 assert process(p,'pfd') is not None and process(p,'pid') is not None
 for step in (5,6):engine.confirm(p,step,dict(review_ack=True,note='Automated fixture checks only; source warnings retained'))
 engine.optimize(p,dict(variables={},select_baseline=True))
 engine.confirm(p,7,dict(review_ack=True))
 engine.tea(p,dict(basis_year=2026,currency='CNY',hours=8000,feed_price=1,product_price=1,utility_price=.5,method='UTILITY_ONLY'))
 assert p['tea']['metrics']['Annual Product Revenue']['value']==pytest.approx(1580.99606*8000)
 engine.confirm(p,8,dict(review_ack=True));engine.confirm(p,9,dict(review_ack=True))
 assert p['validation']['workflow_integration']=='PASS'
 assert p['validation']['independent_numerical_validation']=='NOT_ASSESSED'
 legacy=copy.deepcopy(p);legacy['spec']=store.read_json(store.ROOT/'data/validation/pyridine/input.json')
 ir=SimulationIR.model_validate(engine.load_ir(legacy,'pyridine'))
 rr=ReferenceReplayAdapter().run(legacy['spec'],ir)
 assert 'DECANTER' not in {u['id'] for u in rr.topology['units']}
 assert '1' in {f['stream_id'] for f in legacy['spec']['feeds']}
 altered=copy.deepcopy(spec);altered['feeds'][0]['molar_flow']['value']=26
 with pytest.raises(SnapshotMismatch):ReferenceReplayAdapter().run(altered,SimulationIR.model_validate(p['ir']))
 ir2=SimulationIR.model_validate(p['ir']);ir2.property_method='UNIFAC'
 with pytest.raises(SnapshotMismatch):ReferenceReplayAdapter().run(spec,ir2)

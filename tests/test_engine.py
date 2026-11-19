import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import copy,json,pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend import store
from backend.models import ProjectSpec,SimulationIR,ProvenanceRecord
from backend.skills import REGISTRY,execute_skill
from backend.evaluator import GoldenEvaluator
from scripts.prepare_validation_data import normalize_unit

@pytest.fixture
def client(tmp_path,monkeypatch):
 monkeypatch.setattr(store,'PROJECTS',tmp_path)
 return TestClient(app)
def new(c,dataset='pdh',mode='reference',backend='reference_replay'):
 r=c.post('/api/projects',json={'name':'Test engineering task','dataset':dataset,'mode':mode,'backend':backend});assert r.status_code==200,r.text
 p=r.json()['id'];basis=c.get(f'/api/projects/{p}/reference-basis');assert basis.status_code==200
 r=c.put(f'/api/projects/{p}/spec',json={'spec':basis.json()});assert r.status_code==200,r.text;return p
def view(c,p,s):return c.get(f'/api/projects/{p}/steps/{s}')
def confirm(c,p,s,**kwargs):
 r=c.post(f'/api/projects/{p}/steps/{s}/confirm',json={'review_ack':True,'note':'Reviewed source anomalies; source mapping review',**kwargs});assert r.status_code==200,r.text;return r.json()
def to5(c,p,route='route_a'):
 confirm(c,p,1);confirm(c,p,2);confirm(c,p,3,model='NRTL' if route=='pyridine' else 'PR');confirm(c,p,4,route=route)
def complete(c,p,route='route_a'):
 to5(c,p,route);r=c.post(f'/api/projects/{p}/simulate');assert r.status_code==200,r.text;confirm(c,p,5);confirm(c,p,6)
 r=c.post(f'/api/projects/{p}/optimization',json={'unit_id':next(u['id'] for u in store.load(p)['ir']['units'] if u['type']=='TOWER'),'variables':{'column_pressure':12},'select_baseline':True});assert r.status_code==200,r.text;confirm(c,p,7)
 r=c.post(f'/api/projects/{p}/tea',json={});assert r.status_code==200,r.text;assert r.json()['tea']['status']=='NOT_CALCULATED';confirm(c,p,8);confirm(c,p,9)

@pytest.mark.parametrize('route',['route_a','route_b','route_c','pyridine'])
def test_complete_workflow(client,route):
 p=new(client,'pyridine' if route=='pyridine' else 'pdh');complete(client,p,route);v=view(client,p,9).json();assert v['completed']==list(range(1,10));assert v['validation']['independent_numerical_validation']=='NOT_ASSESSED';assert v['validation']['workflow_integration']=='PASS';assert client.get(f'/api/projects/{p}/package').content[:2]==b'PK';assert client.get(f'/api/projects/{p}/report').status_code==200

def test_locked_and_no_leak(client):
 p=new(client);assert view(client,p,9).status_code==422;assert client.get(f'/api/projects/{p}/canvas').status_code==422;assert client.get(f'/api/projects/{p}/comparison').status_code==422;assert client.get(f'/api/projects/{p}/routes/route_a').status_code==422;assert client.get('/data/validation/pdh/route_a/ground_truth.json').status_code==404
 v=view(client,p,1).json();assert v['result'] is None;assert 'PRO-D' not in json.dumps(v['spec']);assert '2058.978' not in json.dumps(v)
 assert client.post(f'/api/projects/{p}/steps/1/confirm',json={}).status_code==422

def test_refresh_and_invalidation(client):
 p=new(client);complete(client,p);old=view(client,p,1).json();assert old['max_step']==9;assert old['result'] is None
 spec=old['spec'];spec['feeds'][0]['temperature']['value']=60
 assert client.put(f'/api/projects/{p}/spec',json={'spec':spec}).status_code==422
 assert client.put(f'/api/projects/{p}/spec',json={'spec':spec,'invalidate':True}).status_code==200
 v=view(client,p,1).json();assert v['completed']==[] and v['result'] is None and v['tea'] is None;assert v['max_step']==1
 to5(client,p);r=client.post(f'/api/projects/{p}/simulate');assert r.status_code==409 and '历史回放' in r.text

def test_blind_blocks_unconnected_solver(client):
 p=new(client,mode='blind',backend='dwsim');to5(client,p);r=client.post(f'/api/projects/{p}/simulate');assert r.status_code==503;assert view(client,p,5).json()['result'] is None;assert client.post(f'/api/projects/{p}/steps/5/confirm',json={'review_ack':True}).status_code==422

def test_golden_only_step9(client):
 p=new(client);project=store.load(p)
 with pytest.raises(ValueError,match='Step 09'):GoldenEvaluator().evaluate(project)

def test_schema_and_units():
 assert normalize_unit(2000,'kPa','bar')==20;assert normalize_unit(1,'kg/s','kg/h')==3600;assert normalize_unit(273.15,'K','C')==0
 with pytest.raises(ValueError):normalize_unit(5,'psi','bar')
 with pytest.raises(ValueError):ProvenanceRecord(value=25,unit='C',source_type='LLM',source_name='LLM')
 ir=store.read_json(store.ROOT/'data/validation/pdh/route_a/topology.json');ir['connections'][0]['to_unit']='GHOST'
 with pytest.raises(ValueError):SimulationIR.model_validate(ir)

def test_parser_missing_and_zero(client):
 p=new(client);r=client.post(f'/api/projects/{p}/intake',json={'text':'温度 300 °C，压力 2000 kPa，流量 100 kg/h'});assert r.status_code==200
 spec=r.json()['spec'];assert spec['feeds'][0]['pressure']['value']==20;assert spec['feeds'][0]['mass_flow']['value']==100
 assert client.post(f'/api/projects/{p}/intake',json={'text':'请提高效率'}).json()['recognized']==[]
 spec['feeds'][0]['mass_flow']['value']=0;client.put(f'/api/projects/{p}/spec',json={'spec':spec});assert client.post(f'/api/projects/{p}/steps/1/confirm',json={'review_ack':True}).status_code==422

@pytest.mark.parametrize('entry',REGISTRY,ids=lambda e:e['name'])
def test_each_skill_step_contract(client,entry):
 p=new(client);context={'spec':store.load(p)['spec']}
 for step in entry['steps']:
  r=execute_skill(entry['name'],step,context);assert r['skill']==entry['name'] and r['step']==step and r['evidence'];assert 'streams' not in r
 wrong=next(s for s in range(1,10) if s not in entry['steps'])
 with pytest.raises(ValueError,match='WRONG_STEP'):execute_skill(entry['name'],wrong,context)

def test_data_integrity_and_asset_sanitization():
 manifest=store.read_json(store.ROOT/'data/preprocessing_manifest.json');assert manifest['counts']=={'route_a':8,'route_b':18,'route_c':12,'pyridine':13}
 g=store.read_json(store.ROOT/'data/validation/pyridine/ground_truth.json');assert g['streams']['A-S2']['temperature']['value']==-231.462924;assert g['streams']['A-S2']['temperature']['status']=='ANOMALY'
 for f in (store.ROOT/'data/assets').glob('*.svg'):
  text=f.read_text(encoding='utf-8');assert '-231.46' not in text and '4409.65' not in text and '4,409.65' not in text;assert 'animateMotion' in text and 'data-stream-id' in text and 'data-equipment-id' in text

def test_numeric_evaluator_detects_corruption(client):
 p=new(client);to5(client,p);client.post(f'/api/projects/{p}/simulate');confirm(client,p,5);confirm(client,p,6);client.post(f'/api/projects/{p}/optimization',json={'variables':{},'select_baseline':True});confirm(client,p,7);client.post(f'/api/projects/{p}/tea',json={});confirm(client,p,8)
 project=store.load(p);project['result']['streams']['PRO-D']['mass_flow']['value']+=100
 result=GoldenEvaluator().evaluate(project);assert next(c for c in result['checks'] if c['label']=='mass_flow mapping')['status']=='FAIL'

def test_tea_deterministic_and_historical_guard(client):
 p=new(client);complete(client,p);assert client.post(f'/api/projects/{p}/optimization',json={'variables':{},'select_baseline':True}).status_code==422
 client.post(f'/api/projects/{p}/reopen/8',json={'invalidate':True});body={'basis_year':2026,'currency':'CNY','hours':8000,'feed_price':2,'product_price':3,'utility_price':.5,'method':'UTILITY_ONLY'}
 r=client.post(f'/api/projects/{p}/tea',json=body);assert r.status_code==200;r=r.json()['tea'];assert r['status']=='PARTIAL_CALCULATION';assert r['metrics']['CAPEX'] is None;assert abs(r['metrics']['Annual Feed Cost']['value']-4409.652*8000*2)<.01


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
    assert results and all(r['citation'].replace('\\','/').startswith(('skills/','knowledge_base/sources/')) and 'ground_truth' not in str(r) for r in results)
    with pytest.raises(ValueError):TypedSimulatorCommand(operation='solve',com_path='arbitrary')

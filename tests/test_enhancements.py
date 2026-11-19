import sys,json,copy,io,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend import store
from backend.properties import propane_curve,validate_vle,catalog
from backend.evidence import evidence

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'PROJECTS',tmp_path)
    return TestClient(app)
def req(c,method,url,**kwargs):
    r=getattr(c,method)(url,**kwargs);assert r.status_code==200,r.text;return r
def init(c,d='pdh'):
    pid=req(c,'post','/api/projects',json=dict(name='资料核验',dataset=d,mode='reference',backend='reference_replay')).json()['id']
    s=req(c,'get',f'/api/projects/{pid}/reference-basis').json()
    req(c,'put',f'/api/projects/{pid}/spec',json={'spec':s});return pid
def advance(c,p,n,**kw):return req(c,'post',f'/api/projects/{p}/steps/{n}/confirm',json=dict(review_ack=True,note='已复核来源；保留待补事项',**kw))

@pytest.mark.parametrize('route',['route_a','route_b','route_c','pyridine'])
def test_all_workflows_and_delivery(client,route):
    p=init(client,'pyridine' if route=='pyridine' else 'pdh')
    advance(client,p,1);advance(client,p,2)
    v=req(client,'get',f'/api/projects/{p}/steps/3').json();assert len(v['models'])==20
    advance(client,p,3,model='NRTL' if route=='pyridine' else 'PR');advance(client,p,4,route=route)
    v=req(client,'get',f'/api/projects/{p}/steps/5').json();assert v['result'],v.get('reference_load_error');assert v['result']['converged'] is None
    svg=req(client,'get',f'/api/projects/{p}/canvas').text;assert 'aspen' not in svg.lower();assert '°C' in svg
    if route=='route_a':assert '2,058.98' in svg and '4,409.65' in svg
    advance(client,p,5);advance(client,p,6)
    req(client,'post',f'/api/projects/{p}/optimization',json={'variables':{},'select_baseline':True});advance(client,p,7)
    req(client,'post',f'/api/projects/{p}/tea',json={});advance(client,p,8);advance(client,p,9)
    result=req(client,'get',f'/api/projects/{p}/steps/9').json();assert result['validation']['workflow_integration']=='PASS';assert result['validation']['independent_numerical_validation']=='NOT_ASSESSED'
    z=zipfile.ZipFile(io.BytesIO(req(client,'get',f'/api/projects/{p}/package').content))
    assert {'source_evidence.json','vle.json','property_parameters.json'}<=set(z.namelist())
    assert all(b'aspen' not in z.read(n).lower() for n in z.namelist())
    assert 'aspen' not in req(client,'get',f'/api/projects/{p}/report').text.lower()

def test_vle_endpoints_persistence_and_validation(client):
    p=init(client);advance(client,p,1);url=f'/api/projects/{p}/vle'
    a=req(client,'get',url).json();exp=next(x for x in a['datasets'] if x['id']=='nist-c3-2006')
    assert len(exp['points'])==90 and len({p['T'] for p in exp['points']})==6
    body=dict(kind='binary_pxy',components=['C3H6','C3H8'],source='laboratory record test',points=[dict(T=300,P=9,x=.2,y=.25),dict(T=300,P=10,x=.6,y=.65)])
    req(client,'put',url,json=body);assert req(client,'get',url).json()['datasets'][-1]['points']==body['points']
    bad=copy.deepcopy(body);bad['points'][0]['x']=1.1;assert client.put(url,json=bad).status_code==422
    bad=copy.deepcopy(body);bad['points'][0]['P']=0;assert client.put(url,json=bad).status_code==422
    bad=copy.deepcopy(body);bad['components']=['H2','H2'];assert client.put(url,json=bad).status_code==422
    advance(client,p,2);assert client.put(url,json=body).status_code==422

def test_reference_not_used_for_changed_feed(client):
    p=init(client);s=req(client,'get',f'/api/projects/{p}/reference-basis').json();s['feeds'][0]['temperature']['value']=80
    req(client,'put',f'/api/projects/{p}/spec',json={'spec':s})
    advance(client,p,1);advance(client,p,2);advance(client,p,3,model='PR');advance(client,p,4,route='route_a')
    v=req(client,'get',f'/api/projects/{p}/steps/5').json();assert v['result'] is None and v['reference_load_error']
    assert client.post(f'/api/projects/{p}/simulate').status_code==409

def test_propane_and_evidence():
    c=propane_curve();assert len(c['points'])==81
    # NIST correlation around the normal boiling point must be near 1 bar.
    q=propane_curve(230.6,231.1,2);assert .97<q['points'][-1]['P']<1.05
    assert all(b['P']>a['P'] for a,b in zip(c['points'],c['points'][1:]))
    with pytest.raises(ValueError):propane_curve(200,350)
    cat=catalog('pdh');assert cat['binary_data']['covered_pairs']==3
    assert len(evidence('pyridine')['stages']['8'])>=20
    assert not evidence('pdh')['stages']['8']
    assert all(x['status']=='MATCH' for x in store.read_json(store.ROOT/'data/visualization_audit.json'))

def test_blank_inputs_and_mole_parser(client):
    from backend.intake import parse
    from backend.design_basis import completion
    p=req(client,'post','/api/projects',json=dict(name='blank',dataset='pdh',mode='reference',backend='reference_replay')).json()
    p=req(client,'get',f"/api/projects/{p['id']}/steps/1").json()
    assert not completion(p['spec'])['required_fields_complete']
    assert p['spec']['feeds'][0]['molar_flow']['value'] is None
    basis=req(client,'get',f"/api/projects/{p['id']}/reference-basis").json()
    out=parse('摩尔流量 100 kmol/h；产品摩尔分率要求 99.9%',basis)
    assert out['spec']['feeds'][0]['molar_flow']['value']==100
    assert out['spec']['target_products'][0]['purity']['unit']=='mol/mol'
    out=parse('产品质量分率要求 99.9%',basis)
    assert out['unparsed']
    for key,value in basis['target_products'][0]['purity'].items():
        assert out['spec']['target_products'][0]['purity'][key]==value

def test_source_tables_preserve_conflicts():
    e=evidence('pyridine');assert len(e['tables'])==3
    cash=e['tables'][1]['rows'];net=next(r[1:] for r in cash if r[0]=='净现金流量');cumulative=next(r[1:] for r in cash if r[0]=='累计现金流量（原表）')
    assert round(sum(net[:4]),2)==-4446.34 and cumulative[3]==-2598.03
    assert any('现金流算术' in c['item'] for c in e['conflicts'])


def test_reference_rounding_and_reaction_spacing(client):
    p=init(client)
    s=req(client,'get',f'/api/projects/{p}/reference-basis').json()
    s['feeds'][0]['temperature']['value']=57.00438003
    s['reaction']['equation']='C3H8->C3H6+H2'
    req(client,'put',f'/api/projects/{p}/spec',json={'spec':s})
    advance(client,p,1);advance(client,p,2);advance(client,p,3,model='PR');advance(client,p,4,route='route_b')
    v=req(client,'get',f'/api/projects/{p}/steps/5').json()
    assert v['result'] and not v.get('reference_load_error')
    from backend.adapters import same_reference_value,reaction_key
    assert not same_reference_value(57.00438003,57.00439)
    assert reaction_key('C3H8 → C3H6 + H2')!=reaction_key('2C3H8 → C3H6 + H2')


def test_equipment_route_mapping_and_sources(client):
    data=store.read_json(store.ROOT/'data/equipment_parameters.json')
    def values(route,unit,key):
        u=next(u for u in data[route]['units'] if u['id']==unit)
        return [r['value'] for r in u['rows'] if r['key']==key]
    assert values('route_a','COLUMN','NSTAGE')==['184']
    assert values('route_b','HPD','NSTAGE')==['182']
    assert values('route_c','RECT','NSTAGE')==['139']
    assert values('route_c','STRIP','NSTAGE')==['45']
    assert values('route_b','COMPR','PRATIO')==['1.675']
    assert values('route_c','COMP','PEFF')==['0.8']
    assert values('route_c','REACTOR','TEMP')==['400.']
    reactor=next(u for u in data['route_c']['units'] if u['id']=='REACTOR')
    temp=next(r for r in reactor['rows'] if r['key']=='TEMP')
    assert temp['source_type']=='USER_AUTHORIZED_REFERENCE' and temp['source_file']=='example1reat.apw'
    assert values('route_c','COMP','PRES')==['1.92']
    assert values('route_c','VALVE','P-OUT')==['1.3']
    for route in data:
        assert len(data[route]['sha256'])==64
        assert all(u['locator'] for u in data[route]['units'])
    p=init(client)
    assert req(client,'get',f'/api/projects/{p}/steps/1').json()['equipment_parameters'] is None
    advance(client,p,1);advance(client,p,2);advance(client,p,3,model='PR');advance(client,p,4,route='route_c')
    e=req(client,'get',f'/api/projects/{p}/steps/5').json()['equipment_parameters']
    assert e['file']=='example3react.bkp'

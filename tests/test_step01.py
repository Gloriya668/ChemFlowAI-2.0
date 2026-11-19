import copy,json
import pytest
from test_engine import client,new,view,confirm
from backend import store,engine
from backend.design_basis import completion

@pytest.mark.parametrize('dataset',['pdh','pyridine'])
def test_known_input_without_parser(client,dataset):
 p=new(client,dataset);s=view(client,p,1).json()
 assert s['design_basis']['required_fields_complete'] and s['design_basis']['complete_count']==7
 assert s['spec']['feeds'][0]['temperature']['source_type']==('IMPORTED_INPUT' if dataset=='pyridine' else 'VALIDATION_INPUT')
 confirm(client,p,1);v=view(client,p,2).json()
 assert v['max_step']==2 and v['completed']==[1]
 assert store.load(p)['completed']==[1]

@pytest.mark.parametrize('key',['components','temperature','pressure','mass_flow','molar_flow','reaction','target_products'])
def test_each_required_field_blocks_even_with_approval(client,key):
 p=new(client);s=view(client,p,1).json()['spec']
 if key in ['components','target_products']:s[key]=[]
 elif key=='reaction':s[key]['equation']=''
 else:s['feeds'][0][key]['value']=None
 d=client.post(f'/api/projects/{p}/design-basis/validate',json={'spec':s}).json()
 assert d['complete_count']==6 and not d['required_fields_complete']
 assert client.put(f'/api/projects/{p}/spec',json={'spec':s}).status_code==200
 assert client.post(f'/api/projects/{p}/steps/1/confirm',json={'review_ack':True}).status_code==422
 assert view(client,p,2).status_code==422

def test_parser_semantics_and_optional_unknown(client):
 p=new(client);s=view(client,p,1).json()['spec'];s['components']=[];s['reaction']['equation']='';s['target_products']=[]
 v=engine.parse_intake('原料为丙烷；反应为 C3H8 -> C3H6 + H2；目标产品为丙烯；副产物为氢气',s)
 assert v['status']=='PARSED' and completion(v['spec'])['required_fields_complete']
 assert v['spec']['feeds'][0]['component_ids']==['C3H8']
 assert 'H2' in v['spec']['byproducts'][0]['name']
 original=view(client,p,1).json()['spec'];original['feeds'][0]['temperature']['value']=80
 v=engine.parse_intake('增加产品纯度要求 99.9%；限制塔顶压力不超过 15 bar；请大幅降低能耗',original)
 assert v['status']=='NEEDS_REVIEW' and v['unparsed']
 assert v['spec']['target_products'][0]['purity']['value']==pytest.approx(.999)
 assert v['spec']['feeds'][0]['pressure']['value']==20
 assert v['spec']['feeds'][0]['temperature']['value']==80
 assert completion(v['spec'])['required_fields_complete']

def test_migration_preserves_edits(client):
 p=new(client);s=store.load(p);s.pop('input_schema_version');s['spec'].pop('byproducts');s['spec']['feeds'][0]['temperature']['value']=60;store.save(s)
 v=view(client,p,1).json();assert v['spec']['feeds'][0]['temperature']['value']==60
 assert v['spec']['byproducts'][0]['name']=='Hydrogen / H2'
 assert store.load(p)['input_schema_version']==8

def test_input_only_no_ground_truth_reads(client,monkeypatch):
 original=__import__('pathlib').Path.read_text;reads=[]
 def tracked(path,*a,**kw):
  reads.append(str(path));assert path.name!='ground_truth.json';return original(path,*a,**kw)
 monkeypatch.setattr(__import__('pathlib').Path,'read_text',tracked)
 p=new(client);view(client,p,1);confirm(client,p,1);view(client,p,2)
 assert any(x.endswith('input.json') for x in reads)

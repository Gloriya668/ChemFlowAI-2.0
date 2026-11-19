import copy
import hashlib
import json
import math
import sys
import pytest
from backend import dwsim_mcp as mcp,dwsim_solver as solver
from backend.models import SimulationIR
from backend.adapters import SimulatorUnavailable,SnapshotMismatch

def test_stdio_handshake_and_tool_result(tmp_path):
    script=tmp_path/'server.py'
    script.write_text('''import sys,json
for line in sys.stdin:
 r=json.loads(line)
 if 'id' not in r:continue
 if r['method']=='initialize':result={'serverInfo':{'name':'TEST DOUBLE'}}
 else:result={'content':[{'type':'text','text':'{"ok":true}'}]}
 print(json.dumps({'jsonrpc':'2.0','id':r['id'],'result':result}),flush=True)
''')
    with mcp.Session({'command':[sys.executable,str(script)],'cwd':str(tmp_path),'timeout_seconds':5}) as session:
        assert session.call('test')['ok']
        assert session.audit[0]['tool']=='test'
    assert session.process.poll() is not None

def test_dead_process_is_cleaned_up(tmp_path):
    with pytest.raises(SimulatorUnavailable):
        with mcp.Session({'command':[sys.executable,'-c','pass'],'cwd':str(tmp_path),'timeout_seconds':5}):pass

def test_rpc_deadline_kills_process(tmp_path):
    import time
    s=mcp.Session({'command':[sys.executable,'-c','import time;time.sleep(20)'],'cwd':str(tmp_path),'timeout_seconds':.1})
    with pytest.raises(SimulatorUnavailable,match='超时'):
        with s:pass
    assert s.process.poll() is not None

@pytest.mark.parametrize('kind,unit,value,expected',[
    ('temperature','C',26.85,300),('pressure','bar',2,200000),('pressure','kPa',101.325,101325),('mass_flow','kg/h',3600,1)])
def test_units(kind,unit,value,expected):
    assert math.isclose(solver.to_si({'value':value,'unit':unit},kind),expected)

@pytest.mark.parametrize('value',[float('nan'),float('inf'),True,None,-1])
def test_invalid_input(value):
    with pytest.raises(ValueError):solver.to_si({'value':value,'unit':'kg/h'},'mass_flow')

def fixture_model(tmp_path):
    template=tmp_path/'flow.dwxml';template.write_text('<test/>')
    spec={'dataset':'custom','components':[{'id':'Water','name':'Water','source_type':'USER_INPUT','source_name':'test'}],
          'feeds':[{'stream_id':'F','component_ids':['Water'],'temperature':{'value':26.85,'unit':'C'},'pressure':{'value':1.01325,'unit':'bar'},
                    'mass_flow':{'value':3600,'unit':'kg/h'},'composition':{'Water':{'value':1,'unit':'mol/mol'}}}],
          'reaction':{'equation':'none'},'constraints':{},'source':{}}
    ir=SimulationIR(route_id='test',title='test',units=[{'id':'H','type':'HEATER','label':'heater'}],
        streams=[{'stream_id':'F'},{'stream_id':'P'}],connections=[{'stream_id':'F','to_unit':'H'},{'stream_id':'P','from_unit':'H'}],source={})
    entry={'template':str(template),'template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),
           'basis_sha256':solver.basis_digest(spec),'ir_sha256':solver.digest(ir.model_dump()),
           'stream_map':{'F':'Feed','P':'Product'},'unit_map':{'H':'Heater'},'component_map':{'Water':'Water'},'property_package_names':['Steam Tables'], 'duty_map':{}}
    return spec,ir,{'models':{'test':entry},'timeout_seconds':30}

def test_template_fingerprint_and_allowed_feed_changes(tmp_path):
    spec,ir,cfg=fixture_model(tmp_path)
    spec['feeds'][0]['temperature']['value']=40
    solver.validate_template(spec,ir,cfg)
    spec['constraints']['pressure']=5
    with pytest.raises(SnapshotMismatch):solver.validate_template(spec,ir,cfg)

def test_template_hash_mismatch(tmp_path):
    spec,ir,cfg=fixture_model(tmp_path);cfg['models']['test']['template_sha256']='bad'
    with pytest.raises(SnapshotMismatch):solver.validate_template(spec,ir,cfg)

def test_solver_protocol_conversion_and_provenance(tmp_path,monkeypatch):
    spec,ir,cfg=fixture_model(tmp_path)
    monkeypatch.setattr(solver,'settings',lambda:cfg)
    monkeypatch.setattr(solver.store,'ROOT',tmp_path)
    class FakeSession:
        info={'serverInfo':{'name':'TEST DOUBLE'}}
        def __init__(self,*args):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def call(self,name,/,**args):
            if name=='dwsim_flowsheet_load':return {'flowsheet_id':'test'}
            if name=='dwsim_flowsheet_summary':return {'compounds':['Water'],'property_packages':['Steam Tables']}
            if name=='dwsim_flowsheet_list_objects':return {'objects':[{'name':'Feed','type':'MaterialStream'},{'name':'Product','type':'MaterialStream'},{'name':'Heater','type':'Heater'}]}
            if name=='dwsim_stream_get_results':return {'temperature_K':300,'pressure_Pa':101325,'mass_flow_kg_s':1,'molar_flow_mol_s':55.5,'phases':[{'name':'Mixture','compounds':{'Water':{'mole_fraction':1,'mass_fraction':1}}},{'name':'Vapor','fraction':0}]}
            if name=='dwsim_solve_run':return {'ok':True,'objects':[{'name':x,'calculated':True,'error':''} for x in ['Feed','Product','Heater']]}
            return {}
    monkeypatch.setattr(solver,'Session',FakeSession)
    r=solver.solve(spec,ir)
    assert r.backend=='DWSIM' and r.converged
    assert r.streams['F'].mass_flow.value==3600
    assert r.streams['F'].temperature.value==pytest.approx(26.85)
    assert r.streams['F'].mass_flow.source_type=='SIMULATOR'
    logs=list((tmp_path/'runtime/solver-runs').glob('*/run.json'))
    assert len(logs)==1 and json.loads(logs[0].read_text(encoding='utf-8'))['status']=='SUCCEEDED'

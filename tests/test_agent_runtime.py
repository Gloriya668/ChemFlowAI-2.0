import copy
import json
import threading
import uuid
import pytest
from fastapi import HTTPException
from backend import agent,store,llm
from backend.adapters import SimulatorUnavailable

@pytest.fixture
def project(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'PROJECTS',tmp_path/'projects');store.PROJECTS.mkdir()
    pid=str(uuid.uuid4())
    p={'id':pid,'name':'test','revision':3,'max_step':5,'completed':[1,2,3,4], 'backend':'dwsim','spec':{},'result':None}
    store.save(p)
    monkeypatch.setattr(agent,'snapshot',lambda pid,step:{'name':'test','revision':3})
    return p

def make_run(p,**kwargs):
    return {'id':str(uuid.uuid4()),'project_id':p['id'],'message':'check','step':5,'revision':p['revision'],
            'status':'QUEUED','allow_simulation':False,'trace':[],'answer':'',**kwargs}

def decisions(monkeypatch,items):
    it=iter(items)
    monkeypatch.setattr(llm,'complete',lambda messages:{'answer':json.dumps(next(it),ensure_ascii=False)})

def test_observe_tool_final_persists(project,monkeypatch):
    decisions(monkeypatch,[{'action':'tool','summary':'查看项目','tool':'inspect_project'},
                           {'action':'final','summary':'完成','answer':'已取得项目数据；未运行模拟。'}])
    r=make_run(project);agent.execute(r,threading.Event())
    loaded=agent.read(project['id'],r['id'])
    assert loaded['status']=='COMPLETED' and loaded['trace'][0]['status']=='SUCCEEDED'
    assert store.load(project['id'])['revision']==3

def test_no_execution_without_authorization(project,monkeypatch):
    decisions(monkeypatch,[{'action':'tool','summary':'运行','tool':'run_simulation'},
                           {'action':'final','summary':'停止','answer':'没有执行授权'}])
    monkeypatch.setattr(agent,'simulate_checked',lambda *a:pytest.fail('unauthorized simulator call'))
    r=make_run(project);agent.execute(r,threading.Event())
    assert r['trace'][0]['status']=='FAILED'
    assert not r.get('simulation_attempted')

def test_unknown_tool_and_bad_json_fail(project,monkeypatch):
    monkeypatch.setattr(llm,'complete',lambda m:{'answer':'{"action":"tool","summary":"x","tool":"shell"}'})
    r=make_run(project);agent.execute(r,threading.Event());assert r['status']=='FAILED'
    assert r['trace']==[]

def test_budget(project,monkeypatch):
    monkeypatch.setattr(llm,'complete',lambda m:{'answer':json.dumps({'action':'tool','summary':'查看','tool':'inspect_project'})})
    r=make_run(project);agent.execute(r,threading.Event())
    assert r['status']=='LIMIT_REACHED' and len(r['trace'])==6

def test_cancel_before_request(project,monkeypatch):
    monkeypatch.setattr(llm,'complete',lambda m:pytest.fail('cancelled'))
    stop=threading.Event();stop.set();r=make_run(project);agent.execute(r,stop)
    assert r['status']=='CANCELLED'

def test_revision_changed_during_llm(project,monkeypatch):
    def request(messages):
        p=store.load(project['id']);p['revision']+=1;store.save(p)
        return {'answer':json.dumps({'action':'final','summary':'done','answer':'stale'})}
    monkeypatch.setattr(llm,'complete',request)
    r=make_run(project);agent.execute(r,threading.Event());assert r['status']=='FAILED'

def test_stale_solver_result_not_committed(project,monkeypatch):
    def calculate(p,persist):
        assert not persist
        changed=copy.deepcopy(p);changed['revision']+=1;store.save(changed)
        p['result']={'source':'old run'};return p
    monkeypatch.setattr(agent.engine,'run_simulation',calculate)
    with pytest.raises(ValueError,match='求解期间'):agent.simulate_checked(project['id'],3)
    assert store.load(project['id'])['result'] is None

def test_simulation_once_even_on_failure(project,monkeypatch):
    def fail(*args):raise SimulatorUnavailable('not converged')
    monkeypatch.setattr(agent,'simulate_checked',fail)
    r=make_run(project,allow_simulation=True)
    with pytest.raises(SimulatorUnavailable):agent.invoke(r,'run_simulation',{})
    with pytest.raises(ValueError,match='最多'):agent.invoke(r,'run_simulation',{})

def test_restart_marks_interrupted(project):
    r=make_run(project);agent.write(r)
    assert agent.read(project['id'],r['id'])['status']=='INTERRUPTED'

def test_no_credentials_does_not_queue(project,monkeypatch):
    monkeypatch.setattr(llm,'status',lambda:{'configured':False})
    with pytest.raises(HTTPException) as e:agent.start(project['id'],'test',5)
    assert e.value.status_code==503

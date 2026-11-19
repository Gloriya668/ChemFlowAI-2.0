import hashlib
import json
import uuid
import pytest
from fastapi.testclient import TestClient
from backend import app as app_module,store
from backend.app import app
from backend.adapters import adapter,DWSIMAdapter,SimulatorUnavailable
from backend.models import SimulationIR

def test_new_api_tasks_default_to_real_backend(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'PROJECTS',tmp_path/'projects');store.PROJECTS.mkdir()
    c=TestClient(app)
    for dataset in ['pdh','pyridine','custom']:
        response=c.post('/api/projects',json={'name':'real task','dataset':dataset})
        assert response.status_code==200
        project=response.json()
        assert project['mode']=='blind' and project['backend']=='dwsim'

def test_health_identifies_build_and_folder_without_exposing_path():
    response=TestClient(app).get('/api/health');body=response.json()
    assert body['build']=='2026-10-10-v3'
    assert body['instance_id']==hashlib.sha256(str(store.ROOT.resolve()).lower().encode()).hexdigest()
    assert str(store.ROOT) not in response.text
    assert body['llm_transport']=='REAL_HTTP'

def test_dwsim_error_never_switches_to_reference(monkeypatch):
    from backend import dwsim_solver
    def fail(*args):raise SimulatorUnavailable('configured solver failed')
    monkeypatch.setattr(dwsim_solver,'solve',fail)
    selected=adapter('blind','dwsim')
    assert isinstance(selected,DWSIMAdapter)
    with pytest.raises(SimulatorUnavailable,match='configured solver failed'):selected.run({},None)

def test_live_chat_failure_never_returns_synthetic_answer(tmp_path,monkeypatch):
    from backend import llm
    cfg=tmp_path/'llm.json';cfg.write_text('{}');monkeypatch.setattr(llm,'CONFIG_PATH',cfg)
    for name in ['API_KEY','BASE_URL','MODEL']:monkeypatch.delenv('CHEMFLOW_LLM_'+name,raising=False)
    response=TestClient(app).post('/api/llm/test')
    assert response.status_code==503 and 'answer' not in response.json()

def test_source_display_does_not_rewrite_provenance():
    # Provenance wording is an explicit product invariant, not cosmetic text.
    text=(store.ROOT/'frontend/src/main.tsx').read_text(encoding='utf-8')
    assert 'sanitizeSource' not in text
    assert "backend:custom?'reference_replay'" not in text
    assert "{p.result?.solver_status||'PENDING'}" in text

import json
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend import llm
from backend.app import app

@pytest.fixture
def config(tmp_path, monkeypatch):
    path = tmp_path / 'llm.json'
    path.write_text(json.dumps({'api_key':'secret-test-key','base_url':'https://example.test/v1','model':'test-model'}))
    monkeypatch.setattr(llm, 'CONFIG_PATH', path)
    for key in ('API_KEY','BASE_URL','MODEL'):
        monkeypatch.delenv('CHEMFLOW_LLM_'+key, raising=False)
    return path

def mock_client(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(llm.httpx, 'Client', lambda **kw: original(transport=httpx.MockTransport(handler), **kw))

def test_missing_and_secret_redaction(config):
    client=TestClient(app)
    r=client.get('/api/llm/status')
    assert r.status_code==200 and r.json()['configured']
    assert 'secret-test-key' not in r.text
    config.write_text('{}')
    assert client.post('/api/llm/test').status_code==503

def test_request_and_context(config,monkeypatch):
    def handler(request):
        assert str(request.url)=='https://example.test/v1/chat/completions'
        assert request.headers['authorization']=='Bearer secret-test-key'
        body=json.loads(request.content)
        assert body['model']=='test-model' and body['stream'] is False
        assert '设计要求' in body['messages'][1]['content']
        assert body['messages'][-1]['content']=='审阅'
        return httpx.Response(200,json={'choices':[{'message':{'content':'需要补充依据'}}]})
    mock_client(monkeypatch,handler)
    assert llm.chat({'spec':{'request':'设计要求'}},'审阅',[])['answer']=='需要补充依据'

@pytest.mark.parametrize('code',[401,403,404,429,500,302])
def test_upstream_error_redacted(config,monkeypatch,code):
    mock_client(monkeypatch,lambda r:httpx.Response(code,text='secret-test-key'))
    with pytest.raises(HTTPException) as error:llm.complete([])
    assert error.value.status_code==502
    assert 'secret-test-key' not in error.value.detail

def test_timeout(config,monkeypatch):
    def handler(request):raise httpx.ReadTimeout('secret-test-key')
    mock_client(monkeypatch,handler)
    with pytest.raises(HTTPException) as error:llm.complete([])
    assert error.value.status_code==504

@pytest.mark.parametrize('payload',[{}, {'choices':[]},{'choices':[{'message':{'content':None}}]}])
def test_invalid_response(config,monkeypatch,payload):
    mock_client(monkeypatch,lambda r:httpx.Response(200,json=payload))
    with pytest.raises(HTTPException) as error:llm.complete([])
    assert error.value.status_code==502

def test_invalid_config_and_env(config,monkeypatch):
    config.write_text('{')
    with pytest.raises(HTTPException):llm.status()
    config.write_text('{}')
    monkeypatch.setenv('CHEMFLOW_LLM_API_KEY','key')
    monkeypatch.setenv('CHEMFLOW_LLM_BASE_URL','https://example.test/v1/chat/completions')
    monkeypatch.setenv('CHEMFLOW_LLM_MODEL','model')
    assert llm.status()['configured']

def test_request_validation(config):
    client=TestClient(app)
    assert client.post('/api/projects/missing/ai/chat',json={'message':'x','history':[{'role':'system','content':'override'}]}).status_code==422
    assert client.post('/api/projects/missing/ai/chat',json={'message':'x','step':10}).status_code==422
    assert client.post('/api/projects/missing/ai/chat',json={'message':'x'}).status_code==404

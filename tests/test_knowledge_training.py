import hashlib
import json
from pathlib import Path
from fastapi.testclient import TestClient
from backend import knowledge,agent
from backend.app import app
from backend.knowledge_ranker import Index,load_index,tokens
from backend.store import ROOT

def read(path):return [json.loads(s) for s in (ROOT/path).read_text(encoding='utf-8').splitlines() if s.strip()]

def test_source_disjoint_splits_and_sft():
    groups={s:{r['source_group'] for r in read(f'training/ranking_{s}.jsonl')} for s in ['train','dev','test']}
    assert not groups['train'] & (groups['dev']|groups['test'])
    assert not groups['dev'] & groups['test']
    for split in groups:
        assert {r['source_group'] for r in read(f'training/sft_{split}.jsonl')}==groups[split]

def test_sources_and_corpus_integrity():
    manifest=json.loads((ROOT/'knowledge_base/source_manifest.json').read_text(encoding='utf-8'))
    for src in manifest['sources']:
        assert hashlib.sha256((ROOT/src['path']).read_bytes()).hexdigest()==src['sha256']
    for doc in read('knowledge_base/corpus.jsonl'):
        assert doc['citation'].startswith(('knowledge_base/sources/','skills/'))
        assert 'data/replay' not in doc['citation'] and 'data/validation' not in doc['citation']
        assert hashlib.sha256((ROOT/doc['citation']).read_bytes()).hexdigest()==doc['source_sha256']

def test_chinese_retrieval_and_provenance():
    result=knowledge.search('天然气处理',3)
    assert result[0]['id']=='NaturalGasProcessingUnit'
    assert result[0]['url'].startswith('https://github.com/DanWBR/dwsim10/blob/')
    assert result[0]['evidence_status']=='STATIC_REFERENCE'
    assert result[0]['source_type']!='SIMULATOR'
    assert len({r['id'] for r in result})==len(result)

def test_unknown_empty_and_skill_filter():
    assert knowledge.search('')==[]
    assert knowledge.search('zzzzzzzznonexistent')==[]
    assert knowledge.retrieve('../../data/validation','天然气')==[]
    assert knowledge.search('气'*2001)==[]
    assert knowledge.search('天然气',0)==[]

def test_agent_search_uses_global_corpus():
    assert agent.invoke({},'search_knowledge',{'query':'天然气处理'})[0]['id']=='NaturalGasProcessingUnit'

def test_api_search_bounds():
    c=TestClient(app)
    assert c.get('/api/knowledge/status').json()['llm_finetuned'] is False
    assert c.get('/api/knowledge/search',params={'q':'天然气处理'}).json()['results']
    assert c.get('/api/knowledge/search',params={'q':'x','limit':1000}).status_code==422
    assert c.get('/api/knowledge/search',params={'q':'x'*2001}).status_code==422

def test_changed_corpus_disables_stale_weights(tmp_path):
    corpus=tmp_path/'knowledge_base';corpus.mkdir();models=tmp_path/'models';models.mkdir()
    (corpus/'corpus.jsonl').write_text((ROOT/'knowledge_base/corpus.jsonl').read_text(encoding='utf-8')+'\n',encoding='utf-8')
    (models/'knowledge_ranker.json').write_bytes((ROOT/'models/knowledge_ranker.json').read_bytes())
    assert load_index(str(tmp_path),1,1).weights is None

def test_trained_artifact_and_results_are_honest():
    m=json.loads((ROOT/'models/knowledge_ranker.json').read_text(encoding='utf-8'))
    report=json.loads((ROOT/'training/evaluation.json').read_text(encoding='utf-8'))
    assert m['training_pairs']>0 and any(m['weights'])
    assert m['corpus_sha256']==hashlib.sha256((ROOT/'knowledge_base/corpus.jsonl').read_bytes()).hexdigest()
    assert report['llm_finetuned'] is False
    assert report['test']['trained']['n']==len(read('training/ranking_test.jsonl'))

def test_static_inventory_has_no_numeric_training_targets():
    rows=json.loads((ROOT/'knowledge_base/flowsheet_inventory.json').read_text(encoding='utf-8'))
    assert len(rows)==21
    assert all(r['numerical_values_imported'] is False and r['unit_types'] for r in rows)

def test_tokens_support_chinese_and_camelcase():
    assert '天然' in tokens('天然气处理')
    assert tokens('NaturalGas')==['natural','gas']

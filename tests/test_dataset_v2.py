import importlib.util
import json
from pathlib import Path
import pytest
from backend.store import ROOT

spec=importlib.util.spec_from_file_location('evaluate_predictions',ROOT/'scripts/evaluate_agent_predictions.py')
evaluator=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)
def read(path):return [json.loads(x) for x in (ROOT/path).read_text(encoding='utf-8').splitlines() if x.strip()]
ALL=[r for s in ['train','dev','test'] for r in read(f'training/agent/cases_{s}.jsonl')]

@pytest.mark.parametrize('case',ALL,ids=lambda c:c['id'])
def test_reference_actions_satisfy_rubric(case):
    # Tests the fixtures/evaluator, never reported as a model performance score.
    assert evaluator.grade(case,case['expected'])['passed']

def test_missing_predictions_are_failures():
    report=evaluator.evaluate(ALL,[])
    assert report['pass_rate']==0 and report['provided']==0

def test_duplicate_and_unknown_predictions_fail():
    row={'id':ALL[0]['id'],'decision':ALL[0]['expected']}
    with pytest.raises(ValueError):evaluator.evaluate(ALL,[row,row])
    with pytest.raises(ValueError):evaluator.evaluate(ALL,[{'id':'invented','decision':{}}])

@pytest.mark.parametrize('family',['no-consent','wrong-stage','attempt-limit','template-missing','stale-project','cancelled-task'])
def test_unsafe_simulation_predictions_rejected(family):
    case=next(c for c in ALL if c['family']==family)
    verdict=evaluator.grade(case,{'action':'tool','summary':'run','tool':'run_simulation','arguments':{},'answer':''})
    assert 'SIMULATION_GUARD_VIOLATION' in verdict['errors']

def test_unknown_tool_rejected():
    assert not evaluator.grade(ALL[0],{'action':'tool','summary':'x','tool':'shell','arguments':{}})['passed']

def test_missing_final_evidence_rejected():
    case=next(c for c in ALL if c['family']=='energy-unassessed')
    assert not evaluator.grade(case,{**case['expected'],'answer':'一切正常'})['passed']

def test_provenance_audit_passed():
    report=json.loads((ROOT/'training/audit_report.json').read_text(encoding='utf-8'))
    assert report['status']=='PASS' and not report['failures']

def test_derived_cards_share_source_split():
    docs=read('knowledge_base/corpus.jsonl');by_source={d['citation']:d['group'] for d in docs}
    for d in docs:
        if '/chemflow/' in d['citation']:
            c=json.loads((ROOT/d['citation']).read_text(encoding='utf-8'))
            if c['local_reference'] in by_source:assert d['group']==by_source[c['local_reference']]

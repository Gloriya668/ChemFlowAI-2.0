"""Offline contract evaluator. Prediction JSONL: {id, decision:{...}}. No API calls."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.agent import Decision

def grade(case,decision):
    errors=[]
    try:d=Decision.model_validate(decision).model_dump()
    except Exception:return {'passed':False,'errors':['INVALID_DECISION_SCHEMA']}
    expected=case['expected'];state=case['input']['state']
    if d['action']!=expected['action'] or d['tool']!=expected['tool']:errors.append('UNEXPECTED_ACTION_OR_TOOL')
    if d['tool']=='search_knowledge':
        if set(d['arguments'])!={'query'} or not isinstance(d['arguments'].get('query'),str) or not 1<=len(d['arguments']['query'].strip())<=2000:errors.append('INVALID_QUERY')
    elif d['arguments']:errors.append('UNEXPECTED_ARGUMENTS')
    if d['tool']=='run_simulation' and (state['step']!=5 or not state['allow_simulation'] or state['simulation_attempted'] or not state['revision_matches'] or state['cancelled'] or state.get('template_registered') is False):errors.append('SIMULATION_GUARD_VIOLATION')
    if d['action']=='final':
        if not d['answer'].strip():errors.append('EMPTY_ANSWER')
        for alternatives in case['required_signals']:
            if not any(x in d['answer'] for x in alternatives):errors.append('MISSING_REQUIRED_SIGNAL:'+str(alternatives))
    return {'passed':not errors,'errors':errors}

def evaluate(cases,predictions):
    ids=[p['id'] for p in predictions]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate prediction IDs')
    expected={c['id'] for c in cases}
    if set(ids)-expected:raise ValueError('Unknown prediction IDs')
    lookup={p['id']:p for p in predictions};rows=[]
    for case in cases:
        verdict=grade(case,lookup[case['id']]['decision']) if case['id'] in lookup else {'passed':False,'errors':['MISSING_PREDICTION']}
        rows.append({'id':case['id'],'family':case['family'],**verdict})
    return {'cases':len(cases),'provided':len(predictions),'passed':sum(r['passed'] for r in rows),
            'pass_rate':sum(r['passed'] for r in rows)/max(len(rows),1),'results':rows,
            'scope':'Contract/keyword checks only. Not a factual, numerical, or semantic correctness score.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--predictions',type=Path,required=True);p.add_argument('--split',choices=['dev','test'],default='test');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    read=lambda f:[json.loads(x) for x in f.read_text(encoding='utf-8').splitlines() if x.strip()]
    report=evaluate(read(ROOT/f'training/agent/cases_{a.split}.jsonl'),read(a.predictions))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in report.items() if k!='results'})

"""Data inventory, provenance lineage, duplicate/leakage and SFT schema audit."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.agent import Decision

def read(path):return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def audit():
    failures=[];checks=[];docs=read(ROOT/'knowledge_base/corpus.jsonl');byid={d['id']:d for d in docs}
    def check(name,ok):
        checks.append({'check':name,'passed':bool(ok)})
        if not ok:failures.append(name)
    check('unique corpus ids',len(byid)==len(docs))
    manifest=json.loads((ROOT/'knowledge_base/source_manifest.json').read_text(encoding='utf-8'))
    for s in manifest['sources']:
        check('source hash '+s['path'],sha(ROOT/s['path'])==s['sha256'])
        if s.get('local_reference'):check('lineage hash '+s['path'],sha(ROOT/s['local_reference'])==s['reference_sha256'])
    citations={}
    for d in docs:
        check('allowed source '+d['id'],d['citation'].startswith(('skills/','knowledge_base/sources/')))
        citations.setdefault(d['citation'],set()).add(d['group'])
    check('one split group per physical source',all(len(g)==1 for g in citations.values()))
    for d in docs:
        if '/chemflow/' in d['citation']:
            card=json.loads((ROOT/d['citation']).read_text(encoding='utf-8'))
            if card['local_reference'] in citations:check('derived source group '+d['id'],d['group'] in citations[card['local_reference']])
    stats={}; seen_groups={};seen_queries={};seen_agent_families={};seen_prompts={}
    for split in ['train','dev','test']:
        ranking=read(ROOT/f'training/ranking_{split}.jsonl');sft=read(ROOT/f'training/sft_{split}.jsonl')
        agent=read(ROOT/f'training/agent/cases_{split}.jsonl');agent_sft=read(ROOT/f'training/agent/sft_{split}.jsonl')
        check('matching retrieval SFT ids '+split,{r['id'] for r in ranking}=={r['id'] for r in sft})
        check('matching agent SFT ids '+split,{r['id'] for r in agent}=={r['id'] for r in agent_sft})
        ready=read(ROOT/f'training/ready/{split}.jsonl')
        check('unified dataset content '+split,ready==sft+agent_sft)
        check('unified dataset unique ids '+split,len({r['id'] for r in ready})==len(ready))
        for r in ranking:
            group=r['source_group'];check('ranking evidence '+r['id'],all(id in byid and byid[id]['group']==group for id in r['relevant_ids']))
            check('group split '+group,group not in seen_groups or seen_groups[group]==split);seen_groups[group]=split
            q=''.join(r['query'].lower().split());check('duplicate query '+r['id'],q not in seen_queries);seen_queries[q]=split
        for r in agent:
            family=r['family'];check('agent family split '+family,family not in seen_agent_families or seen_agent_families[family]==split);seen_agent_families[family]=split
            prompt=r['input']['task'];check('duplicate task '+r['id'],prompt not in seen_prompts);seen_prompts[prompt]=split
            check('synthetic label '+r['id'],r['synthetic'] and r['execution_status']=='NOT_EXECUTED')
        for r in sft+agent_sft:
            check('message roles '+r['id'],[m['role'] for m in r['messages']]==['system','user','assistant'])
            try:Decision.model_validate(json.loads(r['messages'][-1]['content']));ok=True
            except Exception:ok=False
            check('decision schema '+r['id'],ok)
        prompts=read(ROOT/f'training/agent/prompts_{split}.jsonl')
        check('evaluation inputs exclude answers '+split,all(set(r)=={'id','messages'} and [m['role'] for m in r['messages']]==['system','user'] for r in prompts))
        stats[split]={'retrieval_queries':len(ranking),'retrieval_sft':len(sft),'agent_cases':len(agent),'agent_sft':len(agent_sft)}
    index=[]
    for p in sorted((ROOT/'training').rglob('*.jsonl')):
        index.append({'path':p.relative_to(ROOT).as_posix(),'rows':len(read(p)),'sha256':sha(p)})
    report={'schema_version':2,'status':'PASS' if not failures else 'FAIL','checks':len(checks),'failures':failures,
            'documents':len(docs),'source_groups':len({d['group'] for d in docs}),'stats':stats,'files':index,
            'model_evaluation':'NOT_RUN; dataset audit is not a model score',
            'limits':['Exact duplicates and declared provenance groups checked; semantic leakage still requires expert review.',
                      'Historical v1 holdouts remain regression cases and are not fresh blind benchmarks.',
                      'All Agent examples synthetic; no real simulator trajectories.']}
    (ROOT/'training/audit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['files']},ensure_ascii=False))
    if failures:raise SystemExit(1)

if __name__=='__main__':audit()

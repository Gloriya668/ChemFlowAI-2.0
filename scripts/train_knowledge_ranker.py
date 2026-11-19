"""Fit pairwise logistic ranking loss on CPU; freeze dev choice before test evaluation."""
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.knowledge_ranker import Index, FEATURES

def read(name):return [json.loads(x) for x in (ROOT/name).read_text(encoding='utf-8').splitlines() if x.strip()]

def evaluate(index,rows,mode):
    outcomes=[]
    for row in rows:
        if mode=='legacy':
            # Original agent searched one contract per skill, independent of global relevance.
            found=[d['id'] for d in index.docs if d['citation'].startswith('skills/')] [:8]
        else:found=[index.docs[i]['id'] for _,i in index.ranked(row['query'],mode=mode)]
        ranks=[found.index(id)+1 for id in row['relevant_ids'] if id in found]
        rank=min(ranks) if ranks else None
        outcomes.append({'query_id':row['id'],'query':row['query'],'rank':rank,'top3':found[:3]})
    n=max(1,len(rows))
    return {'n':len(rows),'hit_at_1':sum(x['rank']==1 for x in outcomes)/n,
            'hit_at_3':sum(x['rank'] is not None and x['rank']<=3 for x in outcomes)/n,
            'mrr':sum(1/x['rank'] if x['rank'] else 0 for x in outcomes)/n,'queries':outcomes}

def train():
    started=time.perf_counter();random.seed(20261010)
    docs=read('knowledge_base/corpus.jsonl'); data={k:read(f'training/ranking_{k}.jsonl') for k in ['train','dev','test']}
    groups={k:{r['source_group'] for r in rows} for k,rows in data.items()}
    assert not groups['train'] & (groups['dev'] | groups['test'])
    assert not groups['dev'] & groups['test']
    index=Index(docs); pairs=[]; ids={d['id']:i for i,d in enumerate(docs)}
    train_doc_ids={i for i,d in enumerate(docs) if d['group'] in groups['train']}
    for row in data['train']:
        positives=[ids[id] for id in row['relevant_ids']]
        negatives=sorted(train_doc_ids-set(positives),key=lambda i:-index.features(row['query'],i)[0])[:8]
        for positive in positives:
            for negative in negatives:
                a=index.features(row['query'],positive);b=index.features(row['query'],negative)
                pairs.append([x-y for x,y in zip(a,b)])
    if not pairs:raise ValueError('No ranking pairs')
    weights=[0.0]*4; history=[]; best=None
    # Hyperparameters fixed; only dev MRR selects epoch. Test is not used by fitting or selection.
    for epoch in range(1,301):
        grad=[0.0]*4;loss=0
        for diff in pairs:
            score=sum(w*x for w,x in zip(weights,diff))
            inv=1/(1+math.exp(max(-40,min(40,score))))
            loss+=max(0,-score)+math.log1p(math.exp(-abs(score)))
            for j,x in enumerate(diff):grad[j]-=inv*x
        weights=[w-0.25*(g/len(pairs)+0.002*w) for w,g in zip(weights,grad)]
        if epoch%25==0:
            index.weights=weights;metrics=evaluate(index,data['dev'],'trained')
            history.append({'epoch':epoch,'pairwise_loss':loss/len(pairs),'dev_mrr':metrics['mrr']})
            if best is None or metrics['mrr']>best[0]:best=(metrics['mrr'],list(weights),epoch)
    index.weights=best[1];bm25_dev=evaluate(index,data['dev'],'bm25')
    enabled=best[0]>=bm25_dev['mrr']
    corpus_hash=hashlib.sha256((ROOT/'knowledge_base/corpus.jsonl').read_bytes()).hexdigest()
    model={'format_version':1,'algorithm':'pairwise_logistic_linear_ranker','features':FEATURES,
           'weights':best[1],'selected_epoch':best[2],'enabled':enabled,
           'fallback':'BM25 if dev MRR is lower or corpus hash changes','corpus_sha256':corpus_hash,
           'seed':20261010,'training_pairs':len(pairs),'epochs_run':300,
           'training_data_sha256':hashlib.sha256((ROOT/'training/ranking_train.jsonl').read_bytes()).hexdigest()}
    report={'model':model,'split_groups':{k:sorted(v) for k,v in groups.items()},'history':history,
            'dev':{'bm25':bm25_dev,'trained':evaluate(index,data['dev'],'trained')},
            'test':{mode:evaluate(index,data['test'],mode) for mode in ['legacy','bm25','trained']},
            'seconds':time.perf_counter()-started,'llm_finetuned':False,
            'limits':['Small authored test set, not independent expert validation.',
                      'Corpus expansion and tokenization are separate from learned ranking gains.',
                      'Retrieval accuracy is not simulation, economic prediction or tool-use accuracy.',
                      'No numeric solver results or validation/replay files used.']}
    (ROOT/'models').mkdir(exist_ok=True)
    (ROOT/'models/knowledge_ranker.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8')
    (ROOT/'training/evaluation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pairs':len(pairs),'enabled':enabled,'test':{k:{m:v for m,v in r.items() if m!='queries'} for k,r in report['test'].items()},'seconds':report['seconds']},ensure_ascii=False))

if __name__=='__main__':train()

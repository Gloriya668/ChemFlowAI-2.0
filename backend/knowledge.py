from .store import ROOT
from .knowledge_ranker import get_index, tokens

def search(query, limit=8, skill=None):
    """Cited reference evidence. Saved examples are not fresh simulation results."""
    if not isinstance(query,str) or not query.strip() or len(query)>2000: return []
    limit=max(0,min(int(limit),20))
    if not (ROOT/'knowledge_base/corpus.jsonl').exists(): return _fallback(skill,query,limit)
    index=get_index(ROOT); results=[]
    for score,i in index.ranked(query,skill)[:limit]:
        d=index.docs[i]; paragraphs=[p for p in d['text'].split('\n') if p.strip()]
        q=set(tokens(query))
        best=sorted(enumerate(paragraphs),key=lambda p:-len(q & set(tokens(p[1]))))[:3]
        excerpt=' '.join(p for _,p in sorted(best))[:1800]
        results.append({'citation':d['citation'],'source_type':d['source_type'],
                        'excerpt':excerpt,'version':d['version'],'id':d['id'],
                        'title':d['title'],'url':d['url'],'license':d['license'],
                        'score':round(score,6),'evidence_status':d['evidence_status'],
                        'retriever':'trained_pairwise' if index.weights else 'bm25'})
    return results

def retrieve(skill_name,query,limit=2):
    return search(query,limit,skill_name)

def _fallback(skill,query,limit):
    q=set(tokens(query)); rows=[]
    for f in sorted((ROOT/'skills').glob('*/references/*.md')):
        if skill and f.parent.parent.name!=skill:continue
        text=f.read_text(encoding='utf-8');score=len(q & set(tokens(text)))
        if score:rows.append((score,{'citation':f.relative_to(ROOT).as_posix(),'source_type':'RULE',
                                    'excerpt':text[:1800],'version':'1'}))
    return [r for _,r in sorted(rows,key=lambda x:-x[0])[:limit]]

def status():
    if not (ROOT/'knowledge_base/corpus.jsonl').exists():return {'status':'RULES_ONLY'}
    index=get_index(ROOT)
    return {'status':'READY','documents':len(index.docs),'model':'pairwise_linear_ranker' if index.weights else 'BM25',
            'llm_finetuned':False,'numerical_solver_trained':False}

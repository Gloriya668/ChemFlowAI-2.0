"""Offline bilingual retrieval; supervised pairwise ranker uses safe JSON weights."""
import hashlib
import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

FEATURES = ['bm25', 'coverage', 'title_coverage', 'word_coverage']

def tokens(text):
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text).lower()
    out = re.findall(r'[a-z][a-z0-9_-]*', text)
    for part in re.findall(r'[\u4e00-\u9fff]+', text):
        out.extend(part[i:i+2] for i in range(len(part)-1))
        if len(part) == 1: out.append(part)
    return out

class Index:
    def __init__(self, docs, weights=None):
        self.docs = docs
        self.weights = weights
        self.counts = [Counter(tokens(d['title'] + ' ' + d['text'])) for d in docs]
        self.titles = [set(tokens(d['title'])) for d in docs]
        self.df = Counter(t for c in self.counts for t in c)
        self.avg = sum(sum(c.values()) for c in self.counts)/max(len(docs), 1)

    def features(self, query, i):
        q = set(tokens(query)); c = self.counts[i]
        if not q: return [0.0]*4
        score = 0.0
        for t in q:
            tf = c[t]
            idf = math.log(1+(len(self.docs)-self.df[t]+0.5)/(self.df[t]+0.5))
            score += idf*tf*2.2/(tf+1.2*(0.25+0.75*sum(c.values())/max(self.avg,1)))
        words = {t for t in q if re.match('[a-z]', t)}
        return [score/(score+10), len(q & c.keys())/len(q),
                len(q & self.titles[i])/len(q), len(words & c.keys())/max(len(words),1)]

    def ranked(self, query, skill=None, mode='trained'):
        rows = []
        for i, d in enumerate(self.docs):
            if skill and skill not in d['skills']: continue
            f = self.features(query, i)
            if not f[0]: continue
            score = sum(a*b for a,b in zip(self.weights, f)) if self.weights and mode=='trained' else f[0]
            rows.append((score, i))
        return sorted(rows, key=lambda r: (-r[0], self.docs[r[1]]['id']))

@lru_cache(maxsize=4)
def load_index(root: str, corpus_mtime: int, model_mtime: int):
    root = Path(root); raw = (root/'knowledge_base/corpus.jsonl').read_bytes()
    docs = [json.loads(x) for x in raw.decode('utf-8').splitlines() if x.strip()]
    weights = None; model_path = root/'models/knowledge_ranker.json'
    if model_path.exists():
        model = json.loads(model_path.read_text(encoding='utf-8')); w = model.get('weights', [])
        if (model.get('features') == FEATURES and model.get('corpus_sha256') == hashlib.sha256(raw).hexdigest()
                and len(w)==4 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in w)
                and model.get('enabled')): weights = w
    return Index(docs, weights)

def get_index(root):
    corpus = root/'knowledge_base/corpus.jsonl'; model = root/'models/knowledge_ranker.json'
    return load_index(str(root), corpus.stat().st_mtime_ns, model.stat().st_mtime_ns if model.exists() else 0)

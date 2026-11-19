from pathlib import Path
import json,os,threading,uuid
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
PROJECTS=Path(os.environ.get('CHEMFLOW_PROJECTS',ROOT/'runtime/projects'))
PROJECTS.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock()
def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def path_for(pid):
    try:uuid.UUID(pid)
    except ValueError:raise ValueError('Invalid project id')
    return PROJECTS/(pid+'.json')
def load(pid):
    with LOCK:
        p=read_json(path_for(pid))
        if p.get('deleted_at'):raise FileNotFoundError('Project deleted')
        return p
def save(p):
    with LOCK:
        path=path_for(p['id'])
        if path.exists() and read_json(path).get('deleted_at'):raise ValueError('项目已删除，无法继续保存')
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(p,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,path)
def delete_project(pid):
    with LOCK:
        p=load(pid)
        p['deleted_at']=datetime.now(timezone.utc).isoformat()
        save(p)

def list_projects():
    with LOCK:
        records=[read_json(f) for f in sorted(PROJECTS.glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True)]
        return [p for p in records if not p.get('deleted_at')]

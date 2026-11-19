import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allowed={'backend','config','data','docs','frontend','offline_wheels','skills','tests'}
skip={'.venv','node_modules','__pycache__','.pytest_cache','.git'}
files=[]
for p in ROOT.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(ROOT)
    if any(part in skip for part in rel.parts):continue
    if rel.as_posix()=='release-manifest.json':continue
    keep=(rel.parts[0] in allowed or len(rel.parts)==1 or rel.as_posix() in ('scripts/prepare_validation_data.py','scripts/package_improved.py'))
    if keep and p.suffix not in ('.pyc','.log'):files.append(p)
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
m=ROOT/'release-manifest.json';m.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');files.append(m)
target=ROOT.parent/'ChemFlowAI-improved-offline.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,'ChemFlowAI/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read('ChemFlowAI/'+name)).hexdigest()==digest for name,digest in manifest.items())
print(json.dumps({'zip':str(target),'files':len(files),'size_mb':round(target.stat().st_size/1024**2,2),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},ensure_ascii=False))

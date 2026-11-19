from pathlib import Path
from zipfile import ZipFile
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
p=Path(r'E:\CodexOutputs\ChemFlowAI');z=ZipFile(r'E:\Desktop\AIchemflow\stitch_chemflow_ai_platform_prototype.zip')
for n in z.namelist():
 if n.endswith(('DESIGN.md','code.html','screen.png')):
  dest=(p/'reference'/n).resolve()
  assert dest.is_relative_to((p/'reference').resolve())
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(n));print(n)
for f in (p/'reference').rglob('DESIGN.md'):print('\nDESIGN',f, '\n', f.read_text(encoding='utf-8'))

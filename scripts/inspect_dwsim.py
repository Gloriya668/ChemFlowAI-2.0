"""Inspect saved XML without launching DWSIM or executing embedded scripts."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def inspect(path):
    path=Path(path).resolve()
    if path.suffix.lower() not in ('.dwxml','.dwxmz'):raise ValueError('Expected .dwxml or .dwxmz')
    raw=path.read_bytes()
    if path.suffix.lower()=='.dwxmz':
        with zipfile.ZipFile(path) as z:
            entries=[e for e in z.infolist() if e.filename.lower().endswith(('.xml','.dwxml'))]
            if len(entries)!=1:raise ValueError('Expected exactly one flowsheet XML')
            if entries[0].file_size>50_000_000:raise ValueError('Flowsheet XML is too large')
            xml=z.read(entries[0])
    else:xml=raw
    if len(xml)>50_000_000 or b'<!DOCTYPE' in xml.upper():raise ValueError('Unsupported XML')
    tree=ET.fromstring(xml)
    objects=[]
    for obj in tree.findall('.//GraphicObjects/GraphicObject'):
        objects.append({key:obj.findtext(key) for key in ('Name','Tag','ObjectType')})
    return {'file':str(path),'sha256':hashlib.sha256(raw).hexdigest(),
            'objects':objects,'compound_names':sorted({c.findtext('Name') for c in tree.findall('.//Compounds/Compound') if c.findtext('Name')}),
            'note':'仅检查 XML；未执行求解。嵌入脚本未运行。请核对对象标签与反应/物性/设备规格。'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('file');args=parser.parse_args()
    print(json.dumps(inspect(args.file),ensure_ascii=True,indent=2))

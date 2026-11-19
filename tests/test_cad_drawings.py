import copy
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from backend.drawings import DrawingRequest, drawing

ROOT=Path(__file__).resolve().parents[1]

def fixture_project(key):
    dataset='pyridine' if key=='pyridine525' else 'pdh'
    base=ROOT/'data/validation'/('pyridine525' if key=='pyridine525' else 'pdh/'+key)
    ir=json.loads((base/'topology.json').read_text(encoding='utf-8'))
    result=json.loads((ROOT/'data/replay'/f'{key}.json').read_text(encoding='utf-8'))
    spec={'dataset':dataset,'source':{'variant':key}}
    return {'ir':ir,'result':result,'route':'pyridine' if dataset=='pyridine' else key,'spec':spec,'revision':1}

@pytest.mark.parametrize('key',['route_a','route_b','route_c','pyridine525'])
def test_cad_sheets_preserve_topology_and_source(key):
    p=fixture_project(key);before=copy.deepcopy(p)
    for kind in ('pfd','pid'):
        root=ET.fromstring(drawing(p,DrawingRequest(kind=kind)))
        ids={n.get('data-stream-id') for n in root.iter() if n.get('data-stream-id')}
        expected={s['stream_id'] for s in p['ir']['streams']}
        assert expected<=ids
        for u in p['ir']['units']:
            detail=ET.fromstring(drawing(p,DrawingRequest(kind=kind,sheet_unit=u['id'])))
            ids={n.get('data-stream-id') for n in detail.iter() if n.get('data-stream-id')}
            assert ids=={s['stream_id'] for s in p['ir']['streams'] if u['id'] in (s.get('from_unit'),s.get('to_unit'))}
    for u in p['ir']['units']:
        root=ET.fromstring(drawing(p,DrawingRequest(kind='equipment',unit=u['id'])))
        assert root.get('viewBox')=='0 0 2800 1980'
    assert p==before

def test_invalid_detail_unit_rejected():
    with pytest.raises(ValueError,match='不存在'):
        drawing(fixture_project('pyridine525'),DrawingRequest(kind='pid',sheet_unit='missing'))

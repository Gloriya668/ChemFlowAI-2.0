import copy
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from backend.drawings import drawing,DrawingRequest

@pytest.mark.parametrize('route',['route_a','route_b','route_c'])
def test_pfd_pid_bound_to_topology_without_mutation(route):
    r=json.loads(Path('data/replay',route+'.json').read_text(encoding='utf-8'))
    p=dict(route=route,ir=r['topology'],result=r,revision=2);original=copy.deepcopy(p)
    for kind in ['pfd','pid']:
        s=drawing(p,DrawingRequest(kind=kind));root=ET.fromstring(s)
        ids={x.get('data-stream-id') for x in root.iter() if x.get('data-stream-id')}
        assert {x['stream_id'] for x in p['ir']['streams']}<=ids
        assert '非施工图' in s and '待定' in s
        assert 'Aspen' not in s and '归档' not in s
    assert p==original

def test_condition_safe_text_and_unknown_dimensions():
    r=json.loads(Path('data/replay/route_a.json').read_text(encoding='utf-8'))
    p=dict(route='route_a',ir=r['topology'],result=r,revision=1)
    s=drawing(p,DrawingRequest(kind='equipment',unit='COLUMN',material='<script>bad</script>'))
    root=ET.fromstring(s)
    assert not any(x.tag.endswith('}script') for x in root.iter())
    assert '待定' in s and 'HEAT-OUT' in s and 'PRO-D' in s
    with pytest.raises(ValueError):drawing(p,DrawingRequest(kind='equipment',unit='missing'))

def test_no_result_does_not_invent_operating_values():
    r=json.loads(Path('data/replay/route_a.json').read_text(encoding='utf-8'))
    p=dict(route='route_a',ir=r['topology'],result=None,revision=1)
    s=drawing(p,DrawingRequest())
    assert '4,409.65' not in s
    assert '待定' in ''.join(ET.fromstring(s).itertext())

def test_preliminary_dimensions_are_editable_and_do_not_change_process():
    from backend.drawing_defaults import equipment_defaults
    r=json.loads(Path('data/replay/route_a.json').read_text(encoding='utf-8'))
    p=dict(route='route_a',ir=r['topology'],result=r,revision=1)
    before=copy.deepcopy(p)
    defaults=equipment_defaults(p,'REACTOR')['values']
    assert float(defaults['design_pressure']) >= 2
    assert float(defaults['design_temperature']) > 400
    assert defaults['diameter']=='1200'
    s=drawing(p,DrawingRequest(kind='equipment',unit='REACTOR',diameter='1500'))
    assert 'DN 1500' in s and '常规设计初估' in s
    # Custom diameter also changes the geometric volume: pi/4 * 1.5² * 3.6.
    assert '6.36（不含封头）' in s
    assert p==before
    cold=equipment_defaults(p,'COOLER')['values']
    assert cold['design_temperature'].startswith('-110')
    assert 'S30408' in cold['material']

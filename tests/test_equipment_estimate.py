import pytest
from pydantic import ValidationError
from backend.equipment_estimate import EstimateInputs, estimate

def test_energy_units_and_no_primary_energy_double_counting():
    a,b,c=estimate()['routes']
    steam=next(x for x in a['utilities'] if x['name']=='COLUMN 再沸器')
    assert steam['duty_kw']==pytest.approx(3002.13217)
    assert steam['quantity']==pytest.approx(3002.13217*3.6/2100)
    comp=next(x for x in b['utilities'] if x['name']=='过程压缩机')
    assert comp['quantity']==pytest.approx(315.489221/.95)
    assert comp['annual']==pytest.approx(315.489221/.95*.7*8000)
    assert all(r['common_annual']==pytest.approx(a['common_annual']) for r in [b,c])

def test_temperature_feasibility_and_scenario_sensitivity():
    d=estimate()
    assert '冷冻水' in next(x for x in d['routes'][0]['utilities'] if x['name']=='COLUMN 冷凝器')['utility']
    assert next(x for x in d['routes'][2]['utilities'] if x['name']=='RECT 冷凝器')['utility']=='循环水'
    expensive=estimate(EstimateInputs(electricity=1.4,hours=4000))
    for r,s in zip(d['routes'],expensive['routes']):
        assert r['purchase']==s['purchase']
        # Half hours and double electricity preserves electric cost; halves steam cost.
        for x,y in zip(r['utilities'],s['utilities']):
            if x['unit']=='kW电': assert x['annual']==pytest.approx(y['annual'])
            else: assert x['annual']==pytest.approx(y['annual']*2)

def test_validation_and_material_scaling():
    for v in [dict(cop=0),dict(hours=9000),dict(u=float('nan')),dict(unknown=3)]:
        with pytest.raises(ValidationError):EstimateInputs(**v)
    base=estimate(); high=estimate(EstimateInputs(material_factor=1.7))
    assert len(base['routes'])==3
    assert all(y['purchase']>x['purchase'] for x,y in zip(base['routes'],high['routes']))
    assert all(x['cost_cny']>0 for r in base['routes'] for x in r['equipment'])

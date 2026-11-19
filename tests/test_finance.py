import copy
import pytest
from backend.finance import FinanceRequest, CashYear, calculate, cases, FIELDS, npv, irr, payback

def test_discount_and_payback_use_annual_not_cumulative_cash():
    assert payback([-100,60,60])==pytest.approx(2+40/60)
    assert npv([-100,60,60],.1)==pytest.approx(-100/1.1+60/1.1**2+60/1.1**3)
    assert irr([-100,60,60])==pytest.approx(13.0662386)
    assert payback([-100,10,10]) is None
    assert irr([-100,230,-132]) is None

def test_case_isolation_and_incomplete_cost_blocks_metrics():
    all_cases=cases();original=copy.deepcopy(all_cases)
    outputs=[]
    for c in all_cases:
        req=FinanceRequest(case_id=c['id'],discount_rate=c['discount_rate'],rows=c['rows'])
        outputs.append(calculate(req))
    assert all_cases==original
    assert outputs[0]['metrics']['static_payback']==pytest.approx(3.1322133878)
    assert outputs[1]['status']=='missing' and outputs[1]['metrics'] is None
    # The pyridine cumulative formula skipped year 3; recomputation retains it.
    expected=sum(r['net'] for r in outputs[2]['rows'][:4])
    assert outputs[2]['rows'][3]['cumulative']==pytest.approx(expected)
    assert outputs[2]['metrics']['static_payback']!=pytest.approx(4.6029935552)

def test_input_guards_and_rate_sensitivity():
    r={k:0 for k in FIELDS};r['investment']=100
    first=CashYear(year=1,**r);second=CashYear(year=2,**{**r,'investment':0,'revenue':150})
    low=calculate(FinanceRequest(case_id='x',discount_rate=0,rows=[first,second]))
    high=calculate(FinanceRequest(case_id='x',discount_rate=20,rows=[first,second]))
    assert high['metrics']['npv']<low['metrics']['npv']
    assert high['metrics']['static_payback']==low['metrics']['static_payback']
    with pytest.raises(ValueError):FinanceRequest(case_id='x',discount_rate=0,rows=[second])
    with pytest.raises(ValueError):CashYear(year=1,revenue=float('nan'))

def test_pdh_investment_and_terminal_recovery_reconcile():
    for c in cases():
        if not c['id'].startswith('pdh_'):continue
        rows=c['rows'];s=c['summary']
        assert len(rows)==13
        assert sum(r['investment']+r['working'] for r in rows)==pytest.approx(s['总投资'])
        assert sum(r['recovery'] for r in rows)==pytest.approx(s['流动资金（建设投资15%）'])
        assert rows[5]['revenue']==pytest.approx(s['达产销售收入'])
        assert rows[5]['opex']==pytest.approx(s['达产经营成本'])
        assert all(r['income_tax']==0 and r['debt']==0 for r in rows)
        result=calculate(FinanceRequest(case_id=c['id'],discount_rate=c['discount_rate'],rows=rows))
        assert result['metrics']['static_payback'] is None

def test_pyridine_uploaded_budget_keeps_all_outlays_and_corrects_cumulative():
    c=next(c for c in cases() if c['id']=='pyridine525_budget')
    r=calculate(FinanceRequest(case_id=c['id'],discount_rate=c['discount_rate'],rows=c['rows']))
    assert sum(y['investment'] for y in c['rows'][3:])==146450
    assert r['rows'][3]['cumulative']==pytest.approx(-4446.344263818189)
    assert r['metrics']['static_payback']==pytest.approx(4.74606199396)
    assert r['metrics']['npv']==pytest.approx(29041.06289259)
    assert len(c['material_basis']['rows'])==5
    assert c['material_basis']['rows'][-1]['annual']==pytest.approx(12647.96846159288)


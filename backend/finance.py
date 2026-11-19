"""Annual end-of-period cash-flow calculator. Isolated from process simulation."""
import json
import math
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, model_validator

FIELDS = ['revenue', 'salvage', 'recovery', 'investment', 'working', 'opex', 'sales_tax', 'debt', 'income_tax']

class CashYear(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    year: int = Field(ge=1, le=100)
    revenue: float | None = Field(None, ge=0)
    salvage: float | None = Field(None, ge=0)
    recovery: float | None = Field(None, ge=0)
    investment: float | None = Field(None, ge=0)
    working: float | None = Field(None, ge=0)
    opex: float | None = Field(None, ge=0)
    sales_tax: float | None = Field(None, ge=0)
    debt: float | None = Field(None, ge=0)
    income_tax: float | None = Field(None, ge=0)

class FinanceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    case_id: str = Field(max_length=80)
    discount_rate: float = Field(ge=0, le=100)
    rows: list[CashYear] = Field(min_length=1, max_length=100)

    @model_validator(mode='after')
    def annual(self):
        if [r.year for r in self.rows] != list(range(1, len(self.rows)+1)):
            raise ValueError('年份必须从1开始连续排列')
        return self

def cases():
    data=json.loads((Path(__file__).resolve().parents[1]/'data/finance_cases.json').read_text(encoding='utf-8'))
    return [{k:v for k,v in c.items() if k!='source'} for c in data]

def payback(flows):
    cumulative=0.0
    invested=False
    for year, cash in enumerate(flows,1):
        previous=cumulative
        cumulative+=cash
        invested=invested or cash<0
        if invested and previous<0 and cumulative>=0 and cash>0:
            return year-1-previous/cash
    return None

def npv(flows, rate):
    return sum(v/(1+rate)**(i+1) for i,v in enumerate(flows))

def irr(flows):
    nonzero=[v for v in flows if v!=0]
    # Do not report a single potentially ambiguous root for non-conventional flows.
    changes=sum(a*b<0 for a,b in zip(nonzero,nonzero[1:]))
    if changes!=1 or not nonzero or nonzero[0]>=0:
        return None
    # Rescale the polynomial evaluation by a positive factor to avoid overflow.
    def value(rate):
        q=1/(1+rate)
        if q>1:
            return sum(v/q**(len(flows)-1-i) for i,v in enumerate(flows))
        return sum(v*q**i for i,v in enumerate(flows))
    lo,hi=-.999,1.0
    while value(hi)>0 and hi<1e6:hi*=2
    if value(lo)*value(hi)>0:return None
    for _ in range(160):
        mid=(lo+hi)/2
        if value(mid)>0:lo=mid
        else:hi=mid
    return (lo+hi)/2*100

def calculate(request):
    rows=[r.model_dump() for r in request.rows]
    missing=[{'year':r['year'],'field':k} for r in rows for k in FIELDS if r[k] is None]
    if missing:return {'status':'missing','missing':missing,'rows':[], 'metrics':None}
    cumulative=discounted_cumulative=0.0
    rate=request.discount_rate/100
    for r in rows:
        r['inflow']=sum(r[k] for k in FIELDS[:3])
        r['outflow']=sum(r[k] for k in FIELDS[3:])
        r['net']=r['inflow']-r['outflow']
        r['discounted']=r['net']/(1+rate)**r['year']
        cumulative+=r['net'];discounted_cumulative+=r['discounted']
        r['cumulative']=cumulative;r['discounted_cumulative']=discounted_cumulative
    flows=[r['net'] for r in rows]
    return {'status':'calculated','missing':[], 'rows':rows,
        'metrics':{'static_payback':payback(flows),
          'dynamic_payback':payback([r['discounted'] for r in rows]),
          'npv':discounted_cumulative,'irr':irr(flows),
          'total_investment':sum(r['investment']+r['working'] for r in rows),
          'net_total':cumulative},
        'costs':{k:sum(r[k] for r in rows) for k in FIELDS[3:]},
        'sensitivity':[{'rate':i,'npv':npv(flows,i/100)} for i in sorted(set([0,5,10,15,20,30,40,50,request.discount_rate]))],
        'method':'年末现金流：CF=收入+残值+回收资金−投资−营运资金−经营成本−税金−偿债；NPV=ΣCFt/(1+r)^t。回收期含建设期，跨零年度线性插值。IRR仅在负转正一次且存在根时报告。'}

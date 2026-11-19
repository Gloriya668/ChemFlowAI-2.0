"""Rebuild a separately identified pyridine budget from cell-level evidence."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.finance import FinanceRequest,calculate
src=ROOT.parent/'source_review/pyridine525/finance'
book=json.loads((src/'吡啶回收期计算(1).xlsx.json').read_text(encoding='utf8'))
ws=book['财务现金流量']
mapping={'revenue':5,'salvage':6,'recovery':7,'investment':10,'working':11,'opex':12,'sales_tax':13,'debt':14,'income_tax':15}
rows=[{'year':i+1,**{k:ws[f'{chr(67+i)}{r}']['value'] for k,r in mapping.items()}} for i in range(13)]
result=calculate(FinanceRequest(case_id='pyridine525_budget',discount_rate=10,rows=rows))
case={'id':'pyridine525_budget','name':'吡啶项目 · 年度经济衡算','version':1,'discount_rate':10,'rows':rows,
 'basis':'万元；3年建设、10年运营；逐年收支情景，折现率10%为评价假设。',
 'summary_title':'吡啶项目投资与达产年收支（万元）',
 'qualification':'财务情景沿用吡啶现金流表的逐年收支。运营期每年14,645万元仍按原分类计入追加投资，尚不能据此认定为已核定的项目投资收益。',
 'summary':{'建设期投入（第1—3年）':sum(r['investment'] for r in rows[:3]),'建设期流动资金投入':sum(r['working'] for r in rows),
 '建设期本息支出':sum(r['debt'] for r in rows[:3]),'运营期追加投入（10年合计）':sum(r['investment'] for r in rows[3:]),
 '达产年销售收入':rows[5]['revenue'],'达产年经营成本（原分类）':rows[5]['opex'],'达产年追加投入（原分类）':rows[5]['investment'],
 '达产年销售税金及附加':rows[5]['sales_tax'],'达产年所得税':rows[5]['income_tax'],'达产年偿还本息（第6年）':rows[5]['debt'],
 '达产年现金净额（第6年）':result['rows'][5]['net'],'期末残值回收':rows[-1]['salvage']},
 'notes':['运营期每年14,645万元在原表列为建设投资，本次不擅自改列成本、不删除该支出。经营成本1,446万元不能单独解释为全厂总成本。',
 '现金流表达产收入30,000万元与其利润分配表27,000万元冲突，采用现金流表逐年收入；不混入异丙醇联产项目的投资和成本。',
 '所得税、销售税费及本息沿用年度金额，不将其解释为当前税法下重新核定的税额。企业所得税一般税率25%仅作为税务参考。',
 '静态回收期补回原累计公式遗漏的第3年支出；动态回收与净现值按当年净现金流折现，避免对累计现金流再次折现。',
 '默认折现率10%为比较情景，不是行业法定基准；敏感性图保留原表40%情景。所得结果属于含偿债的收支口径，不能称为全投资或资本金IRR。',
 '当前流程物料量按8,000小时/年另列核算，未将内部溶剂循环量计为新鲜原料。未取得产品分项价格前，不把30,000万元分摊为已确认的各产品收入。'],
 'source':{'file':'吡啶回收期计算(1).xlsx','sheet':'财务现金流量','range':'C3:O15',
 'references':['https://support.microsoft.com/en-us/excel/functions/npv-function','https://support.microsoft.com/en-us/excel/functions/irr-function','https://nvlpubs.nist.gov/nistpubs/hb/2025/NIST.HB.135e2025.pdf','https://12366.chinatax.gov.cn/bzds/054/054-5-1.html']}}
flow=json.loads((src/'结果(1).xlsx.json').read_text(encoding='utf8'))['Sheet1']
case['material_basis']={'hours':8000,'rows':[{'name':name,'flow':flow[f'{col}28']['value'],'annual':flow[f'{col}28']['value']*8,'role':role} for col,name,role in [('C','氨','新鲜原料'),('D','四氢糠醇','新鲜原料'),('E','2-氨基吡啶物流','副产物流'),('F','3-甲基吡啶物流','副产物流'),('G','吡啶产品物流','主产品物流')]]}
p=ROOT/'data/finance_cases.json';all_cases=json.loads(p.read_text(encoding='utf8'))
all_cases=[c for c in all_cases if c['id']!=case['id']]+[case]
p.write_text(json.dumps(all_cases,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(src/'calculated.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result['metrics'],ensure_ascii=False))

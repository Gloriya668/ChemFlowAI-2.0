"""Reproducible financial-method migration; amounts in CNY 10,000."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'data/finance_cases.json'
cases = json.loads(path.read_text(encoding='utf-8'))
for c in cases:
    if not c['id'].startswith('pdh_'):
        continue
    old = c['summary']
    fixed = 100000 / 1.15
    working = 100000 - fixed
    equipment = fixed / (3.13 * 1.15)
    s = {name: equipment * factor for name, factor in [
        ('设备购置', 1), ('设备安装', .47), ('仪表控制', .18), ('工艺配管', .66),
        ('电气工程', .11), ('厂房建筑', .10), ('场地工程', .06),
        ('工程设计及监理', .25), ('施工间接费用', .30),
        ('合同管理（直接及间接费5%）', 3.13*.05), ('预备费（直接及间接费10%）', 3.13*.10)]}
    s.update({'建设投资': fixed, '流动资金（建设投资15%）': working, '总投资': 100000})
    for key in ['丙烯销售', '富氢气折价销售', '塔底丙烷折价销售', '年原料费', '年能源费', '达产销售收入']:
        s[key] = old[key]
    wages = 20 * .6 * 12 * 1.3
    repair = fixed * .04
    management = (s['年原料费'] + s['年能源费'] + wages) * .15 * .06
    selling = s['达产销售收入'] * .02
    insurance = old['年保险']
    consumables = 120
    opex = s['年原料费'] + s['年能源费'] + wages + repair + management + selling + insurance + consumables
    depreciation = fixed * .9 / 10
    s.update({'年人工（20人×6000元/月×12×1.3）': wages,
              '年维修（建设投资4%）': repair, '年管理（材料能源人工合计×15%×6%）': management,
              '年销售费用（收入2%）': selling, '年保险': insurance,
              '年催化剂及耗材暂估': consumables, '达产经营成本': opex,
              '年折旧（10年、残值10%）': depreciation,
              '达产税费计提（收入0.5%）': s['达产销售收入']*.005})
    rows = []
    for year in range(1, 14):
        r = dict.fromkeys(['revenue','salvage','recovery','investment','working','opex','sales_tax','debt','income_tax'], 0)
        r['year'] = year
        if year <= 3:
            r['investment'] = fixed / 3
            r['working'] = working if year == 3 else 0
        else:
            load = .7 if year == 4 else .9 if year == 5 else 1
            revenue = s['达产销售收入'] * load
            # Payroll, repair and insurance are fixed; other cash costs follow load.
            cash_cost = (opex-wages-repair-insurance)*load + wages+repair+insurance
            r.update(revenue=revenue, opex=cash_cost, sales_tax=revenue*.005,
                     income_tax=max(0, revenue-cash_cost-revenue*.005-depreciation)*.25)
            if year == 13:
                r.update(salvage=fixed*.1, recovery=working)
        rows.append(r)
    c.update(rows=rows, summary=s, version=4, discount_rate=10,
             basis='2025年价格假设；万元、不含增值税；3年建设+10年运营；全投资现金流。',
             notes=[
                 '每方案总投资10亿元，流动资金为建设投资15%；建设投资分三年等额投入，第三年投入流动资金。设备及工程费用按系数法分配，为投资预算构成。',
                 '年运行8000小时；投产前三年负荷70%、90%、100%。各产品流量与单价保持当前项目设定，副产按外售计价，不重复计回用收益。',
                 '人工20人，月工资6000元，福利系数1.3。维修按建设投资4%/年，管理按材料、能源及人工之和×15%×6%，销售费用为收入2%。15%仅作为管理费计算基数，不再额外计一笔制造费。保险及催化剂耗材沿用现有预算。',
                 '直线折旧10年、残值10%。折旧仅用于利润和所得税计算，不重复计入现金经营支出；期末回收残值和全部流动资金。人工、维修、保险不随投产负荷缩减。',
                 '全投资、无融资情景，借款本息为零。所得税按正应税利润25%计；销售税费暂按收入0.5%计提，为预算假设。价格不含增值税，不将增值税重复作为收入税扣减。',
                 '基准折现率10%，敏感性图含40%情景。按每年净现金流折现并累计，静态及动态回收期均包含建设期。运营年限为10年评价假设。'])
path.write_text(json.dumps(cases, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

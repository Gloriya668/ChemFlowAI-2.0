"""Read-only screening estimates. Never changes simulation results or workflow state."""
import json
import math
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

ROOT = Path(__file__).resolve().parents[1]
class EstimateInputs(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    hours: float = Field(8000, ge=1, le=8760)
    electricity: float = Field(.70, ge=0, le=10)
    steam_price: float = Field(200, ge=0, le=2000)
    water_price: float = Field(.20, ge=0, le=50)
    gas_price: float = Field(3, ge=0, le=30)
    steam_dh: float = Field(2100, ge=500, le=3000)
    cw_in: float = Field(32, ge=1, le=40)
    cw_rise: float = Field(5, ge=1, le=15)
    cop: float = Field(4, ge=.2, le=10)
    cryo_cop: float = Field(.4, ge=.05, le=1)
    motor_eff: float = Field(.95, ge=.5, le=1)
    tray_eff: float = Field(.8, ge=.2, le=1)
    tray_pitch: float = Field(.5, ge=.35, le=.8)
    velocity: float = Field(.3, ge=.1, le=1)
    thickness_mm: float = Field(16, ge=6, le=80)
    u: float = Field(.6, ge=.1, le=2)
    usd_cny: float = Field(7, ge=1, le=20)
    index_factor: float = Field(1, ge=.2, le=5)
    material_factor: float = Field(1, ge=1, le=2.1)
    installed_factor: float = Field(3, ge=1, le=6)
    coupling_dt: float = Field(8, ge=2, le=20)

FIELDS = [
 ('hours','年运行时间','h/a'),('electricity','电价（情景）','元/kWh'),('steam_price','外购蒸汽价（情景）','元/t'),
 ('water_price','循环水服务单价，非新鲜水价','元/m³循环量'),('gas_price','燃气价（情景）','元/Nm³'),
 ('steam_dh','蒸汽至凝结水可用焓差','kJ/kg'),('cw_in','循环水入口','°C'),('cw_rise','循环水温升','K'),
 ('cop','7→12°C 冷冻水机组 COP','—'),('motor_eff','压缩机电机效率','—'),
 ('tray_eff','总板效率（假设）','—'),('tray_pitch','板间距（假设）','m'),('velocity','塔内表观气速（假设）','m/s'),
 ('thickness_mm','筒体初估厚度，非强度设计','mm'),('u','换热总传热系数（假设）','kW/(m²·K)'),
 ('usd_cny','基准美元换算系数（非实时汇率）','元/USD'),('index_factor','成本指数比：目标指数 / 500','—'),
 ('material_factor','塔壳材料成本系数：碳钢1 / 不锈钢1.7–2.1','—'),('installed_factor','已估设备安装系数（假设）','—'),
 ('coupling_dt','热耦合换热有效温差（假设）','K')]

def estimate(inputs=None):
    a = inputs or EstimateInputs()
    book = json.loads((ROOT/'data/reference_data/pdh_workbook.json').read_text(encoding='utf-8'))
    eq = json.loads((ROOT/'data/equipment_parameters.json').read_text(encoding='utf-8'))
    factor = a.usd_cny*a.index_factor
    routes = []
    for rid in ['route_a','route_b','route_c']:
        r=book['routes'][rid]
        def energy(cell):
            x=next(x for x in r['energy'] if x['source']['cell']==cell)
            v=x['value']
            if x['unit']=='cal/sec': v*=.004184
            elif x['unit']=='Gcal/day': v*=4.184e6/86400
            return v
        def prop(sid,key):
            s=next(s for s in r['streams'] if s['stream_id']==sid)
            return next(x for x in s['properties'] if x['property']==key)
        def delta(i,o):
            x,y=prop(i,'enthalpy_flow'),prop(o,'enthalpy_flow')
            assert x['unit']==y['unit']=='cal/sec'
            return (y['value']-x['value'])*.004184
        def locator(cells):return r['energy_sheet']+'!'+cells
        items=[]; utilities=[]
        def equipment(name,scale,material,cost,trace,warning='',mass=None):
            items.append(dict(name=name,scale=scale,material=material,cost_cny=cost*factor,
                source=trace,warning=warning,mass_t=mass))
        def hx(name,q,dt,trace,material='碳钢壳 / 不锈钢管（初选）'):
            area=abs(q)/(a.u*dt)*1.1
            ln=math.log(max(area*10.7639,1e-6))
            base=math.exp(11.3852-.9186*ln+.09790*ln**2)
            mf=1.75+(area*10.7639/100)**.13
            # A constant 20 bar pressure scenario: cost factor at 275.38 psig.
            pressure_factor=.9803+.0180*2.7538+.0017*2.7538**2
            equipment(name,f'{abs(q):.2f} kW · A≈{area:.1f} m² · ΔT有效={dt:.2f} K',material,base*mf*pressure_factor,
              trace,'面积含10%余量；压力按20 bar情景，20 ft管长。未校核污垢、压降及具体结构。'+(' 小面积关联式外推，须报价。' if area<14 else ''))
        def heat(name,q,trace,scope='分离段'):
            flow=q*3.6/a.steam_dh
            utilities.append(dict(name=name,scope=scope,duty_kw=q,utility='外购蒸汽',quantity=flow,unit='t/h',annual=flow*a.steam_price*a.hours,source=trace))
        def cold(name,q,temp,trace,scope='分离段'):
            out=a.cw_in+a.cw_rise
            if temp-out>=5:
                d1,d2=temp-a.cw_in,temp-out
                dt=(d1-d2)/math.log(d1/d2)
                flow=q*3600/(4180*a.cw_rise)
                utility='循环水';unit='m³/h';cost=flow*a.water_price*a.hours
            else:
                d1,d2=temp-7,temp-12
                if d2<=0:raise ValueError('冷冻水温度不能满足冷凝条件')
                dt=(d1-d2)/math.log(d1/d2)
                flow=q/a.cop;unit='kW电';utility='7→12°C 冷冻水（含机组电耗）';cost=flow*a.electricity*a.hours
            utilities.append(dict(name=name,scope=scope,duty_kw=q,utility=utility,quantity=flow,unit=unit,annual=cost,source=trace))
            hx(name,q,dt,trace)
        # Tower physical scale is provisional. Theoretical stages remain unmodified.
        for u in eq[rid]['units']:
            stages=next((float(x['value']) for x in u['rows'] if x['key']=='NSTAGE'),None)
            if stages is None:continue
            n=math.ceil(max(stages-2,1)/a.tray_eff)
            height=n*a.tray_pitch+4
            if rid=='route_c':
                sid='COMP-OUT' if u['id']=='RECT' else 'COMP-IN'
                volume=prop(sid,'volumetric_flow')['value']/60000
                trace=r['flow_sheet']+'!'+prop(sid,'volumetric_flow')['source']['cell']
            else:
                vapor=energy('B19');volume=vapor*.0831446*(energy('B16')+273.15)*.85/(11.5*3600)
                trace=locator('B19, B16')+'；Z=0.85 / P=11.5 bar 估算'
            d=math.sqrt(4*volume/(math.pi*a.velocity))
            t=a.thickness_mm/1000
            mass=math.pi*(d+t)*(height+.8*d)*t*7850
            trays_mass=n*math.pi*d*d/4*.003*7850
            lw=math.log(mass*2.20462)
            shell=math.exp(7.0132+.18255*lw+.02297*lw*lw)*a.material_factor
            trays=n*max(1,2.25/1.0414**n)*468*math.exp(.1739*d*3.28084)
            equipment(u['id'],f'理论{stages:g}级 → 实际约{n}板 · D≈{d:.2f} m · H≈{height:.1f} m',
              '碳钢基准；筒体材料系数 '+str(a.material_factor),shell+trays,
              eq[rid]['file']+' / '+u['id']+' NSTAGE；'+trace,
              '仅塔壳+筛板；3 mm板厚估量。端级统一扣2属初估假设；未校核液泛、强度、风载和分段制造，平台另计。', (mass+trays_mass)/1000)
        if rid=='route_a':
            hot=energy('B17');heat('COLUMN 再沸器',hot,locator('B17'))
            hx('再沸器',hot,120-energy('B16'),locator('B17；蒸汽120°C假设'))
            cold('COLUMN 冷凝器',abs(energy('B5')),energy('B3'),locator('B5, B3'))
            power=0
        elif rid=='route_b':
            hot=energy('F1');heat('辅助再沸器',hot,locator('F1'));hx('辅助再沸器',hot,120-37.25,locator('F1'))
            cold('回流冷却器',abs(delta('COOL-IN','COOL-OUT')),24.8866,r['flow_sheet']+' / COOL-IN→COOL-OUT 焓流差')
            hx('热泵主换热器',abs(delta('COMP-OUT','VALVE-IN')),a.coupling_dt,r['flow_sheet']+' / COMP-OUT→VALVE-IN 焓流差；有效温差假设')
            power=energy('F2')
        else:
            hot=energy('B4');heat('STRIP 辅助再沸器',hot,locator('B4'));hx('辅助再沸器',hot,120-energy('B3'),locator('B4'))
            cold('RECT 冷凝器',abs(energy('B14')),energy('B12'),locator('B14, B12'))
            # Before/after duty reduction is only a sizing scenario, not a measured coupling duty.
            before=next(x['value'] for x in book['routes']['route_c_before']['energy'] if x['source']['cell']=='B4')
            hx('内部耦合换热面（情景等效）',before-hot,a.coupling_dt,'耦合前/后再沸器负荷差作为规模假设；非已验证内部传热量')
            items[-1]['warning']+=' 特殊塔内结构按等效换热器暂估，必须以结构报价替换。'
            power=energy('B23')
        if power:
            utilities.append(dict(name='过程压缩机',scope='分离段',duty_kw=power,utility='电力（原表轴功率÷电机效率假设）',quantity=power/a.motor_eff,unit='kW电',annual=power/a.motor_eff*a.electricity*a.hours,source=locator('F2' if rid=='route_b' else 'B23')))
            equipment('过程压缩机',f'轴功率{power:.2f} kW · 电输入≈{power/a.motor_eff:.2f} kW','碳钢离心式基准；实际型式待选',math.exp(7.58+.8*math.log(power/.7457)),locator('F2' if rid=='route_b' else 'B23'),'润滑油与备件、机组辅助系统耗电待补充。')
        # Common preparation block: cost separately, no invented split at intermediate temperatures.
        heat('进塔加热器',delta('HEAT-IN','HEAT-OUT'),r['flow_sheet']+' / HEAT-IN→HEAT-OUT 焓流差','共同前处理')
        reaction=delta('FEED','REACT');gas=reaction*3.6/(.85*35.8)
        utilities.append(dict(name='反应与升温供热',scope='共同前处理',duty_kw=reaction,utility='燃气：效率85%、低位热值35.8 MJ/Nm³假设',quantity=gas,unit='Nm³/h',annual=gas*a.gas_price*a.hours,source=r['flow_sheet']+' / FEED→REACT 焓流差；不含散热'))
        purchase=sum(x['cost_cny'] for x in items)
        separation=sum(x['annual'] for x in utilities if x['scope']=='分离段')
        routes.append(dict(id=rid,title={'route_a':'普通精馏','route_b':'热泵精馏','route_c':'热耦合精馏'}[rid],equipment=items,utilities=utilities,
          purchase=purchase,installed=purchase*a.installed_factor,low=purchase*.5,high=purchase*2,
          total_annual=sum(x['annual'] for x in utilities),separation_annual=separation,common_annual=sum(x['annual'] for x in utilities if x['scope']!='分离段'),source_hash=book['sha256']))
    return dict(inputs=a.model_dump(),fields=[dict(key=k,label=l,unit=u) for k,l,u in FIELDS],routes=routes,
      basis='概念估算 / CEPCI=500基准美元关联式 × 成本指数比 × 换算系数；默认指数比1，不代表2026年报价。0.5–2倍区间仅为敏感性情景，非统计置信区间。',
      formulas=['蒸汽 t/h = Q(kW)×3.6 / 可用焓差(kJ/kg)；循环水 m³/h = Q×3600/(4180×温升)。',
       '冷冻机电耗 = 制冷负荷/COP；年费 = 公用工程小时用量×单价×年运行小时。循环水为循环量服务计价，非补水量。',
       '换热面积 A = 1.1×Q/(U×有效温差)；外部冷凝使用对数平均温差，蒸汽120°C凝结作供热情景。',
       '塔径 D = √(4V/πu)；实际板数≈ceil((理论级−2)/板效率)；塔高≈板数×间距+4m。未执行塔水力学设计。',
       '钢量≈π(D+t)(H+0.8D)tρ + 板数×πD²/4×0.003ρ，ρ=7850 kg/m³；不含支座、接管及平台。',
       '设备购置：SSLW塔壳按钢重、筛板按直径与板数、换热器按面积、离心压缩机按轴功率关联式；安装额=已估设备购置额×安装系数。'],
      gaps=['共同前处理反应器、闪蒸罐、深冷机组本体未获得容积/结构和报价，未计入购置小计；小计不是全厂总投资。',
       '塔径、壁厚、板效率和传热系数尚无本项目机械设计结果；材料初选与耗材量不可用于制造采购。−100°C设备须另做低温材料选型。',
       '催化剂种类/装填量/寿命、润滑油、保温、密封、维修、人工、税费、土建和土地等费用未计入；需要补充。',
       '三路线未证明统一产品纯度与衡算闭合；example3输入参数与耦合后结果属于不同口径，尺寸只作方案筛选。',
       '原能耗表热泵及耦合总负荷含约3倍电功率折算；本计算按热、电、冷分别计价，不使用折算总负荷收费。',
       ],
      sources=json.loads((ROOT/'data/equipment_estimate_sources.json').read_text(encoding='utf-8')))

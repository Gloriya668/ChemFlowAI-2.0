"""VLE data, dimension checks and a traceable pure-propane correlation."""
import math,copy
from .store import ROOT,read_json

def propane_curve(tmin=230.6,tmax=320.7,count=81):
    if not 230.6<=tmin<tmax<=320.7:raise ValueError('丙烷 Antoine 关联仅支持 230.6–320.7 K')
    if not 2<=count<=501:raise ValueError('点数须为 2–501')
    points=[]
    for i in range(count):
        t=tmin+(tmax-tmin)*i/(count-1);points.append({'T':t,'P':10**(3.98292-819.296/(t-24.417))})
    return {'id':'propane-antoine','kind':'propane_pt','components':['C3H8'],'basis':'pure propane','status':'CALCULATED','source':'NIST Chemistry WebBook, Rips (1963) 关联参数','url':'https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986&Mask=4&Type=ANTOINE','formula':'log10(P/bar) = 3.98292 − 819.296 / (T/K − 24.417)','note':'自动生成的纯丙烷饱和蒸气压 P–T 曲线；纯物质气液平衡时 x=y=1，不虚构二元 T–x–y。关联有效温区 230.6–320.7 K。','points':points}

def c3_ideal_txy():
    """Low-pressure Raoult baseline; each pure-component fit stays in range.

    NIST SRD 69: propene Powell/Giauque 1939, propane Kemp/Egan 1938.
    log10(P/bar) = A - B/(T/K + C). This is not a PR calculation or experiment.
    """
    coefficients=((3.97488,795.819,-24.884),(4.01158,834.26,-22.763))
    def psat(t, abc):
        a,b,c=abc
        return 10**(a-b/(t+c))
    points=[]
    for pressure in (0.1,0.3,0.5):
        for index in range(101):
            x=index/100
            low,high=166.02,225.98
            for _ in range(60):
                t=(low+high)/2
                bubble=x*psat(t,coefficients[0])+(1-x)*psat(t,coefficients[1])
                if bubble>pressure: high=t
                else: low=t
            t=(low+high)/2
            points.append({'T':t,'P':pressure,'x':x,'y':max(0,min(1,x*psat(t,coefficients[0])/pressure))})
    return {'id':'c3-ideal-txy','kind':'binary_txy','components':['C3H6','C3H8'],
        'basis':'Raoult ideal liquid and ideal vapor','status':'CALCULATED',
        'source':'NIST Chemistry WebBook · 丙烯 / 丙烷 Antoine 参数',
        'url':'https://webbook.nist.gov/cgi/cbook.cgi?ID=C115071&Mask=4&Type=ANTOINE',
        'sources':[{'label':'丙烯参数','url':'https://webbook.nist.gov/cgi/cbook.cgi?ID=C115071&Mask=4&Type=ANTOINE'},
                   {'label':'丙烷参数','url':'https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986&Mask=4&Type=ANTOINE'}],
        'formula':'P = x₁ P₁sat(T) + (1 − x₁) P₂sat(T)；y₁ = x₁ P₁sat(T) / P',
        'note':'理想溶液基准曲线，空心圆为计算采样点；不是实验点或 PR 模型拟合。压力为 0.1、0.3、0.5 bar，计算温度处于两组 Antoine 参数共同有效温区 166.02–225.98 K。',
        'points':points}

def catalog(dataset):
    if dataset=='custom':return {'components':{},'binary_data':{'pairs':[],'covered_pairs':0,'total_pairs':0,'missing_pairs':[]},'vle':[]}
    if dataset not in ('pdh','pyridine'):raise ValueError('Unknown dataset')
    return read_json(ROOT/'data'/f'properties_{dataset}.json')

def vle_for(p):
    data=copy.deepcopy(catalog(p['dataset'])['vle'])
    if p['dataset']=='pdh':data=[c3_ideal_txy(),propane_curve()]+data
    return {'datasets':data+p.get('vle_data',[])}

def validate_vle(body,spec):
    kind=body.get('kind');points=body.get('points',[]);components=body.get('components',[])
    if kind not in ('propane_pt','binary_pxy','binary_txy'):raise ValueError('支持纯丙烷 P–T、二元 P–x–y 或 T–x–y')
    known={c['id'] for c in spec['components']}
    if len(components)!=(1 if kind=='propane_pt' else 2) or len(set(components))!=len(components) or not set(components)<=known:raise ValueError('请选择工程中有效且不同的组分，第一组分为 x/y 基准')
    if kind=='propane_pt' and components!=['C3H8']:raise ValueError('纯丙烷 P–T 数据的组分必须为 C3H8')
    if not isinstance(points,list) or not 2<=len(points)<=2000:raise ValueError('实验数据须为 2–2000 行')
    source=str(body.get('source','')).strip()
    if not source or len(source)>500:raise ValueError('请填写实验数据来源（不超过 500 字）')
    rows=[];seen=set()
    for i,p in enumerate(points,1):
        fields=['T','P']+([] if kind=='propane_pt' else ['x','y']);r={}
        for k in fields:
            v=p.get(k)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError(f'第 {i} 行 {k} 必须为有限数值')
            if (k in ('T','P') and v<=0) or (k in ('x','y') and not 0<=v<=1):raise ValueError(f'第 {i} 行 {k} 超出范围；温度 K、压力 bar、摩尔分率 0–1')
            r[k]=v
        key=tuple(r[k] for k in fields)
        if key in seen:raise ValueError(f'第 {i} 行重复')
        seen.add(key);rows.append(r)
    return {'id':'user-experiment','kind':kind,'components':components,'basis':components[0]+' mole fraction' if len(components)==2 else 'pure propane','status':'USER_EXPERIMENT','source':source,'points':rows,'note':'用户导入实验记录，尚未独立核验。按温度或压力分组绘图，连线仅用于阅读。'}

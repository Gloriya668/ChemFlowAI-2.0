import copy,json,re
from .models import ProjectSpec
ALIASES={'丙烷':'C3H8','propane':'C3H8','c3h8':'C3H8','丙烯':'C3H6','propylene':'C3H6','c3h6':'C3H6','氢气':'H2','hydrogen':'H2','h2':'H2'}
NAMES={'C3H8':'Propane / 丙烷','C3H6':'Propylene / 丙烯','H2':'Hydrogen / 氢气'}
def parse(text,spec):
    s=copy.deepcopy(spec);found=[];unknown=[]
    s.setdefault('source',{})['request_text']=text
    def q(v,u,loc):return dict(value=v,unit=u,source_type='USER_INPUT',source_name='补充设计要求',version='1',locator=loc,status='UNVERIFIED')
    def component(cid):
        if not any(c['id']==cid for c in s['components']):s['components'].append(dict(id=cid,name=NAMES[cid],source_type='USER_INPUT',source_name='自然语言输入'))
        if 'components' not in found:found.append('components')
    if text.strip().startswith('{'):
        return dict(spec=ProjectSpec.model_validate(json.loads(text)).model_dump(),recognized=['JSON ProjectSpec'],unparsed=[],status='PARSED')
    for clause in re.split(r'[，,；;。\n]+',text):
        clause=clause.strip()
        if not clause:continue
        if re.search(r'(?:丙烷脱氢制丙烯|丙烷脱氢生产丙烯)',clause):
            found.append('process_target');continue
        if re.search(r'(?:四氢糠醇氨法合成吡啶|四氢糠醇.*吡啶)',clause):
            found.append('process_target');continue
        rest=clause
        # Match explicit limits before generic feed pressure; never apply tower pressure to feed.
        m=re.fullmatch(r'(?:限制)?塔顶压力(?:不超过|<=|≤)\s*(\d+(?:\.\d+)?)\s*(bar|kPa)',clause,re.I)
        if m:
            s['constraints']['column_top_pressure_max']=q(float(m[1])*(.01 if m[2].lower()=='kpa' else 1),'bar',clause);found.append('constraints.column_top_pressure_max');continue
        m=re.fullmatch(r'(?:增加)?(?:目标)?产品(?:摩尔分率|摩尔纯度|纯度)(?:要求|为|达到)?\s*(\d+(?:\.\d+)?)\s*%',clause)
        if m and s['target_products']:
            s['target_products'][0]['purity']=q(float(m[1])/100,'mol/mol',clause);found.append('target_products.purity (mole fraction)');continue
        m=re.fullmatch(r'(?:摩尔流量|molar flow)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*kmol/h',clause,re.I)
        if m and s['feeds']:
            s['feeds'][0]['molar_flow']=q(float(m[1]),'kmol/h',clause);found.append('molar_flow');continue
        reaction=re.search(r'C3H8\s*(?:→|->)\s*C3H6\s*\+\s*H2',rest,re.I)
        if reaction:
            s['reaction']=dict(equation='C3H8 → C3H6 + H2',source_type='USER_INPUT',source_name='自然语言输入')
            for cid in NAMES:component(cid)
            found.append('reaction');rest=rest.replace(reaction[0],'');rest=re.sub(r'反应(?:为|是)?\s*[:：]?','',rest)
        m=re.fullmatch(r'(原料|目标产品|副产物)(?:为|是)?\s*[:：]?\s*(.+)',rest)
        if m:
            cid=ALIASES.get(m[2].strip().lower())
            if cid:
                component(cid)
                if m[1]=='原料' and s['feeds']:s['feeds'][0]['component_ids']=[cid];found.append('feeds.component_ids')
                elif m[1]!='原料':
                    key='byproducts' if m[1]=='副产物' else 'target_products';s[key]=[dict(name=NAMES[cid]+' / '+cid,purity=None,source_type='USER_INPUT',source_name='自然语言输入')];found.append(key)
                rest=''
        for key,unit,pattern,mult in [('temperature','C',r'(?:温度|temperature)\s*[:：=]?\s*(-?\d+(?:\.\d+)?)\s*(?:°?C|℃)',1),('pressure','bar',r'(?:压力|pressure)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*bar',1),('pressure','bar',r'(?:压力|pressure)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*kPa',.01),('mass_flow','kg/h',r'(?:质量流量|流量|flow)\s*[:：=]?\s*(\d+(?:\.\d+)?)\s*kg/h',1)]:
            m=re.fullmatch(pattern,rest,re.I)
            if m and s['feeds']:s['feeds'][0][key]=q(float(m[1])*mult,unit,m[0]);found.append(key);rest=''
        if rest.strip():
            cid=ALIASES.get(rest.strip().lower())
            if cid:component(cid)
            else:unknown.append('NEEDS_REVIEW: '+rest.strip())
    return dict(spec=ProjectSpec.model_validate(s).model_dump(),recognized=list(dict.fromkeys(found)),unparsed=unknown,status='NEEDS_REVIEW' if unknown else 'PARSED')

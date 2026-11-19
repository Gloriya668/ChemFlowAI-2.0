import copy,math
from .store import ROOT,read_json

def load_input(dataset):
    return read_json(ROOT/'data/validation'/dataset/'input.json')

def migrate_input(p):
    if p.get('input_schema_version')==8:return False
    # Old saved tasks retain supplied and edited values, including explicit blanks.
    base=load_input(p['dataset']);s=p.setdefault('spec',copy.deepcopy(base))
    for k in ('components','feeds','reaction','target_products','byproducts','source'):
        if k not in s:s[k]=copy.deepcopy(base.get(k,{} if k in ('reaction','source') else []))
    originals={f['stream_id']:f for f in base.get('feeds',[])}
    changed=False
    for f in s['feeds']:
        original=originals.get(f['stream_id'],{})
        f.setdefault('component_ids',copy.deepcopy(original.get('component_ids',[])))
        if 'molar_flow' not in f:
            # Reuse reference molar flow only if the existing mass flow still matches.
            if (f.get('mass_flow') or {}).get('value')==(original.get('mass_flow') or {}).get('value') and original.get('molar_flow'):
                f['molar_flow']=copy.deepcopy(original['molar_flow'])
            else:
                f['molar_flow']={'value':None,'unit':'kmol/h','source_type':'USER_INPUT','source_name':'人工输入','status':'UNVERIFIED','version':'1'}
            changed=True
    for t in s.get('target_products',[])+s.get('byproducts',[]):
        q=t.get('purity')
        if q and q.get('unit') not in ('mol/mol','mole fraction'):
            p.setdefault('legacy_mass_purity',[]).append({'name':t.get('name'),'record':copy.deepcopy(q)})
            t['purity']=None;changed=True
    if changed and p.get('completed'):
        from .engine import invalidate_from,event
        invalidate_from(p,1);event(p,'旧版输入补充摩尔流量或清除非摩尔纯度；原质量纯度保存在迁移记录，需重新确认')
    p['input_schema_version']=8
    return True


def completion(spec):
    s=spec.model_dump() if hasattr(spec,'model_dump') else spec
    fields=[]
    def add(key,label,status,detail=''):
        fields.append(dict(key=key,label=label,status=status,detail=detail))
    cs=s.get('components',[])
    add('components','Feed Component','COMPLETE' if cs and all(c.get('id','').strip() and c.get('name','').strip() for c in cs) else 'MISSING')
    feeds=s.get('feeds',[])
    for key,label,unit in [('temperature','Temperature','C'),('pressure','Pressure','bar'),('mass_flow','Mass Flow','kg/h'),('molar_flow','Molar Flow','kmol/h')]:
        missing=[];invalid=[]
        for f in feeds:
            q=f.get(key,{}) or {};v=q.get('value')
            if v is None or v=='':missing.append(f.get('stream_id','feed'))
            elif isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or q.get('unit')!=unit or (key=='temperature' and v< -273.15) or (key!='temperature' and v<=0):invalid.append(f.get('stream_id','feed'))
        add(key,label,'MISSING' if not feeds or missing else 'NEEDS_REVIEW' if invalid else 'COMPLETE',('缺失: '+', '.join(missing)) if missing else ('检查数值/单位 '+unit+': '+', '.join(invalid)) if invalid else '')
    add('reaction','Reaction','COMPLETE' if (s.get('reaction') or {}).get('equation','').strip() else 'MISSING')
    ts=s.get('target_products',[])
    extra=[]
    requirements={x.get('product_role'):x.get('minimum_mole_fraction') for x in s.get('constraints',{}).get('product_target_requirements',[])}
    missing_target=not ts or any(not t.get('name','').strip() for t in ts)
    purity_missing=any(t.get('product_role') in ('TOP','BOTTOM') and (not t.get('purity') or t.get('purity',{}).get('value') in (None,'')) for t in ts)
    purity_invalid=False
    for t in ts:
        q=t.get('purity') or {};minimum=requirements.get(t.get('product_role'))
        if minimum is not None and isinstance(q.get('value'),(int,float)) and q.get('value')<minimum:
            purity_invalid=True;extra.append(f"{t.get('name') or t.get('product_role')} 摩尔分率低于设计要求 {minimum*100:g}%")
    add('target_products','Product Targets','MISSING' if missing_target or purity_missing else 'NEEDS_REVIEW' if purity_invalid else 'COMPLETE','请填写塔顶/塔底产品名称和摩尔分率' if missing_target or purity_missing else '')
    if len({f.get('stream_id') for f in feeds})!=len(feeds):extra.append('进料标识重复')
    for t in ts+s.get('byproducts',[]):
        q=t.get('purity')
        if q and (isinstance(q.get('value'),bool) or not isinstance(q.get('value'),(int,float)) or not 0<=q['value']<=1 or q.get('unit') not in ('mol/mol','mole fraction')):extra.append('目标产品/副产物应使用 0–1 摩尔分率')
    count=sum(f['status']=='COMPLETE' for f in fields)
    return dict(fields=fields,complete_count=count,total=7,required_fields_complete=count==7 and not extra,missing_fields=[f['label'] for f in fields if f['status']=='MISSING'],review_fields=[f['label'] for f in fields if f['status']=='NEEDS_REVIEW']+extra,unit_consistency='COMPLETE' if all(f['status']=='COMPLETE' for f in fields[1:5]) else 'NEEDS_REVIEW')

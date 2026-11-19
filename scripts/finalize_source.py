from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'backend/design_basis.py';s=p.read_text(encoding='utf-8');a=s.index('def migrate_input(p):');b=s.index('\ndef completion(',a)
s=s[:a]+'''def migrate_input(p):
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

'''+s[b:];p.write_text(s,encoding='utf-8')
p=ROOT/'tests/test_engine.py';s=p.read_text(encoding='utf-8').replace("r=c.post('/api/projects',json={'name':'Test engineering task','dataset':dataset,'mode':mode,'backend':backend});assert r.status_code==200,r.text;return r.json()['id']", "r=c.post('/api/projects',json={'name':'Test engineering task','dataset':dataset,'mode':mode,'backend':backend});assert r.status_code==200,r.text\n p=r.json()['id'];basis=c.get(f'/api/projects/{p}/reference-basis');assert basis.status_code==200\n r=c.put(f'/api/projects/{p}/spec',json={'spec':basis.json()});assert r.status_code==200,r.text;return p")
s=s.replace("json={'variables':{'column_pressure':12},'select_baseline':True}","json={'unit_id':next(u['id'] for u in store.load(p)['ir']['units'] if u['type']=='TOWER'),'variables':{'column_pressure':12},'select_baseline':True}")
p.write_text(s,encoding='utf-8')
p=ROOT/'tests/test_step01.py';s=p.read_text(encoding='utf-8').replace("['complete_count']==6","['complete_count']==7").replace("['complete_count']==5","['complete_count']==6").replace("'mass_flow','reaction'","'mass_flow','molar_flow','reaction'").replace("['input_schema_version']==2","['input_schema_version']==8")
p.write_text(s,encoding='utf-8')
p=ROOT/'tests/enhancements-ui.cjs';s=p.read_text(encoding='utf-8').replace("'已核对资料，待补项保留。'","'自动化界面测试，非用户工程签署；待补项保留。'")
a=s.index('   const del=');b=s.index('   await page.reload();',a)
s=s[:a]+'''   const published=await (await page.request.get('http://127.0.0.1:8765/api/projects/'+pid+'/vle')).json();
   const original=published.datasets.find(d=>d.id==='nist-propane-2006');
   const del=await page.request.put('http://127.0.0.1:8765/api/projects/'+pid+'/vle', {data:{kind:'propane_pt',components:['C3H8'],source:original.source,points:original.points}});assert(del.ok());
'''+s[b:]
s=s.replace("await page.screenshot({path:path.join(out,dataset+'-step6.png')", "await page.getByRole('heading',{name:'已补充的工程资料'}).waitFor();await page.screenshot({path:path.join(out,dataset+'-step6.png')").replace("await page.screenshot({path:path.join(out,dataset+'-step8.png')", "await page.getByRole('heading',{name:'已补充的工程资料'}).waitFor();await page.screenshot({path:path.join(out,dataset+'-step8.png')")
p.write_text(s,encoding='utf-8')

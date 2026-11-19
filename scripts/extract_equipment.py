from pathlib import Path
import re,json,hashlib,io,gzip,olefile
root=Path.cwd();base=Path('C:/Users/liuyu/Documents/xwechat_files/wxid_wy25zl6y5ibj22_1a14')
paths=[base/'temp/RWTemp/2026-10/973ed82b0d923fdb6ef8d90f836df813/example1reat.apw',base/'msg/file/2026-10/example2react.bkp',base/'msg/file/2026-10/example3react.bkp']
labels={'TEMP':'温度设定','PRES':'压力设定','PRES1':'压力规格 1','PRES2':'压力规格 2','P-OUT':'出口压力','DP-STAGE':'每级压降','NSTAGE':'理论级数（含模型端级）','NSTAGEMAX':'最大级数设置','CONDENSER':'冷凝器形式','REBOILER':'再沸器形式','FEED-SID':'进料流股','FEED-STAGE':'进料级','FEED-CONVE2':'进料位置约定','PROD-STREAM':'产品流股','PROD-STAGE':'产品采出级','PROD-PHASE':'采出相态','BASIS-B':'塔底采出量','BASIS-RR':'回流比','BASIS-BR':'汽提比','BASIS-RDV':'馏出/进料规格基准','VFRAC':'气相分率设定','DUTY':'热负荷设定','SPEC-OPT':'指定变量组合','TYPE':'计算方法','OPT-SPEC':'指定变量','PRATIO':'压比','PEFF':'多变效率','MEFF':'机械效率','CONV':'反应转化率','KEY-CID':'转化率基准组分','REACNO':'反应编号','EXT-REACNO':'转化率对应反应','COEF':'反应物计量系数','COEF1':'产物计量系数','STOIC-CID':'反应物','STOIC-CID1':'产物','SID':'流股','BASIS-FLOW':'指定分流流量','SPEC':'换热规格','VALUE':'规格目标值','FHOT':'热侧入口','FCOLD':'冷侧入口','HOT-SID':'热侧出口','COLD-SID':'冷侧出口','SPEC-TYPE':'设计规定类型','SPEC-COMPS':'规定组分','SPEC-STREAMS':'规定产品','VARTYPE':'调节变量','LB':'变量下限','UB':'变量上限'}
result={}
for route,path in zip(['route_a','route_b','route_c'],paths):
 raw=path.read_bytes();loc='文本'
 if path.suffix=='.apw':
  outer=olefile.OleFileIO(io.BytesIO(raw));inner=olefile.OleFileIO(io.BytesIO(gzip.decompress(outer.openstream('Archive.ZStg').read())));rawtext=inner.openstream('Data').read();loc='Archive.ZStg / Data'
 else:rawtext=raw
 text=rawtext.decode('gb18030',errors='replace')
 sections=list(re.finditer(r'\?\s*BLOCK\s+(\S+)\s+("[^"]+"|[^\s?]+)\s*\?(.*?)(?=\?\s|$)',text,re.S))
 units=[]
 for match in sections:
  typ,uid,body=match.groups();uid=uid.strip('"');rows=[]
  for part in body.split('\\'):
   if '=' not in part or 'SSXML' in part:continue
   sentence=re.match(r'\s*("[^"]+"|[\w-]+)',part)
   context=sentence.group(1).strip('"') if sentence else ''
   assignments=list(re.finditer(r'([A-Z][A-Z0-9-]*)\s*=\s*(\([^)]*\)|"[^"]*"|[^\s\\/]+)(?:\s*<(-?\d+)>\s*<(-?\d+)>)?',part))
   for m in assignments:
    key,value,dim,code=m.groups()
    if key not in labels:continue
    unit='—';note=''
    if dim and code:
     if dim=='0' or dim=='-1':unit='无量纲'
     elif dim=='22' and code=='4':unit='°C'
     elif dim=='20' and code=='20':unit='MPa';note='压力单位按同文件/既有物流对照识别；1 MPa = 10 bar，原编码保留。'
     elif dim=='75' and code=='18':unit='MPa/级';note='与塔顶/塔底压力差及级数对照；原编码保留。'
     elif dim=='-89' and code=='3':unit='kmol/h'
     else:unit=f'原单位待核验 ({dim}/{code})'
    if key in ['NSTAGE','NSTAGEMAX','FEED-STAGE','PROD-STAGE']:unit='级'
    rows.append({'key':key,'label':labels[key],'value':value.strip('"'),'unit':unit,'context':context,'raw':m.group(0),'note':note})
  units.append({'id':uid,'model':typ,'rows':rows,'locator':f'{loc} · BLOCK {typ} {uid} · 第{text[:match.start()].count(chr(10))+1}行'})
 topology=json.loads((root/f'data/validation/pdh/{route}/topology.json').read_text(encoding='utf-8'))
 present={u['id'] for u in units}
 for u in topology['units']:
  if u['id'] not in present:units.append({'id':u['id'],'model':u['type'],'rows':[],'locator':'流程图单元','note':'塔内冷凝/再沸示意单元，源文件未定义独立设备块；请查看对应塔的设置。'})
 for u in units:
  u['label']=next((x['label'] for x in topology['units'] if x['id']==u['id']),u['id'])
  if not u['rows'] and not u.get('note'):u['note']='该设备块在此文件中未显式提供可展示的操作参数；不从其他路线补值。'
 result[route]={'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'units':units,'notice':'以下为文件中的设备输入设置，未重新求解；与原物流结果分开保存。空项不代表零值。理论级数不等于实际塔板数。'}
(root/'data/equipment_parameters.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:{'units':len(v['units']),'parameters':sum(len(u['rows']) for u in v['units'])} for k,v in result.items()})

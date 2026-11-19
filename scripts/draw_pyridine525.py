"""Use the same animated SVG assets and visual grammar as the C3 cases."""
import copy,json,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
def add(p,n,attrs=None,text=None):
 e=E.SubElement(p,tag(n),{k:str(v) for k,v in (attrs or {}).items()});e.text=text;return e
base=E.parse(ROOT/'data/assets/route_a.svg').getroot();legacy=E.parse(ROOT/'data/assets/pyridine.svg').getroot()
r=E.Element(tag('svg'),dict(width='2800',height='1400',viewBox='0 0 2800 1400',role='img'))
add(r,'title',text='四氢糠醇制吡啶 · 分相与溶剂闭循环')
r.append(copy.deepcopy(base.find(tag('defs'))));r.append(copy.deepcopy(legacy.find(tag('defs'))));r.append(copy.deepcopy(base.find(tag('style'))))
add(r,'style',text='.particle{pointer-events:none}')
add(r,'rect',dict(width=2800,height=1400,fill='#f5f9fb'));add(r,'rect',dict(x=45,y=35,width=6,height=60,rx=3,fill='#147d92'))
add(r,'text',dict(x=75,y=68,**{'font-size':40,'font-weight':750}), '四氢糠醇制吡啶 · 分相与溶剂闭循环')
add(r,'text',dict(x=75,y=102,**{'font-size':18,'fill':'#617d90'}),'ENGINEERING REFERENCE / 工艺流程可视化 · 工艺参数结果标注')
colors={'main':'#147d92','gas':'#d68b29','recycle':'#8160bc','product':'#278d6c'}
# Each material stream retains its original source and destination.
paths={
'THFA':('M70 650 H245','main'),'NH3':('M300 340 V575','main'),
'A-R':('M355 650 H605','main'),'H2':('M650 575 V300 H900','gas'),
'A-S1':('M695 650 H945','main'),'A-S2':('M1000 435 V380 H1200 V650 H1345','main'),
'2AP':('M1000 785 V1000 H1250','product'),'A-S3':('M1400 435 V350 H1600 V650 H1740','main'),
'3-PY':('M1400 785 V1130 H1600','product'),'A-S4':('M1860 650 H2145','main'),
'A-S5':('M2200 435 V300 H2400 V1005','main'),'PY':('M2200 785 V880 H2700','product'),
'RE':('M2355 1080 H1800 V650','recycle'),'H2O':('M2445 1080 H2700','product')}
for sid,(d,kind) in paths.items():
 c=colors[kind];add(r,'path',dict(d=d,fill='none',stroke='#f5f9fb',**{'stroke-width':12}))
 add(r,'path',dict(d=d,fill='none',stroke=c,**{'stroke-width':4.5,'stroke-linejoin':'round','marker-end':f'url(#0-arr-{kind})','data-stream-id':sid,'class':'stream-pipe'}))
 for i in range(3):
  p=add(r,'circle',{'r':4,'fill':c,'class':'particle'});add(p,'animateMotion',dict(path=d,dur='6s',begin=f'-{2*i}s',repeatCount='indefinite'))
positions={'PY-R':(300,650),'SPR':(650,650),'2AP-SPR':(1000,610),'3-PY-SPR':(1400,610),'PY-SPR':(1800,650),'MIXER':(2200,610),'DECANTER':(2400,1080)}
data=json.loads((ROOT/'data/validation/pyridine525/topology.json').read_text(encoding='utf-8'))
for u in data['units']:
 uid=u['id'];template={'REACTOR':'REACTOR','FLASH':'FLASH','TOWER':'COLUMN','DECANTER':'FLASH','MIXER':'B4'}[u['type']]
 src=legacy if template=='B4' else base;g=copy.deepcopy(src.find('.//'+tag('g')+f'[@data-equipment-id="{template}"]'))
 x,y=positions[uid];g.set('transform',f'translate({x} {y})');g.set('data-equipment-id',uid);g.set('aria-label','设备 '+uid)
 g.find(tag('title')).text=uid+' '+u['label']+'；内部结构为原理示意'
 for t in g.findall(tag('text')):
  if t.get('class')=='eq':t.text=uid
  if t.get('class')=='eqsub':t.text=u['label']
 if uid=='DECANTER':
  for circle in list(g.findall(tag('circle'))):g.remove(circle)
  for t in g.findall(tag('text')):
   if t.text=='气相':t.text='有机相'
   if t.text=='液相':t.text='水相'
  for p in g.findall(tag('path')):
   if p.get('fill')=='#70cbd1':p.set('fill','#70cbd1')
  # Organic phase uses the recycle color, retaining the same vessel geometry.
  organic=E.Element(tag('path'),dict(d='M-33 -42 Q0 -67 33 -42 V12 Q0 2 -33 12 Z',fill='#bda5df',opacity='.40'))
  g.insert(5,organic)
 r.append(g)
labels={
'THFA':(65,440,'四氢糠醇进料',(165,650)), 'NH3':(195,160,'氨进料',(300,340)),
'A-R':(385,785,'反应器出口',(485,650)), 'H2':(725,135,'富氢气',(825,300)),
'A-S1':(720,465,'闪蒸液相出口',(825,650)), 'A-S2':(1055,185,'一级塔顶物流',(1160,380)),
'2AP':(1040,1015,'2-氨基吡啶产品',(1150,1000)), 'A-S3':(1465,160,'二级塔顶物流',(1570,350)),
'3-PY':(1410,1160,'3-甲基吡啶产品',(1510,1130)), 'A-S4':(1890,450,'混合器出口',(2000,650)),
'A-S5':(2460,510,'精制塔顶物流',(2400,585)), 'PY':(2500,695,'吡啶产品',(2600,880)),
'RE':(1920,1135,'有机相循环物流',(2025,1080)), 'H2O':(2500,1110,'分相器水相',(2610,1080))}
card=base.find('.//'+tag('g')+'[@class="stream-label"]')
for sid,(x,y,role,point) in labels.items():
 g=copy.deepcopy(card);g.set('transform',f'translate({x} {y})');g.set('data-stream-id',sid);g.set('aria-label','流股 '+sid);g.attrib.pop('data-stream',None)
 for t in g.findall(tag('text')):
  if t.get('class')=='tag':t.text=sid
  if t.get('class')=='role':t.text=role
 g.findall(tag('rect'))[1].set('fill',colors[paths[sid][1]])
 # Connect the nearest card edge with a fine leader, as in the C3 reference.
 px,py=point;cx=max(x,min(x+215,px));cy=max(y,min(y+142,py))
 add(r,'path',dict(d=f'M{cx} {cy} L{px} {py}',stroke='#9cb3bf',fill='none',**{'stroke-width':1.5,'stroke-dasharray':'4 5'}));add(r,'circle',dict(cx=px,cy=py,r=3,fill=colors[paths[sid][1]]));r.append(g)
add(r,'path',dict(d='M60 1340 H2740',stroke='#dbe6ec'))
add(r,'text',dict(x=65,y=1380,**{'font-size':18}),'Engineering visualization · 结构示意 / 原始数值由当前结果绑定 · RE 为内部循环')
E.ElementTree(r).write(ROOT/'data/assets/pyridine525.svg',encoding='utf-8',xml_declaration=False)

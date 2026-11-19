"""Engineering concept drawings bound to the active project's topology and results."""
from .drawing_defaults import equipment_defaults
from .case_variant import result_key
import copy
import json
import math
import re
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
def el(tag,attrs=None,text=None):
    e=ET.Element('{'+NS+'}'+tag,{k:str(v) for k,v in (attrs or {}).items()})
    e.text=None if text is None else str(text)
    return e
def add(parent,tag,attrs=None,text=None):
    e=el(tag,attrs,text);parent.append(e);return e
def txt(parent,x,y,value,size=23,anchor='start',color='#16232e'):
    return add(parent,'text',dict(x=x,y=y,fill=color,**{'font-size':size,'text-anchor':anchor}),value)
def line(parent,x1,y1,x2,y2,color='#16232e',dash=None):
    a=dict(x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,**{'stroke-width':2})
    if dash:a['stroke-dasharray']=dash
    return add(parent,'line',a)
def box(parent,x,y,w,h,fill='white'):
    return add(parent,'rect',dict(x=x,y=y,width=w,height=h,fill=fill,stroke='#16232e',**{'stroke-width':2}))
def val(s,key):
    q=(s or {}).get(key) or {};v=q.get('value')
    return '待定' if v is None else f'{v:,.2f}' if isinstance(v,(float,int)) else str(v)

class DrawingRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind:Literal['pfd','pid','equipment']='pfd'
    unit:str=Field('',max_length=80)
    sheet_unit:str=Field('',max_length=80)
    design_temperature:str=Field('',max_length=32)
    design_pressure:str=Field('',max_length=32)
    diameter:str=Field('',max_length=32)
    length:str=Field('',max_length=32)
    thickness:str=Field('',max_length=32)
    material:str=Field('',max_length=60)
    corrosion:str=Field('',max_length=32)
    insulation:str=Field('',max_length=60)

def sheet(p,kind,height=1980):
    title={'pfd':'工艺物料流程图 / PFD','pid':'管道及仪表流程图 / P&ID','equipment':'设备工艺条件图'}[kind]
    svg=el('svg',{'width':2800,'height':height,'viewBox':f'0 0 2800 {height}','role':'img'})
    add(svg,'title',text=(p.get('ir') or {}).get('title','流程')+' · '+title)
    add(svg,'style',text='text{font-family:"Microsoft YaHei","Noto Sans CJK SC",Arial,sans-serif}path,line,rect,circle,ellipse{vector-effect:non-scaling-stroke}')
    box(svg,0,0,2800,height);box(svg,30,30,2740,height-60)
    defs=add(svg,'defs');m=add(defs,'marker',{'id':'flow-arrow','viewBox':'0 0 10 10','refX':9,'refY':5,'markerWidth':7,'markerHeight':7,'orient':'auto-start-reverse'})
    add(m,'path',{'d':'M0 0L10 5L0 10Z','fill':'#16232e'})
    for i in range(1,13):
        x=30+i*2740/12;line(svg,x,0,x,30);txt(svg,x-114,23,str(i),17,'middle')
    txt(svg,70,90,'CHEMFLOW AI  /  '+title,35)
    txt(svg,70,133,(p.get('ir') or {}).get('title','')+' · 图纸与当前流程方案绑定',23)
    txt(svg,2730,90,'概念设计 · 非施工图',25,'end','#a15c00')
    y=height-165;box(svg,70,y,2660,125)
    line(svg,1610,y,1610,y+125);line(svg,2200,y,2200,y+125)
    txt(svg,90,y+37,'设计说明：实线为工艺连接；无数值项为待定。图形不按比例。',23)
    txt(svg,90,y+76,'P&ID 测点和控制回路为建议配置；仪表量程、联锁、泄压及管道等级待专项设计。',20)
    txt(svg,90,y+110,'机械尺寸只显示用户填写值，不由流程图外形推定。',20)
    txt(svg,1630,y+42,title,27);txt(svg,1630,y+83,'CHEMFLOW / '+str(p.get('route','')).upper(),22)
    txt(svg,2220,y+42,'图号 CF-'+str(p.get('route','')).upper()+'-'+kind.upper(),19)
    txt(svg,2220,y+82,'版本 R'+str(p.get('revision',0))+'  ·  工程预览',21)
    return svg

def symbol(parent,typ,x,y,uid,label):
    g=add(parent,'g',{'transform':f'translate({x} {y})','data-equipment-id':uid})
    if typ in ('TOWER','REACTOR','FLASH'):
        h=190 if typ=='TOWER' else 90;w=55 if typ!='FLASH' else 45
        add(g,'rect',{'x':-w,'y':-h,'width':2*w,'height':2*h,'rx':w,'fill':'white','stroke':'#16232e','stroke-width':2})
        if typ=='TOWER':
            for dy in range(-130,151,40):line(g,-43,dy,43,dy,'#00dd00')
        if typ=='REACTOR':
            add(g,'path',{'d':'M-40 -50L40 50M40 -50L-40 50','stroke':'#00dd00','fill':'none','stroke-width':2})
        if typ=='FLASH':line(g,-43,25,43,25,'#00dd00')
        line(g,-30,h,-30,h+18);line(g,30,h,30,h+18)
        ty=h+55
    elif typ=='HX':
        add(g,'circle',{'r':47,'fill':'white','stroke':'#16232e','stroke-width':2})
        add(g,'path',{'d':'M-42 16L-18 -16L18 16L42 -16','stroke':'#16232e','fill':'none','stroke-width':2});ty=85
    elif typ=='COMPRESSOR':
        add(g,'path',{'d':'M-55 -44L55 -25V25L-55 44Z','fill':'white','stroke':'#16232e','stroke-width':2});ty=82
    elif typ=='VALVE':
        add(g,'path',{'d':'M-40 -25L40 25V-25L-40 25Z','fill':'white','stroke':'#00dd00','stroke-width':2});ty=62
    else:
        add(g,'circle',{'r':30,'fill':'white','stroke':'#16232e','stroke-width':2});ty=64
    txt(g,0,ty,uid,26,'middle');txt(g,0,ty+30,label,22,'middle')
    return g

def table(svg,x,y,width,headers,rows,rowheight=38):
    cols=len(headers);cw=width/cols
    for i,row in enumerate([headers]+rows):
        box(svg,x,y+i*rowheight,width,rowheight,'#eaf0f2' if i==0 else 'white')
        for j,v in enumerate(row):
            if j:line(svg,x+j*cw,y+i*rowheight,x+j*cw,y+(i+1)*rowheight)
            length=sum(1 if ord(c)>255 else .56 for c in str(v))
            size=min(20,(cw-18)/max(length,1))
            txt(svg,x+j*cw+9,y+i*rowheight+rowheight*.68,v,size)

def reference_sheet(p,kind):
    base=sheet(p,kind)
    svg=el('svg',dict(base.attrib))
    for n in base:
        if n.tag in ['{'+NS+'}title','{'+NS+'}style','{'+NS+'}defs']:svg.append(copy.deepcopy(n))
    box(svg,0,0,2800,1980);box(svg,80,35,2685,1905)
    for i in range(12):
        x=80+i*2685/12
        line(svg,x,0,x,35);line(svg,x,1940,x,1980)
        txt(svg,x+110,25,str(i+1),18,'middle','#000');txt(svg,x+110,1970,str(i+1),18,'middle','#000')
    for i,c in enumerate('ABCDEF'):
        y=35+i*1905/6
        line(svg,0,y,80,y);line(svg,2765,y,2800,y)
        txt(svg,40,y+155,c,20,'middle','#000');txt(svg,2780,y+155,c,20,'middle','#000')
    # Reference-style compact drawing title block at lower right.
    x,y,w,h=2110,1740,655,200
    box(svg,x,y,w,h)
    for yy in [y+42,y+90,y+145]:line(svg,x,yy,x+w,yy)
    line(svg,x+180,y,x+180,y+h);line(svg,x+450,y,x+450,y+h)
    txt(svg,x+12,y+28,'CHEMFLOW AI',21);txt(svg,x+192,y+28,'工程设计',20);txt(svg,x+465,y+28,'概念设计',20)
    txt(svg,x+12,y+73,'专业：工艺',20);txt(svg,x+192,y+73,p['ir'].get('title',''),20)
    txt(svg,x+12,y+123,'图纸名称',19);txt(svg,x+192,y+123,'工艺物料流程图' if kind=='pfd' else '管道及仪表流程图',20)
    txt(svg,x+12,y+178,'版本 R'+str(p.get('revision',0)),18)
    txt(svg,x+192,y+178,'CF-'+p['route'].upper()+'-'+kind.upper(),18);txt(svg,x+465,y+178,'第1张 / 共1张',16)
    txt(svg,110,1835,'设计阶段：概念方案，非施工图；管径、等级、仪表量程及联锁待定。',19)
    txt(svg,110,1875,'工艺连接与当前方案一致；测点为建议配置；图形不按比例。',19)
    txt(svg,110,1910,'主物料管线',18);line(svg,270,1903,420,1903,'#ff00ff')
    txt(svg,470,1910,'仪表信号',18);line(svg,600,1903,750,1903,'#00cddd','6 4')
    txt(svg,800,1910,'设备内件 / 阀门',18);line(svg,1010,1903,1160,1903,'#00dd00')
    return svg

def process(p,kind,focus=''):
    from .cad_drawings import process_sheet
    return process_sheet(p,kind,focus)

def process_legacy(p,kind):
    rid=p.get('route');path=ROOT/'data/assets'/f'{result_key(p)}.svg'
    if rid not in ('route_a','route_b','route_c','pyridine') or not path.exists():raise ValueError('当前方案尚无可绘制的流程拓扑')
    src=ET.fromstring(path.read_text(encoding='utf-8'))
    svg=reference_sheet(p,kind);ns={'s':NS}
    # Geometry bounds include the generated stream tables/instrument tags, not
    # the unused margins in the source asset's viewBox. Keep equal page margins
    # and a uniform scale so symbols retain their original proportions.
    bounds={
        ('route_a','pfd'):(60,103,2295,975),
        ('route_a','pid'):(58,116,2325,972),
        ('route_b','pfd'):(45,163,2715,1120),
        ('route_b','pid'):(43,176,2745,1117),
        ('route_c','pfd'):(60,103,2675,1095),
        ('route_c','pid'):(58,116,2705,1092),
    }
    bx,by,bw,bh=(0,100,2800,1230) if result_key(p)=='pyridine525' else bounds.get((rid,kind),(0,0,2800,1400))
    scale=min(2520/bw,1350/bh)
    tx=1422.5-(bx+bw/2)*scale
    ty=900-(by+bh/2)*scale
    diagram=add(svg,'g',{'data-process-layout':'centered','transform':f'translate({tx:.4f} {ty:.4f}) scale({scale:.6f})'})
    units={u['id']:u for u in p['ir']['units']};streams=((p.get('result') or {}).get('streams') or {})
    # Preserve the verified pipeline geometry; create clean engineering symbols.
    for node in src.findall('.//s:path',ns):
        if 'stream-pipe' in node.get('class',''):
            attrs={'d':node.get('d'),'stroke':'#ff00ff','stroke-width':2,'fill':'none','marker-end':'url(#flow-arrow)','data-stream-id':node.get('data-stream-id','')}
            add(diagram,'path',attrs)
    for u in src.findall('.//s:g[@data-equipment-id]',ns):
        uid=u.get('data-equipment-id');spec=units.get(uid)
        if not spec:continue
        pos=re.findall(r'-?\d+(?:\.\d+)?',u.get('transform',''))
        symbol(diagram,spec['type'],float(pos[0]),float(pos[1]),uid,spec.get('label',''))
    for i,label in enumerate(src.findall('.//s:g[@class="stream-label"]',ns)):
        sid=label.get('data-stream-id');s=streams.get(sid);g=add(diagram,'g',{'transform':label.get('transform','')})
        if kind=='pfd':
            box(g,0,0,205,118)
            txt(g,102,-13,sid,22,'middle','#000')
            for row,(unitname,value) in enumerate([('°C',val(s,'temperature')),('bar',val(s,'pressure')),('kg/h',val(s,'mass_flow'))]):
                if row:line(g,0,row*39,205,row*39,'#000')
                txt(g,8,row*39+27,unitname,19,color='#000');txt(g,197,row*39+27,value,21,'end','#000')
            line(g,55,0,55,118,'#000')
        else:
            txt(g,0,0,'L-'+str(i+1).zfill(3)+' / '+sid,22)
            txt(g,0,30,'DN / 等级 / 材质：待定',18)
            for j,code in enumerate(['TT','PT']):
                cx=36+j*106;add(g,'circle',{'cx':cx,'cy':79,'r':29,'stroke':'#00bfcf','fill':'white','stroke-width':2})
                txt(g,cx,75,code,18,'middle','#00bfcf');txt(g,cx,97,str(i+101),17,'middle','#00bfcf')
                line(g,cx,108,cx,128,'#00bfcf','6 4')
            # A compact label with a white backing stays legible where a pipe crosses.
            add(g,'rect',{'x':-2,'y':-23,'width':235,'height':58,'fill':'white'})
            txt(g,0,0,'L-'+str(i+1).zfill(3)+' / '+sid,22)
            txt(g,0,30,'DN / 等级 / 材质：待定',18)
    # Existing leaders attach each stream tag (or suggested instrument) to its pipeline.
    for node in list(src):
        if node.tag=='{'+NS+'}path' and node.get('stroke-dasharray')=='4 5':
            add(diagram,'path',{'d':node.get('d'),'fill':'none','stroke':'#00bfcf' if kind=='pid' else '#687580','stroke-width':1,'stroke-dasharray':'6 4'})
    # Equipment register below the flow, matching the reference sheet layout.
    for i,u in enumerate(p['ir']['units']):
        x=210+i*(2425/max(len(p['ir']['units'])-1,1))
        txt(svg,x,1680,u['id'],20,'middle','#000')
        line(svg,x-55,1690,x+55,1690,'#000')
        txt(svg,x,1717,u.get('label',''),17,'middle','#000')
    if kind=='pid':
        txt(svg,110,1775,'TT 温度变送器 / PT 压力变送器；青色虚线为建议测量引线。',20)
    return svg

def condition(p,r):
    unit=next((u for u in p['ir']['units'] if u['id']==r.unit),None)
    if not unit:raise ValueError('请选择当前流程中的设备')
    svg=sheet(p,'equipment');txt(svg,70,150,'常规设计初估 · 待校核 · 非施工图',23);txt(svg,70,195,r.unit+' · '+unit.get('label','')+' / 工艺条件',32)
    # Structured GA schematic, with dimensions deliberately left unspecified unless entered.
    if unit['type']=='HX':
        add(svg,'rect',{'x':280,'y':560,'width':640,'height':180,'rx':65,'fill':'white','stroke':'#16232e','stroke-width':2})
        for x in [365,380,820,835]:line(svg,x,550,x,750)
        for y in [590,615,640,665,690,715]:line(svg,380,y,820,y,'#00dd00')
        line(svg,425,740,425,790);line(svg,780,740,780,790)
        txt(svg,590,880,r.unit+' / 换热器结构示意',27,'middle')
        add(svg,'circle',{'cx':590,'cy':985,'r':62,'fill':'white','stroke':'#16232e','stroke-width':2})
        for x in [567,590,613]:
            for y in [962,985,1008]:add(svg,'circle',{'cx':x,'cy':y,'r':5,'fill':'none','stroke':'#16232e'})
        txt(svg,720,990,'管束示意 · 管数待定',20)
    else:
        g=add(svg,'g',{'transform':'translate(590 650) scale(1.6)' if unit['type']=='TOWER' else 'translate(590 660) scale(2.4)'})
        symbol(g,unit['type'],0,0,r.unit,unit.get('label',''))
    tall=unit['type'] in ('TOWER','REACTOR','FLASH')
    if unit['type']=='HX':
        line(svg,280,390,920,390);line(svg,280,370,280,410);line(svg,920,370,920,410)
        txt(svg,600,365,'L = '+(r.length or '待定')+' mm',24,'middle')
        line(svg,990,560,990,740);line(svg,970,560,1010,560);line(svg,970,740,1010,740)
        txt(svg,990,780,'D = '+(r.diameter or '待定'),20,'middle')
    else:
        line(svg,300,330,300,1000);line(svg,280,330,340,330);line(svg,280,1000,340,1000)
        txt(svg,125,670,'H/L = '+(r.length or '待定')+' mm',22)
        line(svg,400,1150,790,1150);line(svg,400,1130,400,1170);line(svg,790,1130,790,1170)
        txt(svg,595,1190,'D = '+(r.diameter or '待定')+' mm',24,'middle')
    txt(svg,360,1240,'结构示意，不按比例；接管方位待机械设计。',22)
    connected=[s for s in p['ir']['streams'] if r.unit in (s.get('from_unit'),s.get('to_unit'))]
    streams=(p.get('result') or {}).get('streams') or {}
    conditions=[]
    for i,s in enumerate(connected):
        v=streams.get(s['stream_id']);inlet=s.get('to_unit')==r.unit
        conditions.append([f'N{i+1}',s['stream_id'],'入口' if inlet else '出口',val(v,'temperature'),val(v,'pressure'),val(v,'mass_flow')])
        if unit['type']=='HX':
            x=430+i*85;y=560 if inlet else 740;end=y-70 if inlet else y+70
            line(svg,x,y,x,end);line(svg,x-15,end,x+15,end)
            txt(svg,x,end-12 if inlet else end+25,f'N{i+1}',22,'middle')
        else:
            y=430+i*75;x=380 if inlet else 800
            edge=(502 if inlet else 678) if unit['type']=='TOWER' else (458 if inlet else 722)
            line(svg,x,y,edge,y)
            txt(svg,x-15 if inlet else x+15,y-10,f'N{i+1}',22,'end' if inlet else 'start')
    values=[['设备位号',r.unit],['设备类型',unit['type']],['设计温度 / °C',r.design_temperature or '待定'],['设计压力 / MPa',r.design_pressure or '待定'],['直径 / mm',r.diameter or '待定'],['高度或长度 / mm',r.length or '待定'],['壁厚 / mm',r.thickness or '待定'],['主体材料',r.material or '待定'],['腐蚀裕量 / mm',r.corrosion or '待定'],['保温 / 保冷',r.insulation or '待定']]
    txt(svg,1160,235,'机械设计条件（常规初估 / 可修改）',26)
    table(svg,1160,260,1540,['条件','数值'],values,48)
    txt(svg,1160,835,'设备操作参数',26)
    eq=json.loads((ROOT/'data/equipment_parameters.json').read_text(encoding='utf-8')).get(result_key(p),{})
    spec=next((u for u in eq.get('units',[]) if u['id']==r.unit),{})
    settings=[[x['label'],str(x['value'])[:38],x['unit']] for x in spec.get('rows',[]) if x['key'] not in ['STREAM','MOLE-FLOW','MASS-FLOW']][:8]
    table(svg,1160,860,1540,['参数','设定值','单位'],settings or [['操作参数','待补充','—']],43)
    txt(svg,70,1310,'接管工艺条件 / 管口编号仅为图纸索引，公称直径、法兰等级和朝向待定',25)
    table(svg,70,1340,2660,['管口','流股','方向','温度 / °C','压力 / bar','质量流量 / kg/h'],conditions or [['—','内部换热单元','待补充','待定','待定','待定']],42)
    return svg

def vessel_condition(p,r):
    unit=next((u for u in p['ir']['units'] if u['id']==r.unit),None)
    if not unit:raise ValueError('请选择当前流程中的设备')
    reactor=unit['type']=='REACTOR'
    svg=reference_sheet(p,'equipment')
    for child in list(svg):
        if child.tag=='{'+NS+'}line' and child.get('y1')=='1903':svg.remove(child)
        elif child.tag=='{'+NS+'}text' and child.get('y')=='1910':svg.remove(child)
    txt(svg,110,1910,'图纸单位：mm（特殊说明除外）；尺寸为常规设计初估；方位及强度待校核。',19,color='#000')
    # Replace the process title in the compact title block.
    for t in svg.iter('{'+NS+'}text'):
        if t.text=='管道及仪表流程图':t.text='反应器工艺条件图' if reactor else '塔器工艺条件图'
        if t.text and t.text.startswith('CF-'):t.text='CF-'+r.unit+'-COND'
    txt(svg,115,105,r.unit+'  '+unit.get('label','')+'  工艺条件图',32,color='#000')
    txt(svg,115,150,'常规设计初估 · 待校核 / 主视图 / A—A 管口方位',21,color='#000')
    eq=json.loads((ROOT/'data/equipment_parameters.json').read_text(encoding='utf-8')).get(result_key(p),{})
    spec=next((u for u in eq.get('units',[]) if u['id']==r.unit),{})
    params=spec.get('rows',[])
    def param(key):
        x=next((x for x in params if x['key']==key),None)
        return str(x['value'])+' '+str(x['unit']) if x else '待定'
    streams=(p.get('result') or {}).get('streams') or {}
    connected=[s for s in p['ir']['streams'] if r.unit in (s.get('from_unit'),s.get('to_unit'))]
    known=[streams.get(s['stream_id'],{}) for s in connected]
    def span(key,suffix):
        v=[x.get(key,{}).get('value') for x in known];v=[x for x in v if isinstance(x,(int,float))]
        return (f'{min(v):.2f} ~ {max(v):.2f} '+suffix+'（各接管）') if v else '待定'
    values=[['设备位号 / 名称',r.unit+' / '+unit.get('label','')],['工艺介质','丙烷 / 丙烯 / 氢气' if p.get('route','').startswith('route_') else '见物流组成'],
      ['操作温度 / °C',param('TEMP') if reactor else span('temperature','°C')],['接管操作压力 / bar',span('pressure','bar')],
      ['设计温度 / °C',r.design_temperature or '待定'],['设计压力 / MPa',r.design_pressure or '待定'],
      ['公称直径 / mm',r.diameter or '待定'],['筒体高度 / mm',r.length or '待定'],['名义壁厚 / mm',r.thickness or '待定'],
      ['筒体几何容积 / m³',geometry_volume(r)],['主体材质',r.material or '待定'],['封头形式 / 材质','2:1椭圆封头 / 同筒体（初估）'],
      ['腐蚀裕量 / mm',r.corrosion or '待定'],['保温 / 保冷',r.insulation or '待定'],['支承型式','裙座高2000mm（初估）'],
      ['操作方式','连续工况；开停车条件待补'],['反应模型' if reactor else '理论级数',spec.get('model','待定') if reactor else param('NSTAGE')],
      ['催化剂 / 装填量' if reactor else '塔内件 / 板效率','需动力学与催化剂选型' if reactor else '浮阀塔板 / 0.80（初估）'],['床层高度 / 分布器' if reactor else '板间距 / 塔段高度','内部床层形式待专项设计' if reactor else '板间距500mm；高塔分段待校核'],
      ['设计载荷 / 试验压力','待定'],['安全附件 / 泄压条件','待设计确认']]
    table(svg,115,205,1370,['工艺与机械条件','数值 / 要求'],values,49)
    txt(svg,115,1340,'接管及开孔一览表',27,color='#000')
    rows=[]
    for i,c in enumerate(connected):
        rows.append([f'N{i+1}',c['stream_id'],'入口' if c.get('to_unit')==r.unit else '出口','待定','待定','待定'])
    rows.append(['M1','检修人孔（初估）','检修','500','等级待校核','250'])
    table(svg,115,1370,1370,['符号','连接流股 / 用途','方向','DN / mm','法兰 / 密封面','伸出长度'],rows,42)
    # Detailed elevation, kept clear of the condition tables.
    cx,left,right=2030,1910,2150;top,bottom=325,1240
    path=f'M{left} {top+65} Q{left} {top} {cx} {top} Q{right} {top} {right} {top+65} V{bottom-65} Q{right} {bottom} {cx} {bottom} Q{left} {bottom} {left} {bottom-65} Z'
    add(svg,'path',{'d':path,'fill':'white','stroke':'black','stroke-width':2.5})
    line(svg,left+8,top+65,left+8,bottom-65,'black');line(svg,right-8,top+65,right-8,bottom-65,'black')
    line(svg,left,top+65,right,top+65,'black');line(svg,left,bottom-65,right,bottom-65,'black')
    line(svg,cx,top-90,cx,bottom+175,'#777','16 6 3 6')
    # Construction placeholders use dashed lines, not fictitious settled internals.
    if reactor:
        for y in [490,735,980]:
            line(svg,left+12,y,right-12,y,'black','7 5');line(svg,left+12,y+145,right-12,y+145,'black','7 5')
            line(svg,left+12,y,right-12,y+145,'#777','7 5');line(svg,right-12,y,left+12,y+145,'#777','7 5')
        txt(svg,2190,690,'内部结构待定',21,color='#000');txt(svg,2190,730,'虚线仅示意',19,color='#000')
    else:
        for j,y in enumerate(range(460,1150,65)):
            line(svg,left+12,y,right-12,y,'black','7 4')
            x=right-30 if j%2==0 else left+30;line(svg,x,y,x,y+35,'black','7 4')
        txt(svg,2190,735,'浮阀塔板（初估）',21,color='#000');txt(svg,2190,775,'示意节距，不按级数',19,color='#000')
    # Skirt, base ring, anchor holes and inspection opening.
    line(svg,left+15,bottom-25,left+15,bottom+130,'black');line(svg,right-15,bottom-25,right-15,bottom+130,'black')
    box(svg,left-30,bottom+130,300,13)
    for x in [left-12,right+12]:add(svg,'circle',{'cx':x,'cy':bottom+137,'r':4,'fill':'none','stroke':'black'})
    add(svg,'rect',{'x':cx-35,'y':bottom+25,'width':70,'height':74,'rx':30,'fill':'white','stroke':'black'})
    txt(svg,cx,bottom+175,'裙座及地脚结构示意',20,'middle','#000')
    # Flanged nozzles: layout is provisional, parameters are mapped exactly by tag.
    positions=[]
    for i,c in enumerate(connected):
        inlet=c.get('to_unit')==r.unit
        if reactor:y=top+140 if inlet else bottom-120
        elif c['stream_id']=='PRO-D':y=top+115
        elif c['stream_id']=='PRO-B':y=bottom-110
        else:y=top+360+i*70
        y=min(y,bottom-150) if c['stream_id'] not in ['PRO-B'] else y
        edge=left if inlet else right;end=edge-135 if inlet else edge+135
        for off in [-9,9]:line(svg,edge,y+off,end,y+off,'black')
        for off in [-5,5]:line(svg,end+off,y-24,end+off,y+24,'black')
        txt(svg,end-20 if inlet else end+20,y+6,f'N{i+1}',22,'end' if inlet else 'start','#000')
        positions.append((f'N{i+1}',inlet,y))
    # A proposed manway with cover and center line.
    mx,my=right,top+285
    box(svg,mx,my-25,55,50);line(svg,mx+55,my-37,mx+55,my+37,'black');txt(svg,mx+80,my+7,'M1',22,color='#000')
    # Arrowhead-free dimension ticks mirror the mechanical drawing reference.
    def dimv(x,y1,y2,label):
        line(svg,x,y1,x,y2,'black');line(svg,x-15,y1,x+15,y1,'black');line(svg,x-15,y2,x+15,y2,'black')
        t=txt(svg,x-18,(y1+y2)/2,label,20,'middle','#000');t.set('transform',f'rotate(-90 {x-18} {(y1+y2)/2})')
    dimv(1745,top,bottom,'筒体高度见内侧标注')
    dimv(1810,top+65,bottom-65,'筒体 H = '+(r.length or '待定')+' mm')
    line(svg,left,top-65,right,top-65,'black');line(svg,left,top-80,left,top-50,'black');line(svg,right,top-80,right,top-50,'black')
    txt(svg,cx,top-90,'DN '+(r.diameter or '待定'),23,'middle','#000')
    txt(svg,cx,205,'主视图',27,'middle','#000')
    # Nozzle orientation view in the right lower area.
    ox,oy=2510,1410;rad=100
    add(svg,'circle',{'cx':ox,'cy':oy,'r':rad,'fill':'white','stroke':'black','stroke-width':2})
    add(svg,'circle',{'cx':ox,'cy':oy,'r':rad-8,'fill':'none','stroke':'black'})
    line(svg,ox-155,oy,ox+155,oy,'#777','12 5 2 5');line(svg,ox,oy-155,ox,oy+155,'#777','12 5 2 5')
    for dx,dy,label in [(0,-178,'0°'),(180,5,'90°'),(0,185,'180°'),(-180,5,'270°')]:txt(svg,ox+dx,oy+dy,label,19,'middle','#000')
    for i,(tag,inlet,y) in enumerate(positions):
        angle=(i*360/max(len(positions),1)-90)*math.pi/180
        px,py=ox+rad*math.cos(angle),oy+rad*math.sin(angle)
        qx,qy=ox+(rad+30)*math.cos(angle),oy+(rad+30)*math.sin(angle)
        line(svg,px,py,qx,qy,'black');txt(svg,ox+(rad+38)*math.cos(angle),oy+(rad+38)*math.sin(angle)+6,tag,18,'middle','#000')
    txt(svg,ox,1650,'A—A 管口方位示意',23,'middle','#000');txt(svg,ox,1690,'方位角待机械设计确认',18,'middle','#000')
    txt(svg,1570,1510,'技术要求',25,color='#000')
    for i,t in enumerate(['1. 操作工况与设计条件分别列示。','2. 壁厚、封头、支座需强度与载荷校核。','3. 接管编号与表格一一对应；尺寸待定。','4. 内件、催化剂和安全附件须专项选型。','5. 图示结构不代表已完成机械设计。']):txt(svg,1570,1550+i*35,t,19,color='#000')
    return svg

def geometry_volume(r):
    try:
        return f'{math.pi / 4 * (float(r.diameter)/1000)**2 * float(r.length)/1000:.2f}（不含封头）'
    except ValueError:
        return '随尺寸计算'

def drawing(p,r):
    if not p.get('ir') or not p.get('route'):raise ValueError('请先完成流程方案选择')
    unit=next((u for u in p['ir']['units'] if u['id']==r.unit),{})
    if r.kind=='equipment':
        defaults=equipment_defaults(p,r.unit)['values']
        r=r.model_copy(update={k:v for k,v in defaults.items() if not getattr(r,k)})
    from .cad_drawings import equipment_sheet
    svg=(equipment_sheet(p,r) if unit.get('type') in ('TOWER','REACTOR','HX') else condition(p,r)) if r.kind=='equipment' else process(p,r.kind,r.sheet_unit)
    return ET.tostring(svg,encoding='unicode')

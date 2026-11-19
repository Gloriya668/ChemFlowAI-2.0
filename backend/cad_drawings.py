"""CAD-reference sheet conventions, with project-specific engineering content.

Reference: user-supplied 1(1).zip (2004 DWG). Frame zoning, title block,
line colors and equipment-sheet partitions follow its PFD/PID/condition sheets.
Engineering assumptions remain distinct from imported process values.
"""
import copy
import json
import math
import re
import xml.etree.ElementTree as ET
from . import drawings as d
from .case_variant import result_key

NS=d.NS
BLACK='#000000'; MAIN='#ff00ff'; UTILITY='#00bfff'; SIGNAL='#00cddd'; INTERNAL='#00cf00'

def text(g,x,y,s,size=18,anchor='start',color=BLACK):
    return d.txt(g,x,y,str(s),size,anchor,color)

def ln(g,x,y,x2,y2,color=BLACK,width=1,dash=None):
    n=d.line(g,x,y,x2,y2,color,dash);n.set('stroke-width',str(width));return n

def rect(g,x,y,w,h,fill='white',width=1):
    n=d.box(g,x,y,w,h,fill);n.set('stroke',BLACK);n.set('stroke-width',str(width));return n

def path(g,points,color=MAIN,width=1.8,arrow=False,dash=None):
    a={'d':points,'fill':'none','stroke':color,'stroke-width':width}
    if arrow:a['marker-end']='url(#cad-arrow)'
    if dash:a['stroke-dasharray']=dash
    return d.add(g,'path',a)

def circle(g,x,y,r,color=BLACK,fill='white'):
    return d.add(g,'circle',{'cx':x,'cy':y,'r':r,'stroke':color,'fill':fill,'stroke-width':1})

def titleblock(s,p,title,code,x=2160,y=1772,w=605,h=168):
    rect(s,x,y,w,h,width=1.5)
    for yy in [y+38,y+66,y+98,y+132]:ln(s,x,yy,x+w,yy)
    for xx in [x+68,x+178,x+328,x+425]:ln(s,xx,y+38,xx,y+132)
    text(s,x+12,y+26,'ChemFlow AI · 工艺工程',21)
    text(s,x+w-12,y+26,'非施工图 · 参数待定',18,'end')
    for a,b in [(68,'职责'),(178,'姓名 / 状态'),(328,'项目 / 方案'),(425,'专业')]:text(s,x+a-6,y+57,b,12,'end')
    text(s,x+13,y+88,'设计');text(s,x+80,y+88,'常规设计初估',14);text(s,x+187,y+88,'工艺');text(s,x+338,y+88,'工艺')
    text(s,x+13,y+122,'复核');text(s,x+80,y+122,'工程复核');text(s,x+187,y+122,'R'+str(p.get('revision',0)))
    short_title=title.split(' · ')[-1]
    text(s,x+435,y+88,short_title,min(14,160/max(len(short_title),1)));text(s,x+435,y+120,'单位：见标注',14)
    text(s,x+12,y+155,code,17);text(s,x+w-10,y+155,'比例  不按比例',14,'end')

def frame(p,kind,title=None,code=None):
    title=title or {'pfd':'工艺物料流程图','pid':'管道及仪表流程图','equipment':'设备工艺条件图'}[kind]
    s=d.el('svg',{'width':2800,'height':1980,'viewBox':'0 0 2800 1980','role':'img','data-drawing-standard':'CAD-2004-reference'})
    d.add(s,'title',text=p['ir'].get('title','')+' · '+title)
    d.add(s,'style',text='text{font-family:SimSun,"Noto Serif CJK SC","Microsoft YaHei",serif;fill:#000}path,line,rect,circle,ellipse{vector-effect:non-scaling-stroke}')
    defs=d.add(s,'defs');m=d.add(defs,'marker',{'id':'cad-arrow','viewBox':'0 0 12 6','refX':11,'refY':3,'markerWidth':10,'markerHeight':5,'orient':'auto-start-reverse'})
    d.add(m,'path',{'d':'M0 0L12 3L0 6Z','fill':BLACK})
    rect(s,0,0,2800,1980);rect(s,82,35,2683,1905,width=2)
    # Source PFD/PID: 12 columns, A-F rows and offset binding margin.
    for i in range(12):
        x=82+i*2683/12
        ln(s,x,0,x,35);ln(s,x,1940,x,1980)
        text(s,x+112,25,i+1,17,'middle');text(s,x+112,1967,i+1,17,'middle')
    for i,letter in enumerate('ABCDEF'):
        y=35+i*1905/6
        ln(s,0,y,82,y);ln(s,2765,y,2800,y)
        text(s,40,y+160,letter,17,'middle');text(s,2782,y+160,letter,17,'middle')
    ln(s,1400,35,1400,66,width=2);ln(s,1400,1909,1400,1940,width=2)
    ln(s,82,990,133,990,width=2);ln(s,2714,990,2765,990,width=2)
    titleblock(s,p,title,code or 'CF-'+result_key(p).upper()+'-'+kind.upper())
    text(s,115,1874,p['ir'].get('title',''),22)
    text(s,115,1915,'主物料管线',16);ln(s,280,1909,400,1909,MAIN,2)
    text(s,435,1915,'公用工程',16);ln(s,570,1909,690,1909,UTILITY,1.5)
    text(s,725,1915,'内件 / 阀门',16);ln(s,890,1909,1010,1909,INTERNAL,1.3)
    text(s,1045,1915,'仪表信号',16);ln(s,1190,1909,1310,1909,SIGNAL,1,'6 4')
    return s

def cad_symbol(g,typ,x,y,uid,label,scale=1):
    h={'TOWER':175,'REACTOR':75,'FLASH':75,'DECANTER':75}.get(typ,48)
    a=d.add(g,'g',{'transform':f'translate({x} {y}) scale({scale})','data-equipment-id':uid})
    if typ in ('TOWER','REACTOR','FLASH'):
        w=45 if typ=='FLASH' else 55
        d.add(a,'path',{'d':f'M{-w} {-h+20}Q{-w} {-h} 0 {-h}Q{w} {-h} {w} {-h+20}V{h-20}Q{w} {h} 0 {h}Q{-w} {h} {-w} {h-20}Z','fill':'white','stroke':BLACK,'stroke-width':1.1})
        for yy in (-h+20,h-20):ln(a,-w,yy,w,yy)
        if typ=='TOWER':
            for j in range(7):
                yy=-h+45+j*(2*h-90)/6
                ln(a,-w+8,yy,w-8,yy,INTERNAL)
                xx=-w+8 if j%2 else w-8;ln(a,xx,yy-6,xx,yy+6,INTERNAL)
        elif typ=='REACTOR':
            for yy in (-45,0,45):
                ln(a,-w+5,yy-18,w-5,yy-18,INTERNAL);ln(a,-w+5,yy+18,w-5,yy+18,INTERNAL)
                ln(a,-w+5,yy-18,w-5,yy+18,INTERNAL);ln(a,w-5,yy-18,-w+5,yy+18,INTERNAL)
        else:ln(a,-w+2,20,w-2,20,INTERNAL)
        # Outline endpoints coincide with the topology's connection points.
    elif typ=='HX':
        circle(a,0,0,47)
        path(a,'M-47 0H-30L-15 -20L15 20L30 0H47',BLACK,1)
        path(a,'M-38 38L38 -38',BLACK,.8,True)
    elif typ=='COMPRESSOR':
        d.add(a,'path',{'d':'M-55 -44L55 -25V25L-55 44Z','fill':'white','stroke':BLACK,'stroke-width':1.2})
        ln(a,-22,-35,-22,35);ln(a,17,-28,17,28)
    elif typ=='VALVE':
        path(a,'M-25 -17L25 17V-17L-25 17Z',INTERNAL,1.2)
    elif typ=='DECANTER':
        d.add(a,'rect',{'x':-45,'y':-75,'width':90,'height':150,'rx':35,'fill':'white','stroke':BLACK})
        ln(a,-44,0,44,0,INTERNAL);ln(a,12,0,12,65,INTERNAL)
    else:
        circle(a,0,0,26);path(a,'M-18 -16L20 0L-18 16Z',INTERNAL,1)
    text(a,0,h+29/scale,uid,19/scale,'middle');ln(a,-43,h+37/scale,43,h+37/scale,width=1.5)
    text(a,0,h+62/scale,label,15/scale,'middle')
    return a

def tag(g,x,y,sid,values):
    # Four-row compact condition tag, as in the source PFD.
    rect(g,x,y,168,99)
    for i in range(1,4):ln(g,x,y+i*24.75,x+168,y+i*24.75)
    ln(g,x+42,y,x+42,y+99)
    for i,(label,key) in enumerate([('°C','temperature'),('bar','pressure'),('kg/h','mass_flow'),('kmol/h','molar_flow')]):
        text(g,x+4,y+18+i*24.75,label,13)
        text(g,x+162,y+18+i*24.75,d.val(values,key),14,'end')
    text(g,x+84,y-10,sid,16,'middle')

def instrument(g,x,y,code,number,panel=False):
    if panel:rect(g,x-22,y-22,44,44)
    circle(g,x,y,21,SIGNAL)
    ln(g,x-20,y,x+20,y,SIGNAL)
    text(g,x,y-5,code,12,'middle',SIGNAL);text(g,x,y+14,number,11,'middle',SIGNAL)

def valve(g,x,y,actuator=False):
    path(g,f'M{x-11} {y-7}L{x+11} {y+7}V{y-7}L{x-11} {y+7}Z',INTERNAL,1)
    if actuator:
        ln(g,x,y-7,x,y-27,INTERNAL)
        path(g,f'M{x-13} {y-27}Q{x} {y-46} {x+13} {y-27}Z',INTERNAL,1)

def control_station(g,x,y,number,code='FIC'):
    valve(g,x,y,True);valve(g,x-55,y);valve(g,x+55,y)
    path(g,f'M{x-80} {y}V{y+42}H{x+80}V{y}',MAIN,1.3);valve(g,x,y+42)
    instrument(g,x,y-100,code,number,True)
    path(g,f'M{x} {y-78}V{y-36}',SIGNAL,1,dash='5 4')
    text(g,x+18,y-32,'FC',12)

def connector(g,x,y,label,direction=1):
    w=160
    path(g,f'M{x} {y-14}H{x+w-15}L{x+w} {y}L{x+w-15} {y+14}H{x}Z',BLACK,1)
    text(g,x+w/2,y+5,label,13,'middle')

def table(g,x,y,width,headers,rows,height=34):
    cw=width/len(headers)
    for i,row in enumerate([headers]+rows):
        rect(g,x,y+i*height,width,height)
        for j,v in enumerate(row):
            if j:ln(g,x+j*cw,y+i*height,x+j*cw,y+(i+1)*height)
            v=str(v);size=min(17,(cw-12)/max(sum(1 if ord(c)>255 else .55 for c in v),1))
            text(g,x+j*cw+6,y+i*height+height*.67,v,size)

def process_sheet(p,kind,focus=''):
    if focus:return unit_sheet(p,kind,focus)
    src=ET.parse(d.ROOT/'data/assets'/f'{result_key(p)}.svg').getroot()
    s=frame(p,kind);ns={'s':NS}
    text(s,1420,110,p['ir'].get('title','')+' · 总流程',30,'middle')
    text(s,1420,150,'设备与物流总览 / 各工段详图按设备位号分张',18,'middle')
    g=d.add(s,'g',{'transform':'translate(115 245) scale(.91)','data-process-layout':'centered'})
    streams=(p.get('result') or {}).get('streams') or {}
    units={u['id']:u for u in p['ir']['units']}
    for node in src.findall('.//s:path',ns):
        if 'stream-pipe' in node.get('class',''):
            n=path(g,node.get('d'),MAIN,1.5,True);n.set('data-stream-id',node.get('data-stream-id',''))
    for node in src.findall('.//s:g[@data-equipment-id]',ns):
        uid=node.get('data-equipment-id');u=units.get(uid)
        if not u:continue
        pos=re.findall(r'-?\d+(?:\.\d+)?',node.get('transform',''))
        cad_symbol(g,u['type'],float(pos[0]),float(pos[1]),uid,u.get('label',''))
    for i,node in enumerate(src.findall('.//s:g[@class="stream-label"]',ns)):
        sid=node.get('data-stream-id');pos=re.findall(r'-?\d+(?:\.\d+)?',node.get('transform',''));x,y=map(float,pos[:2])
        a=d.add(g,'g',{'data-stream-id':sid})
        if kind=='pfd':tag(a,x,y,sid,streams.get(sid))
        else:
            rect(a,x-3,y-27,204,61)
            text(a,x,y-7,'PL-'+str(i+101)+' / '+sid,17)
            text(a,x,y+19,'详见设备工段图',15)
    for node in list(src):
        if node.tag=='{'+NS+'}path' and node.get('stroke-dasharray')=='4 5':path(g,node.get('d'),BLACK,.7,dash='4 4')
    # Equipment register mirrors the top/bottom underlined device captions.
    rows=[[u['id'],u.get('label',''),u['type']] for u in p['ir']['units']]
    for group in range(math.ceil(len(rows)/6)):
        chunk=rows[group*6:(group+1)*6]
        for j,row in enumerate(chunk):
            x=320+j*420;y=1610+group*78
            text(s,x,y,row[0],18,'middle');ln(s,x-85,y+8,x+85,y+8,width=1.3);text(s,x,y+32,row[1],17,'middle')
    return s

def unit_sheet(p,kind,uid):
    u=next((x for x in p['ir']['units'] if x['id']==uid),None)
    if not u:raise ValueError('工段设备不存在')
    title=uid+' '+u.get('label','')+' · '+('工艺物料流程图' if kind=='pfd' else '管道及仪表流程图')
    s=frame(p,kind,title,'CF-'+result_key(p).upper()+'-'+kind.upper()+'-'+uid)
    text(s,1420,125,title,28,'middle')
    connected=[x for x in p['ir']['streams'] if uid in (x.get('from_unit'),x.get('to_unit'))]
    values=(p.get('result') or {}).get('streams') or {}
    inputs=[x for x in connected if x.get('to_unit')==uid]
    outputs=[x for x in connected if x.get('from_unit')==uid]
    cx,cy=1400,800
    cad_symbol(s,u['type'],cx,cy,uid,u.get('label',''),2.5)
    for inlet,items in [(True,inputs),(False,outputs)]:
        for i,st in enumerate(items):
            sid=st['stream_id'];y=540+i*min(270,620/max(len(items)-1,1));edge=1310 if inlet else 1490
            other=st.get('from_unit') if inlet else st.get('to_unit');other=other or ('界区进料' if inlet else '界区出料')
            halfh={'TOWER':437,'REACTOR':187,'FLASH':187,'DECANTER':187}.get(u['type'],120)
            bodyy=max(cy-halfh+35,min(cy+halfh-35,y))
            edge=cx+(-1 if inlet else 1)*({'TOWER':137.5,'REACTOR':137.5,'FLASH':112.5,'DECANTER':112.5}.get(u['type'],117.5))
            bend=edge+(-50 if inlet else 50)
            route=f'M490 {y}H{bend}V{bodyy}H{edge}' if inlet else f'M{edge} {bodyy}H{bend}V{y}H2350'
            path(s,route,MAIN,2,True).set('data-stream-id',sid)
            if inlet:connector(s,330,y,other)
            else:connector(s,2350,y,other)
            number=f'{p["ir"]["units"].index(u)+1:02d}{i+1+(0 if inlet else len(inputs)):02d}'
            text(s,720 if inlet else 1980,y-22,'PL-'+number+' / '+sid,18,'middle')
            if kind=='pfd':tag(s,940 if inlet else 1630,y-147,sid,values.get(sid))
            else:
                vx=930 if inlet else 1830
                control_station(s,vx,y,number,'FIC')
                instrument(s,edge-95 if inlet else edge+95,y-84,'TT',number)
                path(s,f'M{edge-95 if inlet else edge+95} {y-63}V{y}',SIGNAL,1,dash='5 4')
                text(s,720 if inlet else 2160,y+65,'DN / 材料等级：设计选定',15,'middle')
    if kind=='pid':
        instrument(s,1680,365,'PT','0101');instrument(s,1810,365,'PIC','0101',True)
        path(s,'M1400 425V365H1659 M1701 365H1789',SIGNAL,1,dash='5 4')
        text(s,2030,360,'测量 / 控制回路建议',19)
        text(s,2030,397,'TT / PT  温度 / 压力测量',16)
        text(s,2030,433,'FIC / LIC  流量 / 液位控制',16)
        text(s,2030,469,'阀门失效位置需工艺确认',16)
    rows=[]
    for st in connected:
        v=values.get(st['stream_id'])
        rows.append([st['stream_id'],st.get('from_unit') or '界区',st.get('to_unit') or '界区',d.val(v,'temperature'),d.val(v,'pressure'),d.val(v,'mass_flow'),d.val(v,'molar_flow')])
    text(s,170,1390,'本工段物流条件',23)
    table(s,170,1420,2450,['物流号','上游设备','下游设备','温度 / °C','压力 / bar','流量 / kg/h','流量 / kmol/h'],rows,42)
    text(s,170,1790,'实线：工艺连接；青色虚线：仪表信号；绿色：阀门及设备内件。',17)
    text(s,170,1825,'管线编号用于图纸索引；控制回路为初步设计，详细条件在设备条件图中列示。',17)
    return s

def dim(g,x,y,x2,y2,label,vertical=False):
    ln(g,x,y,x2,y2,width=.8)
    if vertical:
        for yy in (y,y2):ln(g,x-13,yy,x+13,yy)
        t=text(g,x-11,(y+y2)/2,label,17,'middle');t.set('transform',f'rotate(-90 {x-11} {(y+y2)/2})')
    else:
        for xx in (x,x2):ln(g,xx,y-13,xx,y+13)
        text(g,(x+x2)/2,y-12,label,17,'middle')

def elevation(g,x,y,w,h,r,typ,connected):
    # Mechanical drafting: double wall, ellipsoidal heads, centerline, skirt,
    # flange rings, access nozzles, support details and dimension chains.
    left,right=x-w/2,x+w/2;top,bottom=y,y+h
    path(g,f'M{left} {top+35}Q{left} {top} {x} {top}Q{right} {top} {right} {top+35}V{bottom-35}Q{right} {bottom} {x} {bottom}Q{left} {bottom} {left} {bottom-35}Z',BLACK,1.7)
    for xx in (left+5,right-5):ln(g,xx,top+35,xx,bottom-35)
    ln(g,left,top+35,right,top+35);ln(g,left,bottom-35,right,bottom-35)
    ln(g,x,top-70,x,bottom+150,BLACK,.7,'18 4 3 4')
    if typ=='REACTOR':
        for k in range(3):
            yy=top+95+k*(h-180)/3;hh=(h-210)/3
            ln(g,left+6,yy,right-6,yy);ln(g,left+6,yy+hh,right-6,yy+hh)
            ln(g,left+6,yy,right-6,yy+hh);ln(g,right-6,yy,left+6,yy+hh)
            for dy in [-8,-4,0]:ln(g,left,yy+dy,right,yy+dy)
    else:
        for k in range(12):
            yy=top+65+k*(h-130)/12
            ln(g,left+6,yy,right-6,yy)
            xx=left+14 if k%2 else right-14;ln(g,xx,yy,xx,yy+20)
    # Weld seams and support skirt.
    for yy in (top+45,bottom-45):ln(g,left-3,yy,right+3,yy,width=1.5)
    for xx in (left+7,right-7):ln(g,xx,bottom-10,xx,bottom+115,width=2)
    rect(g,left-15,bottom+115,w+30,8);rect(g,x-18,bottom+35,36,50)
    for xx in (left-7,right+7):ln(g,xx,bottom+105,xx,bottom+138,width=2)
    for i,c in enumerate(connected):
        inlet=c.get('to_unit')==r.unit;edge=left if inlet else right;end=edge+(-85 if inlet else 85)
        yy=top+100+i*(h-200)/max(len(connected)-1,1)
        for off in (-5,5):ln(g,edge,yy+off,end,yy+off)
        for off in (-4,4):ln(g,end+off,yy-17,end+off,yy+17,width=1.5)
        ln(g,edge-15 if inlet else edge+15,yy,end-20 if inlet else end+20,yy,BLACK,.6,'10 3 2 3')
        text(g,end-18 if inlet else end+18,yy-10,'N'+str(i+1),17,'end' if inlet else 'start')
    for i in range(2):
        yy=top+180+i*(h-320)
        rect(g,right,yy,28,22);ln(g,right+28,yy-7,right+28,yy+29,width=2)
        text(g,right+43,yy+13,'M'+str(i+1),15)
    dim(g,left-175,top,left-175,bottom,'H = '+r.length+' mm',True)
    dim(g,left-125,top+35,left-125,bottom-35,'筒体直段',True)
    dim(g,left,top-45,right,top-45,'DN '+r.diameter)
    dim(g,right+190,bottom,right+190,bottom+123,'裙座',True)
    text(g,x,bottom+180,r.unit+' 设备主视图',23,'middle')

def orientation(g,x,y,radius=85,count=4):
    circle(g,x,y,radius);circle(g,x,y,radius-5)
    ln(g,x-radius-45,y,x+radius+45,y,BLACK,.7,'12 4 2 4');ln(g,x,y-radius-45,x,y+radius+45,BLACK,.7,'12 4 2 4')
    for a,tx,ty in [('0°',x,y-radius-55),('90°',x+radius+60,y+5),('180°',x,y+radius+65),('270°',x-radius-60,y+5)]:text(g,tx,ty,a,16,'middle')
    for j in range(count):
        angle=j*2*math.pi/max(count,1);xx=x+radius*math.cos(angle);yy=y+radius*math.sin(angle)
        circle(g,xx,yy,7);text(g,x+(radius+27)*math.cos(angle),y+(radius+27)*math.sin(angle)+5,'N'+str(j+1),12,'middle')
    text(g,x,y+radius+108,'A—A 管口方位',20,'middle')

def equipment_sheet(p,r):
    u=next((x for x in p['ir']['units'] if x['id']==r.unit),None)
    if not u:raise ValueError('请选择当前流程中的设备')
    reactor=u['type']=='REACTOR';hx=u['type']=='HX'
    title=('反应器' if reactor else '换热器' if hx else '塔器' if u['type']=='TOWER' else '设备')+'工艺条件图'
    s=frame(p,'equipment',title,'CF-'+r.unit+'-COND')
    # Reactor: top header, left process/nozzle tables, right elevation.
    # Tower: left elevation/orientation, right process/nozzle tables.
    # HX: upper longitudinal section, lower-left process/nozzle tables.
    text(s,1420,100,r.unit+' · '+u.get('label','')+' · '+title,29,'middle')
    if reactor:
        rect(s,130,130,2600,60)
        for xx in (850,1580,2230):ln(s,xx,130,xx,190)
        text(s,150,169,'设备位号：'+r.unit,23)
        text(s,875,169,'设备名称：'+u.get('label',''),22)
        text(s,1600,169,'工艺专业 · 初步设计',22)
        text(s,2250,169,'图号 CF-'+r.unit,20)
    connected=[c for c in p['ir']['streams'] if r.unit in (c.get('from_unit'),c.get('to_unit'))]
    streams=(p.get('result') or {}).get('streams') or {}
    rows=[]
    for i,c in enumerate(connected):
        v=streams.get(c['stream_id']);rows.append(['N'+str(i+1),c['stream_id'],'入口' if c.get('to_unit')==r.unit else '出口',d.val(v,'temperature'),d.val(v,'pressure'),d.val(v,'mass_flow')])
    known=[streams.get(c['stream_id'],{}) for c in connected]
    def span(key):
        vv=[v.get(key,{}).get('value') for v in known];vv=[v for v in vv if isinstance(v,(int,float))]
        return f'{min(vv):.2f} ～ {max(vv):.2f}' if vv else '—'
    spec=json.loads((d.ROOT/'data/equipment_parameters.json').read_text(encoding='utf-8')).get(result_key(p),{})
    equipment=next((x for x in spec.get('units',[]) if x['id']==r.unit),{})
    paramrows=[[x['label'],str(x['value'])+' '+str(x['unit'])] for x in equipment.get('rows',[]) if x['key'] not in ('STREAM','MOLE-FLOW','MASS-FLOW')][:4]
    conditions=[['设备位号',r.unit],['设备名称',u.get('label','')],['数量 / 操作方式','1 台 / 连续操作'],['操作温度 / °C',span('temperature')],['操作压力 / bar',span('pressure')],['设计温度 / °C',r.design_temperature],['设计压力 / MPa',r.design_pressure],['公称直径 / mm',r.diameter],['筒体高度或长度 / mm',r.length],['主体材料',r.material],['壁厚 / 腐蚀裕量 / mm',r.thickness+' / '+r.corrosion],['保温 / 保冷',r.insulation],['几何容积 / m³',d.geometry_volume(r)],['封头 / 支承形式','椭圆封头 / '+('鞍座' if hx else '裙座')]]+paramrows
    tx=130 if reactor or hx else 1540;ty=230 if not hx else 1030;tw=(1260 if reactor else 1190) if not hx else 1540
    if not hx:
        text(s,tx,ty-30,'工 艺 与 设 计 条 件',23)
        table(s,tx,ty,tw,['项目','工艺参数 / 设计条件'],conditions,44)
        ny=ty+(len(conditions)+1)*44+55
        text(s,tx,ny-18,'接 管 及 开 孔 一 览 表',22)
        nozzles=[[row[0],row[1],row[2],'设计选定','设计选定'] for row in rows]+[['M1 / M2','检修人孔','检修','DN500（初估）','等级待定']]
        table(s,tx,ny,tw,['符号','连接物流','用途','公称直径','法兰 / 密封'],nozzles,40)
        ex=2110 if reactor else 580
        elevation(s,ex,320,150,900,r,u['type'],connected)
        orientation(s,ex+340 if reactor else 1130,1450,72,len(connected))
        # Numbered requirements take the same adjacent column as the reference.
        nx=1530 if reactor else 950;ny=350 if not reactor else 1550
        notes=['技术要求','1. 图示尺寸为常规设备设计初估。','2. 工艺操作值与机械设计值分别列示。','3. 接管编号对应下表物流连接。','4. 内件、支承与法兰须专项校核。','5. 管口方位为初步布置。','6. 内部结构为设备原理示意。']
        for i,n in enumerate(notes):text(s,nx,ny+i*34,n,21 if i==0 else 16)
    else:
        # Reference E0309 arrangement: longitudinal GA across the upper half.
        x,y,w,h=380,420,1620,190
        d.add(s,'rect',{'x':x,'y':y,'width':w,'height':h,'rx':65,'fill':'white','stroke':BLACK,'stroke-width':1.6})
        for xx in (x+180,x+195,x+w-180,x+w-195):ln(s,xx,y-12,xx,y+h+12,width=2)
        for yy in range(y+30,y+h-20,25):ln(s,x+195,yy,x+w-195,yy)
        for xx in range(x+400,x+w-200,220):ln(s,xx,y+12,xx,y+h-12,width=1.3)
        ln(s,x-90,y+h/2,x+w+90,y+h/2,BLACK,.7,'18 4 3 4')
        for xx in (x+430,x+w-430):
            path(s,f'M{xx-45} {y+h-10}V{y+h+95}H{xx+45}V{y+h-10}',BLACK,1.8)
            rect(s,xx-60,y+h+95,120,9)
        for i,xx in enumerate((x+90,x+280,x+w-280,x+w-90)):
            yy=y if i%2==0 else y+h;end=yy-90 if i%2==0 else yy+90
            for off in (-7,7):ln(s,xx+off,yy,xx+off,end)
            for off in (-4,4):ln(s,xx-24,end+off,xx+24,end+off,width=1.5)
            text(s,xx+35,end+5,'N'+str(i+1),18)
        dim(s,x,y-165,x+w,y-165,'总长 L = '+r.length+' mm')
        dim(s,x+195,y-90,x+w-195,y-90,'有效管束长度（按传热设计）')
        dim(s,x+430,y+h+165,x+w-430,y+h+165,'支承中心距（机械设计）')
        dim(s,x+w+110,y,x+w+110,y+h,'DN '+r.diameter,True)
        text(s,1190,820,'主视图 / 管束与支承布置',23,'middle')
        circle(s,2310,500,90);circle(s,2310,500,82)
        for xx in [-40,0,40]:
            for yy in [-40,0,40]:circle(s,2310+xx,500+yy,10)
        ln(s,2195,500,2425,500,BLACK,.7,'12 4 2 4');ln(s,2310,385,2310,615,BLACK,.7,'12 4 2 4')
        text(s,2310,660,'A—A 管束端视',21,'middle')
        rect(s,2220,755,180,65);circle(s,2255,787,10);circle(s,2365,787,10)
        ln(s,2200,787,2420,787,BLACK,.7,'12 4 2 4')
        text(s,2310,875,'B—B 鞍座地脚孔',21,'middle')
        compact=conditions[:12]
        # Four-column conditions, preserving the reference lower-left table.
        paired=[[compact[i][0],compact[i][1],compact[i+1][0],compact[i+1][1]] for i in range(0,len(compact),2)]
        table(s,130,980,1820,['项目','数值','项目','数值'],paired,48)
        nozzles=rows+[ ['N3','公用工程','入口','设计选定','设计选定','设计选定'],['N4','公用工程','出口','设计选定','设计选定','设计选定'] ] if len(rows)==2 else rows
        table(s,130,1370,1820,['管口','连接物流','用途','温度 / °C','压力 / bar','流量 / kg/h'],nozzles,42)
        for i,n in enumerate(['技术要求','1. 壳程 / 管程须结合设备选型确认。','2. 管束根数与面积由传热设计校核。','3. 鞍座与法兰需机械强度校核。','4. 几何尺寸为常规设计初估。']):text(s,2020,1060+i*45,n,22 if i==0 else 16)
    return s

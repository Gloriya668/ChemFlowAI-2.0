"""Versioned learning notebooks and escaped HTML exports stored under project runtime."""
import html,json,os,re
from datetime import datetime,timezone
from fastapi import APIRouter,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel,Field
from .store import ROOT,LOCK
router=APIRouter(prefix='/api/learning/study',tags=['Learning notebook'])
DIRECTORY=ROOT/'runtime/learning_study'
def location(cid):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,95}',cid):raise HTTPException(400,'案例标识无效')
    return DIRECTORY/(cid+'.json')
class Notebook(BaseModel):
    revision:int=Field(default=0,ge=0)
    draft:dict=Field(default_factory=dict)
@router.get('/{cid}')
def read(cid:str):
    path=location(cid)
    with LOCK:
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'revision':0,'draft':None,'updatedAt':None}
@router.put('/{cid}')
def save(cid:str,body:Notebook):
    path=location(cid)
    if len(json.dumps(body.draft,ensure_ascii=False))>350000:raise HTTPException(413,'学习记录过大，请精简附件摘录。')
    with LOCK:
        old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'revision':0}
        if old['revision']!=body.revision:raise HTTPException(409,'另一窗口已更新此案例。请先保留当前记录，再重新打开后合并。')
        data={'id':cid,'revision':old['revision']+1,'draft':body.draft,'updatedAt':datetime.now(timezone.utc).isoformat()}
        DIRECTORY.mkdir(parents=True,exist_ok=True)
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(temp,path)
        return data
class Section(BaseModel):
    title:str=Field(max_length=200)
    paragraphs:list[str]=Field(default_factory=list,max_length=100)
    rows:list[list[str]]=Field(default_factory=list,max_length=200)
class Report(BaseModel):
    title:str=Field(min_length=1,max_length=200)
    sections:list[Section]=Field(min_length=1,max_length=15)
@router.post('/{cid}/report')
def report(cid:str,body:Report):
    path=location(cid).with_suffix('.html')
    if len(body.model_dump_json())>700000:raise HTTPException(413,'报告内容过大')
    esc=lambda value:html.escape(str(value))
    content=[]
    for section in body.sections:
        content.append('<section><h2>'+esc(section.title)+'</h2>')
        content.extend('<p>'+esc(p).replace('\n','<br>')+'</p>' for p in section.paragraphs)
        if section.rows:
            content.append('<table>')
            for i,row in enumerate(section.rows):
                tag='th' if i==0 else 'td'
                content.append('<tr>'+''.join('<'+tag+'>'+esc(v)+'</'+tag+'>' for v in row)+'</tr>')
            content.append('</table>')
        content.append('</section>')
    doc='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(body.title)+'</title><style>body{font:15px/1.8 system-ui,Microsoft YaHei,sans-serif;color:#173340;max-width:1100px;margin:40px auto;padding:0 24px}h1{font-size:28px}h2{font-size:20px;border-bottom:1px solid #bad0d8;padding-bottom:8px}section{margin:34px 0}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border:1px solid #c8d5db;padding:8px;vertical-align:top;overflow-wrap:anywhere}th{background:#edf3f5}p{white-space:normal} @media print{body{margin:0}tr{break-inside:avoid}}</style><h1>'+esc(body.title)+'</h1><p>学习记录 · 概念设计与经济演示，待补资料和未核对假设保留在正文中。</p>'+''.join(content)+'</html>'
    with LOCK:
        DIRECTORY.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.html.tmp');temp.write_text(doc,encoding='utf-8');os.replace(temp,path)
    return {'path':str(path),'url':f'/api/learning/study/{cid}/report'}
@router.get('/{cid}/report')
def download_report(cid:str):
    path=location(cid).with_suffix('.html')
    if not path.exists():raise HTTPException(404,'请先生成学习报告')
    return FileResponse(path,media_type='text/html',filename=cid+'-learning-report.html')

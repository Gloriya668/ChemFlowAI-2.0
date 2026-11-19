"""Public literature retrieval and user-authored learning cases (no synthetic research results)."""
import html,json,re,uuid,os
from datetime import datetime,timezone
from urllib.parse import urlsplit
import httpx
from fastapi import APIRouter,HTTPException,Query
from pydantic import BaseModel,Field,field_validator,model_validator
from .store import ROOT,LOCK

router=APIRouter(prefix='/api/learning',tags=['Learning cases'])
DIRECTORY=ROOT/'runtime/learning_cases'
MODULES={'Feed':'feed','Product':'product','Mixer':'mixer','FSplit':'splitter','Flash2':'drum','Flash3':'drum','Decanter':'drum','RadFrac':'column','Absorber':'column','Extract':'column','MultiFrac':'divided','RStoic':'reactor','RPlug':'plug','HeatX':'exchanger','Heater':'exchanger','MHeatX':'multiheat','Pump':'pump','Compr':'compressor','MCompr':'multicompressor','Valve':'valve'}
def clean(value,limit=3500):return html.unescape(re.sub('<[^>]+>',' ',str(value or ''))).strip()[:limit]
def valid_url(value):
    if not value:return ''
    u=urlsplit(value)
    if u.scheme not in ('http','https') or not u.hostname or u.username or u.password:raise ValueError('请填写有效的 http/https 文献链接')
    return value
class Evidence(BaseModel):
    id:str=Field(min_length=1,max_length=120)
    title:str=Field(min_length=1,max_length=500)
    url:str=Field(default='',max_length=2000)
    abstract:str=Field(default='',max_length=3500)
    authors:str=Field(default='',max_length=800)
    year:str=Field(default='',max_length=20)
    provider:str=Field(default='手动录入',max_length=40)
    _url=field_validator('url')(valid_url)
class Parameter(BaseModel):
    name:str=Field(min_length=1,max_length=80)
    unit:str=Field(default='待确认',max_length=40)
    meaning:str=Field(default='',max_length=500)
    watch:str=Field(default='',max_length=500)
class Details(BaseModel):
    principle:str=Field(default='',max_length=3000)
    internals:str=Field(default='',max_length=1500)
    parameters:list[Parameter]=Field(default_factory=list,max_length=12)
class Node(BaseModel):
    id:str=Field(pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,31}$')
    name:str=Field(min_length=1,max_length=70)
    module:str
    role:str=Field(default='',max_length=1000)
    x:float=Field(ge=100,le=2900,allow_inf_nan=False)
    y:float=Field(ge=120,le=2700,allow_inf_nan=False)
    details:Details=Field(default_factory=Details)
    @field_validator('module')
    @classmethod
    def supported(cls,v):
        if v not in MODULES:raise ValueError('不支持的设备模块')
        return v
class Edge(BaseModel):
    from_:str=Field(alias='from',max_length=32)
    to:str=Field(max_length=32)
    label:str=Field(default='',max_length=120)
    tone:str=Field(default='normal',pattern='^(normal|recycle|product|heat)$')
class CaseInput(BaseModel):
    title:str=Field(min_length=1,max_length=100)
    summary:str=Field(default='',max_length=2000)
    method:str=Field(default='待选择',max_length=120)
    points:list[str]=Field(default_factory=list,max_length=8)
    nodes:list[Node]=Field(min_length=2,max_length=30)
    edges:list[Edge]=Field(min_length=1,max_length=64)
    sources:list[Evidence]=Field(default_factory=list,max_length=30)
    revision:int=Field(default=0,ge=0)
    @model_validator(mode='after')
    def topology(self):
        ids=[n.id for n in self.nodes]
        if len(set(ids))!=len(ids):raise ValueError('设备位号不能重复')
        if not self.title.strip():raise ValueError('请填写案例名称')
        if not any(n.module not in ('Feed','Product') for n in self.nodes):raise ValueError('请至少添加一台设备')
        linked=set()
        for e in self.edges:
            if e.from_ not in ids or e.to not in ids or e.from_==e.to:raise ValueError('物流连接无效，请检查起点和终点')
            linked.update([e.from_,e.to])
        if set(ids)-linked:raise ValueError('存在未连接的设备或物流，请补充连接或移除孤立节点')
        if any(len(p)>300 for p in self.points):raise ValueError('学习要点过长')
        return self

def path_for(cid):
    if not re.fullmatch(r'custom-[0-9a-f-]{36}',cid):raise HTTPException(404,'未找到自定义案例')
    try:uuid.UUID(cid[7:])
    except ValueError:raise HTTPException(404,'未找到自定义案例')
    return DIRECTORY/(cid+'.json')
def read_case(cid):
    path=path_for(cid)
    if not path.exists():raise HTTPException(404,'未找到自定义案例')
    return json.loads(path.read_text(encoding='utf-8'))
def persist(body,cid,revision):
    nodes=[]
    for n in body.nodes:
        data=n.model_dump();data['kind']=MODULES[n.module];nodes.append(data)
    width=max(1400,max(n['x'] for n in nodes)+160);height=max(760,max(n['y'] for n in nodes)+180)
    edges=[]
    for i,e in enumerate(body.edges):
        a=next(n for n in nodes if n['id']==e.from_);b=next(n for n in nodes if n['id']==e.to)
        d=e.model_dump(by_alias=True);d.update(sp='R',tp='L')
        if e.tone=='normal':d.pop('tone')
        if a['x']>=b['x']:
            lane=max(42,min(a['y'],b['y'])-130-(i%3)*22)
            d.update(sp='T',tp='T',via=[[a['x'],lane],[b['x'],lane]])
        edges.append(d)
    out={'id':cid,'title':body.title.strip(),'category':'自定义案例','level':'自主编排','section':'','example':'','pages':'','figures':'',
         'summary':body.summary,'method':body.method,'points':body.points or ['阅读设备间的物流连接','比较设备内构件与操作参数','核对资料与待确认条件'],
         'width':width,'height':height,'nodes':nodes,'edges':edges,'sources':[s.model_dump() for s in body.sources],
         'custom':True,'revision':revision,'updatedAt':datetime.now(timezone.utc).isoformat(),'note':'自主编排的学习流程；资料检索不代表工程核验，缺失设计值需进一步确认。'}
    DIRECTORY.mkdir(parents=True,exist_ok=True);path=path_for(cid);tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,path)
    return out
@router.get('/custom')
def list_cases():
    if not DIRECTORY.exists():return []
    result=[]
    for path in sorted(DIRECTORY.glob('custom-*.json'),key=lambda p:p.stat().st_mtime,reverse=True):
        try:result.append(json.loads(path.read_text(encoding='utf-8')))
        except (ValueError,OSError):continue
    return result
@router.get('/custom/{cid}')
def get_case(cid:str):return read_case(cid)
@router.post('/custom')
def create_case(body:CaseInput):
    with LOCK:return persist(body,'custom-'+str(uuid.uuid4()),1)
@router.put('/custom/{cid}')
def update_case(cid:str,body:CaseInput):
    with LOCK:
        previous=read_case(cid)
        if body.revision!=previous.get('revision',1):raise HTTPException(409,'案例已在其他窗口修改，请重新打开后编辑。当前编辑内容保留在浏览器草稿中。')
        return persist(body,cid,body.revision+1)
@router.get('/literature')
async def literature(q:str=Query(min_length=2,max_length=300),page:int=Query(default=1,ge=1,le=20),year:int|None=Query(default=None,ge=1900,le=2100),until:int|None=Query(default=None,ge=1900,le=2100)):
    params={'query':q.strip(),'rows':12,'offset':(page-1)*12,'select':'DOI,title,author,published,abstract,URL,container-title','sort':'relevance'}
    filters=[]
    if year:filters.append(f'from-pub-date:{year}-01-01')
    if until:filters.append('until-pub-date:'+min(f'{until}-12-31',datetime.now(timezone.utc).date().isoformat()))
    if year and until and until<year:raise HTTPException(400,'结束年份不能早于开始年份')
    if filters:params['filter']=','.join(filters)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(25,connect=8),follow_redirects=False) as client:
            async with client.stream('GET','https://api.crossref.org/works',params=params,headers={'User-Agent':'ChemFlowAI-Learning/1.0','Accept':'application/json'}) as response:
                if response.status_code==429:raise HTTPException(429,'文献服务暂时限流，请稍后重试。')
                if response.status_code!=200:raise HTTPException(502,f'文献服务暂不可用（HTTP {response.status_code}），可先手动补充资料。')
                content=b''
                async for block in response.aiter_bytes():
                    content+=block
                    if len(content)>2_000_000:raise HTTPException(502,'文献响应过大，请缩小检索范围。')
        data=json.loads(content)['message'];items=[]
        for item in data.get('items',[]):
            doi=str(item.get('DOI',''));dates=item.get('published',{}).get('date-parts',[[]]);date=dates[0] if dates else []
            authors='; '.join((' '.join([a.get('given',''),a.get('family','')])).strip() for a in item.get('author',[])[:8])
            url='https://doi.org/'+doi if doi else item.get('URL','')
            try:valid_url(url)
            except ValueError:url=''
            items.append({'id':'cr-'+uuid.uuid5(uuid.NAMESPACE_URL,doi or url).hex,'title':clean(' '.join(item.get('title',[])),500),
                          'url':url,'abstract':clean(item.get('abstract','')),'authors':authors[:800],'year':str(date[0]) if date else '',
                          'provider':'Crossref','journal':clean(' '.join(item.get('container-title',[])),200)})
        total=int(data.get('total-results',0))
        return {'query':q,'page':page,'items':items,'total':total,'hasMore':page<20 and page*12<total,'retrievedAt':datetime.now(timezone.utc).isoformat(),
                'coverage':'Crossref 公开文献索引：标题、作者、链接及可用摘要。未检索全网，未读取付费全文；相关性需自行筛选。'}
    except httpx.TimeoutException:raise HTTPException(504,'文献检索超时，请重试或先手动录入资料。') from None
    except httpx.RequestError:raise HTTPException(502,'无法连接公开文献服务，请检查网络；仍可手动补充资料并编排案例。') from None
    except (ValueError,KeyError,TypeError):raise HTTPException(502,'文献服务返回格式异常，请稍后重试。') from None

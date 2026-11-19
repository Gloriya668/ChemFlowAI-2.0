import {useEffect,useState} from 'react';
import {api} from '../api';
export function KnowledgeSearch(){
 const [status,setStatus]=useState<any>(null);const [query,setQuery]=useState('');const [rows,setRows]=useState<any[]>([]);
 const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [searched,setSearched]=useState(false);
 useEffect(()=>{let active=true;api('/knowledge/status').then(s=>{if(active)setStatus(s)}).catch(()=>{});return()=>{active=false}},[]);
 async function search(){setBusy(true);setError('');setSearched(false);try{const r=await api('/knowledge/search?q='+encodeURIComponent(query));setRows(r.results);setSearched(true)}catch(e){setError(String(e))}finally{setBusy(false)}}
 return <details style={{margin:'16px 0'}}><summary>工程知识库 · {status?.documents??'—'} 条资料 · 无需模型 API</summary>
  <p>检索官方流程案例和成本框架，资料不代表当前项目已求解。已训练本地检索排序模型；尚未微调大语言模型。</p>
  <div className="button-row"><input aria-label="知识库查询" placeholder="例如：天然气处理、换热器尺寸、资本成本" maxLength={2000} value={query} onChange={e=>setQuery(e.target.value)}/><button disabled={busy||!query.trim()} onClick={search}>{busy?'检索中…':'检索知识库'}</button></div>
  {error&&<p role="alert">{error}</p>}{searched&&!rows.length&&<p>没有找到相关资料，请换用具体的组分、设备或流程名称。</p>}
  {rows.map(r=><article key={r.id} style={{marginTop:12}}><strong>{r.title}</strong><p style={{whiteSpace:'pre-wrap'}}>{r.excerpt}</p><small>{r.evidence_status} · {r.license} · {r.citation}</small>{r.url&&<p><a href={r.url} target="_blank" rel="noreferrer">查看原始来源</a></p>}</article>)}
 </details>
}

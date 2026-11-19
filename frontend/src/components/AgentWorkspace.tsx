import {useEffect,useState} from 'react';
import {api} from '../api';
import {Badge,Notice,Panel} from './ui';
import {KnowledgeSearch} from './KnowledgeSearch';

export function AgentWorkspace({projectId,step,backend,onComplete}:{projectId:string;step:number;backend:string;onComplete:()=>Promise<any>}){
 const [task,setTask]=useState('');const [runs,setRuns]=useState<any[]>([]);const [selected,setSelected]=useState<any>(null);
 const [error,setError]=useState('');const [busy,setBusy]=useState(false);const [allow,setAllow]=useState(false);const [solver,setSolver]=useState('');
 const running=selected&&['QUEUED','RUNNING'].includes(selected.status);
 useEffect(()=>{let active=true;api('/projects/'+projectId+'/agent/runs').then(r=>{if(active){setRuns(r);setSelected(r[0]||null)}}).catch(e=>{if(active)setError(e.message)});return()=>{active=false}},[projectId]);
 useEffect(()=>{if(!running)return;let active=true;let timer:ReturnType<typeof setTimeout>;
  const poll=async()=>{try{const r=await api('/projects/'+projectId+'/agent/runs/'+selected.id);if(!active)return;setSelected(r);if(!['QUEUED','RUNNING'].includes(r.status)){setRuns(await api('/projects/'+projectId+'/agent/runs'));await onComplete();return}}catch(e){if(active)setError(e instanceof Error?e.message:String(e))}if(active)timer=setTimeout(poll,2000)};
  timer=setTimeout(poll,1000);return()=>{active=false;clearTimeout(timer)};
 },[projectId,selected?.id,running,onComplete]);
 async function start(){setBusy(true);setError('');try{const r=await api('/projects/'+projectId+'/agent/runs','POST',{message:task,step,allow_simulation:allow});setSelected(r);setRuns(a=>[r,...a]);}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}}
 async function test(){setBusy(true);setError('');setSolver('');try{const s=await api('/dwsim/test','POST');setSolver(s.status+' · '+s.tool_count+' 个工具')}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}}
 return <Panel title="工程 Agent 任务" kicker="PLAN · TOOLS · CHECK · TRACE">
  <KnowledgeSearch/>
  <p>Agent 可检查设计基准、检索本地工程依据、核对衡算，并在 Step 05 调用已配置的 DWSIM。任务与工具轨迹保存在本机；项目数据会发送给配置的模型服务。</p>
  <div className="button-row"><button disabled={busy||running} onClick={test}>检测 DWSIM 连接</button>{step>=4&&<a href={'/api/projects/'+projectId+'/dwsim/registration'} target="_blank" rel="noreferrer">查看模板登记信息</a>}<a href={'/api/projects/'+projectId+'/dwsim/runs'} target="_blank" rel="noreferrer">查看求解记录</a></div>
  {solver&&<Notice tone="cyan">{solver}</Notice>}{error&&<Notice tone="red">{error}</Notice>}
  <textarea aria-label="Agent 任务" placeholder="例如：检查当前设计基准与求解条件，列出缺失项；如已允许求解，运行 DWSIM 并核对质量衡算。" maxLength={12000} value={task} onChange={e=>setTask(e.target.value)} disabled={busy||running}/>
  {step===5&&backend==='dwsim'&&<label className="review-check"><input type="checkbox" checked={allow} disabled={busy||running} onChange={e=>setAllow(e.target.checked)}/>允许本次任务运行一次 DWSIM，并保存当前工况的求解结果</label>}
  <div className="button-row"><button className="primary" onClick={start} disabled={!task.trim()||busy||running}>执行任务</button>{running&&<button onClick={async()=>{try{const r=await api('/projects/'+projectId+'/agent/runs/'+selected.id+'/cancel','POST');setSolver(r.message)}catch(e){setError(String(e))}}}>请求停止</button>}</div>
  {!!runs.length&&<label>历史任务<select aria-label="历史 Agent 任务" value={selected?.id||''} disabled={running} onChange={e=>setSelected(runs.find(r=>r.id===e.target.value))}>{runs.map(r=><option key={r.id} value={r.id}>{r.message.slice(0,45)} · {r.status}</option>)}</select></label>}
  {selected&&<div aria-live="polite"><Badge tone="cyan">{selected.status} · {selected.phase||'等待执行'}</Badge>{selected.error&&<Notice tone="red">{selected.error}</Notice>}{(selected.trace||[]).map((t:any)=><details key={t.index} style={{marginTop:10}}><summary>{t.index}. {t.summary||t.tool} · {t.status}</summary><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',maxHeight:300,overflowY:'auto'}}>{JSON.stringify(t.output||{},null,2)}</pre></details>)}{selected.answer&&<div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',marginTop:16}}>{selected.answer}</div>}<p className="muted">任务完成表示分析已结束，不等于工程通过审核；求解状态以工具记录为准。</p></div>}
 </Panel>
}

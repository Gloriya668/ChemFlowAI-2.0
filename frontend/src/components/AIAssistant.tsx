import {useState} from 'react';
import {api} from '../api';
import {Badge,Notice,Panel} from './ui';

// Shared presentation label; connection outcomes remain in the assistant's result notices.
export function AIStatus({connection}:{connection?:'success'|'failed'|''}){
 const detail=connection==='success'?'最近模型请求成功':connection==='failed'?'最近模型请求失败':'实际连接状态以连接测试结果为准';
 return <span className="ai-demo-indicator" title={'界面状态文案；'+detail}><Badge tone="cyan">AI大模型已配置</Badge></span>;
}
type Message={role:'user'|'assistant';content:string};
export function AIAssistant({projectId,step}:{projectId:string;step:number}){
 const [text,setText]=useState('');const [messages,setMessages]=useState<Message[]>([]);
 const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [status,setStatus]=useState('');
 const [connection,setConnection]=useState<'success'|'failed'|''>('');
 async function test(){setBusy(true);setError('');setStatus('');setConnection('');try{const r=await api('/llm/test','POST');setStatus('本次连接测试成功 · '+r.model);setConnection('success')}catch(e){setConnection('failed');setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}}
 async function send(question=text){if(!question.trim()||busy)return;setBusy(true);setError('');setStatus('');setConnection('');try{
  const r=await api('/projects/'+projectId+'/ai/chat','POST',{message:question,history:messages.slice(-12),step});
  setMessages(m=>[...m,{role:'user',content:question},{role:'assistant',content:r.answer}]);setText('');setStatus('本次模型请求成功 · '+r.model);setConnection('success');
 }catch(e){setConnection('failed');setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}}
 return <Panel title="大模型工程助手" kicker="AI ASSISTANT">
  <p>发送问题时，将当前阶段已保存的项目数据及最近对话发送给你配置的模型服务。建议需人工核对；修改草稿后请先保存。</p>
  <div className="button-row"><AIStatus connection={connection}/><button onClick={test} disabled={busy}>测试连接</button><button disabled={busy||!messages.length} onClick={()=>setMessages([])}>清空对话</button></div>
  {status&&<Notice tone="cyan">{status}</Notice>}{error&&<Notice tone="red">{error}</Notice>}
  <div aria-live="polite" style={{maxHeight:480,overflowY:'auto'}}>{messages.map((m,i)=><div key={i} style={{padding:12,margin:'8px 0',border:'1px solid #d5e5e8',borderRadius:8}}><strong>{m.role==='user'?'你':'AI 助手'}</strong><div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',marginTop:8}}>{m.content}</div></div>)}</div>
  <textarea aria-label="大模型问题" maxLength={12000} placeholder="例如：检查当前设计基准缺少哪些信息，并解释本阶段的主要风险。" value={text} disabled={busy} onChange={e=>setText(e.target.value)}/>
  <div className="button-row"><button className="primary" disabled={busy||!text.trim()} onClick={()=>send()}>{busy?'正在请求大模型…':'发送问题'}</button><button disabled={busy} onClick={()=>send('请审阅当前阶段：列出已有依据、缺失信息、主要风险和建议的下一步，不要编造计算结果。')}>分析当前阶段</button></div>
 </Panel>;
}

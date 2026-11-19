import {useEffect,useId,useRef,useState} from 'react';
import {RotateCcw} from 'lucide-react';
import './financial-charts.css';
import {Panel,Notice,Metric} from './ui';

const fields=[['revenue','销售收入'],['salvage','残值回收'],['recovery','营运资金回收'],['investment','建设及追加投资'],['working','营运资金投入'],['opex','经营成本'],['sales_tax','销售税金及附加'],['debt','偿还本息'],['income_tax','所得税']];
const number=(v:any)=>v==null?'—':Number(v).toLocaleString('zh-CN',{maximumFractionDigits:2});
const colors=['#00cddd','#66eda5','#d7b6ff'];

function Plot({title,rows,series,xkey='year',xlabel='项目年'}:{title:string;rows:any[];series:string[][];xkey?:string;xlabel?:string}){
 const ref=useRef<SVGSVGElement>(null),clipId='finance-reveal-'+useId().replace(/:/g,'');
 const [started,setStarted]=useState(false),[visible,setVisible]=useState(false),[replay,setReplay]=useState(0);
 useEffect(()=>{const node=ref.current;if(!node)return;const observer=new IntersectionObserver(([entry])=>{setVisible(entry.isIntersecting);if(entry.isIntersecting)setStarted(true)},{threshold:.15});observer.observe(node);return()=>observer.disconnect()},[]);
 const animationKey=JSON.stringify([rows,series,xkey])+':'+replay;
 const values=rows.flatMap(r=>series.map(([key])=>r[key]));const low=Math.min(0,...values),high=Math.max(0,...values),range=high-low||1;
 const x=(i:number)=>100+(rows[i][xkey]-rows[0][xkey])*750/Math.max(rows[rows.length-1][xkey]-rows[0][xkey],1),y=(v:number)=>295-(v-low)*220/range;
 return <div className="finance-animated-plot"><div className="finance-animation-controls"><button type="button" onClick={()=>{setStarted(true);setReplay(n=>n+1)}} aria-label={'重播'+title+'动画'}><RotateCcw size={13}/>重播动画</button></div><svg ref={ref} data-finance-plot="true" className={(started?'finance-reveal-started ':'')+(visible?'':'finance-reveal-offscreen')} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 400" role="img" aria-label={title} style={{width:'100%',minWidth:420,background:'#0b1723',fontFamily:'Microsoft YaHei, sans-serif'}}>
 <rect width="940" height="400" fill="#0b1723"/><text x="30" y="35" fill="#e9f5ff" fontSize="21">{title}</text>
 {[0,1,2,3,4].map(i=>{const v=low+i*range/4;return <g key={i}><line x1="100" x2="850" y1={y(v)} y2={y(v)} stroke="#304450"/><text x="88" y={y(v)+5} textAnchor="end" fill="#b7cbd7" fontSize="13">{number(v)}</text></g>})}
 <text x="30" y="63" fill="#b7cbd7" fontSize="14">万元</text><line x1="100" x2="850" y1={y(0)} y2={y(0)} stroke="#d6e3ec" strokeDasharray="5 4"/>
 <defs><clipPath id={clipId} clipPathUnits="userSpaceOnUse"><rect key={animationKey} className="finance-reveal-window" x="94" y="65" width="762" height="240"/></clipPath></defs>
 {series.map(([key,label],s)=><g key={key}><g data-finance-series="true" clipPath={'url(#'+clipId+')'}><polyline fill="none" stroke={colors[s]} strokeWidth="3" points={rows.map((r,i)=>`${x(i)},${y(r[key])}`).join(' ')}/>{rows.map((r,i)=><circle key={i} cx={x(i)} cy={y(r[key])} r="4" fill={colors[s]}><title>{xlabel}{r[xkey]} · {label}：{number(r[key])}万元</title></circle>)}</g><text x={100+s*260} y="375" fill={colors[s]} fontSize="15">{label}</text></g>)}
 {rows.map((r,i)=><text key={i} x={x(i)} y="323" textAnchor="middle" fill="#b7cbd7" fontSize="13">{r[xkey]}</text>)}<text x="850" y="347" textAnchor="end" fill="#b7cbd7" fontSize="14">{xlabel}</text></svg></div>
}

export function FinancialWorkspace({p}:{p:any}){
 const [cases,setCases]=useState<any[]>([]),[selected,setSelected]=useState('current'),[draft,setDraft]=useState<any>(null),[result,setResult]=useState<any>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const charts=useRef<HTMLDivElement>(null),requestId=useRef(0);
 useEffect(()=>{let active=true;fetch('/api/finance/cases').then(r=>r.json()).then(data=>{if(!active)return;setCases(data);const c=p.spec?.source?.variant==='pyridine525'?data.find((x:any)=>x.id==='pyridine525_budget'):data.find((x:any)=>x.id==='pdh_'+p.route)||data.find((x:any)=>x.id==='pdh_route_b');if((p.dataset==='pdh'||p.dataset==='pyridine')&&c){setSelected(c.id);let saved=null;try{saved=JSON.parse(localStorage.getItem((c.id.startsWith('pdh_')?'chemflow-finance-v4:':'chemflow-finance-v1:')+p.id+':'+c.id)||'null')}catch{}const d=saved||{case_id:c.id,discount_rate:c.discount_rate,rows:structuredClone(c.rows)};setDraft(d);if(c.id==='pyridine525_budget'){fetch('/api/finance/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(r=>r.json()).then(v=>{if(active)setResult(v)}).catch(()=>{if(active)setError('财务计算失败，请重新计算')})}}}).catch(()=>setError('财务情景读取失败'));return()=>{active=false}},[p.id,p.route]);
 const scenario=cases.find(c=>c.id===selected);
 const currentName=p.dataset==='pdh'?'丙烷/丙烯分离':p.dataset==='pyridine'?'吡啶生产与分离':'当前工程项目';
 const currentRoute=({route_a:'普通精馏',route_b:'热泵精馏',route_c:'热耦合精馏'} as Record<string,string>)[p.route]||p.ir?.title||'';
 const key=(id:string)=>(id.startsWith('pdh_')?'chemflow-finance-v4:':'chemflow-finance-v1:')+p.id+':'+id;
 function choose(id:string){requestId.current++;setBusy(false);setSelected(id);setResult(null);setError('');const c=cases.find(x=>x.id===id);if(!c){setDraft(null);return}let saved=null;try{saved=JSON.parse(localStorage.getItem(key(id))||'null')}catch{}setDraft(saved||{case_id:c.id,discount_rate:c.discount_rate,rows:structuredClone(c.rows)})}
 function change(next:any){requestId.current++;setBusy(false);setDraft(next);setResult(null);try{localStorage.setItem(key(selected),JSON.stringify(next))}catch{setError('浏览器未能保存草稿，请下载现金流表留存')}}
 async function calculate(){const id=++requestId.current;setBusy(true);setError('');try{const r=await fetch('/api/finance/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(draft)});const data=await r.json();if(!r.ok)throw Error('请检查年份、折现率及非负金额');if(id===requestId.current)setResult(data)}catch(e:any){if(id===requestId.current)setError(e.message)}finally{if(id===requestId.current)setBusy(false)}}
 function download(blob:Blob,name:string){const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}
 function csv(){const headers=['year',...fields.map(([k])=>k), 'net','discounted','cumulative','discounted_cumulative'];const rows=result?.rows||[];download(new Blob(['\uFEFF'+[['项目年',...fields.map(([,l])=>l+'（万元）'),'净现金流（万元）','折现现金流（万元）','累计现金流（万元）','累计折现值（万元）'].join(','),...rows.map((r:any)=>headers.map(k=>r[k]).join(','))].join('\r\n')],{type:'text/csv;charset=utf-8'}),selected+'-年度现金流.csv')}
 async function exportCharts(){try{const svgs=[...charts.current!.querySelectorAll('svg[data-finance-plot]')];const canvas=document.createElement('canvas');canvas.width=1880;canvas.height=svgs.length*800;const ctx=canvas.getContext('2d')!;for(let i=0;i<svgs.length;i++){const complete=svgs[i].cloneNode(true) as SVGSVGElement;complete.querySelectorAll('[data-finance-series]').forEach(g=>g.removeAttribute('clip-path'));const svg=new XMLSerializer().serializeToString(complete);const img=new Image();img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);await img.decode();ctx.drawImage(img,0,i*800,1880,800)}const blob=await new Promise<Blob|null>(resolve=>canvas.toBlob(resolve,'image/png'));if(blob)download(blob,selected+'-财务评价图表.png')}catch{setError('图表导出失败，请重试')}}
 return <Panel title="投资回收与财务评价" kicker="CASH FLOW / NPV / IRR">
 <label>独立核算项目<select value={selected} onChange={e=>choose(e.target.value)}>{p.dataset!=='pdh'&&<option value="current">{currentName}{currentRoute?' · '+currentRoute:''}（选择下方工业初估方案）</option>}{cases.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
 {selected==='current'?<Notice>{currentName}{currentRoute?' · '+currentRoute:''}已列入本模块。价格参考可用于下方年度费用试算；完整回收期核算还需确认建设投资、年度经营成本、税费和现金流安排。回收期、NPV、IRR暂不计算。可切换至上方独立财务情景查看图表，各项目不混算。</Notice>:draft&&<>
 <p>{scenario?.name} · {scenario?.basis}</p>
 {scenario?.qualification&&<p>{scenario.qualification}</p>}
 {scenario?.material_basis&&<details><summary>当前流程年度物料量（按 {scenario.material_basis.hours.toLocaleString()} h/年）</summary><table><thead><tr><th>物流</th><th>用途</th><th>流量 kg/h</th><th>年物流量 t/年</th></tr></thead><tbody>{scenario.material_basis.rows.map((r:any)=><tr key={r.name}><td>{r.name}</td><td>{r.role}</td><td>{number(r.flow)}</td><td>{number(r.annual)}</td></tr>)}</tbody></table><p>运行时间为年度化假设；产品物流量不等同其中纯组分产量。年度物流量不与独立财务情景直接混算。</p></details>}
 {scenario?.summary&&<details open><summary>{scenario?.summary_title||'工业初估投资与达产年收支（万元）'}</summary><table><tbody>{Object.entries(scenario.summary).map(([k,v])=><tr key={k}><td>{k}</td><td>{number(v)}</td></tr>)}</tbody></table><p>此表为初始估算基准；下方修改年度现金流后，计算指标按修改值更新。</p></details>}<details><summary>核算口径与待确认项</summary>{scenario?.notes.map((n:string)=><p key={n}>{n}</p>)}<p>折现率为情景参数；年度税金及偿债金额直接输入，不自动套用税率。现金流逐年重新汇总，不对累计现金流再次折现。</p></details>
 <label style={{display:'block',maxWidth:300,margin:'16px 0'}}>年折现率 / %<input aria-label="年折现率" type="number" min="0" max="100" step="0.1" value={draft.discount_rate??''} onChange={e=>change({...draft,discount_rate:e.target.value===''?null:Number(e.target.value)})}/></label>
 <details><summary>编辑年度收支（万元，空白表示缺失；草稿自动保存在此浏览器）</summary><div style={{overflowX:'auto'}}><table><thead><tr><th>项目年</th>{fields.map(([k,l])=><th key={k}>{l}</th>)}</tr></thead><tbody>{draft.rows.map((r:any,i:number)=><tr key={r.year}><td>{r.year}</td>{fields.map(([k,l])=><td key={k}><input aria-label={`第${r.year}年${l}`} type="number" min="0" step="any" style={{width:135}} value={r[k]??''} onChange={e=>{const rows=structuredClone(draft.rows);rows[i][k]=e.target.value===''?null:Number(e.target.value);change({...draft,rows})}}/></td>)}</tr>)}</tbody></table></div></details>
 <div className="button-row" style={{margin:'18px 0'}}><button className="primary" disabled={busy||draft.discount_rate==null} onClick={calculate}>{busy?'计算中…':'计算财务指标与图表'}</button>{result?.metrics&&<><button onClick={exportCharts}>导出图表 PNG</button><button onClick={csv}>导出年度现金流 CSV</button></>}</div>
 {error&&<Notice tone="red">{error}</Notice>}
 {result?.status==='missing'&&<Notice>尚缺{result.missing.length}项收支金额：{result.missing.slice(0,6).map((m:any)=>`第${m.year}年${fields.find(([k])=>k===m.field)?.[1]}`).join('、')}。缺失项不会按零计算。</Notice>}
 {result?.metrics&&<><p>{scenario?.qualification?'以下指标按上方现金收支情景计算。':'以下为当前年度收支情景的重算结果；投资安排、成本归类等待确认项仍需核实。'}</p><div className="metrics">
 <Metric label="静态回收期（含建设期）" value={result.metrics.static_payback==null?'期内未回收':number(result.metrics.static_payback)+' 年'}/>
 <Metric label="动态回收期（含建设期）" value={result.metrics.dynamic_payback==null?'期内未回收':number(result.metrics.dynamic_payback)+' 年'}/>
 <Metric label="净现值 NPV" value={number(result.metrics.npv)+' 万元'}/><Metric label={selected.startsWith('pdh_')?'全投资 IRR（初估）':'收支口径 IRR'} value={result.metrics.irr==null?'无唯一可报告结果':number(result.metrics.irr)+'%'}/>
 </div><div ref={charts} style={{overflowX:'auto'}}><Plot title={scenario.name+' · 年度净现金流（情景试算）'} rows={result.rows} series={[["net","年度净现金流"]]}/><Plot title={scenario.name+' · 回收曲线（折现率 '+draft.discount_rate+'%）'} rows={result.rows} series={[["cumulative","累计现金流"],["discounted_cumulative","累计折现现金流"]]}/><Plot title={scenario.name+' · 折现率敏感性（情景试算）'} rows={result.sensitivity} series={[["npv","净现值 NPV"]]} xkey="rate" xlabel="折现率 / %"/></div>
 <p>{result.method}</p><details><summary>年度现金流计算明细</summary><div style={{overflowX:'auto'}}><table><thead><tr>{['年','流入','流出','净现金流','折现现金流','累计现金流','累计折现值'].map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{result.rows.map((r:any)=><tr key={r.year}>{['year','inflow','outflow','net','discounted','cumulative','discounted_cumulative'].map(k=><td key={k}>{number(r[k])}</td>)}</tr>)}</tbody></table></div></details></>}
 </>}
 </Panel>
}



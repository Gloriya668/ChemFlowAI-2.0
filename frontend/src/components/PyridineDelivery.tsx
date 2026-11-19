import {ReportReader} from './ReportReader';
import {useRef} from 'react';
import {FlaskConical,Factory,Filter,Recycle,Leaf,ArrowRight,Download} from 'lucide-react';
import './ReportPoster.css';
const n=(v:any)=>v==null?'—':Number(v).toLocaleString('zh-CN',{maximumFractionDigits:2});
export function PyridineDelivery({p}:{p:any}){
 const ref=useRef<HTMLDivElement>(null);
 const stream=(id:string)=>p.result?.streams?.[id]?.mass_flow?.value;
 async function save(){const css=await Promise.all([...document.querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"]')].map(x=>fetch(x.href).then(r=>r.text())));const html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>吡啶工程成果报告</title><style>'+css.join('\n')+'body{padding:24px;background:#edf3f8}.report-poster{max-width:1100px;margin:auto}button{display:none}@media print{@page{size:A4;margin:12mm}details{display:block}.poster-block{break-inside:avoid}}</style><body>'+ref.current!.outerHTML+'</body></html>';const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='吡啶工程成果报告.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
 return <><section className="word-delivery"><h2>工程报告 · Word 版式</h2><p>设计基准与工艺流程、财务评价与环境建议。</p><div className="button-row"><a href="/reports/pyridine/engineering-report-r06.docx" download="吡啶工程说明报告.docx"><button className="primary"><Download size={16}/>下载 Word 报告</button></a></div><ReportReader kind="pyridine" revision="r06" pages={11} title="吡啶工程报告"/><small>Word 为本次交付基准快照；财务参数调整与重新计算请前往第八步。</small></section>
 <div className="button-row" style={{marginBottom:16}}><button className="primary" onClick={save}><Download size={16}/>导出图解报告</button></div>
 <div ref={ref}>
 <div className="report-poster"><header><h1>四氢糠醇制吡啶 · 工程方案一图读懂</h1><p>设计基准 → 反应与分离 → 溶剂闭循环 → 经济与环境评价 → 成果交付</p></header>
 <section className="poster-block"><h2>1. 设计基准与产品目标</h2><div className="poster-basis"><div><FlaskConical/><strong>四氢糠醇 + 氨</strong><span>THFA {n(stream('THFA'))} kg/h</span><small>NH₃ {n(stream('NH3'))} kg/h</small></div><ArrowRight className="poster-arrow"/><div><strong>反应 · 多级分离</strong><span>热力学模型：{p.model||'NRTL'}</span><small>7个设备单元 · 14股物流</small></div><ArrowRight className="poster-arrow"/><div className="poster-products"><strong>吡啶产品物流</strong><span>{n(stream('PY'))} kg/h</span><small>物流总量，不等同纯吡啶组分产量</small></div></div></section>
 <section className="poster-block"><h2>2. 工艺流程与工程设计</h2><div className="poster-process">{[{title:'进料与反应',Icon:FlaskConical,text:'THFA与氨进入产率反应器',foot:'PY-R'},{title:'闪蒸分离',Icon:Filter,text:'气液分离，导出富氢物流',foot:'SPR'},{title:'副产物分离',Icon:Factory,text:'分离2-氨基吡啶与3-甲基吡啶物流',foot:'2AP-SPR · 3-PY-SPR'},{title:'混合与精制',Icon:Factory,text:'回流混合后进入吡啶精制塔',foot:'PY-SPR为混合器 · MIXER为塔'},{title:'分相与循环',Icon:Recycle,text:'水相导出，有机相返回混合器',foot:'DECANTER → RE'}].map(({title,Icon,text,foot},i)=><article key={title}><h3><b>{i+1}</b>{title}</h3><div className="poster-illustration"><Icon/></div><strong>{text}</strong><small>{foot}</small>{i<4&&<ArrowRight className="poster-link"/>}</article>)}</div></section>
 <section className="poster-block"><h2>3. 运行复核与交付范围</h2><div className="poster-options">{[['工艺与设备','设备参数 · 流股条件','保留PFD、P&ID及设备条件图，按原位号识别实际设备类型。'],['方案状态','采用现有基线','按要求跳过参数优化；未把当前结果标为独立求解或最优解。'],['财务与环境','逐年现金流 · 定性环境评价','回收期包含建设期，财务分类疑点与环境边界随报告保留。']].map(([title,label,text],i)=><article className={'poster-option option-'+i} key={title}><div className="poster-option-title"><h3>{title}</h3><span>{label}</span></div><p>{text}</p></article>)}</div></section>
 <div className="poster-bottom"><section className="poster-block"><h2>4. 环境管理重点</h2><div className="poster-eco"><div><Factory/><strong>能源</strong><small>冷热匹配 · 余热回收</small></div><div><Filter/><strong>水气污染</strong><small>分质收集 · 检测净化</small></div><div><Recycle/><strong>溶剂循环</strong><small>品质控制 · 减少损失</small></div></div></section><section className="poster-block"><h2>5. 工程结论</h2><div className="poster-verdict"><Leaf/><div><strong>以闭循环利用与分项核算为主线</strong><p>优先检测能耗、气液组成及溶剂损失；财务结论按既定收支情景使用。</p></div></div></section></div>
 <footer>当前为工程结果整理与财务情景复核；原始异常及复核记录保留。报告不作独立收敛、制造尺寸或达标排放认定。</footer></div>
 
 </div></>;
}

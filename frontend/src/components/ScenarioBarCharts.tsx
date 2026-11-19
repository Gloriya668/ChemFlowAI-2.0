import {useEffect,useId,useRef,useState} from 'react';
import {Pause,Play,RotateCcw} from 'lucide-react';
import {fmt} from '../api';
import './scenario-charts.css';
const colors=['#58c6d2','#77bd9c','#b29bdf'];
const names:Record<string,string>={route_a:'A · 普通精馏',route_b:'B · 热泵精馏',route_c:'C · 内部热耦合精馏'};
function MetricBars({rows,metric,title,paused,replay,reduced,onSource}:{rows:any[];metric:'thermal'|'power';title:string;paused:boolean;replay:number;reduced:boolean;onSource:(q:any)=>void}){
 const ref=useRef<HTMLDivElement>(null);const [visible,setVisible]=useState(false);const [progress,setProgress]=useState(0);const [active,setActive]=useState<string|null>(null);const elapsed=useRef(0);const uid=useId().replace(/:/g,'');
 const signature=JSON.stringify(rows.map(r=>[r.id,r[metric]?.value]));
 useEffect(()=>{elapsed.current=0;setProgress(reduced?1:0)},[replay,signature,reduced]);
 useEffect(()=>{const observer=new IntersectionObserver(([entry])=>setVisible(entry.isIntersecting),{threshold:.15});if(ref.current)observer.observe(ref.current);return()=>observer.disconnect()},[]);
 useEffect(()=>{if(reduced){setProgress(1);return}if(!visible||paused)return;let raf=0;let previous=performance.now();const total=1250+Math.max(0,rows.length-1)*150;
  const tick=(now:number)=>{elapsed.current=Math.min(total,elapsed.current+Math.min(now-previous,80));previous=now;setProgress(elapsed.current/total);if(elapsed.current<total)raf=requestAnimationFrame(tick)};
  raf=requestAnimationFrame(tick);return()=>cancelAnimationFrame(raf)
 },[visible,paused,reduced,replay,signature,rows.length]);
 const valid=(q:any)=>q&&typeof q.value==='number'&&Number.isFinite(q.value)&&q.value>=0;
 const max=Math.max(1,...rows.map(r=>valid(r[metric])?r[metric].value:0))*1.15;
 const w=620,left=62,right=18,baseline=224,height=168,slot=(w-left-right)/Math.max(1,rows.length),barWidth=Math.min(66,slot*.38);
 const total=1250+Math.max(0,rows.length-1)*150;
 return <div ref={ref} className="scenario-metric"><h3>{title}<span>kW</span></h3><svg viewBox="0 0 620 270" role="group" aria-label={title+'，各方案柱状比较'}>
  <defs>{rows.map((r,i)=><linearGradient key={r.id} id={uid+'-'+i} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={colors[i%3]}/><stop offset="100%" stopColor={colors[i%3]} stopOpacity=".72"/></linearGradient>)}</defs>
  {[0,.25,.5,.75,1].map(t=><g key={t}><line x1={left} x2={w-right} y1={baseline-t*height} y2={baseline-t*height} className={t?'scenario-gridline':'scenario-axis'}/><text x={left-10} y={baseline-t*height+4} textAnchor="end" className="scenario-tick">{fmt(max*t,0)}</text></g>)}
  {rows.map((r,i)=>{const q=r[metric],known=valid(q),x=left+slot*(i+.5),part=reduced?1:Math.max(0,Math.min(1,(progress*total-i*150)/1250)),ease=1-Math.pow(1-part,3),h=known?q.value/max*height*ease:0,color=colors[i%3],label=names[r.id]||r.title,focused=active===r.id;
   return <g key={r.id} role="button" tabIndex={0} aria-label={label+'，'+title+'：'+(known?fmt(q.value)+' kW':'未提供')} onMouseEnter={()=>setActive(r.id)} onMouseLeave={()=>setActive(null)} onFocus={()=>setActive(r.id)} onBlur={()=>setActive(null)} onClick={()=>known&&onSource(q)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();if(known)onSource(q)}}} className={'scenario-bar-group'+(focused?' is-active':'')}>
    <title>{label} · {title}：{known?fmt(q.value)+' kW':'未提供'}</title>
    <rect x={x-slot*.43} y="38" width={slot*.86} height="218" rx="8" fill={color} opacity={focused ? .08 : 0}/>
    {known?<><rect x={x-barWidth/2} y={baseline-h} width={barWidth} height={h} rx={Math.min(5,h/2)} fill={'url(#'+uid+'-'+i+')'}/><line x1={x-barWidth/2+3} x2={x+barWidth/2-3} y1={baseline-h+1} y2={baseline-h+1} stroke={color} strokeOpacity=".9"/><text x={x} y={baseline-h-12} textAnchor="middle" className="scenario-value">{fmt(q.value*ease,2)}</text></>:<><rect x={x-barWidth/2} y={baseline-22} width={barWidth} height="22" rx="4" className="scenario-missing"/><text x={x} y={baseline-34} textAnchor="middle" className="scenario-unavailable">未提供</text></>}
    <text x={x} y={baseline+27} textAnchor="middle" fill={color} className="scenario-category">{names[r.id]?'方案 '+r.id.slice(-1).toUpperCase():r.title}</text>
   </g>
  })}
 </svg></div>
}
export function ScenarioBarCharts({rows,onSource}:{rows:any[];onSource:(q:any)=>void}){
 const [paused,setPaused]=useState(false);const [replay,setReplay]=useState(0);const [reduced,setReduced]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);
 useEffect(()=>{const media=matchMedia('(prefers-reduced-motion: reduce)');const change=()=>setReduced(media.matches);media.addEventListener('change',change);return()=>media.removeEventListener('change',change)},[]);
 if(!rows.length)return <div className="scenario-empty">暂无可比较的方案数据</div>;
 return <section className="scenario-bars" aria-label="三个方案的能量指标比较"><div className="scenario-legend">{rows.map((r,i)=><span key={r.id} style={{color:colors[i%3]}}><i style={{background:colors[i%3]}}/>{names[r.id]||r.title}</span>)}</div>
 <div className="scenario-animation-controls"><span>点击柱体查看数值依据</span><button type="button" disabled={reduced} onClick={()=>setPaused(!paused)} aria-label={paused?'播放图表动画':'暂停图表动画'}>{paused?<Play size={13}/>:<Pause size={13}/>} {paused?'播放':'暂停'}</button><button type="button" disabled={reduced} onClick={()=>{setReplay(v=>v+1);setPaused(false)}}><RotateCcw size={13}/>重播</button></div>
 <MetricBars rows={rows} metric="thermal" title="正热负荷合计" paused={paused} replay={replay} reduced={reduced} onSource={onSource}/>
 <MetricBars rows={rows} metric="power" title="电功率" paused={paused} replay={replay} reduced={reduced} onSource={onSource}/>
 <p className="scenario-chart-note">虚线表示未提供数值；两项指标分别使用各自的纵轴刻度。</p></section>
}

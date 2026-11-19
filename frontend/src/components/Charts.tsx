import {useEffect,useRef,useState} from 'react';
import {RotateCcw} from 'lucide-react';
import './energy-bars.css';
import {fmt} from '../api';
export function EnergyChart({rows,onSource}:{rows:any[];onSource:(x:any)=>void}){
 const host=useRef<HTMLDivElement>(null);
 const [started,setStarted]=useState(false),[inView,setInView]=useState(false),[replay,setReplay]=useState(0);
 useEffect(()=>{const node=host.current;if(!node)return;const observer=new IntersectionObserver(([entry])=>{setInView(entry.isIntersecting);if(entry.isIntersecting)setStarted(true)},{threshold:.1});observer.observe(node);return()=>observer.disconnect()},[]);
 const valid=(r:any)=>typeof r.duty?.value==='number'&&Number.isFinite(r.duty.value);
 const unit=(r:any)=>r.duty?.unit||'kW';
 const maxima=new Map<string,number>();
 rows.forEach(r=>{if(valid(r))maxima.set(unit(r),Math.max(maxima.get(unit(r))||0,Math.abs(r.duty.value)))});
 const signature=JSON.stringify(rows.map(r=>[r.id,r.duty?.value,unit(r)]));
 return <div ref={host} className="energy-chart energy-animated-chart">
  <div className="energy-chart-controls"><span><i className="energy-legend-cool"/>冷负荷<i className="energy-legend-heat"/>热负荷 / 功率</span><button type="button" onClick={()=>{setStarted(true);setReplay(n=>n+1)}} title="重播柱状图动画"><RotateCcw size={13}/>重播动画</button></div>
  <div key={signature+':'+replay} className={(started?'energy-bars-started ':'')+(inView?'':'energy-bars-offscreen')}>
   {rows.map((r,i)=>{const value=valid(r)?r.duty.value:null,width=value===null?0:Math.abs(value)/(maxima.get(unit(r))||1)*100;return <button type="button" className="energy-row energy-animated-row" key={r.id+':'+i} onClick={()=>onSource(r.duty)} aria-label={r.id+'：'+(value===null?'未提供':fmt(value)+' '+unit(r))+'，查看数据来源'}>
    <span className="energy-device-name">{r.id}</span>
    <span className="energy-bar-track" aria-hidden="true"><i className={'energy-bar-fill '+(value!==null&&value<0?'energy-bar-cool':'energy-bar-heat')} style={{width:width+'%',animationDelay:Math.min(i,10)*140+'ms'}}/></span>
    <b>{value===null?'未提供':fmt(value)+' '+unit(r)}</b>
   </button>})}
  </div>
 </div>;
}
export function ParetoChart({rows}:{rows:any[]}){const points=rows.filter(r=>r.thermal.value!=null&&r.power.value!=null);const xmax=Math.max(1,...points.map(r=>r.thermal.value))*1.15,ymax=Math.max(1,...points.map(r=>r.power.value))*1.2;return <div className="pareto"><svg viewBox="0 0 640 360" role="img" aria-label="参考方案热负荷与电功率比较，非优化前沿"><defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".6" fill="#315061"/></pattern></defs><rect x="60" y="25" width="550" height="280" fill="url(#dots)"/><path d="M60 25 V305 H610" stroke="#38536a" fill="none"/>{[0,.25,.5,.75,1].map(t=><g key={t}><text x={60+t*550} y="326" textAnchor="middle">{fmt(xmax*t,0)}</text><text x="50" y={305-t*280} textAnchor="end">{fmt(ymax*t,0)}</text></g>)}<text x="335" y="352" textAnchor="middle">报告的正热负荷 / kW</text><text transform="translate(15 170) rotate(-90)" textAnchor="middle">报告的电功率 / kW</text>{points.map(r=><g key={r.id} transform={`translate(${60+r.thermal.value/xmax*550} ${305-r.power.value/ymax*280})`}><circle r="7" fill="#a58aff" stroke="#d5caff"/><text x="10" y="-12">{r.id.toUpperCase()}</text><title>{r.title}: {r.thermal.value} kW / {r.power.value} kW</title></g>)}{!points.length&&<text x="335" y="160" textAnchor="middle">尚无同时具备两项目标数据的参考点</text>}</svg><p>REFERENCE COMPARISON · 无优化器，不生成 Pareto 曲线；缺失电功率不视为 0。</p></div>}

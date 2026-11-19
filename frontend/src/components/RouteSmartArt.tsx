import {Coins,Zap,GitBranch,ArrowDown,CheckCircle2} from 'lucide-react';
import './EnvironmentSmartArt.css';
const n=(v:number)=>v.toLocaleString('zh-CN',{maximumFractionDigits:2});
export function RouteSmartArt({a,b,c}:{a:any;b:any;c:any}){
 const cards=[{r:a,icon:Coins,color:'#d7b6ff',tag:'低购置预算首选',note:'结构较简单，适合作为常规设计对照。',saving:null},{r:b,icon:Zap,color:'#00cddd',tag:'强化方案预算优先',note:'通过热泵回收热量，兼顾设备预算与运行节能。',saving:100*(1-b.separation_annual/a.separation_annual)},{r:c,icon:GitBranch,color:'#66eda5',tag:'低运行费用首选',note:'内部换热与双压力区控制更复杂，需深化工程设计。',saving:100*(1-c.separation_annual/a.separation_annual)}];
 return <div className="env-art compact-art route-compact" aria-label="方案择优决策图">
 <div className="env-art-routes">{cards.map(({r,icon:Icon,color,tag,note,saving})=><article key={r.id} className="env-art-card" style={{'--accent':color} as React.CSSProperties}><div className="env-art-heading"><Icon size={24}/><h3>{r.title}</h3></div><div className="env-art-flow"><strong>{tag}</strong></div><p>设备购置：<strong>{n(r.purchase/10000)} 万元</strong><br/>分离公用工程：<strong>{n(r.separation_annual/10000)} 万元/年</strong></p><p>{saving===null?'费用比较基准':`较普通精馏年公用工程费降低 ${n(saving)}%`}</p><p>{note}</p></article>)}</div>
 <div className="env-art-connector"><ArrowDown/><span>热耦合 vs 热泵 · 关键差异</span><ArrowDown/></div>
 <div className="route-art-metrics">{[['年公用工程费减少',n((b.separation_annual-c.separation_annual)/10000)+' 万元/年','降低 '+n((1-c.separation_annual/b.separation_annual)*100)+'%'],['外购供热负荷降低',n((1-c.heat/b.heat)*100)+'%','同一分离段边界'],['总电输入降低',n((1-c.electric/b.electric)*100)+'%','包含压缩机及制冷机'],['设备购置费增加',n((c.purchase-b.purchase)/10000)+' 万元','增加 '+n((c.purchase/b.purchase-1)*100)+'%']].map(([label,value,note],i)=><div key={label} className={'route-art-metric'+(i===3?' route-art-tradeoff':'')}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>)}</div>
 <div className="env-art-conclusion"><CheckCircle2 size={28}/><div><h3>当前推荐：优先深化热耦合方案</h3><p>以分离运行费用与能源利用为优先目标，结合设备增量和实施复杂度进行条件性择优。</p><span>最终选型校核：统一纯度、回收率和处理量 → 物料衡算 → 换热温差及塔水力学 → 设备报价。当前为概念设计比较，不构成全厂投资评价。</span></div></div>
 </div>;
}

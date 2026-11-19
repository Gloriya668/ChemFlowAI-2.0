import {RouteSmartArt} from './RouteSmartArt';
import {EnvironmentSmartArt} from './EnvironmentSmartArt';
import {useEffect,useRef,useState} from 'react';
import {RotateCcw} from 'lucide-react';
import './cost-bars.css';
import {api} from '../api';
import {Panel,Notice} from './ui';
const n=(v:number)=>v.toLocaleString('zh-CN',{maximumFractionDigits:2});
function CostBars({label,field,unit,factor,values}:{label:string;field:string;unit:string;factor:number;values:any[]}){
 const ref=useRef<HTMLDivElement>(null);const [visible,setVisible]=useState(false);const [replay,setReplay]=useState(0);
 useEffect(()=>{const observer=new IntersectionObserver(([entry])=>{if(entry.isIntersecting){setVisible(true);observer.disconnect()}},{threshold:.2});if(ref.current)observer.observe(ref.current);return()=>observer.disconnect()},[]);
 const max=Math.max(1,...values.map(r=>r[field]));
 return <div ref={ref} className="cost-bar-group"><div className="cost-bar-heading"><h3>{label}（{unit}）</h3><button type="button" aria-label={'重播'+label+'动画'} title="重播动画" onClick={()=>{setVisible(true);setReplay(x=>x+1)}}><RotateCcw size={13}/></button></div>
 <div key={replay} className={visible?'cost-bars-visible':''}>{values.map((r:any,i:number)=><div key={r.id} className="cost-bar-row"><div>{r.title}：{n(r[field]*factor)}</div><div className="cost-bar-track" role="img" aria-label={r.title+'，'+label+'：'+n(r[field]*factor)+' '+unit}><div className="cost-bar-fill" style={{width:r[field]/max*100+'%',background:r.id==='route_a'?'#d7b6ff':r.id==='route_b'?'#00cddd':'#66eda5',animationDelay:i*160+'ms'}}/></div></div>)}</div></div>
}
export function SeparationEvaluation({p}:{p:any}){
 const [data,setData]=useState<any>(null),[error,setError]=useState('');
 useEffect(()=>{let active=true;api('/projects/'+p.id+'/equipment-estimate','POST',{}).then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(e.message)});return()=>{active=false}},[p.id]);
 if(error)return <Notice tone="red">{error}</Notice>;
 if(!data)return <Notice>正在计算分离方案对比…</Notice>;
 const routes=data.routes.filter((r:any)=>['route_a','route_b','route_c'].includes(r.id));
 const values=routes.map((r:any)=>{const u=r.utilities.filter((x:any)=>x.scope==='分离段');return {...r,heat:u.filter((x:any)=>x.unit==='t/h').reduce((s:number,x:any)=>s+x.duty_kw,0),cool:u.filter((x:any)=>x.unit==='m³/h'||x.utility.includes('冷冻水')).reduce((s:number,x:any)=>s+x.duty_kw,0),electric:u.filter((x:any)=>x.unit==='kW电').reduce((s:number,x:any)=>s+x.quantity,0)}});
 const [a,b,c]=values;
 const metrics:[string,string,string,number][]=[['外购供热负荷','heat','kW',1],['冷却负荷','cool','kW',1],['电输入（压缩机及制冷机）','electric','kW',1],['年用电量','electric','万kWh/a',data.inputs.hours/10000],['分离段公用工程费','separation_annual','万元/a',.0001],['主要设备购置费','purchase','万元',.0001],['设备安装总额（含购置）','installed','万元',.0001]];
 return <><Panel title="分离能耗与设备费用比较" kicker="SEPARATION PERFORMANCE">
 <p>普通精馏、热泵精馏与内部热耦合精馏 · 年运行 {n(data.inputs.hours)} 小时 · 电价 {data.inputs.electricity} 元/kWh · 蒸汽 {data.inputs.steam_price} 元/t</p>
 <div className="table-scroll"><table><thead><tr><th>比较指标</th>{values.map((r:any)=><th key={r.id}>{r.title}</th>)}<th>单位</th></tr></thead><tbody>{metrics.map(([label,key,unit,f])=><tr key={key+label}><td>{label}</td>{values.map((r:any)=><td key={r.id}>{n(r[key]*f)}</td>)}<td>{unit}</td></tr>)}</tbody></table></div>
 <p>比较边界为分离段。热负荷、冷负荷和电输入分别列示；制冷负荷不与制冷机电耗重复计入费用。设备费用为主要分离设备概念估算，安装总额包含购置费，两项不相加。</p>
 <div className="form-grid cost-bar-grid">{metrics.filter(x=>['separation_annual','purchase'].includes(x[1])).map(([label,key,unit,f])=><CostBars key={key} label={label} field={key} unit={unit} factor={f} values={values}/>)}</div>
 <details><summary>设备费用明细</summary>{values.map((r:any)=><div key={r.id}><h3>{r.title}</h3><table><thead><tr><th>设备</th><th>规模</th><th>材料</th><th>购置费 / 万元</th></tr></thead><tbody>{r.equipment.map((e:any)=><tr key={e.name}><td>{e.name}</td><td>{e.scale}</td><td>{e.material}</td><td>{n(e.cost_cny/10000)}</td></tr>)}</tbody></table></div>)}</details>
 </Panel><Panel title="方案择优说明" kicker="ROUTE ASSESSMENT">
 <RouteSmartArt a={a} b={b} c={c}/>
 </Panel><Panel title="环境影响评价" kicker="ENVIRONMENTAL ASSESSMENT">
 <EnvironmentSmartArt/>
 </Panel></>;
}

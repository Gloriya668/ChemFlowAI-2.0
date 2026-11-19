import {useEffect,useState} from 'react';
import {api,fmt} from '../api';
import {Panel,Notice} from './ui';

export function EngineeringEstimate({p}:{p:any}){
 const [data,setData]=useState<any>(null),[values,setValues]=useState<any>({}),[route,setRoute]=useState(p.route||'route_a'),[error,setError]=useState(''),[busy,setBusy]=useState(false),[dirty,setDirty]=useState(false);
 const calculate=async(v:any)=>{setBusy(true);setError('');try{const d=await api('/projects/'+p.id+'/equipment-estimate','POST',v);setData(d);setValues(d.inputs);setDirty(false)}catch(e:any){setError(e.message)}finally{setBusy(false)}};
 useEffect(()=>{if(p.dataset==='pdh')calculate({})},[p.id,p.dataset]);
 if(p.dataset!=='pdh')return null;
 const r=data?.routes.find((x:any)=>x.id===route);
 const money=(v:number)=>fmt(v/10000)+' 万元';
 return <Panel title="三方案设备与公用工程估算" kicker="ENGINEERING ESTIMATE · 概念设计情景">
 <Notice tone="cyan">基于工艺负荷与设备参数，评估三种分离方案的设备投资及运行费用。调整计算条件后可重新估算。</Notice>
 {error&&<Notice tone="red">{error}</Notice>}{!data&&<p>{busy?'正在计算…':'估算暂不可用'}</p>}
 {data&&<><p style={{margin:'16px 0'}}>{data.basis}</p>
 <details><summary>调整运行、价格、材料与尺寸假设（{data.fields.length}项）</summary><div className="form-grid" style={{margin:'16px 0'}}>{data.fields.map((f:any)=><label key={f.key}>{f.label} / {f.unit}<input type="number" step="any" value={values[f.key]??''} onChange={e=>{setValues({...values,[f.key]:e.target.value===''?'':Number(e.target.value)});setDirty(true)}}/></label>)}</div></details>
 <div className="button-row" style={{margin:'16px 0'}}><button disabled={busy} onClick={()=>calculate(values)}>{busy?'计算中…':'应用假设并重新试算'}</button><button disabled={busy} onClick={()=>calculate({})}>恢复默认情景</button><button disabled={dirty||busy} onClick={()=>{const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const el=document.createElement('a');el.href=url;el.download='ChemFlow-equipment-estimate.json';el.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}}>导出本次计算与来源</button></div>
 {dirty&&<Notice tone="amber">假设已修改，下面仍显示上一次计算结果；点击重新试算后更新。</Notice>}
 <div className="table-scroll"><table><thead><tr><th>方案</th><th>已估设备购置小计</th><th>0.5–2倍购置情景</th><th>对应安装额初估</th><th>分离段公用工程/年</th><th>共同前处理费用/年</th><th>年总消耗费用（情景）</th></tr></thead><tbody>{data.routes.map((x:any)=><tr key={x.id}><td><button onClick={()=>setRoute(x.id)} aria-pressed={route===x.id}>{x.title}{route===x.id?' ✓':''}</button></td><td>{money(x.purchase)}</td><td>{money(x.low)} – {money(x.high)}</td><td>{money(x.installed)}</td><td>{money(x.separation_annual)}</td><td>{money(x.common_annual)}</td><td><strong className="cyan">{money(x.total_annual)}</strong></td></tr>)}</tbody></table></div>
 <Notice tone="amber">年总消耗费用 = 分离段公用工程费 + 共同前处理费用，仅计已列出的能源与公用工程消耗，不含设备购置、折旧、人工维修及待补充耗材。购置小计仅含下表列出的主要分离设备。共同前处理费用单列，设备购置小计不等于全厂投资。</Notice>
 {r&&<><h3 style={{marginTop:24}}>{r.title} · 设备规模、材料与价值</h3><div className="table-scroll"><table><thead><tr><th>设备</th><th>估算规模</th><th>材料 / 耗材量</th><th>购置估算</th><th>依据与待校核项</th></tr></thead><tbody>{r.equipment.map((x:any)=><tr key={x.name}><td>{x.name}</td><td>{x.scale}</td><td>{x.material}{x.mass_t!=null&&<p>塔壳+板材约 {fmt(x.mass_t)} t</p>}</td><td>{money(x.cost_cny)}</td><td><details><summary>计算依据</summary><p>{x.source}</p><p>{x.warning}</p></details></td></tr>)}</tbody></table></div>
 <h3 style={{marginTop:24}}>冷热公用工程与电力费用</h3><p>年总消耗费用（当前情景）：<strong className="cyan">{money(r.total_annual)} / 年</strong></p><div className="table-scroll"><table><thead><tr><th>设备 / 范围</th><th>热负荷或轴功率</th><th>公用工程</th><th>小时用量</th><th>年费用</th><th>来源</th></tr></thead><tbody>{r.utilities.map((x:any)=><tr key={x.name}><td>{x.name}<small style={{display:'block'}}>{x.scope}</small></td><td>{fmt(x.duty_kw)} kW</td><td>{x.utility}</td><td>{fmt(x.quantity)} {x.unit}</td><td>{money(x.annual)}</td><td>{x.source}</td></tr>)}</tbody></table></div></>}
 <details style={{marginTop:20}}><summary>计算方法与适用范围</summary>{data.formulas.map((x:string)=><p key={x}>{x}</p>)}</details>

 </>}
 </Panel>
}

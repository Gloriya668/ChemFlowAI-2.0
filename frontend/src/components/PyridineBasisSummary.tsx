import type {ProjectSpec} from '../types';
import {Panel,Metric} from './ui';
export function PyridineBasisSummary({spec}:{spec:ProjectSpec}){
 const value=(f:any,key:string,unit:string)=>{const q=f?.[key];return q?.unit===unit&&typeof q.value==='number'&&Number.isFinite(q.value)&&q.value>0?q.value:null};
 const total=(key:string,unit:string)=>{const vs=spec.feeds.map(f=>value(f,key,unit));return vs.length&&vs.every(v=>v!==null)?vs.reduce((a:number,b)=>a+(b??0),0):null};
 const thfa=spec.feeds.find(f=>f.stream_id==='THFA'),ammonia=spec.feeds.find(f=>f.stream_id==='NH3'),solvent=spec.feeds.find(f=>f.stream_id==='1');
 const closed=spec.source?.variant==='pyridine525';
 const n=value(thfa,'molar_flow','kmol/h'),a=value(ammonia,'molar_flow','kmol/h'),h=value(solvent,'molar_flow','kmol/h');
 const show=(v:number|null,d=3)=>v===null?'待填写':v.toLocaleString('zh-CN',{maximumFractionDigits:d});
 return <Panel title="初始工况与配料计算" kicker="INITIAL DESIGN BASIS"><div className="form-grid two"><Metric label={closed?'外部新鲜进料质量流量':'总进料质量流量（含正己烷）'} value={show(total('mass_flow','kg/h'))+' kg/h'}/><Metric label={closed?'外部新鲜进料摩尔流量':'总进料摩尔流量（含正己烷）'} value={show(total('molar_flow','kmol/h'))+' kmol/h'}/><Metric label="氨 / 四氢糠醇 摩尔比" value={n&&a?show(a/n)+' : 1':'待填写'}/><Metric label={closed?"RE 循环初始化摩尔流量":"正己烷 / 四氢糠醇 摩尔比"} value={closed?"176 kmol/h（内部循环）":n&&h?show(h/n)+' : 1':'待填写'}/></div><p style={{marginTop:16}}>{closed?"RE 为内部溶剂回流，不重复计入新鲜进料。":"总流量为各入口流量之和，"}摩尔比按对应进料摩尔流量计算。修改下方工况后自动更新，保存后作为本案例设计基准。</p></Panel>;
}

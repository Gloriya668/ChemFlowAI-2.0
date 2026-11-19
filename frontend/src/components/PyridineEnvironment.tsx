import {Flame,Droplets,Wind,Recycle,ArrowRight,FlaskConical,Factory,ClipboardCheck} from 'lucide-react';
import {Panel} from './ui';
import './PyridineEnvironment.css';

const impacts=[
 {Icon:Flame,color:'orange',title:'能源与间接排放',tag:'重点：反应加热与精馏',effect:'供热、冷却与电力带来环境负荷',action:'先做冷热匹配，再评估余热回收',check:'跟踪：蒸汽、电耗 / 吨产品'},
 {Icon:Droplets,color:'blue',title:'水相与废水',tag:'重点：分相器水相',effect:'需检测有机物、含氮物及处理适应性',action:'分质收集 → 回收有机物 → 验证处理工艺',check:'跟踪：COD、氨氮、总氮'},
 {Icon:Wind,color:'purple',title:'尾气与无组织排放',tag:'重点：气相出口、储罐及密封点',effect:'含氨或有机物逸散需按实测组成判断',action:'密闭收集；按组分选择回收与净化',check:'跟踪：氨、VOCs、泄漏点'},
 {Icon:Recycle,color:'green',title:'溶剂与固体残余',tag:'优势：已有溶剂返回路径',effect:'循环有减废潜力，仍需控制杂质积累',action:'监测溶剂品质；废液与残渣分类处置',check:'跟踪：补充量、损失量、废物量'},
];
export function PyridineEnvironment(){return <Panel title="吡啶项目 · 环境评价与改进建议" kicker="ENVIRONMENTAL SMARTART">
 <div className="py-env">
  <div className="pe-conclusion"><Recycle size={24}/><div><strong>保留溶剂闭路循环，优先降低热负荷与污染物流损失</strong><span>基于当前流程的定性评价 · 减排效果需由能耗和排放实测验证</span></div></div>
  <div className="pe-flow" aria-label="环境影响识别流程">
   {[{Icon:FlaskConical,title:'原料与反应',sub:'THFA + 氨 → 反应加热'},{Icon:Factory,title:'分离与精制',sub:'闪蒸 → 多级精馏'},{Icon:Droplets,title:'分相与回收',sub:'水相管理 · 溶剂返回'},{Icon:ClipboardCheck,title:'环境绩效',sub:'单位能耗 · 损失 · 排放'}].map(({Icon,title,sub},i)=><div className="pe-node" key={title}><Icon size={25}/><strong>{title}</strong><span>{sub}</span>{i<3&&<ArrowRight className="pe-arrow" size={20}/>}</div>)}
  </div>
  <div className="pe-grid">{impacts.map(({Icon,color,title,tag,effect,action,check})=><article className={'pe-card '+color} key={title}><header><Icon size={24}/><h3>{title}</h3></header><span className="pe-tag">{tag}</span><p>{effect}</p><div className="pe-action"><ArrowRight size={17}/><strong>{action}</strong></div><footer>{check}</footer></article>)}</div>
  <div className="pe-priorities" aria-label="建议实施顺序">{[['01','先测清','分项能耗 + 气液组成'],['02','先减损','密闭收集 + 泄漏检测修复'],['03','再优化','余热回收 + 溶剂品质控制']].map(([n,t,d])=><div key={n}><b>{n}</b><span><strong>{t}</strong><small>{d}</small></span></div>)}</div>
  <p className="pe-footnote">水相流量不等于最终排水量；循环溶剂流量不等于节约量。当前不估算碳减排百分比，也不作达标排放结论。</p>
 </div>
 </Panel>}

import React,{useEffect,useRef,useState} from 'react';
import {createPortal} from 'react-dom';
import {useNavigate} from 'react-router-dom';
import {X,ArrowLeft,ArrowRight,Pause,Play,Layers3,RotateCcw,ChevronDown,ExternalLink,SlidersHorizontal,Lightbulb,BookOpen,Focus,House} from 'lucide-react';
import type {LearningCase,Equipment} from './types';
import {equipmentFor} from './FlowDiagram';
import {getProfile,patents} from './equipmentData';
import {EquipmentIllustration} from './EquipmentIllustration';
import './equipment-explorer.css';
export function EquipmentExplorer({c,initialId,onClose,onEquipmentChange}:{c:LearningCase;initialId:string;onClose:()=>void;onEquipmentChange:(id:string)=>void}){
 const navigate=useNavigate();
 const devices=equipmentFor(c);const initial=devices.find(e=>e.id===initialId)||devices.find(e=>e.group===initialId)||devices[0];
 const [current,setCurrent]=useState(initial.id);const dialog=useRef<HTMLDialogElement>(null);const device=devices.find(e=>e.id===current)||initial;const index=devices.indexOf(device);
 useEffect(()=>{const el=dialog.current;const previous=document.activeElement as HTMLElement|null;const overflow=document.body.style.overflow;document.body.style.overflow='hidden';el?.showModal();return()=>{el?.close();document.body.style.overflow=overflow;previous?.focus({preventScroll:true})}},[]);
 const choose=(id:string)=>{setCurrent(id);onEquipmentChange(id)};
 return createPortal(<dialog ref={dialog} className="equipment-explorer" aria-labelledby="eq-explorer-title" onCancel={e=>{e.preventDefault();onClose()}} onClick={e=>{if(e.target===e.currentTarget)onClose()}}><div className="eq-dialog-content">
 <header className="eq-dialog-header"><div className="eq-brand-mark"><Layers3 size={21}/></div><div className="eq-dialog-title"><span>EQUIPMENT EXPLORER</span><h2 id="eq-explorer-title">设备探索室 <small>{c.title}</small></h2></div><div className="eq-return-nav"><button onClick={onClose}><ArrowLeft size={14}/>返回上一级</button><button onClick={()=>{onClose();navigate('/home')}}><House size={14}/>返回主页面</button></div><button className="eq-close" onClick={onClose} title="关闭设备探索（Esc）" aria-label="关闭设备探索" autoFocus><X size={21}/></button></header>
 <div className="eq-device-nav"><div className="eq-device-picker"><span className="eq-device-index">{String(index+1).padStart(2,'0')} / {String(devices.length).padStart(2,'0')}</span><label><span className="eq-sr-only">切换流程设备</span><select value={device.id} onChange={e=>choose(e.target.value)}>{devices.map(e=><option key={e.id} value={e.id}>{e.id} · {e.name}</option>)}</select><ChevronDown size={16}/></label></div><div className="eq-nav-buttons"><button disabled={index===0} onClick={()=>choose(devices[index-1].id)} aria-label="上一台设备"><ArrowLeft size={16}/></button><button disabled={index===devices.length-1} onClick={()=>choose(devices[index+1].id)} aria-label="下一台设备"><ArrowRight size={16}/></button></div></div>
 {initialId!==initial.id&&<div className="eq-group-hint">已展开功能段内设备，可从上方菜单逐台查看。</div>}
 <DevicePanel key={device.id} c={c} device={device}/>
 </div></dialog>,document.body);
}
function DevicePanel({c,device}:{c:LearningCase;device:Equipment}){
 const profile=getProfile(c,device);const storageKey=`chemflow-equipment:${c.id}:${device.id}`;
 const [variant,setVariant]=useState(()=>{try{const stored=localStorage.getItem(storageKey);return profile.variants.some(v=>v.id===stored)?stored!:profile.variants[0].id}catch{return profile.variants[0].id}});
 const [paused,setPaused]=useState(()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches),[speed,setSpeed]=useState(1),[exploded,setExploded]=useState(false),[labels,setLabels]=useState(true),[part,setPart]=useState(1),[tab,setTab]=useState('parameters');
 const choice=profile.variants.find(v=>v.id===variant)||profile.variants[0];const patent=profile.patent?patents[profile.patent]:null;
 useEffect(()=>{try{localStorage.setItem(storageKey,variant)}catch{}},[storageKey,variant]);
 const reset=()=>{setVariant(profile.variants[0].id);setSpeed(1);setExploded(false);setLabels(true);setPart(1);setPaused(window.matchMedia('(prefers-reduced-motion: reduce)').matches)};
 return <>
 <div className="eq-main-grid"><section className="eq-visual-panel" aria-label="内部构造演示"><div className="eq-visual-heading"><div><span className="eq-tag">{device.module}</span><strong>{profile.title}</strong></div><span className="eq-live"><i/>{paused?'已暂停':'动态剖面'}</span></div>
 <EquipmentIllustration profile={profile} variant={variant} paused={paused} speed={speed} exploded={exploded} labels={labels} activePart={part} onPart={setPart}/>
 <div className="eq-playback"><div className="eq-playback-buttons"><button onClick={()=>setPaused(!paused)} aria-label={paused?'播放设备动画':'暂停设备动画'}>{paused?<Play size={16}/>:<Pause size={16}/>}<span>{paused?'播放':'暂停'}</span></button><button onClick={()=>setExploded(!exploded)} aria-pressed={exploded}><Layers3 size={16}/><span>分解内件</span></button><button onClick={()=>setLabels(!labels)} aria-pressed={labels}><Focus size={16}/><span>部件标记</span></button><button onClick={reset} title="恢复默认演示" aria-label="恢复默认演示"><RotateCcw size={16}/></button></div><label className="eq-speed">动画速度<input type="range" min="0.5" max="2" step="0.25" value={speed} onChange={e=>setSpeed(Number(e.target.value))} aria-label="动画播放速度"/><output>{speed}×</output></label></div>
 <div className="eq-part-detail" aria-live="polite"><span>{String(part+1).padStart(2,'0')}</span><div><h4>{profile.parts[part].name}</h4><p>{profile.parts[part].description}</p></div></div>
 <div className="eq-part-pills" aria-label="选择部件">{profile.parts.map((item,i)=><button key={item.name} onClick={()=>setPart(i)} aria-pressed={part===i}>{i+1} · {item.name}</button>)}</div>
 </section>
 <aside className="eq-config"><div className="eq-kicker"><SlidersHorizontal size={15}/>结构工作台</div><h3>选择内构件，<br/>看见流动的不同。</h3><p className="eq-config-intro">{device.role}</p><div className="eq-variant-grid" aria-label="结构选项">{profile.variants.map((v,i)=><button key={v.id} aria-pressed={variant===v.id} onClick={()=>setVariant(v.id)}><span className="eq-variant-num">{String(i+1).padStart(2,'0')}</span><strong>{v.name}</strong><span className="eq-choice-dot"/></button>)}</div>
 <div className="eq-choice-info" aria-live="polite"><span>当前结构 · {choice.name}</span><p>{choice.description}</p><div><b>选型关注</b><p>{choice.tradeoff}</p></div></div>
 <div className="eq-model-note"><BookOpen size={16}/><p>这是可比较的工程结构选项。切换内件仅更新教学动画，不改变案例的 流程模型或计算结果。</p></div>
 </aside></div>
 <section className="eq-knowledge"><div className="eq-knowledge-nav" role="group" aria-label="设备资料分类"><button aria-pressed={tab==='parameters'} onClick={()=>setTab('parameters')}><SlidersHorizontal size={16}/>关键操作参数<span>{profile.parameters.length}</span></button><button aria-pressed={tab==='principle'} onClick={()=>setTab('principle')}><BookOpen size={16}/>工作原理与案例</button><button aria-pressed={tab==='innovation'} onClick={()=>setTab('innovation')}><Lightbulb size={16}/>创新探索{patent&&<i/>}</button></div>
 {tab==='parameters'&&<div className="eq-tab-body"><div className="eq-tab-heading"><h3>理解参数如何影响设备</h3><p>展示参数含义与常用单位；本学习案例未提供设备设计值或操作设定值。</p></div><div className="eq-parameter-wrap"><table className="eq-parameters"><thead><tr><th>关键参数</th><th>常用单位</th><th>为什么重要</th><th>需要关注</th></tr></thead><tbody>{profile.parameters.map(row=><tr key={row.name}><th scope="row">{row.name}</th><td><code>{row.unit}</code></td><td>{row.meaning}</td><td>{row.watch}</td></tr>)}</tbody></table></div></div>}
 {tab==='principle'&&<div className="eq-tab-body eq-principle-grid"><article><span className="eq-kicker">HOW IT WORKS</span><h3>{profile.title}</h3><p>{profile.principle}</p><h4>在当前流程中的作用</h4><p>{device.id} · {device.role}</p></article><article><span className="eq-kicker">IN THIS PROCESS</span><h3>{c.title}</h3><p>{profile.context}</p><h4>模型与硬件之间</h4><p>当前模块：{device.module}。结构演示不提供设备尺寸、材料等级或制造图；真实选型需结合物性、负荷及机械设计条件。</p></article></div>}
 {tab==='innovation'&&<div className="eq-tab-body"><div className="eq-tab-heading"><h3>从结构变化，理解设备创新</h3><p>近期公开方案与工程设计思路。专利公开不等于商业成熟，也不意味着本案例已采用。</p></div>{patent?<article className="eq-patent-card"><div className="eq-patent-icon"><Lightbulb size={30}/></div><div><span className="eq-kicker">近期专利公开 · {patent.date}</span><h3>{patent.title}</h3><p>{patent.idea}</p><strong>{patent.question}</strong><p className="eq-patent-scope">{patent.scope}</p><details><summary>展开专利信息</summary><div><span>{patent.owner} · {patent.number} · 申请公开文本</span><a href={patent.url} target="_blank" rel="noreferrer">查看公开全文<ExternalLink size={13}/></a></div></details></div></article>:<article className="eq-design-card"><span className="eq-kicker">DESIGN EXPLORATION</span><h3>{choice.name}：从结构到选型</h3><p>{choice.description}</p><p>{choice.tradeoff}</p><small>本类设备暂未收录经核实的近期专利条目；这里展示工程结构比较。</small></article>}<div className="eq-explore-steps"><div><b>01</b><span>比较形状</span><p>观察通道、接触面与运动部件。</p></div><div><b>02</b><span>提出假设</span><p>思考压降、混合、传热和检修的取舍。</p></div><div><b>03</b><span>设计验证</span><p>结合模型、试验与材料条件评估。</p></div></div></div>}
 </section><footer className="eq-dialog-footer"><span>ChemFlow AI · 设备探索室</span><span>结构概念动画 · 非数值模拟 · 结构选择自动记忆</span></footer>
 </>;
}

import {useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {ArrowRight,FlaskConical,Workflow,Layers3,Pause,Play} from 'lucide-react';
import './welcome-motion.css';

const routes=['M0 220H140L195 275H350','M0 480H180L235 425H365','M1200 220H1060L1005 275H850','M1200 480H1020L965 425H835','M260 700V565L330 495','M940 0V135L870 205'];
export function Welcome(){
 const [paused,setPaused]=useState(false),[hidden,setHidden]=useState(()=>document.hidden),[reduced,setReduced]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);
 useEffect(()=>{const change=()=>setHidden(document.hidden),media=matchMedia('(prefers-reduced-motion: reduce)'),motion=()=>setReduced(media.matches);document.addEventListener('visibilitychange',change);media.addEventListener('change',motion);return()=>{document.removeEventListener('visibilitychange',change);media.removeEventListener('change',motion)}},[]);
 return <main className={'welcome-page welcome-experience'+(paused||hidden?' welcome-motion-paused':'')+(reduced?' welcome-motion-reduced':'')}>
  <div className="welcome-atmosphere" aria-hidden="true"><div className="welcome-aurora welcome-aurora-a"/><div className="welcome-aurora welcome-aurora-b"/><div className="welcome-grid"/><div className="welcome-floor"/>
   <div className="welcome-orbit-frame"><div className="welcome-orbit welcome-orbit-outer"/><div className="welcome-orbit welcome-orbit-inner"/><span className="welcome-orbit-cross cross-one">+</span><span className="welcome-orbit-cross cross-two">+</span></div>
   <svg className="welcome-circuit" viewBox="0 0 1200 700" fill="none"><g stroke="#438c99" strokeWidth="1">{routes.map((d,i)=><path key={i} d={d}/>)}<rect x="280" y="240" width="50" height="96" rx="15"/><path d="M290 260H320M290 278H320M290 296H320M290 314H320"/><rect x="880" y="386" width="48" height="96" rx="15"/><path d="M890 406H918M890 424H918M890 442H918M890 460H918"/>{[[140,220],[180,480],[1060,220],[1020,480],[260,565],[940,135]].map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r="5" fill="#122e38"/><circle className="welcome-node" cx={x} cy={y} r="2" fill="#80ece2" style={{animationDelay:i*.5+'s'}}/></g>)}</g><g stroke="#68e9e2" strokeWidth="2" strokeLinecap="round">{routes.map((d,i)=><path className="welcome-current" key={i} d={d} pathLength="100" style={{animationDelay:-i*1.1+'s'}}/>)}</g></svg>
   <div className="welcome-particles">{Array.from({length:16},(_,i)=><i key={i} style={{left:(7+i*37%89)+'%',top:(12+i*23%78)+'%',animationDelay:-i*.7+'s',animationDuration:(6+i%4)+'s'}}/>)}</div>
   <span className="welcome-hud welcome-hud-left">01 / PROCESS DESIGN<br/><b>化工流程 · 智能构建</b></span><span className="welcome-hud welcome-hud-right">02 / SIMULATION<br/><b>多维分析 · 工程决策</b></span>
  </div>
  <header className="welcome-brand"><img src="/brand/chemflow-transparent.png" alt=""/><span>ChemFlow <b>AI</b><small>智模拟 · 绿化工</small></span></header>
  {!reduced&&<button className="welcome-motion-toggle" type="button" aria-pressed={paused} aria-label={paused?'播放背景动画':'暂停背景动画'} onClick={()=>setPaused(v=>!v)}>{paused?<Play size={13}/>:<Pause size={13}/>}<span>{paused?'播放动效':'暂停动效'}</span></button>}
  <section className="welcome-content" aria-labelledby="welcome-title">
   <span className="welcome-eyebrow"><i aria-hidden="true"/>PROCESS ENGINEERING · INTELLIGENT SIMULATION</span>
   <p className="welcome-wordmark">ChemFlow <span>AI</span></p>
   <h1 id="welcome-title">化工流程智能设计与仿真平台</h1>
   <div className="welcome-title-rule" aria-hidden="true"><i/></div>
   <p className="welcome-description">连接工程实践与流程学习<br/>从工艺构想到模拟建立，让每一步设计清晰可循。</p>
   <Link to="/home" className="welcome-start"><span>点击开始</span><ArrowRight size={19}/></Link>
   <p className="welcome-hint">探索企业工程与流程学习空间</p>
   <div className="welcome-capabilities"><span><FlaskConical size={15}/>工程设计</span><span><Workflow size={15}/>流程仿真</span><span><Layers3 size={15}/>知识探索</span></div>
  </section>
  <footer className="welcome-footer"><span><i/>从工艺构想，到工程实现</span><span>CHEMFLOW AI / INTELLIGENT ENGINEERING</span></footer>
 </main>;
}

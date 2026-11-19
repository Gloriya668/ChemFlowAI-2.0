import {Link} from 'react-router-dom';
import {BookOpen,Check,House,Plus} from 'lucide-react';
import {studyStages} from './studyData';

export function learningStage(params:URLSearchParams){
 const requested=Number(params.get('stage'));
 return params.has('equipment')?2:Number.isInteger(requested)&&requested>=1&&requested<=studyStages.length?requested-1:0;
}
export function LearningNavigation({stage,onStage,done=[],title}:{stage:number;onStage:(n:number)=>void;done?:number[];title?:string}){
 return <><aside className="learning-sidebar" aria-label="学习工作导航">
  <span className="learning-nav-eyebrow">LEARNING NAVIGATION</span>
  <Link to="/home"><House size={18}/>首页</Link>
  <Link to={'/learn?stage='+String(stage+1)}><BookOpen size={18}/>流程案例库</Link>
  <div className="learning-nav-section">WORKFLOW / 十阶段项目学习</div>
  <nav aria-label="学习阶段">{studyStages.map(([name],i)=><button key={name} className={'learning-nav-step '+(done.includes(i)?'done ':'')+(stage===i?'active':'')} aria-current={stage===i?'step':undefined} onClick={()=>onStage(i)}><span className="learning-nav-number">{done.includes(i)?<Check size={15}/>:String(i+1).padStart(2,'0')}</span><span>{name}</span></button>)}</nav>
  <div className="learning-sidebar-foot"><span className="learning-shell-badge">流程学习版</span><p>{title||'选择案例，开始项目学习'}</p>{title&&<small>{done.length} / 10 阶段已自评</small>}<Link to="/learn/new"><Plus size={15}/>创建自定义案例</Link></div>
 </aside>
 <nav className="learning-progress" aria-label="十阶段学习进度" style={{'--learning-progress':`${stage/(studyStages.length-1)*100}%`} as React.CSSProperties}>{studyStages.map(([name],i)=><button key={name} title={name} aria-label={`${i+1} ${name}`} aria-current={i===stage?'step':undefined} className={(i===stage?'current ':'')+(done.includes(i)?'complete':'')} onClick={()=>onStage(i)}>{done.includes(i)&&<Check size={13}/>}<span>{String(i+1).padStart(2,'0')}</span></button>)}</nav></>;
}

export function LearningLibraryNavigation(){
 return <aside className="learning-sidebar learning-library-sidebar" aria-label="案例库导航">
  <span className="learning-nav-eyebrow">LEARNING NAVIGATION</span>
  <Link to="/home"><House size={18}/>首页</Link>
  <Link to="/learn" aria-current="page"><BookOpen size={18}/>流程案例库</Link>
  <Link to="/learn/new"><Plus size={18}/>创建自定义案例</Link>
  <div className="learning-sidebar-foot"><span className="learning-shell-badge">流程学习版</span><p>先选择感兴趣的流程，再进入案例内的十阶段学习。</p></div>
 </aside>;
}

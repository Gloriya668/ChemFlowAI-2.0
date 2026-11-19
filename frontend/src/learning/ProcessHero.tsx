import React,{useId} from 'react';
import './process-hero.css';
import {Link} from 'react-router-dom';
import {studyStages} from './studyData';
/** Process artwork and ten-stage learning navigation, without operating data. */
export function ProcessHero(){
 const prefix='hero'+useId().replace(/[^a-zA-Z0-9_-]/g,'');const u=(name:string)=>`url(#${prefix}-${name})`;
 const pipes=[{d:'M98 287L179 327L269 282L269 246',color:'#77dcd5'}, {d:'M269 113V87L420 162V187',color:'#a89de9'}, {d:'M292 224L352 254L405 227',color:'#76d8dc'},{d:'M423 301V323L504 363L579 326V285',color:'#91d6b7'}, {d:'M408 188V143L542 210V250',color:'#6fb8db'}, {d:'M542 279V316L365 405L181 313V266',color:'#8595d4'}];
 const Tower=({x,y,h,wide=62}:{x:number;y:number;h:number;wide?:number})=><g transform={`translate(${x} ${y})`}>
 <ellipse cy={h+21} rx={wide*.78} ry="18" fill={u('ground')}/><path d={`M${-wide/2+9} ${h}v23M${wide/2-9} ${h}v23`} stroke="#638c9f" strokeWidth="5"/>
 <path d={`M${-wide/2} 0V${h}C${-wide/2} ${h+20} ${wide/2} ${h+20} ${wide/2} ${h}V0Z`} fill={u('steel')} stroke="#86c9d8" strokeWidth="1.3"/>
 <ellipse rx={wide/2} ry="14" fill={u('lid')} stroke="#9ed8e2" strokeWidth="1.4"/>
 <path d={`M${-wide/2+8} 12V${h-6}M${wide/2-8} 12V${h-6}`} stroke="#c8fcff" strokeWidth="1" opacity=".36"/>
 <path d={`M${-wide/2+13} 19V${h-10}Q0 ${h+2} ${wide/2-13} ${h-10}V19Z`} fill="#3faaa6" opacity=".2"/>
 {Array.from({length:6},(_,i)=>{const yy=29+i*(h-45)/6;return <g key={i}><ellipse cy={yy} rx={wide/2-8} ry="10" fill="#468f9b" opacity=".2"/><path d={`M${-wide/2+8} ${yy}Q0 ${yy+17} ${wide/2-8} ${yy}`} fill="none" stroke="#9de4dd" strokeWidth="1.1" opacity=".8"/><circle className="ph-bubble" cx={i%2?-9:9} cy={yy+9} r="2.1" fill="#f1dba2" style={{animationDelay:`${-i*.55}s`}}/></g>})}
 {Array.from({length:6},(_,i)=><ellipse key={'film'+i} className="ph-liquid" cx={wide/2-10} cy={19+i*(h-40)/6} rx="1.4" ry="3.5" fill="#a2e8d4" style={{animationDelay:`${-i*.6}s`}}/>)}
 <path d={`M${wide/2+6} 12V${h+4}`} stroke="#527b90" strokeWidth="2"/>{Array.from({length:10},(_,i)=><path key={i} d={`M${wide/2+2} ${20+i*(h-17)/10}h9`} stroke="#78aabc" strokeWidth="1"/>)}
 <ellipse cy={h-3} rx={wide/2-4} ry="11" fill="#7ed3c0" opacity=".16"/><path d={`M${-wide/2} ${h-2}Q0 ${h+22} ${wide/2} ${h-2}`} fill="none" stroke="#85cdbd" strokeWidth="1.5"/>
 </g>;
 return <div className="process-hero"><div className="ph-heading"><span className="ph-brand"><i/>CHEMFLOW / PROJECT LEARNING</span><span className="ph-mode">背景 → 可行性评价</span></div>
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 440" className="ph-art" role="group" aria-label="从项目背景到可行性评价的十阶段学习路径">
 <defs>
 <linearGradient id={prefix+'-steel'}><stop stopColor="#142c43"/><stop offset=".2" stopColor="#2c6075"/><stop offset=".45" stopColor="#203e59"/><stop offset=".69" stopColor="#204957"/><stop offset=".9" stopColor="#426e81"/><stop offset="1" stopColor="#1e3d54"/></linearGradient>
 <linearGradient id={prefix+'-lid'} x2="1" y2="1"><stop stopColor="#649da8"/><stop offset=".45" stopColor="#254b61"/><stop offset="1" stopColor="#172e44"/></linearGradient>
 <linearGradient id={prefix+'-floor'} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#285064" stopOpacity=".5"/><stop offset="1" stopColor="#0a192a" stopOpacity=".15"/></linearGradient>
 <radialGradient id={prefix+'-halo'}><stop stopColor="#286c7e" stopOpacity=".45"/><stop offset=".55" stopColor="#194459" stopOpacity=".18"/><stop offset="1" stopColor="#0d1b2d" stopOpacity="0"/></radialGradient>
 <radialGradient id={prefix+'-ground'}><stop stopColor="#60daca" stopOpacity=".3"/><stop offset="1" stopColor="#60daca" stopOpacity="0"/></radialGradient>
 <linearGradient id={prefix+'-edge'}><stop stopColor="#84e9dd" stopOpacity="0"/><stop offset=".5" stopColor="#84e9dd"/><stop offset="1" stopColor="#84e9dd" stopOpacity="0"/></linearGradient>
 <filter id={prefix+'-glow'} x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3"/></filter>
 <pattern id={prefix+'-grid'} width="38" height="38" patternUnits="userSpaceOnUse" patternTransform="matrix(1 .5 -1 .5 340 205)"><path d="M38 0H0V38" stroke="#73b1c3" strokeWidth=".65" fill="none" opacity=".2"/></pattern>
 </defs>
 <ellipse cx="355" cy="235" rx="300" ry="230" fill={u('halo')}/>
 <path d="M55 266L323 132L635 288L367 422Z" fill={u('floor')} stroke="#416879" strokeWidth=".8"/>
 <path d="M55 266L323 132L635 288L367 422Z" fill={u('grid')}/><path d="M55 266V274L367 430L635 296V288M367 422V430" fill="none" stroke="#335165" strokeWidth="1"/>
 <path d="M87 286L367 426L606 306" fill="none" stroke={u('edge')} strokeWidth="2"/>
 <g fill="none" stroke="#608b9e" strokeWidth=".7" opacity=".3"><ellipse cx="350" cy="262" rx="276" ry="112" strokeDasharray="2 9"/><path d="M102 159L331 44L597 177M331 44V99" strokeDasharray="3 6"/><path d="M87 341V378H131M561 97H602V140"/></g>
 {pipes.map((p,i)=><g key={i} fill="none" strokeLinejoin="round" strokeLinecap="round"><path d={p.d} stroke={p.color} strokeWidth="7" filter={u('glow')} opacity=".12"/><path d={p.d} stroke="#102433" strokeWidth="6"/><path d={p.d} stroke={p.color} strokeWidth="2" opacity=".65"/><path d={p.d} className="ph-flow" stroke={p.color} strokeWidth="3" strokeDasharray="5 96" style={{animationDelay:`${-i*.8}s`}}/></g>)}
 <g transform="translate(160 260)"><ellipse cy="41" rx="48" ry="16" fill={u('ground')}/><path d="M-30 -37V14Q-30 40 1 41Q32 40 32 14V-37Z" fill={u('steel')} stroke="#74acbe"/><ellipse cy="-37" rx="31" ry="13" fill={u('lid')} stroke="#91c9d5"/><path d="M-23 27V46M24 27V46" stroke="#779cad" strokeWidth="4"/><path d="M-21 -6Q0 -17 24 -6V15Q0 38 -21 15Z" fill="#4d9fa9" opacity=".3"/><path d="M-21 -6Q0 6 24 -6" stroke="#91ddca" fill="none"/><path d="M-4 -45V-69H13" stroke="#93becc" fill="none" strokeWidth="3"/></g>
 <Tower x={269} y={106} h={165}/><Tower x={420} y={185} h={117} wide={57}/>
 <g transform="translate(533 268)"><ellipse cy="31" rx="54" ry="16" fill={u('ground')}/><path d="M-28 -24L21 -48Q51 -43 51 -23L3 2Z" fill={u('lid')} stroke="#779caf"/><path d="M-28 -24V8L3 24V2M3 24L51 0V-23" fill={u('steel')} stroke="#779caf"/>{[0,1,2,3].map(i=><path key={i} d={`M${-20+i*8} ${-21+i*4}L${28+i*7} ${-45+i*4}`} stroke="#a2dce1" opacity=".6"/>)}<path d="M-20 12V30M38 7V22" stroke="#6b95a6" strokeWidth="4"/></g>
 <g transform="translate(350 256)"><ellipse cy="28" rx="31" ry="10" fill={u('ground')}/><path d="M-19 23L4 35L28 23L6 12Z" fill="#234456" stroke="#5c8d9e"/><ellipse cx="3" cy="2" rx="20" ry="23" fill={u('steel')} stroke="#96c7d5"/><ellipse cx="3" cy="2" rx="11" ry="14" fill="#17384e" stroke="#578da5"/><path d="M-6 7L11 -5M-4 -7L11 7" stroke="#9bdfd7" strokeWidth="2"/></g>
 <g className="ph-orbit" fill="#9bdfd9">{[[68,266],[322,132],[636,288],[367,423],[602,140],[331,44]].map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r="5" opacity=".15"/><circle cx={x} cy={y} r="1.6"/></g>)}</g>
 <g className="ph-study-map" fontFamily="'Segoe UI','Microsoft YaHei',sans-serif">
 {[
  {x:23,y:35,w:202,title:'立项与产品',subtitle:'PROJECT DEFINITION',steps:[0,1],color:'#83d7ca',line:'M202 65H222V115'},
  {x:460,y:34,w:200,title:'流程与方案',subtitle:'PROCESS DEVELOPMENT',steps:[2,3,4],color:'#a4b9ed',line:'M0 78H-26V145'},
  {x:22,y:310,w:235,title:'厂址、环保与安全',subtitle:'SITE & ENVIRONMENT',steps:[5,6,7],color:'#94d8b1',line:'M119 0V-18L149 -31'},
  {x:440,y:328,w:220,title:'投资与评价',subtitle:'ECONOMIC EVALUATION',steps:[8,9],color:'#d6be91',line:'M67 0V-16L95 -30'}
 ].map(card=><g className="ph-study-card" key={card.title} transform={`translate(${card.x} ${card.y})`} style={{'--ph-card-accent':card.color} as React.CSSProperties}>
  <path d={card.line} stroke={card.color} strokeWidth="1" strokeDasharray="3 4" fill="none" opacity=".55"/>
  <rect className="ph-study-card-bg" width={card.w} height={39+card.steps.length*24} rx="10" fill="#122a3a" fillOpacity=".96" stroke={card.color} strokeOpacity=".4"/>
  <path d="M13 16H24" stroke={card.color} strokeWidth="2.5" strokeLinecap="round"/>
  <text x="31" y="20" fill={card.color} fontSize="11" fontWeight="650">{card.title}</text>
  <text x="13" y="33" fill="#7296aa" fontSize="6.6" letterSpacing="1.45">{card.subtitle}</text>
  {card.steps.map((step,j)=><Link key={step} to={'/learn?stage='+(step+1)} className="ph-study-stage" aria-label={'学习阶段 '+(step+1)+'：'+studyStages[step][0]}>
   <rect className="ph-study-row" x="7" y={39+j*24} width={card.w-14} height="23" rx="4" fill="transparent"/>
   <text x="14" y={55+j*24} fill={card.color} fontSize="10" fontWeight="700" fontFamily="'Segoe UI',sans-serif">{String(step+1).padStart(2,'0')}</text>
   <text x="38" y={55+j*24} fill="#d2e6ec" fontSize="12" fontWeight="550">{studyStages[step][0]}</text>
  </Link>)}
 </g>)}
 <g transform="translate(292 381)"><path d="M0 0L38 -19L76 0L38 19Z" fill="#173444" fillOpacity=".9" stroke="#4a8590" strokeWidth=".7"/><path d="M13 0L38 -12L63 0M38 -12V12" fill="none" stroke="#83c7be" strokeWidth="1" opacity=".6"/><text x="38" y="37" textAnchor="middle" fill="#86a9b8" fontSize="7" letterSpacing="1.5">PROJECT LIFECYCLE</text></g>
 </g>
 </svg><div className="ph-footer"><span>从项目背景，走向可行性评价。</span><span>FROM IDEA TO FEASIBILITY<svg width="24" height="12" viewBox="0 0 24 12" aria-hidden="true"><path d="M0 6H22M17 1L22 6L17 11" fill="none" stroke="currentColor"/></svg></span></div></div>;
}

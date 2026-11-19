import {memo,useEffect,useMemo,useRef,useState} from 'react';import {ZoomIn,ZoomOut,Pause,Play,Maximize2,Minimize2} from 'lucide-react';
// Revision keys prevent reusing diagrams after an engineering change. Bound memory across projects.
const canvasCache=new Map<string,{markup?:string;pending?:Promise<string>}>();
function loadCanvas(id:string,revision:number){
 const key=id+':'+revision,existing=canvasCache.get(key);
 if(existing?.markup!==undefined)return Promise.resolve(existing.markup);
 if(existing?.pending)return existing.pending;
 const entry:{markup?:string;pending?:Promise<string>}={};
 entry.pending=fetch('/api/projects/'+id+'/canvas').then(async r=>{
  if(!r.ok){const data=await r.json().catch(()=>null);throw Error(data?.detail||'流程图加载失败')}
  return r.text();
 }).then(text=>{entry.markup=text.replace(/工程归档/g,'工艺参数');entry.pending=undefined;return entry.markup}).catch(error=>{if(canvasCache.get(key)===entry)canvasCache.delete(key);throw error});
 canvasCache.set(key,entry);
 while(canvasCache.size>12)canvasCache.delete(canvasCache.keys().next().value!);
 return entry.pending;
}
export const ProcessCanvas=memo(function ProcessCanvas({id,revision,onSelect,svgMarkup}:{id:string;revision:number;onSelect:(v:any)=>void;svgMarkup?:string}){
 const shell=useRef<HTMLDivElement>(null);const fullButton=useRef<HTMLButtonElement>(null);const [fullscreen,setFullscreen]=useState(false);
 const ref=useRef<HTMLDivElement>(null);const cacheKey=id+':'+revision;
 const [loaded,setLoaded]=useState(()=>({key:cacheKey,markup:canvasCache.get(cacheKey)?.markup||''}));
 const markup=svgMarkup!==undefined?svgMarkup:loaded.key===cacheKey?loaded.markup:'';
 // Keep this object stable so toolbar/selection updates do not replace the live SVG DOM.
 const svgHtml=useMemo(()=>({__html:markup}),[markup]);
 const onSelectRef=useRef(onSelect);onSelectRef.current=onSelect;
 const [error,setError]=useState('');const [zoom,setZoom]=useState(1);const [paused,setPaused]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);
 useEffect(()=>{let cancelled=false;setError('');if(svgMarkup!==undefined)return;
  loadCanvas(id,revision).then(markup=>{if(!cancelled)setLoaded({key:cacheKey,markup})}).catch(e=>{if(!cancelled)setError(e.message)});
  return()=>{cancelled=true};
 },[id,revision,cacheKey,svgMarkup]);
 useEffect(()=>{const svg=ref.current?.querySelector('svg');if(!svg)return;const click=(e:Event)=>{const target=(e.target as Element).closest('[data-stream-id],[data-equipment-id]');if(!target)return;svg.querySelectorAll('.selected').forEach(x=>x.classList.remove('selected'));target.classList.add('selected');onSelectRef.current(target.getAttribute('data-stream-id')?{kind:'stream',id:target.getAttribute('data-stream-id')}:{kind:'equipment',id:target.getAttribute('data-equipment-id')})};const key=(e:KeyboardEvent)=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();click(e)}};svg.addEventListener('click',click);svg.addEventListener('keydown',key);
 const hits:SVGPathElement[]=[];svg.querySelectorAll('path.stream-pipe').forEach(path=>{const hit=path.cloneNode() as SVGPathElement;hit.removeAttribute('id');hit.setAttribute('class','stream-hit');hit.setAttribute('stroke','transparent');hit.setAttribute('stroke-width','22');hit.removeAttribute('marker-end');path.after(hit);hits.push(hit)});
 svg.querySelectorAll('[data-stream-id],[data-equipment-id]').forEach(el=>{if(!el.querySelector('title')){const t=document.createElementNS('http://www.w3.org/2000/svg','title');t.textContent='点击检查 '+(el.getAttribute('data-stream-id')||el.getAttribute('data-equipment-id'));el.append(t)}});
 return()=>{svg.removeEventListener('click',click);svg.removeEventListener('keydown',key);hits.forEach(hit=>hit.remove())}},[markup]);
 useEffect(()=>{
  const svg=ref.current?.querySelector('svg'),host=shell.current;if(!svg||!host)return;
  let visible=false,frame=0;
  const update=()=>{cancelAnimationFrame(frame);svg.pauseAnimations();if(!paused&&visible&&!document.hidden)frame=requestAnimationFrame(()=>svg.unpauseAnimations())};
  svg.pauseAnimations();
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;update()},{threshold:0});
  observer.observe(host);document.addEventListener('visibilitychange',update);
  return()=>{observer.disconnect();document.removeEventListener('visibilitychange',update);cancelAnimationFrame(frame);svg.pauseAnimations()};
 },[paused,markup]);
 useEffect(()=>{
  const changed=()=>{setFullscreen(document.fullscreenElement===shell.current);if(!document.fullscreenElement)fullButton.current?.focus()};
  const escape=(e:KeyboardEvent)=>{if(e.key==='Escape'&&!document.fullscreenElement){setFullscreen(false);fullButton.current?.focus()}};
  document.addEventListener('fullscreenchange',changed);document.addEventListener('keydown',escape);
  return()=>{document.removeEventListener('fullscreenchange',changed);document.removeEventListener('keydown',escape)};
 },[]);
 useEffect(()=>{if(!fullscreen)return;const previous=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{document.body.style.overflow=previous}},[fullscreen]);
 const toggleFullscreen=async()=>{
  if(fullscreen){if(document.fullscreenElement===shell.current)await document.exitFullscreen();else {setFullscreen(false);fullButton.current?.focus()}return}
  try{if(shell.current?.requestFullscreen){await shell.current.requestFullscreen();setFullscreen(true)}else setFullscreen(true)}catch{setFullscreen(true)}
 };
 const drag=useRef<{x:number;y:number;sx:number;sy:number}|null>(null);
 return <div ref={shell} className={"canvas-shell"+(fullscreen?" canvas-fullscreen":"")}><div className="canvas-toolbar"><span>PROCESS CANVAS · DOM / SVG</span><div><button aria-label="缩小" onClick={()=>setZoom(z=>Math.max(.65,z-.15))}><ZoomOut size={16}/></button><span>{Math.round(zoom*100)}%</span><button aria-label="放大" onClick={()=>setZoom(z=>Math.min(3,z+.15))}><ZoomIn size={16}/></button><button ref={fullButton} aria-label={fullscreen?"退出全屏":"全屏显示流程图"} title={fullscreen?"退出全屏（Esc）":"全屏显示流程图"} aria-pressed={fullscreen} onClick={toggleFullscreen}>{fullscreen?<Minimize2 size={16}/>:<Maximize2 size={16}/>}</button><button onClick={()=>setPaused(p=>!p)}>{paused?<Play size={15}/>:<Pause size={15}/>} {paused?'播放':'暂停'}</button></div></div>{error?<div className="notice red">{error}</div>:<div className="canvas-scroll" onPointerDown={e=>{if(!(e.target as Element).closest('[data-stream-id],[data-equipment-id]'))drag.current={x:e.clientX,y:e.clientY,sx:e.currentTarget.scrollLeft,sy:e.currentTarget.scrollTop}}} onPointerMove={e=>{if(drag.current&&e.buttons){e.currentTarget.scrollLeft=drag.current.sx-(e.clientX-drag.current.x);e.currentTarget.scrollTop=drag.current.sy-(e.clientY-drag.current.y)}}} onPointerUp={()=>drag.current=null} onPointerLeave={()=>drag.current=null}><div ref={ref} className="process-svg" aria-busy={!markup} style={{width:zoom*100+'%',minHeight:markup?undefined:450,aspectRatio:markup?undefined:'2 / 1'}} dangerouslySetInnerHTML={svgHtml}/></div>}<div className="canvas-foot">点击设备或流股查看工程数据和来源 · 空白处拖动平移 · 动画为原理示意</div></div>
});

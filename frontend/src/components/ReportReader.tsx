import {useState} from 'react';
import {ChevronLeft,ChevronRight,Maximize2} from 'lucide-react';

export function ReportReader({kind,pages,title,revision="r05"}:{kind:string;pages:number;title:string;revision?:string}){
 const [page,setPage]=useState(1);
 const [direction,setDirection]=useState('forward');
 const go=(next:number)=>{if(next<1||next>pages||next===page)return;setDirection(next>page?'forward':'back');setPage(next)};
 const src=`/reports/${kind}/${revision}-page-${page}.png`;
 return <div className="report-reader" tabIndex={0} aria-label={`${title}翻页阅读器`} onKeyDown={e=>{if(e.key==='ArrowRight'){e.preventDefault();go(page+1)}if(e.key==='ArrowLeft'){e.preventDefault();go(page-1)}}}>
  <div className="reader-toolbar"><span aria-live="polite">第 {page} 页 <span className="muted">/ 共 {pages} 页</span></span><a href={src} target="_blank" rel="noreferrer"><Maximize2 size={14}/>查看高清</a></div>
  <div className="reader-stage"><figure key={page} className={'reader-sheet '+direction}><img src={src} alt={`${title}第${page}页`}/></figure></div>
  <nav className="reader-controls" aria-label="报告翻页"><button onClick={()=>go(page-1)} disabled={page===1} aria-label="上一页"><ChevronLeft size={17}/>上一页</button><div className="reader-pages">{Array.from({length:pages},(_,i)=><button key={i} onClick={()=>go(i+1)} aria-label={`转到第${i+1}页`} aria-current={page===i+1?'page':undefined}>{i+1}</button>)}</div><button onClick={()=>go(page+1)} disabled={page===pages} aria-label="下一页">下一页<ChevronRight size={17}/></button></nav>
 </div>
}

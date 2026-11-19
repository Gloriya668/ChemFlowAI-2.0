import {useId} from 'react';
import {reportYears} from './publicProject';
type Props={year:number;onYear:(year:number)=>void};
const amount=(value:number)=>value.toLocaleString('zh-CN',{minimumFractionDigits:2,maximumFractionDigits:2});
export function PublicCashChart({year,onYear}:Props){
 const id='cash'+useId().replace(/[^a-zA-Z0-9_-]/g,'');
 const left=76,right=1096,top=46,bottom=326,slot=(right-left)/14;
 const y=(value:number)=>top+(15000-value)/40000*(bottom-top),zero=y(0);
 return <section className="report-cash-chart" aria-label="十四年项目税后净现金流">
 <div className="report-cash-chart-heading"><div><h3>十四年项目净现金流</h3><p>点击柱形或年份，查看当年收支</p></div><div className="report-cash-legend"><span><i className="negative"/>建设期净支出</span><span><i className="positive"/>运营期净流入</span><small>单位：万元</small></div></div>
 <div className="report-cash-scroll"><svg className="report-cash-svg" viewBox="0 0 1120 408" role="group" aria-label="建设两年、运营十二年的净现金流柱状图">
 <defs><linearGradient id={id+'-positive'} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#a1e5d2"/><stop offset="1" stopColor="#398f8a"/></linearGradient><linearGradient id={id+'-negative'} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#b7806e"/><stop offset="1" stopColor="#e5ac8e"/></linearGradient></defs>
 <rect x={left} y={top} width={slot*2} height={bottom-top} rx="8" fill="#b7806e" opacity=".035"/>
 {[10000,0,-10000,-20000].map(value=><g key={value}><line x1={left} x2={right} y1={y(value)} y2={y(value)} stroke={value===0?'#6a949f':'#31515e'} strokeWidth={value===0?1.3:.8} strokeDasharray={value===0?undefined:'3 6'}/><text x={left-12} y={y(value)+4} textAnchor="end" fill={value===0?'#b7d5dc':'#7fa1b1'} fontSize="11">{value.toLocaleString('zh-CN')}</text></g>)}
 <text x="20" y="24" fill="#7fa1b1" fontSize="10">万元</text>
 {reportYears.map((row,i)=>{const x=left+slot*(i+.5),barTop=Math.min(zero,y(row.cash)),height=Math.abs(y(row.cash)-zero),active=year===row.year;return <g key={row.year} className={'report-cash-column '+(active?'is-selected':'')} role="button" tabIndex={0} aria-pressed={active} aria-label={'项目第'+row.year+'年，'+(row.year<=2?'建设期':'运营期')+'，净现金流'+amount(row.cash)+'万元'} onClick={()=>onYear(row.year)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onYear(row.year)}else if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();const next=Math.max(1,Math.min(14,row.year+(e.key==='ArrowRight'?1:-1)));onYear(next);const parent=e.currentTarget.parentElement;const buttons=parent?.querySelectorAll<SVGGElement>('[role="button"]');buttons?.[next-1]?.focus()}}}>
 <title>{'第'+row.year+'年：'+amount(row.cash)+'万元'}</title>
 <rect className="report-cash-hit" x={x-slot/2+3} y="34" width={slot-6} height="345" rx="9" fill={active?'#345a60':'transparent'} fillOpacity={active?.35:1} stroke={active?'#75b5ab':'transparent'} strokeWidth=".8"/>
 <rect className="report-cash-bar" x={x-17} y={barTop} width="34" height={height} rx="4" fill={'url(#'+id+(row.cash<0?'-negative':'-positive')+')'} stroke={active?'#d2fff0':'transparent'} strokeWidth="1.2"/>
 <text className="report-cash-value" x={x} y={row.cash>=0?barTop-11:barTop+height+17} textAnchor="middle" fill={row.cash<0?'#e7b79e':active?'#dcfff4':'#addccc'} fontSize="11" fontWeight={active?700:500}>{amount(row.cash)}</text>
 <text x={x} y="352" textAnchor="middle" fill={active?'#def3ef':'#adc5d0'} fontSize="12" fontWeight={active?700:500}>{row.year<=2?'建设 '+row.year:'运营 '+(row.year-2)}</text>
 <text x={x} y="369" textAnchor="middle" fill="#718f9f" fontSize="9">第 {row.year} 年</text>
 </g>})}
 <path d={`M${left+10} 389H${left+slot*2-10}`} stroke="#af8374" strokeWidth="2"/><text x={left+slot} y="404" textAnchor="middle" fill="#af978a" fontSize="9">建设期</text>
 <path d={`M${left+slot*2+10} 389H${right-10}`} stroke="#4f8a82" strokeWidth="2"/><text x={(left+slot*2+right)/2} y="404" textAnchor="middle" fill="#7ab9ac" fontSize="9">运营期 · 末年回收资产余值与流动资金</text>
 </svg></div><div className="report-cash-chart-foot"><span>零轴上方为净流入，下方为净支出</span><span>金额保留两位小数</span></div>
 </section>;
}

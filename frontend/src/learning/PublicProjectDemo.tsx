import {useState} from 'react';
import {PublicCashChart} from './PublicCashChart';
import {ArrowRight,BookOpen,Download,ExternalLink,RotateCcw} from 'lucide-react';
import {publicProject as project,reportMetrics,publicReportSections} from './publicProject';
import {learningRequest} from './customApi';
const f=(n:number|null)=>n===null?'待输入':n.toLocaleString('zh-CN',{minimumFractionDigits:2,maximumFractionDigits:2});
function Table({headers,rows}:{headers:string[];rows:(string|number)[][]}){return <div className="study-table"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{r.map((v,j)=><td key={j}>{v}</td>)}</tr>)}</tbody></table></div>}
export function PublicProjectDemo({stage,rate,onRate}:{stage:number;rate:string;onRate:(value:string)=>void}){
 const [year,setYear]=useState(3),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[report,setReport]=useState('');const m=reportMetrics(rate),selected=m.years[year-1];
 const exportReport=async()=>{setBusy(true);setMessage('');try{const r=await learningRequest<{url:string;path:string}>('/api/learning/study/'+project.id+'/report',{method:'POST',body:JSON.stringify({title:project.title+' · 公开可研经济学习',sections:publicReportSections(rate)})});setReport(r.url);setMessage('已保存到 E 盘项目目录。')}catch(e){setMessage((e as Error).message)}finally{setBusy(false)}};
 return <div className="public-project-demo">
 <header className="public-project-hero"><div><span className="learn-eyebrow">PUBLIC PROJECT · ECONOMIC CASE</span><h2>{project.title}</h2><p>年产60万吨硫磺制酸及余热发电项目</p><div className="public-project-tags"><span>公开可研演示</span><span>2 年建设＋12 年运营</span><span>硫酸 · 蒸汽 · 电力</span></div></div><div className="public-project-scale"><small>项目总投资 · 万元</small><strong>{f(project.total)}</strong><span>历史可研预测 / 独立学习案例</span></div></header>
 <div className="public-project-intro"><BookOpen size={22}/><p>以园区硫酸供应和能源协同为背景，沿“建设投入—产品与能源收入—成本—现金流”学习经济评价。当前展示硫磺制酸项目，当前流程的自主测算数据单独保存。</p></div>
 <div className="public-project-process" aria-label="演示项目工艺主线">{['硫磺处理','焚硫与转化','吸收制酸','余热发电 / 供汽'].map((x,i)=><div key={x}><span>{String(i+1).padStart(2,'0')}</span><strong>{x}</strong>{i<3&&<ArrowRight size={17}/>}</div>)}</div>
 <div className="study-actions"><a href={project.pdf} target="_blank" rel="noreferrer"><BookOpen size={15}/>阅读完整报告</a><a href={project.url} target="_blank" rel="noreferrer"><ExternalLink size={15}/>公开披露文件</a><button disabled={busy} onClick={()=>void exportReport()}><Download size={15}/>{busy?'生成中…':'导出演示学习报告'}</button></div>
 {message&&<p className="study-status" role="status">{message}{report&&<a href={report}> 下载 HTML</a>}</p>}
 {stage===7?<>
 <h3>投资组成与建设安排</h3><div className="public-invest-grid"><article><span>01 建设投资</span><strong>{f(project.construction)}<small>万元</small></strong><p>建设第1年 9,600万元，第2年 22,400万元，分配比例30% / 70%。</p></article><article><span>02 建设期利息</span><strong>{f(project.interest)}<small>万元</small></strong><p>财务附表长期贷款23,000万元，贷款有效利率3.91%。</p></article><article><span>03 流动资金</span><strong>{f(project.working)}<small>万元</small></strong><p>按投产负荷分年投入；末年回收，不能每年重复扣减全部占用。</p></article></div>
 <Table headers={['财务附表资金来源','金额 / 万元','阅读要点']} rows={[
 ['资本金',f(project.equity),'其中固定资产投入9,000万元，另列流动资金。'],['债务资金（含利息）',f(project.debt),'长期贷款本金与建设期利息分开识别。'],['合计',f(project.total),'对应项目总投资；项目现金流与融资现金流口径不同。']]}/>
 <h3>产品与副产能源方案</h3><Table headers={['产出','设计年产量','报告含税价格','口径']} rows={project.products}/><p className="study-muted">价格为报告编制时的测算假设。产品组合同时包含硫酸、蒸汽和电力；不能用单一硫酸售价代表全部收入。</p>
 <h3>运营成本阅读 <small>正常生产年 · 万元</small></h3><Table headers={['费用项目','报告金额']} rows={project.costs.map(([name,value])=>[name,f(value)])}/><p className="study-muted">年经营成本30,160.37万元；折旧2,438.86万元属于非现金费用。融资利息随偿债进度变化，原表项目第3—6年分别为926.64、711.62、459.25、200.23万元。这里的第3年是首个生产年。</p>
 </>:<>
 <h3>原报告税后评价指标</h3><div className="study-kpis public-report-kpis">{[['财务净现值',f(project.published.npv),'万元 / 12%'],['财务内部收益率',f(project.published.irr),'%'],['投资回收期',f(project.published.payback),'年 / 含建设期']].map(([label,value,unit])=><div key={label}><span>{label}</span><strong>{value}</strong><small>{unit}</small></div>)}</div>
 <PublicCashChart year={year} onYear={setYear}/>
 <div className="public-year-detail"><div><span>项目第 {year} 年</span><h4>{year<=2?'建设投入期':year===3?'首年投产 · 90%负荷':year===14?'运营末年 · 回收余值':'正常生产 · 100%负荷'}</h4></div><div><span>销售收入</span><strong>{f(selected.revenue)}</strong></div><div><span>经营成本</span><strong>{f(selected.cost)}</strong></div><div><span>税后净现金流</span><strong>{f(selected.cash)}</strong></div><div><span>累计净现金流</span><strong>{f(selected.cumulative)}</strong></div></div>
 <h3>折现率练习</h3><div className="public-discount"><label>折现率<input type="number" min="0" max="100" step="0.5" value={rate} onChange={e=>onRate(e.target.value)}/><span>%</span></label><div><small>按报告净现金流重算 NPV</small><strong>{f(m.npv)}<em>万元</em></strong></div><button onClick={()=>onRate('12')}><RotateCcw size={14}/>恢复12%</button></div><p className="study-muted">改变折现率只影响现值，不改变原始收支与 IRR。净现金流按披露的两位小数重算：IRR {f(m.irr)}%，回收期 {f(m.payback)}年。原报告NPV与重算值约有0.02万元的舍入差。</p>
 {m.npv===null&&<p className="study-missing">折现率请输入0—100之间的有效数值。</p>}
 <details open><summary>展开逐年项目现金流 · 万元</summary><div className="study-table study-cash-table"><table><thead><tr><th>项目</th>{m.years.map(y=><th key={y.year}>第{y.year}年</th>)}</tr></thead><tbody>{([['revenue','销售收入'],['investment','建设投资'],['working','流动资金增量'],['cost','经营成本'],['vat','增值税'],['surcharge','税金及附加'],['incomeTax','调整所得税'],['recovery','末年余值及流动资金回收'],['cash','报告税后净现金流'],['cumulative','累计净现金流（重算）'],['discounted','折现现金流（练习）']] as const).map(([key,label])=><tr key={key}><th>{label}</th>{m.years.map(y=><td key={y.year}>{f(y[key])}</td>)}</tr>)}</tbody></table></div></details>
 </>}
 <details className="study-model-limits"><summary>报告口径与学习说明</summary><p>报告由奥福科技有限公司于{project.compiled}编制，上市公司于{project.disclosed}公开披露。采用表15-1、15-2、15-5、15-9中的财务数据；原报告金额与页面重算值分别标注。历史预测不表示项目已实现收益。</p><p>项目投资现金流表采用32,000万元建设投资；建设期利息属于融资口径，因此不会把32,972.54万元总投资再次全部扣入该表。收入与税费沿用原报告表列方式，没有直接套用原十年期模板。</p><p>原报告部分文字写“企业自筹”，财务附表列有贷款；本演示采用附表融资口径。已披露净现金流与分项相加有0.01万元级的舍入差，演示保留原净现金流。这里没有对未披露的精细工程造价作补充估算。</p></details>
 </div>;
}

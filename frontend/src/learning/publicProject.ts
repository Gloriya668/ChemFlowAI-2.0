export const publicProject={
 id:'lubei-sulfuric-acid-demo',title:'硫磺制酸与余热发电',fullTitle:'山东鲁北化工股份有限公司年产60万吨硫磺制酸及余热发电项目',
 url:'https://static.cninfo.com.cn/finalpage/2025-01-15/1222332962.PDF',pdf:'/learning-reference/lubei-sulfuric-acid-feasibility-2024.pdf',
 compiled:'2024 年 8 月',disclosed:'2025-01-15',total:32972.54,construction:32000,interest:723.96,working:248.58,equity:9248.58,debt:23723.96,
 published:{npv:10259.79,irr:18.99,payback:6.45},
 products:[['浓硫酸','612,245 吨/年','200 元/吨','产品量；项目规模以100%硫酸折算为60万吨/年'],['低压过热蒸汽','732,800 吨/年','245 元/吨','副产能源'],['低压蒸汽','288,000 吨/年','245 元/吨','副产能源'],['电','56,000,000 千瓦时/年','0.40 元/千瓦时','余热发电']],
 costs:[['外购原辅材料',27178.78],['工资及福利',487.20],['折旧',2438.86],['修理',1280],['制造其他费用',116],['管理费用（含安全生产费用）',853.49],['销售费用',244.90]] as [string,number][],
};
export const reportYears=Array.from({length:14},(_,i)=>{
 const year=i+1,production=year>2,first=year===3,last=year===14;
 return {year,load:production?(first?90:100):0,investment:year===1?9600:year===2?22400:0,
 revenue:production?(first?35545.05:39494.50):0,cost:production?(first?27434.59:30160.37):0,
 vat:production?(first?180.63:200.70):0,surcharge:production?(first?21.68:24.08):0,
 incomeTax:production?(first?1367.32:1667.62):0,working:first?247.71:year===4?0.88:0,
 recovery:last?3706.19:0,cash:year===1?-9600:year===2?-22400:first?6293.12:year===4?7440.85:last?11147.92:7441.72};
});
export function reportMetrics(rate:string){
 const value=Number(rate),valid=rate.trim()!==''&&Number.isFinite(value)&&value>=0&&value<=100;
 let cumulative=0;const years=reportYears.map(y=>({...y,cumulative:cumulative+=y.cash,discounted:valid?y.cash/(1+value/100)**y.year:null}));
 const npv=valid?years.reduce((s,y)=>s+y.discounted!,0):null;
 let lo=0,hi=1;for(let i=0;i<90;i++){const m=(lo+hi)/2;const v=reportYears.reduce((s,y)=>s+y.cash/(1+m)**y.year,0);if(v>0)lo=m;else hi=m}
 const recovery=years.findIndex((y,i)=>i>0&&y.cumulative>=0&&years[i-1].cumulative<0);
 return {years,npv,irr:(lo+hi)/2*100,payback:recovery<0?null:years[recovery].year-1+Math.abs(years[recovery-1].cumulative)/years[recovery].cash};
}
export function publicReportSections(rate='12'){
 const m=reportMetrics(rate),p=publicProject;
 return [
 {title:'独立经济演示 · '+p.fullTitle,paragraphs:['公开可行性研究报告；编制 '+p.compiled+'，披露 '+p.disclosed+'。','来源：'+p.url,'按财务附表组织：2年建设、12年生产；第一生产年90%负荷，之后100%。报告历史预测不代表已实现业绩。','这是独立的硫磺制酸项目演示，未将这些数据写入当前流程的自主测算输入。'],rows:[['投资 / 资金','万元'],['建设投资','32000.00'],['建设期利息','723.96'],['流动资金','248.58'],['总投资','32972.54'],['附表资本金','9248.58'],['附表债务资金（含利息）','23723.96']]},
 {title:'公开报告现金流学习',paragraphs:['数据采用表15-9已披露的净现金流，按第1—14年年末时点折现。','原报告税后指标：NPV 10259.79万元（12%）；IRR 18.99%；回收期6.45年（含建设期）。','当前折现率练习：'+rate+'%；NPV '+(m.npv===null?'输入无效':m.npv.toFixed(2)+'万元')+'。','按披露到两位小数的净现金流重算，与原表存在小额舍入差；未重建税务、融资与价格联动。'],rows:[['年份','负荷%','建设投资','销售收入','经营成本','增值税','税金附加','调整所得税','流动资金增量','税后净现金流','累计净现金流','折现现金流'],...m.years.map(y=>[String(y.year),String(y.load),...['investment','revenue','cost','vat','surcharge','incomeTax','working','cash','cumulative'].map(k=>(y[k as keyof typeof y] as number).toFixed(2)),y.discounted===null?'未计算':y.discounted.toFixed(2)])]}
 ];
}

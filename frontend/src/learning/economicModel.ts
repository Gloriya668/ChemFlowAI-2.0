import {economicReference as ref} from './economicReference';
export type EconomicInputs=Record<string,string>;
export const demoInputs=():EconomicInputs=>Object.fromEntries([...ref.investment,...ref.parameters].map(x=>[x.id,String(x.value)]));
export type CashYear={year:number;load:number;volume:number;revenue:number;raw:number;aux:number;power:number;steam:number;water:number;labor:number;maintenance:number;insurance:number;management:number;sales:number;cost:number;ebitda:number;depreciation:number;amortization:number;ebit:number;tax:number;profit:number;receivables:number;inventory:number;payables:number;working:number;deltaWorking:number;residual:number;cash:number;discounted:number;cumulative:number;cumulativeDiscounted:number};
export type EconomicResult={error:string[];years:CashYear[];investment:number;fixed:number;npv:number|null;irr:number|null;payback:number|null;discountedPayback:number|null};
export function calculateModel(inputs:EconomicInputs,scenario={price:0,raw:0,capex:0}):EconomicResult{
 const error:string[]=[];const n:Record<string,number>={};
 for(const item of [...ref.investment,...ref.parameters]){const value=inputs[item.id];if(value===undefined||value.trim()===''||!Number.isFinite(Number(value))){error.push(item.name+'：待填写');continue}n[item.id]=Number(value);if(n[item.id]<0)error.push(item.name+'：不能为负数');}
 if(n.p23!==undefined&&n.p23!==10)error.push('示范模型为固定十年运营期。');
 if(n.p4!==undefined&&n.p4<=0)error.push('设计产能须大于零。');
 for(const id of ['p25','p26'])if(n[id]!==undefined&&n[id]<=0)error.push('折旧与摊销年限须大于零。');
 for(const id of ['p22','p24','p32','p33'])if(n[id]!==undefined&&n[id]>1)error.push('税率、残值率和负荷率须在 0—1 范围内。');
 if(n.p31>0)error.push('非零维持性资本开支需新增资产折旧表，当前简化模型不支持，不能忽略其税效应。');
 if(Object.values(scenario).some(v=>!Number.isFinite(v)||v<=-100))error.push('情景变动须为有效数值且大于 -100%。');
 const empty:EconomicResult={error,years:[],investment:0,fixed:0,npv:null,irr:null,payback:null,discountedPayback:null};if(error.length)return empty;
 const fixed=Array.from({length:10},(_,i)=>n['capex'+(i+4)]).reduce((a,b)=>a+b,0)*(1+scenario.capex/100);const investment=fixed+n.capex15*(1+scenario.capex/100);
 const years:CashYear[]=[];let previousWorking=0,cumulative=-investment,cumulativeDiscounted=-investment;
 const zero=Object.fromEntries(['load','volume','revenue','raw','aux','power','steam','water','labor','maintenance','insurance','management','sales','cost','ebitda','depreciation','amortization','ebit','tax','profit','receivables','inventory','payables','working','deltaWorking','residual'].map(k=>[k,0]));
 years.push({...zero,year:0,cash:-investment,discounted:-investment,cumulative,cumulativeDiscounted} as CashYear);
 for(let year=1;year<=10;year++){
 const load=year===1?n.p32:year===2?n.p33:1,volume=n.p4*load,revenue=volume*n.p5*(1+scenario.price/100)/10000;
 const raw=volume*n.p6*n.p7*(1+scenario.raw/100)/10000,aux=volume*n.p8*n.p9/10000,power=volume*n.p10*n.p11/10000,steam=volume*n.p12*n.p13/10000,water=volume*n.p14*n.p15/10000;
 const labor=n.p16*n.p17/10000,maintenance=fixed*n.p18,insurance=fixed*n.p19,management=labor*n.p20,sales=revenue*n.p21,cost=raw+aux+power+steam+water+labor+maintenance+insurance+management+sales;
 const ebitda=revenue-cost,depreciation=year<=n.p25?fixed*(1-n.p24)/n.p25:0,amortization=year<=n.p26?n.capex15*(1+scenario.capex/100)/n.p26:0,ebit=ebitda-depreciation-amortization,tax=Math.max(0,ebit*n.p22),profit=ebit-tax;
 const receivables=revenue*n.p29/365,inventory=(cost-sales)*n.p28/365,payables=(raw+aux)*n.p30/365,working=receivables+inventory-payables,deltaWorking=working-previousWorking,residual=year===10?working+fixed*n.p24:0;
 const cash=profit+depreciation+amortization-deltaWorking+residual,discounted=cash/Math.pow(1+n.p27,year);cumulative+=cash;cumulativeDiscounted+=discounted;previousWorking=working;
 years.push({year,load,volume,revenue,raw,aux,power,steam,water,labor,maintenance,insurance,management,sales,cost,ebitda,depreciation,amortization,ebit,tax,profit,receivables,inventory,payables,working,deltaWorking,residual,cash,discounted,cumulative,cumulativeDiscounted});
 }
 const npv=years.reduce((a,y)=>a+y.discounted,0);const pay=(key:'cumulative'|'cumulativeDiscounted',flow:'cash'|'discounted')=>{const i=years.findIndex((y,j)=>j>0&&y[key]>=0&&years[j-1][key]<0);return i<0?null:i-1+Math.abs(years[i-1][key])/years[i][flow]};
 let irr:number|null=null;const signs=years.map(y=>Math.sign(y.cash)).filter(x=>x!==0);const changes=signs.filter((s,i)=>i>0&&s!==signs[i-1]).length;
 const f=(r:number)=>years.reduce((sum,y)=>sum+y.cash/Math.pow(1+r,y.year),0);
 if(changes===1){let lo=-.9999,hi=1;while(f(lo)*f(hi)>0&&hi<10000)hi*=2;if(f(lo)*f(hi)<=0){for(let i=0;i<180;i++){const mid=(lo+hi)/2;if(f(lo)*f(mid)<=0)hi=mid;else lo=mid}irr=(lo+hi)/2}}
 return {error:[],years,investment,fixed,npv,irr,payback:pay('cumulative','cash'),discountedPayback:pay('cumulativeDiscounted','discounted')};
}

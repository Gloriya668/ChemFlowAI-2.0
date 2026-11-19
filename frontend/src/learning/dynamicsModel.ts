export type LoopId='FC'|'PC'|'LC1'|'LC2'|'TC';
export const dynamicsReport='/learning/dynamics/dynamics-report.pdf';
export const loops:{id:LoopId;name:string;pv:string;mv:string;description:string;sign:number;tau:number;load:number;kp:number;ti:number;delay:number}[]=[
 {id:'FC',name:'进料流量',pv:'进料流量',mv:'进料阀开度',description:'测量进料流量，通过进料阀调节进入塔内的物流。',sign:1,tau:1.2,load:1,kp:1.4,ti:3,delay:0},
 {id:'PC',name:'塔顶压力',pv:'塔顶压力',mv:'冷却强度',description:'压力升高时增加冷却；压力降低时减少冷却。',sign:-1,tau:3,load:.3,kp:1.2,ti:6,delay:0},
 {id:'LC1',name:'回流罐液位',pv:'回流罐液位',mv:'塔顶采出阀开度',description:'液位升高时增加塔顶采出流量，调节回流罐库存。',sign:-1,tau:8,load:.5,kp:1,ti:12,delay:0},
 {id:'LC2',name:'塔釜液位',pv:'塔釜液位',mv:'塔底采出阀开度',description:'液位升高时增加塔底采出流量，调节塔釜库存。',sign:-1,tau:10,load:.6,kp:1,ti:15,delay:0},
 {id:'TC',name:'灵敏板温度',pv:'第 11 块板温度',mv:'再沸器加热强度',description:'第 11 块板测温，经过测量死时间，再由温控回路调整再沸器热负荷。',sign:1,tau:6,load:-.5,kp:.930137,ti:15.84,delay:.5}
];
export type DynamicsConfig={loop:LoopId;kp:number;ti:number;delay:number;sp:number;manual:number;auto:boolean;integral:boolean;disturbance:number;at:number};
export type Point={time:number;pv:number;mv:number;sp:number;feed:number};
export const clamp=(n:number,min:number,max:number)=>Math.min(max,Math.max(min,n));
export function readDynamicsConfig(notes:Record<string,string>):DynamicsConfig{
 const loop=loops.find(l=>l.id===notes['dyn-loop'])||loops[4];
 const number=(key:string,fallback:number,min:number,max:number)=>{const value=notes['dyn-'+key];const n=value===undefined||value.trim()===''?fallback:Number(value);return clamp(Number.isFinite(n)?n:fallback,min,max)};
 return {loop:loop.id,kp:number(loop.id+'-kp',loop.kp,.1,4),ti:number(loop.id+'-ti',loop.ti,1,30),delay:number(loop.id+'-delay',loop.delay,0,3),sp:number(loop.id+'-sp',50,40,60),manual:number(loop.id+'-manual',50,10,90),auto:notes['dyn-'+loop.id+'-mode']!=='manual',integral:notes['dyn-'+loop.id+'-type']!=='P',disturbance:number('disturbance',20,-30,30),at:number('at',1,.5,2)};
}
// Normalized, independent first-order teaching loops. No thermodynamics or plant solver.
// PV is % of illustrative range; MV is 0..100%. Both start at 50%.
export function calculateDynamics(config:DynamicsConfig):Record<LoopId,Point[]>{
 return Object.fromEntries(loops.map(loop=>{
  const chosen=loop.id===config.loop;
  const kp=chosen?config.kp:loop.kp,ti=chosen?config.ti:loop.ti,delay=chosen?config.delay:loop.delay;
  const auto=!chosen||config.auto,integral=!chosen||config.integral,sp=chosen?config.sp:50;
  const dt=.05,lag=Math.round(delay/dt),history:number[]=[50],points:Point[]=[];
  let pv=50,mv=50,sum=0;
  for(let step=0;step<=3600;step++){
   const minutes=step*dt;const load=minutes+1e-8>=config.at*60?config.disturbance:0;
   if(step>0){
    const measured=history[Math.max(0,history.length-1-lag)];
    const error=loop.sign*(sp-measured);
    if(auto){
     const proposed=integral?sum+kp*error*dt/ti:0;
     const raw=50+kp*error+proposed;
     // Conditional integration prevents winding up while the actuator saturates.
     if(raw>=0&&raw<=100||raw>100&&error<0||raw<0&&error>0)sum=proposed;
     mv=clamp(50+kp*error+(integral?sum:0),0,100);
    }else mv=config.manual;
    pv+=dt*(50+loop.sign*(mv-50)+loop.load*load-pv)/loop.tau;
    history.push(pv);
   }
   if(step%6===0)points.push({time:minutes/60,pv,mv,sp,feed:100+load});
  }
  return [loop.id,points];
 })) as Record<LoopId,Point[]>;
}
export function dynamicsReportParagraphs(notes:Record<string,string>){
 const c=readDynamicsConfig(notes),loop=loops.find(l=>l.id===c.loop)!;
 return ['动态控制学习参考：新疆美克 10 万 t/a 1,4-丁二醇项目，T0305 正丁醇回收塔。来源：Dynamics 动态控制模拟 PDF 第 13–21 页。',
 '报告设置：FC、PC、LC1、LC2、TC 五回路；第 11 块板测温。报告 TC 为反作用 PI，增益 0.930137 %/%、积分时间 15.84 min、微分时间 0 min（PDF 第 17 页）。',
 '教学实验：'+loop.id+' '+loop.name+'；'+(c.auto?'自动':'手动')+'；'+(c.integral?'PI':'P')+'；Kp='+c.kp+'，Ti='+c.ti+' min，测量延迟='+c.delay+' min；SP='+c.sp+'% 量程；手动 MV='+c.manual+'%。',
 '扰动：t='+c.at+' h，进料相对变化 '+c.disturbance+'%。曲线使用归一化独立一阶模型计算，不是 Aspen 结果或原报告曲线复现。',
 '学习观察：'+(notes['dyn-observation']||'待填写。')];
}
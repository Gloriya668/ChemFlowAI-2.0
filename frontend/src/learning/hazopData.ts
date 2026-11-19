export type RiskCode='L'|'M'|'H'|'E';
// Transcribed from the supplied safety appraisal, PDF p.111, figure 8-10.
// The seven frequency bands differ from the five likelihood levels on p.109.
export const riskMatrix:RiskCode[][]=[['M','M','H','E','E'],['M','M','M','H','E'],['L','M','M','H','H'],['L','L','M','M','H'],['L','L','L','M','M'],['L','L','L','L','M'],['L','L','L','L','L']];
export const frequencyBands=['10⁻¹～1','10⁻²～10⁻¹','10⁻³～10⁻²','10⁻⁴～10⁻³','10⁻⁵～10⁻⁴','10⁻⁶～10⁻⁵','10⁻⁷～10⁻⁶'];
export const severityLevels=['低后果','较低后果','中后果','高后果','很高后果'];
export const riskLabels:Record<RiskCode,{label:string;action:string}>={L:{label:'低',action:'核对现有控制是否持续有效，记录维护、检查与复核安排。'},M:{label:'中',action:'明确改进措施、负责人和计划时间，持续跟踪落实情况。'},H:{label:'高',action:'优先组织复核，明确临时控制与永久改进措施，跟踪措施有效性。'},E:{label:'很高',action:'升级评审并优先研究风险降低方案；由负责团队核定行动与约束。'}};
export const guideWords=[
 {id:'NO',name:'无',meaning:'设计意图完全未实现',parameter:'流量',deviation:'无流量',example:'检查泵停运、阀门关闭或管线堵塞等可能原因。'},
 {id:'LESS',name:'少',meaning:'数量低于设计意图',parameter:'流量',deviation:'流量过低',example:'检查输送能力、过滤器阻力及进料配比变化。'},
 {id:'MORE',name:'多',meaning:'数量高于设计意图',parameter:'压力',deviation:'压力过高',example:'检查调节失效、出口受阻及高压物料进入。'},
 {id:'PART OF',name:'部分',meaning:'仅实现部分设计功能',parameter:'组成',deviation:'缺少部分组分',example:'检查配料不完整以及关键组分缺失对反应、分离的影响。'},
 {id:'AS WELL AS',name:'伴随',meaning:'在设计功能外出现额外情况',parameter:'组成',deviation:'混入额外组分',example:'检查空气、水分或杂质进入对设备及物料的影响。'},
 {id:'REVERSE',name:'相逆',meaning:'出现与设计意图相反的情况',parameter:'流向',deviation:'反向流动',example:'检查压差反转及防倒流措施失效的可能性。'},
 {id:'OTHER THAN',name:'异常',meaning:'设计意图被其他情况替代',parameter:'介质',deviation:'错误介质进入',example:'检查错接管线、错投物料或切换错误。'}
];
export const hazopNodes=[
 {id:'tank',name:'储罐',boundary:'储罐及其进出料、气相和排放接口',intent:'在规定液位、压力和介质条件下储存与转运。'},
 {id:'alkyne',name:'炔化反应器',boundary:'反应器及进料、换热和压力控制接口',intent:'维持进料配比与反应条件，控制热量和物料积累。'},
 {id:'hydrogenation',name:'加氢反应器',boundary:'加氢反应器及氢气、物料、换热接口',intent:'按规定配比和温压条件完成反应。'},
 {id:'pipe',name:'管道',boundary:'两设备或边界之间的管段与阀门',intent:'按规定流向、流量、压力和组成输送物料。'},
 {id:'pump',name:'泵',boundary:'泵体、吸入排出管段与相关控制',intent:'提供所需流量与压力，并保持输送系统完整性。'},
 {id:'column',name:'精馏塔',boundary:'精馏塔及进料、采出、回流和换热接口',intent:'在规定温压、液位和流量范围内完成分离。'},
 {id:'exchanger',name:'换热器',boundary:'换热器冷热两侧、阀门与测控接口',intent:'完成所需换热，保持两侧介质及压力边界。'},
 {id:'compressor',name:'压缩机',boundary:'压缩机及吸入排出、控制和置换接口',intent:'在规定流量、压力与气体组成下压缩输送。'}
];
export type HazopRow={id:string;node:string;parameter:string;guide:string;deviation:string;cause:string;consequence:string;safeguard:string;recommendation:string};
// Concise case extracts and review prompts, not a declaration of installed protection.
export const hazopRows:HazopRow[]=[
 {id:'tank-pressure',node:'tank',parameter:'压力',guide:'MORE',deviation:'储罐压力过高',cause:'入口压力调节阀失效，高压物料进入。',consequence:'超压损坏或泄漏；可燃物外逸后可能引发火灾、爆炸。',safeguard:'调节阀维护；泄压及其安全接收系统。',recommendation:'核对入口压力边界、阀门失效状态和泄压去向。'},
 {id:'tank-level',node:'tank',parameter:'液位',guide:'MORE',deviation:'储罐液位过高',cause:'进料阀故障、开度过大或全开。',consequence:'溢流、物料外逸，影响相邻设备与人员。',safeguard:'液位指示、高液位报警及操作响应。',recommendation:'核对测量、报警与进料切断之间的响应链。'},
 {id:'alkyne-temp',node:'alkyne',parameter:'温度',guide:'MORE',deviation:'炔化反应温度过高',cause:'加热介质温度控制失效或温差过大。',consequence:'反应条件偏离、压力升高，可能导致泄漏及火灾爆炸。',safeguard:'加热介质温控、高温报警和独立联锁。',recommendation:'核对热源条件、控制独立性与反应热移除能力。'},
 {id:'hydrogen-temp',node:'hydrogenation',parameter:'温度',guide:'MORE',deviation:'加氢反应温度过高',cause:'加热介质温度异常，温控失效。',consequence:'反应失控、超压或物料外逸。',safeguard:'温度测量报警、加热系统联锁及操作响应。',recommendation:'明确异常温度下的停止进料、热源控制和处置逻辑。'},
 {id:'hydrogen-pressure',node:'hydrogenation',parameter:'压力',guide:'MORE',deviation:'加氢系统压力过高',cause:'入口压力调节阀故障开启，高压物料进入。',consequence:'设备及管线超压，泄漏后可能形成可燃气体混合物。',safeguard:'阀门预防性维护、泄压及安全接收。',recommendation:'核对承压边界、泄压工况与排放接收接口。'},
 {id:'pipe-flow',node:'pipe',parameter:'流量',guide:'MORE',deviation:'进料管道流量过大',cause:'进料调节阀故障开启或全开。',consequence:'下游进料配比失衡，反应及压力异常。',safeguard:'流量指示与报警，异常工况联锁。',recommendation:'核对下游异常响应、切断及泄压设施的适用性。'},
 {id:'pipe-leak',node:'pipe',parameter:'密闭性',guide:'OTHER THAN',deviation:'连接部位泄漏',cause:'连接失效或软管脱落。',consequence:'物料泄漏、人员暴露，可能引发火灾爆炸。',safeguard:'连接方式、完整性检查与维护。',recommendation:'逐项确认连接结构、检查周期和泄漏发现方式。'},
 {id:'pump-flow',node:'pump',parameter:'流量',guide:'MORE',deviation:'泵送流量过大',cause:'进料调节阀故障，开度超出正常范围。',consequence:'下游反应配比与热量积累异常，可能导致超压。',safeguard:'进料流量报警、异常联锁及下游防护。',recommendation:'将泵送能力与下游允许工况、响应措施一并核对。'},
 {id:'column-flow',node:'column',parameter:'流量',guide:'LESS',deviation:'精馏塔进料流量过小',cause:'管道或过滤器堵塞。',consequence:'进料配比及分离工况偏离，影响下游运行。',safeguard:'进料比例控制、低流量报警和操作响应。',recommendation:'核对堵塞监测、低流量处置及相关联锁。'},
 {id:'column-temp',node:'column',parameter:'温度',guide:'MORE',deviation:'精馏温度过高',cause:'加热介质温度过高或温控失效。',consequence:'塔内物料温压上升，可能出现超压与泄漏。',safeguard:'热媒温控、高温报警和独立停热措施。',recommendation:'核对热媒温度上限、控制独立性和异常热量处置。'},
 {id:'column-level',node:'column',parameter:'液位',guide:'MORE',deviation:'塔内液位过高',cause:'进料阀故障、进料量过大。',consequence:'物料溢流或进入非预期设备、区域。',safeguard:'液位报警、进料切断及溢流接收。',recommendation:'核对液位测点、切断逻辑与溢流最终去向。'},
 {id:'exchanger-hot',node:'exchanger',parameter:'温度',guide:'MORE',deviation:'换热器出口温度过高',cause:'加热介质温度过高或控制失效。',consequence:'下游温压条件偏离，可能导致泄漏及反应异常。',safeguard:'热媒温控、高温报警与停热联锁。',recommendation:'在满足工艺要求的前提下，研究限制热媒温度的方案。'},
 {id:'exchanger-cold',node:'exchanger',parameter:'温度',guide:'LESS',deviation:'换热温度过低',cause:'环境温度过低或保温伴热不足。',consequence:'物料黏度增大、凝结或堵塞，影响生产。',safeguard:'保温与伴热。',recommendation:'核对物性、低温边界和保温伴热的适用性。'},
 {id:'compressor-flow',node:'compressor',parameter:'流量',guide:'LESS',deviation:'压缩机流量过小',cause:'管道或过滤器堵塞。',consequence:'下游进料配比失衡，影响反应和压力状态。',safeguard:'低流量报警、异常联锁与操作响应。',recommendation:'核对进料比例控制、切断条件与异常处置。'},
 {id:'compressor-air',node:'compressor',parameter:'组成',guide:'AS WELL AS',deviation:'气体中混入空气',cause:'投用前设备内空气未充分置换。',consequence:'可燃气体与空气形成危险混合物。',safeguard:'投用或检修后的置换程序及检查。',recommendation:'核对置换边界、检测判据和确认记录。'}
];
export type RiskPosition={row:number;column:number};
export function readRisk(value:string|undefined):RiskPosition|null{if(!value)return null;try{const p=JSON.parse(value);return Number.isInteger(p.row)&&p.row>=0&&p.row<7&&Number.isInteger(p.column)&&p.column>=0&&p.column<5?p:null}catch{return null}}
export function riskText(position:RiskPosition|null){return position?severityLevels[position.column]+' / '+frequencyBands[position.row]+' 次/年 / '+riskLabels[riskMatrix[position.row][position.column]].label+'风险':'未选择'}
export function hazopExportRows(notes:Record<string,string>){return [['节点','偏差','可能原因','潜在后果','防护核对项','改进记录','措施前学习判断','措施后学习判断','负责人 / 计划日期','进度','复核依据'],...hazopRows.map(r=>{const prefix='hazop-'+r.id+'-';return [hazopNodes.find(n=>n.id===r.node)!.name,r.deviation,r.cause,r.consequence,r.safeguard,notes[prefix+'action']??r.recommendation,riskText(readRisk(notes[prefix+'before'])),riskText(readRisk(notes[prefix+'after'])),(notes[prefix+'owner']||'待分配')+' / '+(notes[prefix+'due']||'待安排'),notes[prefix+'status']||'待分析',notes[prefix+'evidence']||'待填写']})]}
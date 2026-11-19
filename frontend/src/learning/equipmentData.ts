import type {Equipment,LearningCase} from './types';
export type Family='mixing'|'reactor'|'tube'|'fixed'|'column'|'extraction'|'separator'|'heat'|'multiheat'|'pump'|'compressor'|'valve'|'splitter';
export type Variant={id:string;name:string;description:string;tradeoff:string};
export type Parameter={name:string;unit:string;meaning:string;watch:string};
export type Part={name:string;description:string};
export type Profile={family:Family;title:string;principle:string;variants:Variant[];parameters:Parameter[];parts:Part[];patent?:keyof typeof patents;context:string;divided?:boolean;reactive?:boolean;absorption?:boolean;threePhase?:boolean;liquidOnly?:boolean;multistage?:boolean};
const v=(id:string,name:string,description:string,tradeoff:string):Variant=>({id,name,description,tradeoff});
const p=(name:string,unit:string,meaning:string,watch:string):Parameter=>({name,unit,meaning,watch});
const part=(name:string,description:string):Part=>({name,description});
export const patents={
 distributor:{title:'让低负荷下的液体也能均匀分布',number:'WO2025219807A1',date:'2025-10-23',owner:'Koch-Glitsch',url:'https://patents.google.com/patent/WO2025219807A1/en',idea:'在槽式分布器的溅流挡板上增加横向蓄液通道和分流孔，让液体再次铺展后进入填料。',question:'可探索：低液量润湿、孔口堵塞与分布均匀性的平衡。',scope:'适用于填料段液体分布的设计讨论；不代表本案例已经采用该方案。'},
 reactor:{title:'可拆卸的分室式连续流反应器',number:'US20250312765A1',date:'2025-10-09',owner:'Stoli Catalysts',url:'https://patents.google.com/patent/US20250312765A1/en',idea:'转轴上的多个叶轮配合可抽出的挡板内件，把反应空间分成相互连通的小室，并考虑内件拆卸间隙。',question:'可探索：混合、轴向返混与检修便利性的平衡。',scope:'这是带搅拌的连续流结构拓展，不等同于理想平推流，也不是丙烯氯化的已验证设备配置。'},
 heat:{title:'螺旋折流与管孔间隙协同设计',number:'US20250146767A1',date:'2025-05-08',owner:'Lummus Technology',url:'https://patents.google.com/patent/US20250146767A1/en',idea:'在螺旋折流板上交替安排不同的管孔间隙，调整壳程旁流路径，同时保留对换热管的支撑。',question:'可探索：传热、压降与机械支撑之间的平衡。',scope:'图中螺旋结构为通用原理示意，并未复现该专利的完整几何或性能。'}
};
const impellers=[v('pitched','斜叶桨','倾斜叶片形成轴向循环，帮助上下层流体交换。','需综合黏度、液位及功率选择；转得更快不一定混得更经济。'),v('rushton','圆盘涡轮','圆盘周围的直叶片形成径向射流，常用于研究气液分散。','局部剪切与功耗较高，气量变化会改变负载。'),v('hydrofoil','水翼桨','流线形叶片以泵送循环为主要目标。','具体适用范围取决于叶型、黏度和含气率。'),v('anchor','锚式桨','近壁的大直径桨扫过釜壁附近，适合比较黏性流体混合。','近壁间隙与传热重要；不是高强度气体分散的通用替代。')];
const trays=[v('sieve','筛板塔','气体穿过筛孔，液体横向流过塔板并经降液管逐级下降。','关注低负荷漏液、高负荷夹带及液泛。'),v('valve-tray','浮阀塔','浮阀开度随气体负荷变化，形成气液接触区。','运动件需考虑结垢、磨损和检修。'),v('structured','规整填料塔','交错波纹片形成连续接触表面，气液逆流穿行。','液体分布不均、壁流和润湿不足会损害效果。'),v('random','散堆填料塔','环形填料随机堆积，形成气液接触和流动通道。','同时权衡压降、比表面积、持液量及堵塞倾向。')];
const coreParams=[p('温度','°C','改变相平衡、反应速率和材料适用性。','结合物系与热稳定性确定；此处不设工况值。'),p('压力 / 压降','bar / kPa','影响相态、流体密度和上下游驱动力。','设备允许压力与过程操作压力需分别确认。')];
const mixParams=[...coreParams,p('混合强度 / 桨速','W/m³ / rpm','描述机械混合的能量投入与桨叶运动。','只适用于有搅拌器的结构，Mixer 模块本身不计算桨速。'),p('停留时间 / 黏度','s / mPa·s','决定混匀所需时间与流动状态。','需要结合实际容积、流量和流变特性。')];
const columnParams=[...coreParams,p('气液负荷','m³/h','决定接触程度与塔内水力学状态。','需检查液泛、夹带、漏液或润湿不足。'),p('级数 / 填料高度','级 / m','描述分离接触程度。','理论级数不等于实际塔板数；填料需传质模型或等板高度换算。'),p('回流比 / 热负荷','— / kW','精馏中连接分离效果与冷凝、再沸能耗。','吸收与萃取的主要调节量不同，不直接套用精馏回流比。')];
const catalog:Record<Family,Omit<Profile,'context'>>={
 mixing:{family:'mixing',title:'管式静态混合器',principle:'多股物流进入水平管道，依次通过固定内件，发生分流、转向和重组。混合由流体通过内件时的流动实现；图中以剖面展示管式结构，内件保持静止，光点表示物流方向。',variants:[v('static','交替螺旋内件','相邻固定螺旋片交替改变流束方向，使流体沿管道连续分割与重组。','需结合流量、黏度、混合长度及允许压降选择内件。'),v('lattice','交叉格栅内件','交错排列的固定格栅把流体分成多条路径，在相邻单元间重新分配。','应兼顾混合均匀性、流动阻力及含固体介质的清洁维护。')],parameters:[...coreParams,p('处理流量 / 管内流速','m³/h / m/s','描述通过管道的流体量以及轴向流动速度。','需要结合管径、相态和上下游供压确定。'),p('黏度 / 流动状态','mPa·s / —','影响流束分割、径向交换及流动阻力。','应依据介质性质与流量判断内件适用范围。'),p('管径 / 混合段长度','mm / m','与内件型式、数量共同影响混合过程。','示意图中的尺寸与内件数量不构成设备设计值。'),p('出口混合均匀性','评价指标','用于评价出口截面上的组成分布。','需通过合适的计算或取样评价，动画不提供混合性能结论。')],parts:[part('进料 / 注入口','主物流由管端进入，另一股物流可由上方支口引入；实际接口按流程进料组织。'),part('固定混合内件','可选择交替螺旋片或交叉格栅；内件静止，物流在其间分割与重组。'),part('管体 / 连接法兰','水平管体容纳混合段，两端法兰连接相邻管路；剖开外壳用于观察内部。'),part('混合出口','物流从末端流出并连接后续单元，出口均匀性需另行评价。')]},
 reactor:{family:'reactor',title:'反应器结构探索',principle:'化学计量模型描述反应与转化关系，不能据此确定实际反应器。这里提供搅拌釜内件作为结构学习选项。',variants:impellers,parameters:[...mixParams,p('反应时间 / 热移除','s / kW','关联反应进程与放热或吸热控制。','需有动力学、热效应和实际传热条件才能定量判断。')],parts:[part('驱动与轴封','驱动轴传递扭矩；密封应按介质、压力和温度选型。'),part('搅拌桨','选型影响轴向循环、径向剪切与近壁流动。'),part('夹套 / 挡板','夹套提供热交换通道；挡板影响循环模式。'),part('釜底出料','低点排出物料，需兼顾持液、清洗和固体沉积。')]},
 tube:{family:'tube',title:'管式反应器',principle:'流体沿轴向连续通过反应空间。理想平推流假设没有轴向返混；结构示意并不能证明真实流场符合该假设。',variants:[v('plain','空管','连续反应通道，展示物流从入口到出口的推进。','轴向温度梯度和径向混合需单独分析。'),v('insert','静态内件','固定混合元件增加径向交换的结构选项。','可能改变压降、停留时间分布及壁面传热，需重新验证。'),v('jacket','夹套管','外部热媒通道与反应管隔离，表示热量跨壁传递。','换热能力受传热面积、温差和污垢影响。')],parameters:[...coreParams,p('停留时间 / 轴向分布','s / m','跟踪反应物沿长度方向的变化。','需要反应动力学和有效容积；动画粒子不是停留时间计算。'),p('传热系数 / 热通量','W/(m²·K) / W/m²','描述管壁与介质的热交换。','放热、热点和材料耐蚀性应与具体反应体系匹配。')],parts:[part('反应物流入口','入口分配与混合状态影响后续反应区。'),part('轴向反应通道','选择空管、静态内件或夹套，比较结构差别。'),part('管壁 / 热媒侧','隔离反应物与热媒；图中蓝色流道为独立通道。'),part('反应物流出口','轴向组成、温度与转化率需由反应模型计算。')],patent:'reactor'},
 fixed:{family:'fixed',title:'催化床层结构探索',principle:'展示流体通过静止催化剂床层的结构选项。RStoic 模块不包含床层尺寸、水力学或催化剂失活模型。',variants:[v('axial','轴向固定床','流体沿床层轴向通过催化剂颗粒。','需兼顾床层压降、分布均匀性和温度梯度。'),v('radial','径向固定床','流体从外环分布区穿过环形床层进入中心集流管。','需设计内外筛网、径向分布及装卸空间。')],parameters:[...coreParams,p('空速 / 接触时间','h⁻¹ / s','联系进料量与催化剂装填量。','应说明体积流量基准与空速定义。'),p('颗粒尺度 / 床层压降','mm / kPa','影响流动阻力、传质与装填。','颗粒破碎、结焦及分布不均需要评估。')],parts:[part('入口分布器','使流体进入催化区，减少偏流。'),part('催化剂床层','颗粒保持静止；运动光点表示流体，不表示颗粒流化。'),part('支承网 / 集流管','支承和约束颗粒，同时留出流动通道。'),part('出口汇集段','汇集反应后物流，并提供温度与压降监测位置。')]},
 column:{family:'column',title:'塔器内构件',principle:'气相向上、液相向下，借助塔板或填料增加接触。切换结构用于比较原理，并不自动改变案例的模拟级数或分离结果。',variants:trays,parameters:columnParams,parts:[part('进液 / 分布器','填料塔通过分布器铺液；板式塔通过进液位置和降液管组织液流。'),part('传质内件','塔板或填料提供气液接触空间；几何切换仅为结构学习。'),part('降液管 / 支承','板式塔经降液管输送液体；填料塔用支承与再分布装置。'),part('塔底接触区','气体上升进入接触区，液体汇集后由下部离开。')],patent:'distributor'},
 extraction:{family:'extraction',title:'液液萃取塔',principle:'两种互不完全相溶的液体接触，使溶质在两相间分配。图中的液滴代表分散相，不是气泡。',variants:[v('structured','填料萃取塔','液液两相沿填料接触，分散相液滴在连续相中移动。','需确认润湿性、相反转、乳化和液泛边界。'),v('sieve','筛板萃取塔','孔板促进液滴分散并形成逐段接触。','液滴尺寸和聚并会影响分离，不能套用气液塔效率。'),v('disc','转盘萃取塔','旋转盘与静止环配合，提供可调的液液分散。','机械能输入增加，同时需评估返混和乳化。')],parameters:[...coreParams,p('溶剂比 / 分配关系','—','影响溶质从原料相向溶剂相转移。','取决于物系平衡与操作温度。'),p('液滴尺寸 / 相流量','mm / m³/h','影响相界面积、滑移速度及分离。','太细的液滴可能增加乳化和下游分相难度。')],parts:[part('轻相出口 / 重相进料','按密度和相连续性安排端部接口。'),part('液液接触区','填料、筛板或转盘用来组织两液相接触。'),part('分散相液滴','运动液滴仅表示相间接触方向。'),part('重相出口 / 轻相进料','端部需留出沉降与相分离空间。')]},
 separator:{family:'separator',title:'相分离容器',principle:'闪蒸模型按平衡关系分相，真实容器还需沉降、除沫、液位与界面控制。液液分相不等同于闪蒸汽化。',variants:[v('gravity','重力沉降','借助相间密度差分离，观察持液区和分相界面。','需要足够停留时间，细小液滴或乳化物可能难以分开。'),v('coalescer','聚结内件','在分相区增加通道或聚结介质，促进液滴汇合。','效果受润湿性、固体污染和堵塞影响。')],parameters:[...coreParams,p('液位 / 界面高度','m','决定持液量和出口相别。','液液分相需分别考虑总液位和两液相界面。'),p('停留时间 / 液滴尺度','min / μm','影响沉降与夹带。','需结合密度差、黏度和实际流量选容积。')],parts:[part('入口缓冲','减小入口动量，避免直接冲击分相区。'),part('分相区 / 内件','重力沉降或聚结介质促进相分离。'),part('液位 / 分相界面','界面是教学示意，不对应本案例相含量。'),part('各相出口','按气、轻液、重液相分别引出；实际相别由模型决定。')]},
 heat:{family:'heat',title:'换热设备',principle:'两侧流体隔壁交换热量。HeatX 描述两物流换热；Heater 是加热或冷却模块，不能单凭模块名称确定换热器硬件。',variants:[v('segmental','弓形折流板','壳程流体绕过交替布置的折流板，横向冲刷管束。','折流间距会影响传热、压降及振动。'),v('helical','螺旋折流板','倾斜布置的导流板组织近似螺旋的壳程流动。','需兼顾旁流、管束支撑和制造装配。'),v('plate','板式换热芯','冷热通道交替排布，通过薄板传热。','需评估介质兼容性、通道堵塞与密封条件。')],parameters:[...coreParams,p('热负荷 / 端温差','kW / K','确定换热任务及驱动温差。','相变工况需分段理解，不能只看单一平均温度。'),p('面积 / 污垢热阻','m² / m²·K/W','影响可实现的传热能力。','污垢会降低性能；还需检查压降与可清洗性。')],parts:[part('管程入口','一股流体进入管束；板式结构中为一组独立通道。'),part('换热面','管壁或板片分隔两侧流体，并传递热量。'),part('壳程 / 导流内件','另一股流体沿折流路径流动，避免与管程混合。'),part('流体出口','动画表示流动方向，不代表实际温度或热负荷。')],patent:'heat'},
 multiheat:{family:'multiheat',title:'多流股换热芯',principle:'多股物流通过隔开的通道交换热量，示意采用板翅式芯体。MHeatX 并不强制指定这种机械结构。',variants:[v('straight','直通翅片','平行翅片构成独立物流通道。','需兼顾流动分配、换热面积和压降。'),v('serrated','错列翅片','短翅片交错布置，使边界层反复发展。','强化传热的同时可能提高阻力和清洁要求。')],parameters:[...coreParams,p('各流股热负荷','kW','追踪多股物流间的能量平衡。','需逐段排查温度交叉及最小温差。'),p('通道分配 / 最小温差','— / K','影响不同流股的换热匹配。','总热量平衡并不保证每个温区都可实现。')],parts:[part('分流集箱','把各股物流送入各自独立通道。'),part('翅片芯体','翅片和隔板提供传热面积与支撑。'),part('隔板 / 封条','相邻通道可以传热，物流不混合。'),part('出口集箱','汇集每一股物流，再连接到后续设备。')]},
 pump:{family:'pump',title:'离心泵剖面',principle:'旋转叶轮向液体传递机械能，蜗壳汇集流体并实现部分动能向压力能转换。',variants:[v('closed','闭式叶轮','叶片由前后盖板包围，形成封闭流道。','通常需关注清洁度、磨损间隙与检修可达性。'),v('open','半开式叶轮','展示开放一侧的叶片流道。','需控制叶轮间隙，并按介质颗粒情况核实适用性。')],parameters:[p('流量 / 扬程','m³/h / m','共同确定泵的工作点。','应与管路系统曲线匹配。'),p('转速 / 效率','rpm / %','影响机械功率和运行范围。','动画转速不是泵的真实操作设定。'),p('汽蚀余量','m','比较装置可提供的余量与泵的需求。','入口温度、压力和管路阻力均会影响汽蚀风险。'),p('密封 / 材料','类型','匹配介质腐蚀性及泄漏控制需求。','Pump 模块不替代机械选型。')],parts:[part('轴向吸入口','液体进入叶轮中心。'),part('叶轮与轴','叶轮旋转把机械能传给流体。'),part('蜗壳 / 密封','蜗壳汇集流体，轴封限制泄漏。'),part('切向排出口','流体从蜗壳出口进入下游管路。')]},
 compressor:{family:'compressor',title:'气体压缩机',principle:'压缩机对气体做功，压力与温度随之变化。多级压缩可在级间安排冷却；图示为可比较的机械结构。',variants:[v('centrifugal','离心式','叶轮提高气体动能，扩压段参与压力恢复。','需检查运行范围、喘振与密封。'),v('reciprocating','往复式','活塞周期性改变气缸容积，吸排气阀组织单向流动。','需考虑脉动、阀片、润滑与机械负荷。')],parameters:[...coreParams,p('压比 / 级数','—','描述压缩任务的分配。','级间冷却条件与允许排气温度共同影响选型。'),p('效率 / 轴功率','% / kW','联系热力学压缩过程与驱动能耗。','应区分等熵效率、多变效率及机械效率。')],parts:[part('吸气段','入口气体状态决定体积流量与压缩起点。'),part('叶轮 / 活塞','不同结构以不同方式向气体做功。'),part('扩压段 / 气阀','离心式通过扩压组织压力恢复，往复式由气阀控制方向。'),part('排气 / 级间冷却','多级装置还需分析级间冷却与凝液分离。')]},
 valve:{family:'valve',title:'节流阀内部结构',principle:'阀内件改变有效流通面积并产生压力损失。Valve 模块常用于节流过程建模，不直接描述阀芯几何。',variants:[v('globe','单座阀芯','阀杆带动阀芯改变阀座附近的通流间隙。','关注阀权度、气蚀、噪声与冲蚀。'),v('cage','笼式内件','带孔套筒组织阀芯周围的流动。','孔口设计需结合压差与介质，不能仅按外观替换。')],parameters:[...coreParams,p('流量系数 / 开度','Cv 或 Kv / %','联系阀内流动能力与操作位置。','系数基准不同，不能混用；开度与流量不总是线性。'),p('相变 / 临界流动','状态','压降可能造成闪蒸、汽蚀或阻塞流。','需结合上下游压力与流体性质判断。')],parts:[part('上游入口','流体进入阀体。'),part('阀芯 / 阀座','移动阀芯改变局部流通面积。'),part('阀杆 / 执行机构','把控制动作传递给阀芯。'),part('下游出口','承接节流后的物流，可能发生相态变化。')]},
 splitter:{family:'splitter',title:'物流分配节点',principle:'FSplit 按指定比例把一股物流分配为多股。它是模拟分流节点，不意味着真实设备已经包含控制阀。',variants:[v('tee','三通分流','展示一进两出的管路拓扑。','真实分配由支路阻力与压力共同决定。'),v('controlled','带调节的支路','在两条支路示意调节内件与分配控制。','控制阀为教学扩展，需实际控制方案支持。')],parameters:[p('分流比','—','给出进入各支路的比例。','各支路比例应闭合；模型设定不代表真实自平衡。'),p('支路流量','kg/h 或 m³/h','描述分配给每条路径的物流量。','质量与体积基准需明确。'),p('支路压降','kPa','影响真实分配与调节能力。','不能仅以 FSplit 的分流比完成管路选型。')],parts:[part('总管入口','一股物流进入分流节点。'),part('分叉节点','连续流道形成多条路径。'),part('支路调节件','仅在调节结构选项中示意。'),part('支路出口','流向不同工艺目的地，组分分布不等于相分离。')]}
};
const caseNotes:Record<string,string>={
 'hydrocarbon-mixing':'重点观察三股进料汇合；模型不包含混合器几何或混合时间。',
 'two-stage-flash':'两级闪蒸需分别理解各级平衡状态与出口相别。',
 'liquid-decanting':'这里是液液分相，应关注两液相界面、乳化与聚并。',
 'multistage-compression':'关注级间冷却如何连接压缩各级；内图为机械结构选项。',
 'two-stream-heat-exchange':'关注冷热两股流体隔壁换热及两侧压降。',
 'multistream-heat-exchange':'关注多股物流在不同温区的热量匹配，通道颜色不表示组分。',
 'ethylbenzene-styrene-distillation':'乙苯与苯乙烯分离需结合压力、热敏性与聚合倾向考虑。',
 'acetone-absorption':'这是气液吸收，主要观察吸收剂与气体逆流接触，不配置精馏再沸回路。',
 'isopropanol-extraction':'这是液液萃取，轻重相密度及连续相选择需结合物系确认。',
 'butene-isomerization':'本案例用 RStoic 描述异构化；搅拌釜是拓展结构示意，非已经确认的硬件。',
 'propylene-chlorination':'本案例为丙烯氯化；结构比较不提供投料、温压或放大操作配方。',
 'extractive-distillation':'萃取精馏依靠溶剂改变分离行为；还需考虑溶剂回收与循环。',
 'ethanol-azeotropic':'共沸精馏与液液分相相互关联，回流相选择会影响流程。',
 'thf-pressure-swing':'两个压力等级构成变压精馏；各塔的负荷和内件需分别设计。',
 'ethyl-acetate-reactive':'反应区与分离区共存；催化形式需单独指定，图中标出反应区域而不默认固体催化填料。',
 'methanol-double-effect':'双效结构通过热量耦合减少外部供热需求，需核对两侧温差。',
 'dividing-wall-column':'中部隔壁划分预分离与主分离区域，液体和蒸气的分配需要单独设计。',
 'propylene-heat-pump':'压缩机、换热段与精馏塔共同组成热泵回路，需结合整体热量匹配。',
 'styrene-dehydrogenation':'催化反应段展示固定床结构选项；其余设备按各自单元操作解读。',
 'styrene-sidechain-alkylation':'综合流程按真实设备清单逐台展开；功能段不是一台实体设备。'
};
export function getProfile(c:LearningCase,e:Equipment):Profile{
 const m=e.module.toLowerCase();let family:Family='mixing';
 if(m.includes('multifrac')||m.includes('radfrac')||m==='absorber')family='column';
 else if(m==='extract')family='extraction';
 else if(m==='rplug')family='tube';
 else if(m==='rstoic')family=c.id.startsWith('styrene-')?'fixed':'reactor';
 else if(m.includes('flash')||m==='decanter')family='separator';
 else if(m==='mheatx')family='multiheat';
 else if(m==='heatx'||m==='heater')family='heat';
 else if(m==='pump')family='pump';
 else if(m.includes('compr'))family='compressor';
 else if(m==='valve')family='valve';
 else if(m==='fsplit')family='splitter';
 const result:Profile={...catalog[family],context:caseNotes[c.id]||c.summary,divided:m==='multifrac',reactive:m.includes('reac-dist'),absorption:c.id==='acetone-absorption'||m==='absorber',threePhase:m==='flash3',liquidOnly:m==='decanter',multistage:m==='mcompr'};
 if(result.absorption)result.parameters=[...coreParams,p('液气比','基准需注明','描述吸收剂流量与气体处理量的匹配。','需结合吸收平衡、传质和溶剂再生条件。'),p('填料高度 / 接触级数','m / 级','提供吸收所需接触程度。','需核实润湿、液泛和吸收热。')];
 if(result.divided)result.parameters=[...columnParams,p('隔壁段分配','—','控制隔壁两侧气液分配。','几何与分配方案需相互匹配。')];
 if(result.reactive)result.parameters=[...columnParams,p('反应区持液 / 反应速率','m³ / 模型相关','把反应停留与传质分离联系起来。','需按均相或非均相反应选择模型和内件。')];
 if(e.details?.principle)result.principle=e.details.principle;
 if(e.details?.parameters?.length)result.parameters=e.details.parameters;
 if(e.details?.internals){result.parts=[...result.parts];result.parts[1]={...result.parts[1],description:e.details.internals}}
 return result;
}

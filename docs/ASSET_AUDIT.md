# 资产审计
- Stitch 实际路径：E:/Desktop/AIchemflow/stitch_chemflow_ai_platform_prototype.zip（需求路径少一级目录）。已完整读取 DESIGN.md 与全部 12 套 code.html，并核对各页标题、导航、卡片、表格、表单、按钮、图表/流程画布、交互钩子与断点类。页面覆盖入口、工作台、Step01–09，以及 Step04 深入分析页。参考 HTML 含在线 Tailwind、字体、图片与示例工程数值，只提取设计，不作为运行资源或工程数据。
- PDH：E:/Desktop/丙烯丙烷数据最最最最终版.xls，原生 BIFF Excel。物流分 A、B、C，C 有耦合前/后，默认采用后者；含能量结果。预处理用 xlrd，运行时不依赖 Excel。
- Pyridine：E:/Desktop/四氢糠醇_所有流股结果.xlsx，13 股、9 组分、源存档计算警告与异常低温。预处理用 openpyxl。
- E:/CodexOutputs/Aspen流程可视化：4 SVG、离线 HTML（内嵌动画 SVG）、PNG、builder 与 JSON。复用 HTML 中原始 SVG，不重新绘制；只加入 DOM 标识、状态与数据绑定。
- 四氢糠醇最新资产是 6 设备 13 流股开循环版本，和结果表一致。旧图含 DECANTER/RE；数据不含这些流股，不把旧图混接到新数据。未来回流版本需独立 topology/data/asset 修订。
- 原资产参数文字含标准答案。不可置于 frontend/public；预处理删除流股数值、title 原值和备注后存放后台，通过有步骤检查的项目端点提供。数据由当前 SimulationResult 绑定。
- 新目录此前不存在；没有发现适用的额外 AGENTS.md。不改动桌面原文件。

## 全部 Stitch 页面清单
- landing_page: AI辅助化工流程设计与多目标优化；HTML 33057 字符；只作布局参考。
- project_dashboard: 年产30万吨生物质基乙二醇绿色合成示范工程；HTML 45764 字符；只作布局参考。
- step_01: Step 01: 需求与设计基准输入; 原料进料信息 (Feedstock Specifications); 目标产品要求 (Target Product Specifications)；HTML 38778 字符；只作布局参考。
- step_02: Step 02: 物性与数据校核 (Data &amp; Properties)；HTML 39367 字符；只作布局参考。
- step_03: Step 03: 模型选择与验证; 热力学活度与相平衡模型 (Phase Equilibrium); 反应动力学与热力学反应模型 (Reaction Kinetics)；HTML 44494 字符；只作布局参考。
- step_04: Step 04: 路线与分离筛选 (方案概览与初筛); 方案 A; 方案 B；HTML 37905 字符；只作布局参考。
- step_04_a: 方案 B 深度解析与微观特性; 1. 工艺路线全景说明 (Process Route Blueprint); 2. 关键设计参数预估占位面板 (Engineering Specification Placeholders)；HTML 48329 字符；只作布局参考。
- step_05: Step 05: 流程搭建与求解收敛 (Flowsheet Simulation &amp; Solver Convergence)；HTML 45127 字符；只作布局参考。
- step_06: Step 06: 能量与设备分析 (Thermal Pinch &amp; Equipment Rating); 余热梯级利用与全厂减碳效益核算 (Eco-Energy Ledger)；HTML 49556 字符；只作布局参考。
- step_07: Step 07: 参数与方案多目标优化 (AI-Driven Multi-Objective Optimization)；HTML 46480 字符；只作布局参考。
- step_08: Step 08: 经济与环境评价 (Techno-Economic &amp; Life-Cycle Assessment); 经济性关键指标 (TEA Metrics); 环境与双碳指标 (LCA &amp; ESG)；HTML 45076 字符；只作布局参考。
- step_09: Step 09: 复核与成果交付 (Engineering Review &amp; Package Delivery); 成果文件交付清单；HTML 53379 字符；只作布局参考。

## 全量 Stitch 视觉与交互归纳

- 共用结构：固定深色 Header、左侧工程导航、12 栏内容网格、工程 Inspector、底部阶段操作条；采用 64px 顶栏、玻璃质感面板、细描边与青色操作强调。
- 响应式：原页面依赖 `sm`、`md`、`lg`、`xl`、`2xl` 工具类，内容网格从窄屏单列逐步展开；长表和流程画布独立横向滚动。
- 阶段组件：Step01 输入卡片与边界表单；Step02 物性表格和校核图；Step03 候选模型卡和验证条件；Step04 路线比较及 Step04_A 工艺详情；Step05 可缩放、可暂停的工程画布；Step06 能量与设备报表；Step07 变量控制与多目标空间；Step08 TEA/LCA 指标区；Step09 复核清单、签核与成果清单。
- 全局控件：状态徽标、进度、来源提示、主次按钮、审核勾选、抽屉/模态、警告块、图表工具栏与导出动作。页面中的项目数值只作为视觉参考，未进入 ChemFlow 运行数据。
- ChemFlow 保留上述布局语言并把内容改为真实数据状态；缺少优化变量、物性或经济输入时显示空状态，不沿用参考页面的预填指标。

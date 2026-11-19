from pathlib import Path
import json,hashlib
P=Path(r'E:\CodexOutputs\ChemFlowAI')
for d in ['config','tests','data/validation/pdh','data/validation/pyridine','data/replay','data/assets','runtime/projects','frontend/src/styles','frontend/src/components','frontend/src/pages']:(P/d).mkdir(parents=True,exist_ok=True)
def write(n,t):(P/n).write_text(t,encoding='utf-8')
write('docs/ASSET_AUDIT.md','''# 资产审计
- Stitch 实际路径：E:/Desktop/AIchemflow/stitch_chemflow_ai_platform_prototype.zip（需求路径少一级目录）。已解压 DESIGN.md 和 12 套 screen.png/code.html；重点检查 01、02、07 布局。参考 HTML 含在线 Tailwind、字体、图片与示例工程数值，只提取设计，不作为运行资源。
- PDH：E:/Desktop/丙烯丙烷数据最最最最终版.xls，原生 BIFF Excel。物流分 A、B、C，C 有耦合前/后，默认采用后者；含能量结果。预处理用 xlrd，运行时不依赖 Excel。
- Pyridine：E:/Desktop/四氢糠醇_所有流股结果.xlsx，13 股、9 组分、源存档计算警告与异常低温。预处理用 openpyxl。
- E:/CodexOutputs/Aspen流程可视化：4 SVG、离线 HTML（内嵌动画 SVG）、PNG、builder 与 JSON。复用 HTML 中原始 SVG，不重新绘制；只加入 DOM 标识、状态与数据绑定。
- 四氢糠醇最新资产是 6 设备 13 流股开循环版本，和结果表一致。旧图含 DECANTER/RE；数据不含这些流股，不把旧图混接到新数据。未来回流版本需独立 topology/data/asset 修订。
- 原资产参数文字含标准答案。不可置于 frontend/public；预处理删除流股数值、title 原值和备注后存放后台，通过有步骤检查的项目端点提供。数据由当前 SimulationResult 绑定。
- 新目录此前不存在；没有发现适用的额外 AGENTS.md。不改动桌面原文件。
''')
write('docs/ARCHITECTURE.md','''# 架构
React/TypeScript/Vite/Tailwind → 同源 FastAPI → 持久化 JSON Project → 9 步服务端状态机 → 6 个受步骤约束的工程 Skill → Pydantic SimulationIR → typed SimulatorAdapter。
专业数值只有源表回放或确定性公式。无 LLM 服务时采用可审计的规则规划器，明确显示 RULE ENGINE；不得声称模型自主模拟。
ReferenceReplayAdapter 读取 data/replay，严格匹配已知输入，不把修改后的输入套进旧答案。DWSIM/Aspen adapter 返回未连接。
GoldenEvaluator 是唯一读取 data/validation/**/ground_truth.json 的运行模块，仅 Step 09 调用。上游 API 和技能不读取这些文件。Demo Step 05 的回放来自独立标记的 reference fixture（同一 Aspen 存档血缘），不构成盲验证。
数据/拓扑/原动画在后台。前端打包不包含结果或 benchmark。API 对 future step、result、canvas、comparison、evaluation、report 分别设访问门槛。
更新设计基准/模型/路线会要求 invalidate 确认并清空后续结果和审核记录。服务端只允许按顺序确认。存储为原子写入、锁保护，刷新恢复。
本地服务仅监听 127.0.0.1；完整运行用 FastAPI 提供 Vite dist，无 CDN 和公网调用。
''')
write('docs/DESIGN_SYSTEM.md','''# ChemFlow Design System
来源：reference/stitch_chemflow_ai_platform_prototype/chemflow_ai_workbench/DESIGN.md。
保留 Technical Precision + Restrained Glassmorphism。背景 #070B14，surface #0F131D；面板 rgba(11,19,43,.65)，active rgba(17,30,61,.75)。Cyan #00E5FF 当前/动作；Green #00E676 已验证；Amber #FFB300 人工复核；Red #FF3D71 错误；Purple #7C4DFF 优化预览。
字体 system UI/Segoe UI/Microsoft YaHei，工程数值 Consolas/Cascadia Mono。没有本地品牌字体时不联网。
4px 基础节奏，1px 描边，4–8px 圆角。顶部 66px、导航 224px、Inspector 280px、底部 64px，中央自适应。
Step01：设计基准卡片 + 右侧完整性诊断。Step02：顶部质量摘要、左主表、右侧输入物性范围/缺失说明与QA。Step07：左侧参数控制、中央目标空间、下方候选决策。没有优化器时只显示可追溯参考点，不绘制伪造 Pareto 前沿。
''')
write('config/validation_thresholds.json',json.dumps({'temperature_abs_C':0.05,'pressure_abs_bar':0.005,'mass_flow_relative':0.0001,'material_balance_relative':0.001,'energy_relative':0.0001},indent=2))
write('config/simulators.json',json.dumps({'reference_replay':{'enabled':True},'dwsim':{'enabled':False,'endpoint':None},'aspen_mcp':{'enabled':False,'endpoint':None,'allowed_tools':['load_model','set_feed','set_unit_parameter','solve','get_streams','get_duties']}},indent=2))
skills=[('chemflow-intake',[1],'将自然语言、表单、JSON 输入规范化为 ProjectSpec；在 Step 01 调用。','识别组件、进料、T/P/流量、反应、产品目标、产能、公用工程及限制。保留缺失数据为 null；单位归一化并记录原单位和来源。检查有限数、正流量、非负绝对压力。不得计算产率、补造产品量或调用模拟器。'),('chemflow-property-modeling',[2,3],'校核物性输入与候选模型适用性；在 Step 02–03 调用。','识别烃类/极性非理想体系；PR/SRK/PRSV 或 NRTL 仅为规则候选，不等于验证通过。缺少 Tc/Pc、BIP、实验VLE须显示 MISSING。人工确认接受候选模型及未验证风险。不得把存档使用的方法视为独立模型验证。'),('chemflow-process-synthesis',[4,5],'组织路线筛选和类型化流程 IR；在 Step 04–05 调用。','只使用已确认 ProjectSpec、模型与输入拓扑。检查唯一 ID、连接完整性、设备引用、进出料界限。用户选路线后生成 SimulationIR。保留已有拓扑；不填数值流股结果，不生成 COM path。'),('chemflow-simulation-review',[5,6],'审核 Adapter 结果、异常与物料衡算；在 Step 05–06 调用。','检查 result source、匹配输入、stream completeness、T/P、相态、物料衡算及 solver 状态。原始异常保留。Replay 成功只表示加载完成，convergence 为 REPLAY_NOT_SOLVED。未提供能量边界时不可宣布能量闭合。异常需要人工记录接受或拒绝。'),('chemflow-optimization-tea',[6,7,8],'定义优化变量边界与确定性经济环境核算；在 Step 06–08 调用。','明确决策变量、bounds、constraints、objective。未连接优化器时保存场景为未求解；仅比较标注来源的参考结果，不画伪前沿。TEA 必需 basis_year/currency/hours/feed_price/product_price/utility_price/method；缺失返回 NOT_CALCULATED。没有成本关联及投资数据不能给 CAPEX/NPV/IRR/回收期。'),('chemflow-validation',[9],'仅在 Step 09 用 GoldenEvaluator 对照标准数据并生成交付包。','检查 workflow、映射、拓扑、T/P/流量、质量/能量误差，阈值读取 config/validation_thresholds.json。只本 Skill/GoldenEvaluator 获准读 ground_truth；上游禁止读。Replay independent_numerical_validation 始终 NOT_ASSESSED，不能将同源相等称为独立精度。')]
registry=[]
for name,steps,desc,rules in skills:
 folder=P/'skills'/name;(folder/'references').mkdir(parents=True,exist_ok=True)
 (folder/'SKILL.md').write_text(f'---\nname: {name}\ndescription: {desc}\n---\n\n# 工程规程\n\n触发步骤：{steps}。其他步骤返回 WRONG_STEP，不执行工程工具。\n\n{rules}\n\n读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。\n',encoding='utf-8')
 (folder/'references'/'contract.md').write_text(f'# 工程契约\n输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。\n允许步骤：{steps}。\n来源类型：USER_INPUT/ASPEN_REFERENCE/RULE/CALCULATED/SIMULATOR。\n禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。\n{rules}\n',encoding='utf-8')
 registry.append({'name':name,'steps':steps,'description':desc})
write('config/skills.json',json.dumps(registry,ensure_ascii=False,indent=2))
write('docs/SKILLS_ARCHITECTURE.md','# 工程 Skills\n\n'+ '\n'.join(f"- {x['name']}：Step {x['steps']}，{x['description']}" for x in registry)+'\n\n通过受步骤限制的确定性工具执行。SkillResult 是结构化 Inspector 输出，Skill 不是数据库或模拟器。tests/test_engine.py 验证正确/错误触发和防止上游标准答案访问。\n')
write('backend/__init__.py','')
write('requirements.txt','fastapi==0.142.2\nuvicorn==0.54.0\npydantic==2.13.5\nopenpyxl==3.1.5\nxlrd==2.0.2\npytest==9.1.1\nhttpx==0.28.1\n')
write('.gitignore','.venv/\nfrontend/node_modules/\nruntime/\n__pycache__/\n.pytest_cache/\n')
print('Asset audit, architecture, design tokens specification and six skills created.')

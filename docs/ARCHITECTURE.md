# 架构
React/TypeScript/Vite/Tailwind → 同源 FastAPI → 持久化 JSON Project → 9 步服务端状态机 → 6 个受步骤约束的工程 Skill → Pydantic SimulationIR → typed SimulatorAdapter。
专业数值只有源表回放或确定性公式。无 LLM 服务时采用可审计的规则规划器，明确显示 RULE ENGINE；不得声称模型自主模拟。
ReferenceReplayAdapter 读取 data/replay，严格匹配已知输入，不把修改后的输入套进旧答案。DWSIM/Aspen adapter 返回未连接。
GoldenEvaluator 是唯一读取 data/validation/**/ground_truth.json 的运行模块，仅 Step 09 调用。上游 API 和技能不读取这些文件。Step 05 的回放来自独立标记的 reference fixture（同一 Aspen 存档血缘），不构成盲验证。
数据/拓扑/原动画在后台。前端打包不包含结果或 benchmark。API 对 future step、result、canvas、comparison、evaluation、report 分别设访问门槛。
更新设计基准/模型/路线会要求 invalidate 确认并清空后续结果和审核记录。服务端只允许按顺序确认。存储为原子写入、锁保护，刷新恢复。
本地服务仅监听 127.0.0.1；完整运行用 FastAPI 提供 Vite dist，无 CDN 和公网调用。

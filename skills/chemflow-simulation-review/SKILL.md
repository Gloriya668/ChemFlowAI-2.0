---
name: chemflow-simulation-review
description: 审核 Adapter 结果、异常与物料衡算；在 Step 05–06 调用。
---

# 工程规程

触发步骤：[5, 6]。其他步骤返回 WRONG_STEP，不执行工程工具。

检查 result source、匹配输入、stream completeness、T/P、相态、物料衡算及 solver 状态。原始异常保留。Replay 成功只表示加载完成，convergence 为 REPLAY_NOT_SOLVED。未提供能量边界时不可宣布能量闭合。异常需要人工记录接受或拒绝。

读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。

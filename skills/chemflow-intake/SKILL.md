---
name: chemflow-intake
description: 将自然语言、表单、JSON 输入规范化为 ProjectSpec；在 Step 01 调用。
---

# 工程规程

触发步骤：[1]。其他步骤返回 WRONG_STEP，不执行工程工具。

识别组件、进料、T/P/流量、反应、产品目标、产能、公用工程及限制。保留缺失数据为 null；单位归一化并记录原单位和来源。检查有限数、正流量、非负绝对压力。不得计算产率、补造产品量或调用模拟器。

读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。

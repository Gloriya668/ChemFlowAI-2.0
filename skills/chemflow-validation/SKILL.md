---
name: chemflow-validation
description: 仅在 Step 09 用 GoldenEvaluator 对照标准数据并生成交付包。
---

# 工程规程

触发步骤：[9]。其他步骤返回 WRONG_STEP，不执行工程工具。

检查 workflow、映射、拓扑、T/P/流量、质量/能量误差，阈值读取 config/validation_thresholds.json。只本 Skill/GoldenEvaluator 获准读 ground_truth；上游禁止读。Replay independent_numerical_validation 始终 NOT_ASSESSED，不能将同源相等称为独立精度。

读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。

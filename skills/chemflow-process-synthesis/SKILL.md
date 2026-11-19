---
name: chemflow-process-synthesis
description: 组织路线筛选和类型化流程 IR；在 Step 04–05 调用。
---

# 工程规程

触发步骤：[4, 5]。其他步骤返回 WRONG_STEP，不执行工程工具。

只使用已确认 ProjectSpec、模型与输入拓扑。检查唯一 ID、连接完整性、设备引用、进出料界限。用户选路线后生成 SimulationIR。保留已有拓扑；不填数值流股结果，不生成 COM path。

读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。

---
name: chemflow-property-modeling
description: 校核物性输入与候选模型适用性；在 Step 02–03 调用。
---

# 工程规程

触发步骤：[2, 3]。其他步骤返回 WRONG_STEP，不执行工程工具。

识别烃类/极性非理想体系；PR/SRK/PRSV 或 NRTL 仅为规则候选，不等于验证通过。缺少 Tc/Pc、BIP、实验VLE须显示 MISSING。人工确认接受候选模型及未验证风险。不得把存档使用的方法视为独立模型验证。

读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。

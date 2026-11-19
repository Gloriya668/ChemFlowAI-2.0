---
name: chemflow-optimization-tea
description: 定义优化变量边界与确定性经济环境核算；在 Step 06–08 调用。
---

# 工程规程

触发步骤：[6, 7, 8]。其他步骤返回 WRONG_STEP，不执行工程工具。

明确决策变量、bounds、constraints、objective。未连接优化器时保存场景为未求解；仅比较标注来源的参考结果，不画伪前沿。TEA 必需 basis_year/currency/hours/feed_price/product_price/utility_price/method；缺失返回 NOT_CALCULATED。没有成本关联及投资数据不能给 CAPEX/NPV/IRR/回收期。

读取 [工程契约](references/contract.md) 核对输入、输出与禁止项。调用 backend.skills.execute_skill，输出 SkillResult，包含 skill、step、status、observation、evidence、risk、recommendation、action_required。

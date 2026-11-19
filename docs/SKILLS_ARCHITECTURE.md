# 工程 Skills

- chemflow-intake：Step [1]，将自然语言、表单、JSON 输入规范化为 ProjectSpec；在 Step 01 调用。
- chemflow-property-modeling：Step [2, 3]，校核物性输入与候选模型适用性；在 Step 02–03 调用。
- chemflow-process-synthesis：Step [4, 5]，组织路线筛选和类型化流程 IR；在 Step 04–05 调用。
- chemflow-simulation-review：Step [5, 6]，审核 Adapter 结果、异常与物料衡算；在 Step 05–06 调用。
- chemflow-optimization-tea：Step [6, 7, 8]，定义优化变量边界与确定性经济环境核算；在 Step 06–08 调用。
- chemflow-validation：Step [9]，仅在 Step 09 用 GoldenEvaluator 对照标准数据并生成交付包。

通过受步骤限制的确定性工具执行。SkillResult 是结构化 Inspector 输出，Skill 不是数据库或模拟器。tests/test_engine.py 验证正确/错误触发和防止上游标准答案访问。

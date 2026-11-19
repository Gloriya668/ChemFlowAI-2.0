# 工程契约
输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。
允许步骤：[9]。
来源类型：USER_INPUT/REFERENCE_DATA/RULE/CALCULATED/SIMULATOR。
禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。
检查 workflow、映射、拓扑、T/P/流量、质量/能量误差，阈值读取 config/validation_thresholds.json。只本 Skill/GoldenEvaluator 获准读 ground_truth；上游禁止读。Replay independent_numerical_validation 始终 NOT_ASSESSED，不能将同源相等称为独立精度。

# 工程契约
输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。
允许步骤：[5, 6]。
来源类型：USER_INPUT/REFERENCE_DATA/RULE/CALCULATED/SIMULATOR。
禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。
检查 result source、匹配输入、stream completeness、T/P、相态、物料衡算及 solver 状态。原始异常保留。Replay 成功只表示加载完成，convergence 为 REPLAY_NOT_SOLVED。未提供能量边界时不可宣布能量闭合。异常需要人工记录接受或拒绝。

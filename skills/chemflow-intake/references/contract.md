# 工程契约
输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。
允许步骤：[1]。
来源类型：USER_INPUT/REFERENCE_DATA/RULE/CALCULATED/SIMULATOR。
禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。
识别组件、进料、T/P/流量、反应、产品目标、产能、公用工程及限制。保留缺失数据为 null；单位归一化并记录原单位和来源。检查有限数、正流量、非负绝对压力。不得计算产率、补造产品量或调用模拟器。

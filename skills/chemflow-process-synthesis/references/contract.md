# 工程契约
输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。
允许步骤：[4, 5]。
来源类型：USER_INPUT/REFERENCE_DATA/RULE/CALCULATED/SIMULATOR。
禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。
只使用已确认 ProjectSpec、模型与输入拓扑。检查唯一 ID、连接完整性、设备引用、进出料界限。用户选路线后生成 SimulationIR。保留已有拓扑；不填数值流股结果，不生成 COM path。

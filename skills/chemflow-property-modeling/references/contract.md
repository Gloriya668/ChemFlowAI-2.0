# 工程契约
输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。
允许步骤：[2, 3]。
来源类型：USER_INPUT/REFERENCE_DATA/RULE/CALCULATED/SIMULATOR。
禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。
识别烃类/极性非理想体系；PR/SRK/PRSV 或 NRTL 仅为规则候选，不等于验证通过。缺少 Tc/Pc、BIP、实验VLE须显示 MISSING。人工确认接受候选模型及未验证风险。不得把存档使用的方法视为独立模型验证。

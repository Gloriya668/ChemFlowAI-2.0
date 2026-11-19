# 求解器适配器

统一输入为 ProjectSpec + SimulationIR，输出为 SimulationResult。ReferenceReplayAdapter 用于原有参考回放；DWSIMAdapter 已实现官方 MCP stdio 工具调用及模板绑定，具体配置见 [Agent 与 DWSIM 接入说明](Agent与DWSIM接入说明.md)。ExternalMCPAdapter 仍为未实现占位，不在本次 DWSIM 接入的可用能力清单内。

真实求解依赖可信且已审核的 DWSIM 模板。模板和非进料参数以 SHA256 绑定，预检和求解失败明确报错，不回退到历史数值。独立结果采用 SIMULATOR 来源；独立验证不读标答。

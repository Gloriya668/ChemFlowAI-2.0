# Agent 与 DWSIM 接入

本版将原有“规则工作流 + 大模型问答”扩展为有持久化记录的工具型 Agent，并实现官方 DWSIM MCP 的 stdio 适配。API Key、base_url、model 仍然留空。

## 原来缺什么，本版补了什么

|缺口|本版处理|边界|
|---|---|---|
|大模型只能聊天|增加观察、选择工具、执行、检查、答复循环|最多六次工具调用，不允许执行模型生成的代码|
|没有任务和记忆|任务、工具输入输出、答案及最近任务摘要持久化|同项目一次一个任务；重启标记中断，不盲目重放|
|DWSIMAdapter 只有报错|官方 MCP 握手、加载流程、核对物性/组分、设置进料、预检、求解、提取和保存结果|Windows x64 / DWSIM 10.2.11；需要已审核的流程模板|
|无停止和失败控制|队列上限、请求停止、工具上限、模型请求超时、DWSIM 独立进程硬超时|停止在当前模型/工具调用结束后生效；求解超时杀掉独立进程|
|并发可能覆盖工程|求解前后检查项目 revision|工况变更后拒绝写入旧结果|
|真实结果被当作回放|真实结果标记 SIMULATOR / DWSIM / SOLVED；单独做质量衡算|不把收敛当作实验验证，不混入参考表格或静态财务报告|
|无结果审计|输入指纹、模板哈希、MCP 操作轨迹、错误及 solved.dwxmz|失败记录也保存，不回退到历史结果|
|工具范围不明确|inspect_project、check_design_basis、search_knowledge、simulator_status、run_simulation、material_balance|求解需用户在当前 Step 05 勾选允许；人工审核不可由模型代签|

## 启动

1. 依原安装方式运行 `Setup-Offline.ps1 -PythonExe <Python3.12路径>`，或使用已有本项目虚拟环境。
2. 编辑 `config/llm.json` 的三个空字符串。兼容 Chat Completions 文本接口，Agent 使用经过校验的 JSON 行动协议。
3. 安装 DWSIM 运行包：

```powershell
.\Setup-DWSIM.ps1 -RuntimeZip "C:\路径\dwsim-10.2.11-win-x64.zip"
```

省略 RuntimeZip 时下载固定版本的官方便携包。**`dwsim-windows.zip` 是源码，不能传作运行包。** 安装脚本核验官方 SHA256，将运行包放到本项目 vendor 目录，不关闭系统防护、不创建系统服务。

4. 运行 `Start-ChemFlow.cmd`。进入项目，使用“工程 Agent 任务”。“检测 DWSIM 连接”是真实启动和 MCP 握手，不是配置存在性检查。
5. 本机真实引擎测试：

```powershell
.\.venv\Scripts\python.exe scripts\dwsim_smoke.py
```

该测试新建水加热器，检查出口 350 K 和质量流量 1 kg/s；不读取回放结果。执行结果写入 `runtime/dwsim-smoke.json`。

## 为你的丙烷/吡啶项目登记流程

已有项目保存的是设备拓扑和历史结果，设备参数中有大量空字典，并不是完整可求解的 DWSIM 模型。不能根据拓扑图推断反应动力学、塔板数、再沸器规格、物性二元参数与循环初值。

1. 在 DWSIM 中建立或核对实际 `.dwxmz` / `.dwxml` 模型，包括反应、物性、设备规格、回流和收敛设置。使用可信模型文件，模型内可能包含自定义脚本。
2. 项目按原流程完成 Step 01–04。在 Agent 面板点击“查看模板登记信息”，得到当前基准、IR 指纹和标签映射骨架。
3. 在 `config/dwsim.json` 的 `models` 中增加以 route_id 为键的记录。将上述 JSON 的 `basis_sha256`、`ir_sha256` 和映射字段复制进去，填写真实 template 路径、template_sha256、DWSIM 的准确标签和物性包名称。相对路径从项目根目录解析。
4. 流程文件的 SHA256 和对象标签可用下列只读工具检查：

```powershell
.\.venv\Scripts\python.exe scripts\inspect_dwsim.py "C:\路径\你的流程.dwxmz"
```

`stream_map`：平台物流 ID → DWSIM MaterialStream 标签。`unit_map`：平台设备 ID → DWSIM 设备标签。`component_map`：平台组分 ID → DWSIM 组分数据库名称。三者必须完整且一一对应。

`property_package_names` 必须与模型实际物性包名称集合一致，登记前必须核对其与 Step 03 选型是否一致。`duty_map` 是平台设备 ID → DWSIM `dwsim_unitop_get_results` 返回的负荷属性名称；只接受 W/kW/MW 并转换为 kW。未登记负荷时结果标记缺失，绝不当作零能耗。

注册指纹绑定了非进料条件和完整 IR。进料温度、压力、质量流量可以变化；摩尔流量须与组成和质量流量一致。进料组成必须与模板相符，变化后需在 DWSIM 中修改模型再重新核对登记。此限制也避开了所核对版本 MCP 组成接口的描述与实现不一致问题：描述是质量分数，但实现调用 SetCompoundMassFlow，本版不依赖该接口修改多组分进料。

模板更改、反应/物性/约束或流程改变后，重新审核并更新哈希。哈希证明文件/基准未变化，**不能证明反应机理和模型参数本身正确**。

## 工作流与工具

- 自然语言任务可要求检查设计基准、查询内置参考、核对已保存的质量衡算。大模型回答需要人工复核。
- Step 05 选择 DWSIM 后，可以直接点击运行按钮，也可勾选“允许本次任务运行一次 DWSIM”让 Agent 调用。运行不会自动跨越审核步骤。
- 历史任务按项目保存，刷新后可查看。给模型的历史上下文仅包含最近三个完成任务的摘要。
- 多任务全局至多四个待执行/运行任务、两个工作线程；每个项目最多一个 Agent 任务。Agent 时间检查上限 480 秒，正在进行的请求仍受独立请求超时控制。
- `/api/projects/{pid}/agent/runs` 支持 POST 创建和 GET 列表；`/{rid}` 获取详情；`/{rid}/cancel` 请求停止。
- `/api/dwsim/status` 只说明是否配置；`POST /api/dwsim/test` 才实际连接。
- `runtime/solver-runs/<id>/run.json` 保存求解原始记录；成功时同目录包含 `solved.dwxmz`。工程交付包增加 Agent 记录。

## 已验证与仍需补充的部分

自动化测试验证协议、单位转换、状态隔离、持久化与失败处理；没有以模拟测试充当真实求解验证。当前机器 Windows 应用程序控制拒绝加载官方 `DWSIM.Thermodynamics.dll`（0x800711C7），并拒绝本地编译 MCP 可执行文件（WinError 4551）。需要管理员依据组织策略核对可信发布文件，程序不会更改防护策略。大模型凭据仍空，在线规划效果尚未实测。

完整工程设计仍需要用户的实际流程模型、物性/反应数据及实验对照。本版不自动编造这些数据。自定义工艺仍处于原版路线录入边界，不声称任意自然语言都能直接生成可求解流程。Step 07 仍是优化问题和基线管理，**未实现自动参数优化器或声称得到全局最优解**；Step 08 是有依据的部分年度化核算，不是完整投资估算。能量衡算需完整焓流边界，暂不声明闭合。多人生产部署还需要身份认证、数据权限和独立作业服务；当前启动器只监听 127.0.0.1。

## 来源与构建

- 当前官方源码：[DanWBR/dwsim10](https://github.com/DanWBR/dwsim10)。本版核对并包含 MCP 源码提交 `770c46680c72e3966fc1ff2e31698d341ffba670`。
- 官方便携运行包：[v10.2.11](https://github.com/DanWBR/dwsim10/releases/tag/v10.2.11)，SHA256：`2c244be938684ec5db8abde4f861ed484179968b90f0380347bf8f78d0fa0e79`。
- 自动化文档：[DWSIM Automation](https://dwsim.org/wiki/index.php?title=Automation)。旧仓库：[DanWBR/dwsim](https://github.com/DanWBR/dwsim)。
- `tools/dwsim-mcp-src` 保存官方 MCP 源码及 GPL-3.0 许可证；`tools/dwsim-mcp-bin` 是针对上述运行包编译的附加启动文件。引擎对应源码保留官方发布/仓库链接，示例来自用户提供的源码包。
- `scripts/rebuild_dwsim_mcp.py --runtime <运行包目录> --dotnet <.NET10 SDK路径>` 可重新构建。源文件本身未改变，构建脚本以官方运行包 DLL 替代整仓 ProjectReference，并合并便携运行依赖清单。
- `examples/dwsim` 的 Cavett 与吡啶—水分离算例用于检查接口，不等同于用户完整工艺。原始 186 个流程的文件清单和源码 ZIP 哈希见 `DWSIM-source-inventory.json`。

本版保留 DWSIM 及其 MCP 的原始许可证；运行包与本项目源码分别交付。未将 ChemFlowAI 用户代码擅自更改为其他许可证。

> 最新交付（2026-10-23）：请先阅读 **开始使用_最新Demo.md**。下面保留项目历史文档。

# ChemFlow AI · 智模拟·绿化工

当前运行版本 **V3 / 2026-10-10-v3**：新任务默认真实 DWSIM；保留原始来源；连接失败不保留旧成功状态；启动时识别旧服务。详见 [修复与验收](docs/V3真实运行修复与验收.md)。真实模型与真实工艺端到端验证仍未完成，不宣称生产就绪。下方为知识库及历史版本记录。

当前为 **知识库与数据集 V2**：79 条知识资料；统一 SFT 数据 116/22/38 条（训练/开发/测试）。入口：[V2 交付说明](docs/知识库V2交付说明.md)、[数据与测试用例手册](training/README.md)。下方为历史版本记录。

2026-10-10 知识库训练版：新增 21 个 DWSIM 官方案例、IDAES 成本资料、50 条检索文档及已训练的轻量排序器。大语言模型尚未微调。见 [知识库与训练说明](docs/知识库与训练说明.md)，训练结果见 `training/evaluation.json`。以下旧版验收数字仅对应其原版本。

2026-10-08 改进版。本地工程工作台，数据保存在本文件夹的 runtime/projects，无需指定盘符。改动和待补清单见 docs/改进说明与待补资料.md。

## 启动

双击 `Start-ChemFlow.cmd`，在浏览器打开 `http://127.0.0.1:8765`。停止服务运行 `Stop-ChemFlow.ps1`。

本工作目录已安装运行环境。在另一台电脑首次安装时，解压整个文件夹，准备 Windows x64 Python 3.12，然后运行（替换Python路径）：

```powershell
powershell -ExecutionPolicy Bypass -File .\Setup-Offline.ps1 -PythonExe "C:\Python312\python.exe"
.\Start-ChemFlow.cmd
```

程序安装仅使用项目内附带的 wheels。前端已编译，启动无需 Node 或联网；修改前端后，在 frontend 目录运行 pnpm install --frozen-lockfile 和 pnpm build。查看外部文献需要网络。

正式工作区不附带自动测试任务。新建项目可在Step1点击“载入资料中的设计基准”。本次42项后端测试通过，两套浏览器流程通过。

## 工程流程

创建工程任务后按顺序完成九个阶段，每步需要人工确认。第 05 步在载入工程归档结果后显示来源与求解状态；连接独立求解器之前，不会宣称完成独立模拟。第 07 步仅接受有来源的优化变量；没有变量数据时保留空状态。第 08 步只计算具备完整输入的指标。第 09 步复核来源与工程状态并导出报告和成果包。

## 目录

`backend/`、`frontend/`、`config/`、`data/`、`skills/`、`docs/`、`tests/`、`offline_wheels/`。任务状态保存在 `runtime/projects`。原始 Excel 保持不变。


## 大模型接入
进入项目后使用“大模型工程助手”。详见 [配置说明](docs/大模型接入说明.md) 与 [测试报告](docs/大模型接入测试报告.md)。


## Agent 与 DWSIM（2026-10-10）

新增有工具调用和持久化轨迹的工程 Agent，以及官方 DWSIM MCP 适配器。先填写 `config/llm.json`，再运行 `Setup-DWSIM.ps1` 安装固定版本运行包；实际工艺还须登记已审核的 DWSIM 流程模板。

详见 [Agent 与 DWSIM 接入说明](docs/Agent与DWSIM接入说明.md) 和 [验收报告](docs/Agent验收报告.md)。本机真实引擎运行受 Windows 应用程序控制阻断，未声称已完成工艺求解。

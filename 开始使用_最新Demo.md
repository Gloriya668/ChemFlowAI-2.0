# ChemFlow AI · 最新 Demo 代码包

打包日期：2026-10-23

## 本次内容

- 企业版九步工程工作流、两套完成的演示案例、工程报告和页面动效。
- 学习版十阶段路径：环境保护后加入安全评估。
- 流程建立中的动态控制工作台：五回路、P/PI 参数、进料扰动、曲线及动画。
- 环保、噪声、安全的提炼内容与交互学习模块。
- HAZOP 7×5 风险矩阵、8 类节点、15 项分析条目与改进记录。
- 学习记录本地保存与报告导出；页面已移除环保安全模块的文件入口和来源标签。

## 首次运行（Windows x64）

1. 将整个 ChemFlowAI 文件夹解压到固定位置，例如 E:\ChemFlowAI。不要在压缩包内启动。
2. 准备 Windows x64 Python 3.12。在项目目录打开 PowerShell，运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\Setup-Offline.ps1 -PythonExe "C:\Python312\python.exe"
.\Start-ChemFlow.cmd
```

3. 浏览器打开 http://127.0.0.1:8765/ 。前端已编译，正常运行无需安装 Node.js。
4. 如端口被占用，可运行 `powershell -ExecutionPolicy Bypass -File .\Start-ChemFlow.ps1 -Port 8766`，再打开 http://127.0.0.1:8766/ 。
5. 停止服务：`powershell -ExecutionPolicy Bypass -File .\Stop-ChemFlow.ps1 -Port 8765`（使用其他端口时相应修改）。

## 修改前端

安装 Node.js 后，在 frontend 目录执行 `npm ci`、`npm run build`，后端会提供 frontend/dist 中的页面。

## 数据与配置

- runtime/projects 中包含两套已完成的演示案例；未打包其他临时任务、日志、备份或本机 Python 环境。
- 学习记录在使用后保存到解压目录中的 runtime；浏览器草稿保存在对应浏览器。
- config/llm.json 中的服务地址、模型名与 API 密钥为空；DWSIM 与外部服务需按实际环境配置。
- 动态控制曲线为页面明确标注的教学模型计算；HAZOP 等级为学习者记录，不代表工程审查结论。
- 源码和已编译前端均已包含。本次未重跑应用测试；最近前端生产构建已通过。

## 文件完整性

release-manifest.json 记录各文件的 SHA-256；压缩包旁的 .sha256 文件记录整个 ZIP 的校验值。
README.md 中较早的版本与测试数字为历史记录，当前交付以本文件为准。

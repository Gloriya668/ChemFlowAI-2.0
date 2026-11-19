# ChemFlow 训练数据与测试用例 V2

本目录提供 UTF-8 JSONL 数据、来源追溯、自动审核及评测脚本。所有 Agent 行为样本是合成情境，不是已执行的仿真轨迹；知识库原始 DWSIM 文件是真实公开文件，但本批只索引其静态元数据。

## 直接使用的文件

| 文件 | 用途 | 条数 |
| --- | --- | ---: |
| ready/train.jsonl | 大模型 SFT 训练输入，仅含训练集 | 116 |
| ready/dev.jsonl | 开发与模型选择 | 22 |
| ready/test.jsonl | 留出评测参考，不得用于训练 | 38 |
| ranking_train/dev/test.jsonl | 知识检索查询与相关文档标签 | 92 / 14 / 22 |
| sft_train/dev/test.jsonl | 有证据输入的参考作答 | 92 / 14 / 22 |
| agent/sft_train/dev/test.jsonl | Agent 下一步动作 messages | 24 / 8 / 16 |
| agent/cases_train/dev/test.jsonl | 输入状态、参考动作、判分规则 | 24 / 8 / 16 |
| agent/prompts_test.jsonl | 给待测模型的输入，不含答案 | 16 |
| review_queue.jsonl | 逐资料专家审核待办 | 79 |
| ../tests/cases/engineering_acceptance.jsonl | 真实仿真与经济评价验收计划 | 12 |

`ready` 是前述 SFT 文件的合并视图，不是额外新增样本，不能将两套文件再合并后重复计数。每条 messages 均为 system/user/assistant，assistant 为当前 Agent 支持的 JSON 动作对象，额外元数据保留来源、许可、任务类型和合成标识。

示意（不是额外训练记录）：
```json
{"id":"...","task_type":"agent_next_action","synthetic":true,"messages":[{"role":"system","content":"工具白名单和证据规则"},{"role":"user","content":"任务和当前状态"},{"role":"assistant","content":"{\"action\":\"tool\",\"summary\":\"核对输入\",\"tool\":\"check_design_basis\",\"arguments\":{},\"answer\":\"\"}"}]}
```

## 划分与质量边界

检索数据按完整来源组划分；同一原文的不同分块和引用它的中文检查清单放在同一来源组。Agent 数据按任务家族划分，家族内不同措辞不能跨集。训练负样本只来自训练来源组。测试文档仍保留在检索库中，但测试查询和相关性标签不参与训练。

本版新增单位/组成、模型诊断、初始化、衡算、经济口径、工具权限与不可信文本等内容。中文清单是带来源的项目检查规则，标记 `AUTHOR_CHECKLIST_NOT_EXPERT_VALIDATED`，不冒充实测数据或专家审核结论。英文组分原名保留，未强行翻译不明确的物质别名。

自动审核检查文件哈希、来源白名单、声明的来源组隔离、精确重复查询、消息结构、JSON 动作格式、模型输入不携带测试答案。**精确去重不等于语义去重**；模板问句可能语义接近，且 v1 已用过的测试项在本版只是回归集，不应称为全新盲测。应由审核队列进一步检查术语、适用工况、事实忠实度和样本适用性。

公开资料许可证随原文件保留。不要把 GPL 衍生数据或来源混合数据集统一改标为 CC0。未提供API密钥，也未上传工艺文件至外部训练服务。

## 重建、审计和训练

在项目根目录执行：
```powershell
./Train-Knowledge.ps1 -PythonExe "你的 Python 3.12 路径"
```

该命令依次构建工程清单和知识语料、构建 Agent 样本、整理统一文件、审核数据并训练轻量排序器。不会训练大语言模型。代码与本地来源齐全时，构建与排序训练只需 Python 标准库；动作格式审计复用项目 FastAPI/Pydantic 环境。

`audit_report.json` 是数据审核结果；`evaluation.json` 是本地检索排序评测。二者都不是大模型 Agent 的端到端得分。

## 评测真实模型的下一步动作

向待测模型提供 `agent/prompts_test.jsonl` 的 messages，收集为：
```json
{"id":"agent-no-consent-0","decision":{"action":"final","summary":"遵守授权边界","tool":null,"arguments":{},"answer":"本次没有求解授权，只能分析。"}}
```

然后运行：
```powershell
python scripts/evaluate_agent_predictions.py --predictions predictions.jsonl --split test --output runtime/agent-evaluation.json
```

缺失预测按失败计；重复/未知 ID 拒绝；校验结构、预期动作、工具参数、求解限制以及部分答复关键词。测试集答案和规则在 `cases_test.jsonl`，**不能传给待测模型**。关键词检查不能判断反讽、否定语义或化工事实，需人工复核；该工具也不判断检索 query 与意图是否充分相关。

目前未调用真实大模型评测，未生成假预测报高分。测试代码用参考答案通过判分器，只是验证判分器与数据格式，不是模型成绩。

## 实际工程测试

12 项工程验收计划覆盖加热、泵、闪蒸、回流、模板变化、组成不匹配、求解失败、并发修订、经济参数、成本口径、独立验证与能量缺项。全部保留 `NOT_RUN`；数值容差由工程师在执行前根据参考数据预登记。运行日志、原始输入、真实观察值和审核结论都要保存。

当前 DWSIM 仍有上一版发现的本机应用控制问题；本次没有通过回放或测试替身冒充真实求解。完整 TEA、自动优化和领域大模型微调仍未完成。

Agent 下一步动作数据；全部为合成情境，不是真实求解轨迹。
train 用于训练，dev 用于调参，test 留作评测。
prompts_test.jsonl 不含参考答案；cases_test.jsonl 含判分规则，不得放入模型上下文。
尚未调用任何真实大模型评测。用 scripts/evaluate_agent_predictions.py 对外部预测判分。

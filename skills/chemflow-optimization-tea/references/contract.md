# 工程契约
输入：经过 Pydantic 校验的 ProjectSpec 或当前步骤相关结果。
允许步骤：[6, 7, 8]。
来源类型：USER_INPUT/REFERENCE_DATA/RULE/CALCULATED/SIMULATOR。
禁止 LLM 产生温度、压力、流量、物性、设备 duty、成本及收敛值。null 不是零。
明确决策变量、bounds、constraints、objective。未连接优化器时保存场景为未求解；仅比较标注来源的参考结果，不画伪前沿。TEA 必需 basis_year/currency/hours/feed_price/product_price/utility_price/method；缺失返回 NOT_CALCULATED。没有成本关联及投资数据不能给 CAPEX/NPV/IRR/回收期。

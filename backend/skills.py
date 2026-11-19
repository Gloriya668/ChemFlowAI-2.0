from .store import ROOT,read_json
from .models import ProjectSpec,SkillResult
REGISTRY=read_json(ROOT/'config/skills.json')
def execute_skill(name,step,context):
    entry=next((s for s in REGISTRY if s['name']==name),None)
    if not entry or step not in entry['steps']:raise ValueError('WRONG_STEP')
    spec=ProjectSpec.model_validate(context['spec']);evidence=[];risk='没有连接独立求解器。'
    if name=='chemflow-intake':
        errors=check_spec(spec);obs='设计基准已结构化' if not errors else '设计输入需要补充';evidence=errors or [f'{len(spec.feeds)} 股进料均有可追溯温度、压力和质量流量。']
        risk='目标纯度、公用工程及部分工程约束尚未定义；不可作为实际设计交付。'
    elif name=='chemflow-property-modeling':
        obs='仅进行输入校核和物性方法规则筛选';evidence=['已接入有来源的物性常数与二元参数；C3 实验 VLE 来自 NIST ThermoML，覆盖率与适用范围见物性工作区。','PR/SRK/PRSV 用于烃类候选；NRTL 用于极性非理想候选（待验证）。'];risk='模型推荐不等于物性验证。'
    elif name=='chemflow-process-synthesis':
        obs='保留已审核流程拓扑，生成模拟器无关 IR';evidence=['路线来源：已有用户流程资产；不是数值结果驱动生成。'];risk='流程拓扑与所选案例版本绑定。'
        if spec.source.get('variant')=='pyridine525':risk='闭循环包含分相器及 RE 回流；需复核精制塔进料增压与异常低温。'
    elif name=='chemflow-simulation-review':
        obs='审核 Adapter 输出及质量守恒';evidence=context.get('review',{}).get('issues',[]) or (['参考结果已加载；外部质量差已计算。独立求解仍未执行。'] if context.get('review') else ['结果加载前不提供收敛判断。']);risk='REPLAY_NOT_SOLVED 不代表实际求解收敛；异常原值不修改。'
    elif name=='chemflow-optimization-tea':
        obs='保存优化问题并检查评价输入';evidence=['无优化器时仅参考比较；不绘制伪造最优前沿。','价格、小时、基年、币种和方法缺失时不计算。'];risk='参考方案跨模拟运行，边界可能不一致；不是优化结论。'
    else:
        obs='复核工作流与数据映射';evidence=['Ground Truth 仅此步骤的 Evaluator 可读取。'];risk='同源回放不能证明独立数值精度。'
    from .knowledge import retrieve
    evidence += [r['citation']+': '+r['excerpt'] for r in retrieve(name,obs,limit=1)]
    return SkillResult(skill=name,step=step,status='NEEDS_HUMAN_REVIEW',observation=obs,evidence=evidence,risk=risk,recommendation='检查来源并完成当前阶段工程复核。',action_required='人工确认后继续').model_dump()
def check_spec(spec):
    from .design_basis import completion
    d=completion(spec)
    return [f["label"]+": "+f["status"]+" "+f["detail"] for f in d['fields'] if f['status']!='COMPLETE']+d['review_fields'][sum(f['status']=='NEEDS_REVIEW' for f in d['fields']):]

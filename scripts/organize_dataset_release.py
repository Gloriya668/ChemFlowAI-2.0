"""Publish unified messages datasets, human review queue and integration test plan."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')

SCENARIOS=[
 ('SIM-01','water-heater','受控水加热案例','使用已验证的水加热器模板及固定进料；本次授权求解。','保存真实 SOLVED 日志、出口温度与指定值的偏差、外部衡算和输入指纹。',['DWSIM 可信运行环境','水物性包','已审核温度和压力规格'],'SIMULATOR'),
 ('SIM-02','pump','泵增压案例','使用已验证单相液体泵模板和出口压力规格。','比较出口压力与规格、流量守恒、效率和功率符号；数值容差需预先登记。',['泵模板','经核对效率','独立基准'],'SIMULATOR'),
 ('SIM-03','flash','闪蒸相分配','运行已验证的二元闪蒸模板。','核对组分与总质量平衡、相分率范围及独立相平衡参考。',['闪蒸模板','二元参数','独立相平衡数据'],'SIMULATOR'),
 ('SIM-04','recycle','回流流程','运行明确边界与初值的回流模板。','内回流不重复纳入外部衡算；记录所有单元状态和迭代失败。',['回流模板','可信初值'],'SIMULATOR'),
 ('SIM-05','template-hash','模板指纹变更','登记后修改模板副本，保留原登记。','应拒绝不匹配模板，不提交伪造新结果。',['隔离模板副本'],'INTEGRATION'),
 ('SIM-06','composition-mismatch','组成不匹配','使用模板与项目组成不一致的案例。','应报告不匹配，不在后台自动篡改多组分组成。',['登记模板','不匹配输入'],'INTEGRATION'),
 ('SIM-07','solver-failure','求解器返回错误','使用会失败的受控模板或明确的测试替身。','错误如实保留；不标 SOLVED；测试替身与真实求解报告分开。',['失败基准或明确标记的测试替身'],'INTEGRATION'),
 ('SIM-08','stale-revision','运行中项目变化','求解期间更新项目修订号。','旧结果不得覆盖新输入；应返回版本变化信息。',['可控隔离项目'],'INTEGRATION'),
 ('TEA-01','missing-prices','缺失经济参数','去掉价格、币种或基年中的必要项。','只给缺失项，不输出猜测 CAPEX/NPV/IRR。',['经济评价输入契约'],'ENGINEERING_REVIEW'),
 ('TEA-02','cost-boundary','成本口径不一致','提供购买费用与安装投资口径不同的两条来源。','区分成本边界；不能直接相加比较成最优结论。',['有来源的成本数据'],'ENGINEERING_REVIEW'),
 ('VAL-01','independent-truth','独立验证','用归档值同时作预测与参考。','标记同源性；不得声称完成独立数值验证。',['可追溯归档'],'ENGINEERING_REVIEW'),
 ('VAL-02','energy-gap','缺少能量证据','只提供设备 duty 和质量流量。','能量闭合保持未评估，并列出边界焓流等缺项。',['求解输出或明确测试替身'],'ENGINEERING_REVIEW')]

def build():
    for split in ['train','dev','test']:
        rows=read(ROOT/f'training/sft_{split}.jsonl')+read(ROOT/f'training/agent/sft_{split}.jsonl')
        write(ROOT/f'training/ready/{split}.jsonl',rows)
    docs=read(ROOT/'knowledge_base/corpus.jsonl')
    review_path=ROOT/'training/review_queue.jsonl'
    old={r['document_id']:r for r in read(review_path)} if review_path.exists() else {}
    queue=[]
    for d in docs:
        row={'document_id':d['id'],'title':d['title'],'citation':d['citation'],'source_sha256':d['source_sha256'],
          'source_group':d['group'],'review_status':'PENDING_CHEMICAL_ENGINEER_REVIEW','reviewer':'','reviewed_at':'',
          'checks':{'source_faithfulness':None,'applicable_range':None,'terminology':None,'training_suitability':None},'notes':''}
        previous=old.get(d['id'])
        if previous and previous.get('source_sha256')==d['source_sha256']:row=previous
        elif previous and previous.get('reviewer'):row['previous_review']=previous
        queue.append(row)
    write(review_path,queue)
    cases=[]
    for id,family,title,setup,expected,deps,level in SCENARIOS:
        cases.append({'id':id,'family':family,'title':title,'setup':setup,'expected_observations':expected,
                      'dependencies':deps,'level':level,'status':'NOT_RUN','numeric_tolerance':None,
                      'tolerance_policy':'Engineer must preregister units, reference values and acceptance tolerance where numeric checks apply.',
                      'required_artifacts':['input_snapshot','source_provenance','run_log','observed_result','review_decision'],
                      'actual_result':None,'reviewer':''})
    acceptance=ROOT/'tests/cases/engineering_acceptance.jsonl'
    # Rebuild must not erase a user's recorded engineering acceptance results.
    if not acceptance.exists():write(acceptance,cases)
    card={'version':'2','record_format':'JSONL UTF-8','base_model':'','api_key':'','base_url':'',
          'model_training_status':'LLM_NOT_FINETUNED','training_entry':'training/ready/train.jsonl',
          'development_entry':'training/ready/dev.jsonl','heldout_entry':'training/ready/test.jsonl',
          'warning':'Do not merge dev/test into training; prompts_test excludes reference answers. Model-generated outputs are not simulator evidence.',
          'mix':'grounded_reference_answer + agent_next_action; synthetic labels; chemical expert review pending'}
    (ROOT/'training/dataset_config.json').write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'ready':{s:len(read(ROOT/f'training/ready/{s}.jsonl')) for s in ['train','dev','test']},'expert_review_documents':len(docs),'engineering_test_plans':len(cases)})

if __name__=='__main__':build()

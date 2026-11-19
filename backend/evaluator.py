from .store import ROOT,read_json
from .models import ValidationResult
from .case_variant import case_key,result_key
class GoldenEvaluator:
    def evaluate(self,project):
        if project['max_step']!=9:raise ValueError('Ground Truth access requires Step 09')
        result=project.get('result')
        if not result:raise ValueError('No simulation result')
        if result['backend']=='DWSIM':return validate_simulation(project)
        route=project['route'];base=ROOT/'data/validation'/(case_key(project['spec']) if route=='pyridine' else 'pdh/'+route)
        golden=read_json(base/'ground_truth.json');t=read_json(ROOT/'config/validation_thresholds.json');checks=[]
        def add(label,status,details):checks.append({'label':label,'status':status,'details':details})
        actual=set(result['streams']);expected=set(golden['streams']);add('Data Mapping','PASS' if actual==expected else 'FAIL',f'{len(actual)} / {len(expected)} stream IDs')
        def graph(x):return (sorted((u['id'],u['type']) for u in x['units']),sorted((c['stream_id'],c['from_unit'] or '',c['to_unit'] or '') for c in x['connections']))
        add('Topology Match','PASS' if graph(project['ir'])==graph(golden['topology']) else 'FAIL','设备类型、流股与连接逐项比较')
        for key,limit in [('temperature',t['temperature_abs_C']),('pressure',t['pressure_abs_bar']),('mass_flow',t['mass_flow_relative'])]:
            errors=[]
            for name in expected&actual:
                a=result['streams'][name][key]['value'];b=golden['streams'][name][key]['value']
                if a is None or b is None:continue
                errors.append(abs(a-b)/(max(abs(b),1e-12) if key=='mass_flow' else 1))
            error=max(errors,default=None);add(key+' mapping','PASS' if error is not None and error<=limit and actual==expected else 'FAIL',{'max_error':error,'threshold':limit,'interpretation':'同源回放字段映射检查，非独立模拟精度'})
        balance=material_balance(result);add('Material Balance','PASS' if balance['relative_error']<=t['material_balance_relative'] else 'WARN',balance)
        energy=result['energy'];ge=golden['energy'];ok=len(energy)==len(ge)
        for a,b in zip(energy,ge):ok=ok and a['id']==b['id'] and abs(a['duty']['value']-b['duty']['value'])<=max(abs(b['duty']['value']),1)*t['energy_relative']
        add('Energy Mapping','PASS' if energy and ok else ('NOT_ASSESSED' if not energy else 'FAIL'),'无能量数据时不计算误差；不等价于能量衡算闭合')
        add('State Machine','PASS' if project['completed']==list(range(1,9)) else 'FAIL','服务端已确认步骤 1–8')
        add('Ground Truth Loading','PASS',str(base.relative_to(ROOT)))
        add('Process Visualization','PASS' if (ROOT/'data/assets'/f'{result_key(project)}.svg').exists() else 'FAIL','复用动画 SVG；点击与映射由 E2E 验证')
        is_replay=result['backend']=='REFERENCE_REPLAY'
        return ValidationResult(workflow_integration='PASS' if not any(c['status']=='FAIL' for c in checks) else 'FAIL',independent_numerical_validation='NOT_ASSESSED' if is_replay else ('PASS' if all(c['status'] not in ('FAIL','WARN') for c in checks) else 'NEEDS_REVIEW'),checks=checks,thresholds=t).model_dump()
def material_balance(result):
    ins=[c['stream_id'] for c in result['topology']['connections'] if not c['from_unit']];outs=[c['stream_id'] for c in result['topology']['connections'] if not c['to_unit']]
    total_in=sum(result['streams'][i]['mass_flow']['value'] for i in ins);total_out=sum(result['streams'][i]['mass_flow']['value'] for i in outs)
    return {'input_kg_h':total_in,'output_kg_h':total_out,'residual_kg_h':total_out-total_in,'relative_error':abs(total_out-total_in)/max(total_in,1e-12),'source_type':'CALCULATED','source_name':'外部进出料质量流量之差','formula':'abs(sum(out)-sum(in))/sum(in)','input_streams':ins,'output_streams':outs}


def validate_simulation(project):
    """A solved run is checked on its own boundary, never against unrelated archived values."""
    result=project['result'];t=read_json(ROOT/'config/validation_thresholds.json')
    balance=material_balance(result)
    checks=[{'label':'Solver convergence','status':'PASS' if result.get('converged') is True and result.get('solver_status')=='SOLVED' else 'FAIL','details':result['source']},
            {'label':'Material Balance','status':'PASS' if balance['relative_error']<=t['material_balance_relative'] else 'FAIL','details':balance},
            {'label':'State Machine','status':'PASS' if project['completed']==list(range(1,9)) else 'FAIL','details':'已确认步骤 1–8'},
            {'label':'Independent benchmark','status':'NOT_ASSESSED','details':'真实求解与守恒检查不能替代实验或独立基准验证。'},
            {'label':'Energy balance','status':'NOT_ASSESSED','details':'当前未提取完整边界焓流，不能声称能量衡算闭合。'}]
    return ValidationResult(workflow_integration='FAIL' if any(c['status']=='FAIL' for c in checks) else 'PASS',
        independent_numerical_validation='NEEDS_REVIEW',checks=checks,thresholds=t).model_dump()

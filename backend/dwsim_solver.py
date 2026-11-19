"""Template-bound DWSIM simulations, with explicit mappings and engineering units."""
import copy
import hashlib
import json
import math
import uuid
import datetime
from pathlib import Path
from . import store
from .adapters import SimulatorUnavailable, SnapshotMismatch
from .dwsim_mcp import Session, settings
from .models import SimulationResult


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def basis_digest(spec):
    # Only feed T/P/mass flow are editable on a registered template. Everything else is bound.
    data=copy.deepcopy(spec)
    data.pop('project_id',None);data.pop('source',None)
    for feed in data['feeds']:
        for key in ('temperature','pressure','mass_flow','molar_flow'):feed.pop(key,None)
    return digest(data)


def quantity(value, unit, source, locator=''):
    if isinstance(value,(int,float)) and (isinstance(value,bool) or not math.isfinite(value)):
        raise SimulatorUnavailable('DWSIM 输出包含非有限数值。')
    return {'value':value,'unit':unit,'source_type':'SIMULATOR','source_name':source,
            'version':'1','locator':locator,'status':'SOLVED'}


def finite(value,label):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(label+' 必须是有限数值')
    return float(value)


def to_si(record, kind):
    value=finite(record.get('value'),kind)
    unit=record.get('unit')
    scales={'temperature':{'C':(1,273.15),'°C':(1,273.15),'K':(1,0)},
            'pressure':{'bar':(100000,0),'kPa':(1000,0),'Pa':(1,0)},
            'mass_flow':{'kg/h':(1/3600,0),'kg/s':(1,0)}}
    if unit not in scales[kind]:raise ValueError('DWSIM 不支持的输入单位：'+str(unit))
    scale,offset=scales[kind][unit];value=value*scale+offset
    if value<=0:raise ValueError(kind+' 的 SI 值必须大于零')
    return value


def registration(project):
    if not project.get('ir'):raise ValueError('请先确认流程 IR')
    return {'route_id':project['ir']['route_id'],'basis_sha256':basis_digest(project['spec']),
            'ir_sha256':digest(project['ir']),
            'stream_map':{s['stream_id']:s['stream_id'] for s in project['ir']['streams']},
            'unit_map':{u['id']:u['id'] for u in project['ir']['units']},
            'component_map':{c['id']:c['name'] for c in project['spec']['components']},
            'property_package_names':[project.get('model')],
            'template':'','template_sha256':'','duty_map':{},
            'note':'填写真实模板路径、SHA256、DWSIM 标签/组分名/物性包名；人工核对拓扑与反应后，复制到 config/dwsim.json 的 models 对应 route_id。'}


def validate_template(spec,ir,cfg):
    entry=cfg.get('models',{}).get(ir.route_id)
    if not entry:raise SimulatorUnavailable('没有为路线 '+ir.route_id+' 注册 DWSIM 流程模板；原始拓扑缺少设备规格，不能直接声称可求解。')
    if entry.get('basis_sha256')!=basis_digest(spec) or entry.get('ir_sha256')!=digest(ir.model_dump()):
        raise SnapshotMismatch('设计基准或流程已变化。请重新核对 DWSIM 模板并注册指纹；仅允许进料温度、压力和质量流量变更。')
    path=Path(entry.get('template',''))
    if not path.is_absolute():path=store.ROOT/path
    if not path.is_file() or path.suffix.lower() not in ('.dwxml','.dwxmz'):
        raise SimulatorUnavailable('DWSIM 模板文件不存在或扩展名不受支持。')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=entry.get('template_sha256'):
        raise SnapshotMismatch('DWSIM 模板 SHA256 不一致，请重新审核登记。')
    for key,ids in [('stream_map',{s.stream_id for s in ir.streams}),('unit_map',{u.id for u in ir.units}),
                    ('component_map',{c['id'] for c in spec['components']})]:
        mapping=entry.get(key,{})
        if set(mapping)!=ids or len(set(mapping.values()))!=len(mapping):
            raise ValueError(key+' 必须完整且一一对应')
    inlet_ids={c.stream_id for c in ir.connections if c.from_unit is None}
    if not inlet_ids or inlet_ids!={f['stream_id'] for f in spec['feeds']}:
        raise ValueError('设计基准必须覆盖流程边界的全部进料')
    if not any(c.to_unit is None for c in ir.connections):raise ValueError('流程必须声明边界出料')
    return entry,path.resolve()


def solve(spec,ir):
    cfg=settings();entry,path=validate_template(spec,ir,cfg)
    run_id=str(uuid.uuid4());directory=store.ROOT/'runtime/solver-runs'/run_id
    directory.mkdir(parents=True)
    audit=[]
    record={'id':run_id,'project_id':spec.get('project_id'),'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'status':'RUNNING','input_sha256':digest({'spec':spec,'ir':ir.model_dump()}),
            'template_sha256':entry['template_sha256'],'trace':audit}
    try:
        with Session(cfg,audit) as session:
            loaded=session.call('dwsim_flowsheet_load',filepath=str(path));fid=loaded['flowsheet_id']
            record['server']=session.info.get('serverInfo')
            summary=session.call('dwsim_flowsheet_summary',flowsheet_id=fid)
            if set(summary['compounds'])!=set(entry['component_map'].values()):
                raise SnapshotMismatch('DWSIM 模板组分与设计基准不一致。')
            if set(summary['property_packages'])!=set(entry.get('property_package_names',[])):
                raise SnapshotMismatch('DWSIM 模板物性包与登记信息不一致。')
            objects=session.call('dwsim_flowsheet_list_objects',flowsheet_id=fid)['objects']
            names={o['name']:o for o in objects}
            for tag in entry['stream_map'].values():
                if tag not in names or names[tag]['type']!='MaterialStream':raise SnapshotMismatch('DWSIM 物流映射错误：'+tag)
            for tag in entry['unit_map'].values():
                if tag not in names or 'Stream' in names[tag]['type']:raise SnapshotMismatch('DWSIM 设备映射错误：'+tag)
            for feed in spec['feeds']:
                tag=entry['stream_map'][feed['stream_id']]
                original=session.call('dwsim_stream_get_results',flowsheet_id=fid,name=tag)
                mixture=next((p for p in original['phases'] if p['name'].lower() in ('mixture','overall')),None)
                if mixture is None:raise SimulatorUnavailable('DWSIM 未返回混合相，无法核对进料组成。')
                if not feed['composition']:raise ValueError('必须填写进料组成以核对模板。')
                if len({q['unit'] for q in feed['composition'].values()})!=1:
                    raise ValueError('同一进料的组成必须采用一致的质量或摩尔基准')
                fractions=[finite(q['value'],'进料组成') for q in feed['composition'].values()]
                if any(v<0 or v>1 for v in fractions) or not math.isclose(sum(fractions),1,abs_tol=1e-6):
                    raise ValueError('进料组成必须非负且加和为 1')
                for cid,q in feed['composition'].items():
                    basis={'mol/mol':'mole_fraction','kg/kg':'mass_fraction'}.get(q['unit'])
                    if not basis:raise ValueError('组成单位仅支持 mol/mol 或 kg/kg')
                    actual=mixture['compounds'][entry['component_map'][cid]][basis]
                    if not math.isclose(finite(q['value'],'进料组成'),actual,abs_tol=1e-7,rel_tol=1e-7):
                        raise SnapshotMismatch('进料组成与 DWSIM 模板不一致；请在模型中编辑并重新登记。')
                session.call('dwsim_stream_set_conditions',flowsheet_id=fid,name=tag,
                    temperature_K=to_si(feed['temperature'],'temperature'),pressure_Pa=to_si(feed['pressure'],'pressure'),
                    mass_flow_kg_s=to_si(feed['mass_flow'],'mass_flow'))
            preflight=session.call('dwsim_flowsheet_check',flowsheet_id=fid)
            record['preflight']=preflight
            if preflight.get('blockers',0):raise SimulatorUnavailable('DWSIM 预检阻断：'+json.dumps(preflight.get('findings',[]),ensure_ascii=False)[:1800]+'；记录 '+run_id)
            solved=session.call('dwsim_solve_run',flowsheet_id=fid,timeout_s=max(1,cfg['timeout_seconds']-10))
            record['solver']=solved
            required=set(entry['stream_map'].values())|set(entry['unit_map'].values())
            solved_objects={o['name']:o for o in solved.get('objects',[])}
            if not solved.get('ok') or any(n not in solved_objects or not solved_objects[n].get('calculated') or solved_objects[n].get('error') for n in required):
                failures=solved.get('errors',[])+[str(o.get('name'))+': '+str(o.get('error','未计算')) for o in solved_objects.values() if not o.get('calculated') or o.get('error')]
                raise SimulatorUnavailable('DWSIM 未收敛或存在未计算对象：'+'；'.join(str(x) for x in failures[:5])[:1800]+'；记录 '+run_id)
            source='DWSIM / '+run_id;streams={};energy=[]
            for sid,tag in entry['stream_map'].items():
                raw=session.call('dwsim_stream_get_results',flowsheet_id=fid,name=tag)
                mixture=next((p for p in raw['phases'] if p['name'].lower() in ('mixture','overall')),None)
                if mixture is None:raise SimulatorUnavailable('缺少混合相结果：'+tag)
                vapor=next((p['fraction'] for p in raw['phases'] if p['name'].lower()=='vapor'),None)
                q=lambda v,u:quantity(v,u,source,tag)
                t=finite(raw['temperature_K'],'temperature');pressure=finite(raw['pressure_Pa'],'pressure');flow=finite(raw['mass_flow_kg_s'],'mass flow')
                if t<=0 or pressure<=0 or flow<0:raise SimulatorUnavailable('DWSIM 返回非物理状态。')
                streams[sid]={'stream_id':sid,'component_ids':list(entry['component_map']),
                    'temperature':q(t-273.15,'C'),'pressure':q(pressure/100000,'bar'),'mass_flow':q(flow*3600,'kg/h'),
                    'molar_flow':q(finite(raw['molar_flow_mol_s'],'molar flow')*3.6,'kmol/h'),
                    'phase':q('UNKNOWN' if vapor is None else 'VAPOR' if vapor==1 else 'LIQUID' if vapor==0 else 'MIXED',''),
                    'vapor_fraction':q(vapor,'mol/mol') if vapor is not None else None,
                    'composition':{cid:q(finite(mixture['compounds'][name]['mole_fraction'],'composition'),'mol/mol') for cid,name in entry['component_map'].items()}}
                fractions=[x['value'] for x in streams[sid]['composition'].values()]
                if any(v<0 or v>1 for v in fractions) or (flow>0 and not math.isclose(sum(fractions),1,abs_tol=1e-5)):
                    raise SimulatorUnavailable('DWSIM 输出组成不满足非负和归一化检查。')
            for feed in spec['feeds']:
                molar=feed.get('molar_flow') or {}
                if molar.get('value') is not None:
                    if molar.get('unit')!='kmol/h':raise ValueError('进料摩尔流量单位必须为 kmol/h')
                    if not math.isclose(finite(molar['value'],'进料摩尔流量'),streams[feed['stream_id']]['molar_flow']['value'],rel_tol=.005,abs_tol=1e-6):
                        raise SnapshotMismatch('质量流量、组成计算的摩尔流量与设计基准不一致，结果未应用。')
            # Explicit duty mapping avoids summing both device duty and its energy stream.
            for uid,prop in entry.get('duty_map',{}).items():
                raw=session.call('dwsim_unitop_get_results',flowsheet_id=fid,name=entry['unit_map'][uid])
                duty=raw['properties'][prop];scale={'kW':1,'W':.001,'MW':1000}.get(duty['units'])
                if scale is None:raise ValueError('设备负荷单位不受支持：'+str(duty['units']))
                energy.append({'id':uid,'duty':quantity(finite(float(duty['value']),'duty')*scale,'kW',source,prop)})
            session.call('dwsim_flowsheet_save',flowsheet_id=fid,filepath=str(directory/'solved.dwxmz'),compressed=True)
            notes=['真实 DWSIM 求解；收敛不等于工程有效性，需检查物性与衡算。','运行记录：'+run_id]
            if not energy:notes.append('没有登记设备负荷映射，能量结果未提取；不得按零能耗解释。')
            result=SimulationResult(route_id=ir.route_id,backend='DWSIM',solver_status='SOLVED',converged=True,
                streams=streams,energy=energy,topology=ir.model_dump(),source=source,notes=notes)
            record['status']='SUCCEEDED';record['result']=result.model_dump()
            return result
    except Exception as exc:
        record['status']='FAILED';record['error']=str(exc)[:3000]
        raise
    finally:
        (directory/'run.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def runs_for_project(pid):
    uuid.UUID(pid)
    directory=store.ROOT/'runtime/solver-runs'
    if not directory.exists():return []
    records=[]
    for file in sorted(directory.glob('*/run.json'),key=lambda p:p.stat().st_mtime,reverse=True):
        try:record=store.read_json(file)
        except (OSError,ValueError):continue
        if record.get('project_id')==pid:records.append(record)
        if len(records)>=20:break
    return records

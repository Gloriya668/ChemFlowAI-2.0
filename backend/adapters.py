from abc import ABC,abstractmethod
import math,re
from typing import Literal
from pydantic import BaseModel,ConfigDict
from .store import ROOT,read_json
from .models import SimulationIR,SimulationResult
from .case_variant import case_key
class SimulatorUnavailable(Exception):pass
class SnapshotMismatch(Exception):pass
def same_reference_value(a,b):
    if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
        return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-8)
    if isinstance(a,dict) and isinstance(b,dict):
        return a.keys()==b.keys() and all(same_reference_value(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        return len(a)==len(b) and all(same_reference_value(x,y) for x,y in zip(a,b))
    return a==b
def reaction_key(equation):
    return re.sub(r'\s+','',equation).replace('->','→')
class TypedSimulatorCommand(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation:Literal['load_model','set_feed','set_unit_parameter','solve','get_streams','get_duties']
    unit_id:str|None=None
    stream_id:str|None=None
    parameter:Literal['temperature','pressure','mass_flow','reflux_ratio','feed_stage','compressor_ratio']|None=None
    value:float|None=None
class SimulatorAdapter(ABC):
    @abstractmethod
    def run(self,spec,ir:SimulationIR)->SimulationResult:...
class ReferenceReplayAdapter(SimulatorAdapter):
    def run(self,spec,ir):
        original=read_json(ROOT/'data/validation'/case_key(spec)/'input.json')
        def key(s):return [(f['stream_id'],f['temperature']['value'],f['pressure']['value'],f['mass_flow']['value'],(f.get('molar_flow') or {}).get('value'),{k:q['value'] for k,q in f['composition'].items()}) for f in s['feeds']]
        differences=[]
        if case_key(spec)=='pyridine525' and ir.property_method!='NRTL':differences.append('物性方法（源模型为 NRTL）')
        if not same_reference_value(key(spec),key(original)):differences.append('进料温度、压力、流量或组成')
        if reaction_key(spec['reaction']['equation'])!=reaction_key(original['reaction']['equation']):differences.append('反应式')
        if {c['id'] for c in spec['components']}!={c['id'] for c in original['components']}:differences.append('组分集合')
        if spec['constraints']!=original['constraints']:differences.append('工程约束')
        if spec['utilities']!=original['utilities']:differences.append('公用工程')
        if differences:
            raise SnapshotMismatch('与归档不一致：'+'、'.join(differences)+'。不能将历史回放作为新工况结果。请核对 Step1，或接入真实模拟器。')
        result=SimulationResult.model_validate(read_json(ROOT/'data/replay'/f"{'pyridine525' if ir.route_id=='pyridine' and case_key(spec)=='pyridine525' else ir.route_id}.json"))
        return result
class DWSIMAdapter(SimulatorAdapter):
    def run(self,spec,ir):
        from .dwsim_solver import solve
        return solve(spec,ir)
class ExternalMCPAdapter(SimulatorAdapter):
    def run(self,spec,ir):raise SimulatorUnavailable('SIMULATOR NOT CONNECTED: 工程归档 MCP typed tools 尚未连接')
    def execute(self,command:TypedSimulatorCommand):raise SimulatorUnavailable('请配置受支持 typed-tool 实现；禁止原始 COM path')
def adapter(mode,backend):
    if mode=='blind' and backend=='reference_replay':raise SimulatorUnavailable('独立求解器验证模式不能将 工程归档 存档数据作为新求解结果')
    return {'reference_replay':ReferenceReplayAdapter,'dwsim':DWSIMAdapter,'external_mcp':ExternalMCPAdapter}[backend]()

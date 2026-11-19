from typing import Any,Literal
from pydantic import BaseModel,Field,ConfigDict,model_validator
import math
class ProvenanceRecord(BaseModel):
    value: float|str|None = None
    unit: str=''
    source_type: Literal['VALIDATION_INPUT','IMPORTED_INPUT','USER_INPUT','REFERENCE_DATA','LITERATURE','DATABASE','RULE','LLM','SIMULATOR','CALCULATED']
    source_name: str
    version: str='1'
    locator: str=''
    status: str='UNVERIFIED'
    formula: str|None=None
    parents: list[dict]=Field(default_factory=list)
    @model_validator(mode='after')
    def finite(self):
        if isinstance(self.value,float) and not math.isfinite(self.value):raise ValueError('Finite engineering values required')
        if self.source_type=='LLM' and isinstance(self.value,(float,int)):raise ValueError('LLM cannot author engineering numerical values')
        return self
class ComponentSpec(BaseModel):
    id:str
    name:str
    source_type:str
    source_name:str
class FeedSpec(BaseModel):
    stream_id:str
    component_ids:list[str]=Field(default_factory=list)
    temperature:ProvenanceRecord
    pressure:ProvenanceRecord
    mass_flow:ProvenanceRecord
    molar_flow:ProvenanceRecord|None=None
    composition:dict[str,ProvenanceRecord]=Field(default_factory=dict)
class ReactionSpec(BaseModel):
    equation:str
    source_type:str
    source_name:str
class ProductTarget(BaseModel):
    name:str
    purity:ProvenanceRecord|None=None
    source_type:str
    source_name:str
    product_role:Literal['TOP','BOTTOM','BYPRODUCT']|None=None
    purity_operator:Literal['>=','<=','=']|None=None
class ConstraintSpec(BaseModel):
    model_config=ConfigDict(extra='allow')
class UtilitySpec(ConstraintSpec):pass
class ProjectSpec(BaseModel):
    model_config=ConfigDict(extra='forbid')
    project_id:str=''
    dataset:Literal['pdh','pyridine','custom']
    components:list[ComponentSpec]
    feeds:list[FeedSpec]
    reaction:ReactionSpec
    target_products:list[ProductTarget]
    byproducts:list[ProductTarget]=Field(default_factory=list)
    capacity:ProvenanceRecord|None=None
    constraints:dict=Field(default_factory=dict)
    utilities:dict=Field(default_factory=dict)
    source:dict
class PropertyData(BaseModel):
    component_id:str
    critical_temperature:ProvenanceRecord|None=None
    critical_pressure:ProvenanceRecord|None=None
    interaction_parameters_status:str='MISSING'
class PropertyMethodCandidate(BaseModel):
    id:str
    reason:str
    risk:str
    status:str='NEEDS_HUMAN_REVIEW'
    source_type:str='RULE'
class UnitOperation(BaseModel):
    id:str
    type:str
    label:str
    parameters:dict=Field(default_factory=dict)
class MaterialStream(BaseModel):
    stream_id:str
    from_unit:str|None=None
    to_unit:str|None=None
class EnergyStream(BaseModel):
    id:str
    from_unit:str|None=None
    to_unit:str|None=None
    duty:ProvenanceRecord|None=None
class Connection(MaterialStream):pass
class SimulationIR(BaseModel):
    route_id:str
    title:str
    components:list[ComponentSpec]=Field(default_factory=list)
    property_method:str=''
    units:list[UnitOperation]
    streams:list[MaterialStream]
    connections:list[Connection]
    energy_streams:list[EnergyStream]=Field(default_factory=list)
    source:dict
    @model_validator(mode='after')
    def graph(self):
        ids=[u.id for u in self.units];ss=[s.stream_id for s in self.streams]
        if len(set(ids))!=len(ids) or len(set(ss))!=len(ss):raise ValueError('Duplicate graph IDs')
        if set(c.stream_id for c in self.connections)!=set(ss):raise ValueError('Connection/stream set mismatch')
        if len(self.connections)!=len(ss):raise ValueError('Duplicate connections')
        for c in self.connections:
            if not c.from_unit and not c.to_unit:raise ValueError('Disconnected stream')
            for k in [c.from_unit,c.to_unit]:
                if k and k not in ids:raise ValueError('Unknown equipment reference')
        return self
class StreamResult(BaseModel):
    molar_flow:ProvenanceRecord|None=None
    stream_id:str
    component_ids:list[str]=Field(default_factory=list)
    temperature:ProvenanceRecord
    pressure:ProvenanceRecord
    mass_flow:ProvenanceRecord
    phase:ProvenanceRecord
    vapor_fraction:ProvenanceRecord|None=None
    composition:dict[str,ProvenanceRecord]=Field(default_factory=dict)
class EquipmentResult(BaseModel):
    id:str
    duty:ProvenanceRecord|None=None
class EnergyResult(BaseModel):
    entries:list[EquipmentResult]
    balance_status:str='NOT_ASSESSED'
class SimulationResult(BaseModel):
    route_id:str
    backend:str
    solver_status:str
    converged:bool|None
    streams:dict[str,StreamResult]
    energy:list[EquipmentResult]
    topology:dict
    source:str
    notes:list[str]
class OptimizationCandidate(BaseModel):
    id:str
    variables:dict[str,ProvenanceRecord]=Field(default_factory=dict)
    objectives:dict[str,ProvenanceRecord|None]=Field(default_factory=dict)
    status:str='NOT_SOLVED'
class EconomicResult(BaseModel):
    status:str
    metrics:dict[str,ProvenanceRecord|None]
    missing_inputs:list[str]
class EnvironmentalResult(EconomicResult):pass
class ValidationResult(BaseModel):
    workflow_integration:str
    independent_numerical_validation:str
    checks:list[dict]
    thresholds:dict
class SkillResult(BaseModel):
    skill:str
    step:int
    status:str
    observation:str
    evidence:list[str]
    risk:str
    recommendation:str
    action_required:str

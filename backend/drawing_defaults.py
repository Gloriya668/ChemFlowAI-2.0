"""Reversible concept-design assumptions, never simulator input or certified sizing."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def equipment_defaults(p, uid):
    unit = next((u for u in p['ir']['units'] if u['id'] == uid), None)
    if not unit:
        raise ValueError('请选择当前流程中的设备')
    typ = unit['type']
    source = json.loads((ROOT / 'data/equipment_parameters.json').read_text(encoding='utf-8'))
    spec = next((u for u in source.get(p.get('route'), {}).get('units', []) if u['id'] == uid), {})
    params = {r['key']: r['value'] for r in spec.get('rows', [])}
    streams = (p.get('result') or {}).get('streams') or {}
    connected = [streams.get(s['stream_id'], {}) for s in p['ir']['streams'] if uid in (s.get('from_unit'), s.get('to_unit'))]
    def numbers(key):
        return [s[key]['value'] for s in connected if isinstance((s.get(key) or {}).get('value'), (int, float))]
    temperatures = numbers('temperature')
    pressures = numbers('pressure')
    # Conservative concept envelope; defaults without loaded results are explicit assumptions.
    hot = max(temperatures, default=400 if typ == 'REACTOR' else 50)
    cold = min(temperatures, default=-100 if uid in ('COOLER', 'COOLER1', 'FLASH', 'FLASH1', 'HEATER') else 20)
    pressure = math.ceil(max(pressures, default=20) / 10 * 1.1 * 10) / 10
    temperature = str(int(math.ceil((hot + 30) / 10) * 10))
    if cold < 0:
        temperature = f'{math.floor((cold - 10) / 10) * 10} ~ {temperature}'
    material = 'S30408（低温候选）' if cold < -20 else 'Q345R（候选）'
    if hot >= 350 and cold >= -20:
        material = '15CrMoR（高温候选）'
    d, length, thickness = 600, 6000, 10
    basis = '换热器暂按 DN600、管长6m占位；换热面积与管束需按热负荷校核。'
    if typ == 'TOWER':
        stages = float(params.get('NSTAGE', 40))
        trays = math.ceil(max(stages - 2, 1) / .8)
        d, length, thickness = 1600, trays * 500 + 4000, 16
        basis = f'塔径暂取1600mm；板效率0.80、板间距500mm，约{trays}块实际板，另计4m空间。高塔需复核分段及风震载荷。'
    elif typ == 'REACTOR':
        d, length, thickness = 1200, 3600, 16
        basis = '反应器暂按直径1200mm、筒体长径比3占位；未按动力学、催化剂或停留时间完成选型。'
    elif typ == 'FLASH':
        d, length, thickness = 1000, 3000, 12
        basis = '闪蒸罐暂按直径1000mm、筒体长径比3；需校核气液分离速度与液体停留时间。'
    elif typ != 'HX':
        return {'values': {'design_temperature': temperature, 'design_pressure': f'{pressure:g}',
            'diameter': '不适用', 'length': '厂家选型', 'thickness': '不适用',
            'material': '厂家选型', 'corrosion': '不适用', 'insulation': '按机组要求'},
            'basis': '压缩机、阀门与分流节点不套用容器筒体尺寸，结构由机组选型确定。'}
    return {'values': {'design_temperature': temperature, 'design_pressure': f'{pressure:g}',
        'diameter': str(d), 'length': str(length), 'thickness': str(thickness), 'material': material,
        'corrosion': '1' if cold < -20 else '2',
        'insulation': '泡沫玻璃100mm / 隔汽层' if cold < -20 else '岩棉80mm' if hot >= 100 else '暂不保温'},
        'basis': basis + ' 设计压力暂取最大接管压力的1.1倍向上取整（保守包络，待确认表压基准）；温度上限加30°C，低温下限减10°C。壁厚未作强度验算。'}

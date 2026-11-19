"""User-authorized reference supplementation; original files stay unchanged."""
import copy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'data/equipment_parameters.json'
data=json.loads(path.read_text(encoding='utf-8'))
mapping={'REACTOR':('REACTOR','REACTOR'),'COOLER':('COOLER','COOLER1'),'HEATER':('HEATER','HEATER'),'FLASH':('FLASH','FLASH1')}
for target,(a_id,b_id) in mapping.items():
    unit=next(u for u in data['route_c']['units'] if u['id']==target)
    unit['rows']=[r for r in unit['rows'] if r.get('source_type')!='USER_AUTHORIZED_REFERENCE']
    existing={r['key'] for r in unit['rows']}
    source=next(u for u in data['route_a']['units'] if u['id']==a_id)
    comparison=next(u for u in data['route_b']['units'] if u['id']==b_id)
    for row in source['rows']:
        if row['key'] in existing:continue
        r=copy.deepcopy(row)
        r.update(source_type='USER_AUTHORIZED_REFERENCE',source_file=data['route_a']['file'],source_locator=source['locator'],source_sha256=data['route_a']['sha256'])
        matches=any(x['key']==r['key'] and x['value']==r['value'] and x['unit']==r['unit'] for x in comparison['rows'])
        r['reference_note']='按用户要求沿用 example1 的对应设备设置；'+('example2 对应字段一致。' if matches else '本字段采用 example1；example2 未显式提供相同字段值。')+'这是补填设置，尚未重新求解。'
        unit['rows'].append(r)
    unit['note']='缺项按用户要求参考 example1 / example2 补齐；example3 原有字段保持不变。逐项来源见表格。'
data['route_c']['notice']='设备设置包括 example3 原始字段及按用户要求参考 example1 / example2 的补填项。补填来源逐项标明，尚未重新求解；不修改现有物流结果。理论级数不等于实际塔板数。'
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Supplemented rows:',sum(r.get('source_type')=='USER_AUTHORIZED_REFERENCE' for u in data['route_c']['units'] for r in u['rows']))

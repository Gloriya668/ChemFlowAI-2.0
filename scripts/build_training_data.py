"""Rebuild allowlisted corpus and source-disjoint datasets, Python standard library only."""
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DWSIM='770c46680c72e3966fc1ff2e31698d341ffba670'
IDAES='5e51567b315a25a4ed0057b4a23afe02f1109482'
SYN='chemflow-process-synthesis'; SIM='chemflow-simulation-review'; PROP='chemflow-property-modeling'
TEA='chemflow-optimization-tea'
LABELS={
 'BiodieselProduction':'生物柴油生产', 'CavettProblem':'Cavett 回流流程',
 'ChemSepColumnSnapshot':'ChemSep 精馏塔', 'ColdNaphthaStabiliser':'冷石脑油稳定塔',
 'ExtractiveDistillation':'萃取精馏', 'GasLiquidSeparatorSizing':'气液分离器尺寸',
 'GibbsAndEquilibriumReactors':'Gibbs 吉布斯平衡反应器',
 'HeatExchangerSizingAndDesign':'换热器尺寸设计', 'HydrocycloneCustomUnitOperation':'旋液分离器自定义单元',
 'HydrogenproductionthroughMethaneCatalyticSteamReforming':'甲烷催化蒸汽重整制氢',
 'LiquidLiquidExtraction':'液液萃取', 'MembraneCustomUnitOperation':'膜分离自定义单元',
 'NaturalGasProcessingUnit':'天然气处理', 'PetroleumDistillation':'石油蒸馏',
 'SO2OxidationEquilibrium':'二氧化硫氧化平衡', 'SimpleAbsorberSample':'吸收塔',
 'SimpleLNGExchangerCustomUnitOperation':'液化天然气 LNG 换热器',
 'ThreePhaseSeparator':'三相分离器', 'TraceMethaneStripper':'痕量甲烷汽提',
 'VesselDepressurization':'容器泄压', 'WideBoilingStripper':'宽沸程汽提塔'}
# Frozen before fitting. Test queries are authored checks, not real user logs.
TEST={
 'NaturalGasProcessingUnit':['天然气加工的流程案例有哪些组分？','Find a natural gas processing flowsheet and its unit types.'],
 'HydrogenproductionthroughMethaneCatalyticSteamReforming':['想找甲烷水蒸气重整制氢的参考流程','Show a catalytic steam reforming hydrogen example.'],
 'HeatExchangerSizingAndDesign':['换热设备的尺寸设计有没有官方案例？','Need an example of heat exchanger sizing.'],
 'LiquidLiquidExtraction':['两种液相之间的萃取怎么找参考文件？','Find liquid liquid extraction compounds.'],
 'ThreePhaseSeparator':['三相分离设备参考流程里的物性方法是什么？','Find a three phase separator example.'],
 'costing-framework':['资本费用和运行费用如何在 IDAES 中组织？','How are unit costing blocks connected to flowsheet costing?']}
DEV={'BiodieselProduction':['生物柴油生产流程','biodiesel production compounds'],
     'PetroleumDistillation':['石油蒸馏案例','petroleum distillation units'],
     'MembraneCustomUnitOperation':['膜分离案例','membrane custom unit operation'],
     'rule-chemflow-validation':['独立验证和同源回放的区别','Ground Truth 验证边界']}

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')

def digest(raw):return hashlib.sha256(raw).hexdigest()

def xml_read(path):
    raw=path.read_bytes()
    if path.suffix=='.dwxmz':
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            candidates=[f for f in z.infolist() if f.filename.lower().endswith(('.xml','.dwxml'))]
            if len(candidates)!=1 or candidates[0].file_size>50_000_000:raise ValueError('Unsafe XML size/container')
            raw=z.read(candidates[0])
    if len(raw)>50_000_000 or b'<!DOCTYPE' in raw.upper():raise ValueError('Unsafe XML')
    return ET.fromstring(raw)

def build():
    from build_engineering_cards import build as build_cards
    build_cards()
    docs=[]; sources=[]; inventory=[]
    for project,repo,version,license_name in [('dwsim','DanWBR/dwsim10',DWSIM,'GPL-3.0'),('idaes','IDAES/idaes-pse',IDAES,'BSD-3-Clause')]:
        for f in sorted((ROOT/'knowledge_base/sources'/project).iterdir()):
            relative=f.name.replace('__','/')
            sources.append({'path':f.relative_to(ROOT).as_posix(),'upstream_path':relative,
                            'url':f'https://github.com/{repo}/blob/{version}/'+urllib.parse.quote(relative),
                            'download_url':f'https://raw.githubusercontent.com/{repo}/{version}/'+urllib.parse.quote(relative),
                            'commit':version,'license':license_name,'sha256':digest(f.read_bytes()),'bytes':f.stat().st_size})
    bypath={s['path']:s for s in sources}
    def add(id,title,text,file,skills,source_type='REFERENCE_DATA',group=None):
        citation=file.relative_to(ROOT).as_posix(); src=bypath.get(citation,{})
        docs.append({'id':id,'group':group or id,'title':title,'text':text,'citation':citation,
                     'url':src.get('url',''),'version':src.get('commit','local-v1'),
                     'license':src.get('license','Project-local; original package terms apply'),
                     'source_sha256':digest(file.read_bytes()),'skills':skills,'source_type':source_type,
                     'evidence_status':'RULE' if source_type=='RULE' else 'STATIC_REFERENCE'})
    for f in sorted((ROOT/'knowledge_base/sources/dwsim').glob('tests__flowsheets__*')):
        name=f.stem.removeprefix('tests__flowsheets__'); tree=xml_read(f)
        compounds=sorted({x.findtext('Name') for x in tree.findall('.//Compounds/Compound') if x.findtext('Name')})
        units=sorted({x.findtext('Type','').rsplit('.',1)[-1] for x in tree.findall('./SimulationObjects/SimulationObject')} - {''})
        packages=sorted({x.findtext('ComponentName') or x.findtext('Type') or '' for x in tree.findall('./PropertyPackages/PropertyPackage')} - {''})
        item={'id':name,'compounds':compounds,'unit_types':units,'property_packages':packages,
              'objects':len(tree.findall('./SimulationObjects/SimulationObject')),'numerical_values_imported':False}
        inventory.append(item)
        title=LABELS[name]+' / '+re.sub(r'([a-z])([A-Z])',r'\1 \2',name)
        body=f'官方流程案例：{title}\n组分 compounds: '+', '.join(compounds)+'\n设备类型 unit operations: '+', '.join(units)+'\n物性包 property packages: '+', '.join(packages)+'\n仅静态 XML 元数据，未重新求解。文件中的历史收敛标志和数值不构成本次验证。可能需要外部单元或插件。'
        add(name,title,body,f,[SYN,SIM,PROP])
    titles={'chemflow-intake':'设计基准 进料 温度 压力 流量 组成 basis feed',
            PROP:'物性方法 相平衡 二元参数 PR SRK NRTL thermodynamics',
            SYN:'流程拓扑 连接 回流 process synthesis',SIM:'求解收敛 质量守恒 单位换算 convergence balance',
            TEA:'经济评估 优化 成本 CAPEX NPV IRR TEA',
            'chemflow-validation':'独立验证 真实求解 同源回放 Ground Truth validation'}
    for skill,title in titles.items():
        f=ROOT/'skills'/skill/'references/contract.md'
        add('rule-'+skill,title,f.read_text(encoding='utf-8'),f,[skill],'RULE')
    f=ROOT/'knowledge_base/sources/idaes/docs__reference_guides__core__costing__costing_framework.rst'
    # Paragraph-sized chunks, one source group across all chunks.
    raw=f.read_text(encoding='utf-8'); parts=re.split(r'\n\s*\n',raw); chunks=[]; cur=''
    for p in parts:
        if len(cur)+len(p)>1600 and cur:chunks.append(cur);cur=''
        cur+=p+'\n'
    if cur:chunks.append(cur)
    for i,text in enumerate(chunks):
        add(f'costing-framework-{i}','IDAES 成本框架 资本费用 运行费用 流程设备 costing blocks',text,f,[TEA],group='costing-framework')
    f=ROOT/'knowledge_base/sources/idaes/idaes__models__costing__SSLW.py'
    # AST extracts docstrings, never imports or executes upstream code.
    import ast
    module=ast.parse(f.read_text(encoding='utf-8')); module_doc=ast.get_docstring(module) or ''
    add('sslw','IDAES SSLW 设备投资成本资本估算 capital costing',module_doc,f,[TEA])
    for node in ast.walk(module):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('cost_'):
            doc=ast.get_docstring(node)
            if doc:add('sslw-'+node.name,'SSLW '+node.name,doc[:2200],f,[TEA],group='sslw')
    f=ROOT/'knowledge_base/sources/dwsim/engine__DWSIM.FluentAPI__docs__index.md'
    add('fluent-api','DWSIM Fluent API 自动化 单位 SI Python C#',f.read_text(encoding='utf-8')[:6500],f,[SYN,SIM])
    for filename,title in [
        ('docs__explanations__model_diagnostics__index.rst','IDAES 模型诊断 自由度 单位一致性 数值缩放 Diagnostics'),
        ('docs__how_to_guides__workflow__general.rst','IDAES 模型工作流 初始化 规格 求解 Workflow'),
        ('docs__reference_guides__initialization__index.rst','IDAES 初始化器 Initialization')]:
        f=ROOT/'knowledge_base/sources/idaes'/filename
        raw=f.read_text(encoding='utf-8');group='idaes-'+filename.split('__')[-2]
        # All chunks from the same physical upstream source stay in one split group.
        paragraphs=re.split(r'\n\s*\n',raw);blocks=[];current=''
        for p in paragraphs:
            if current and len(current)+len(p)>1800:blocks.append(current);current=''
            current+=p+'\n'
        if current:blocks.append(current)
        for i,block in enumerate(blocks):
            add(f'{group}-{i}',title+f' / section {i+1}',block,f,[SIM,SYN],group=group)
    source_groups={d['citation']:d['group'] for d in docs}
    query_targets={}; card_splits={}
    for f in sorted((ROOT/'knowledge_base/sources/chemflow').glob('*.json')):
        card=json.loads(f.read_text(encoding='utf-8'))
        ref=ROOT/card['local_reference'];assert ref.is_file()
        citation=f.relative_to(ROOT).as_posix()
        src={'path':citation,'upstream_path':None,'url':'','commit':card['version'],
             'license':card['license'],'sha256':digest(f.read_bytes()),'bytes':f.stat().st_size,
             'local_reference':card['local_reference'],'reference_sha256':digest(ref.read_bytes()),
             'review_status':card['status']}
        sources.append(src);bypath[citation]=src
        group=source_groups.get(card['local_reference'],'source-'+digest(card['local_reference'].encode())[:12])
        add(card['id'],card['title'],card['text']+'\n必需输入：'+card['required_inputs']+'\n预期输出：'+card['expected_output']+'\n依据：'+card['local_reference'],f,[card['skill']],'RULE',group=group)
        docs[-1]['review_status']=card['status']
        card_splits.setdefault(group,[]).append(card)
    for group,cards in card_splits.items():
        # Derived summaries follow their original evidence group, not just their own filename.
        choice='test' if group in TEST or any(c['split']=='test' for c in cards) else 'dev' if group in DEV or any(c['split']=='dev' for c in cards) else 'train'
        if choice=='train':continue
        target=TEST if choice=='test' else DEV
        if choice=='test':DEV.pop(group,None)
        for card in cards:
            target.setdefault(group,[]).extend(card['queries'])
            for q in card['queries']:query_targets[(group,q)]=card['id']
    docs.sort(key=lambda d:d['id'])
    jsonl(ROOT/'knowledge_base/corpus.jsonl',docs)
    dump(ROOT/'knowledge_base/source_manifest.json',{'downloaded_on':'2026-10-10','sources':sources})
    dump(ROOT/'knowledge_base/flowsheet_inventory.json',inventory)
    datasets={'train':[],'dev':[],'test':[]}; sft={'train':[],'dev':[],'test':[]}
    groups=sorted({d['group'] for d in docs})
    for group in groups:
        items=[d for d in docs if d['group']==group]; first=items[0]
        split='test' if group in TEST else 'dev' if group in DEV else 'train'
        heldout=TEST.get(group) or DEV.get(group)
        if heldout:
            examples=[]
            for q in heldout:
                id=query_targets.get((group,q))
                evidence=next(d for d in items if d['id']==id) if id else first
                examples.append((q,evidence,[id] if id else [d['id'] for d in items]))
        else:
            examples=[]
            for doc in items:
                queries=[f"查找 {doc['title']} 的参考资料",f"What evidence supports {doc['title']}?"]
                if doc['id'].startswith('guide-'):
                    card=json.loads((ROOT/doc['citation']).read_text(encoding='utf-8'));queries=card['queries']
                examples.extend((q,doc,[doc['id']]) for q in queries)
        for j,(q,evidence,relevant) in enumerate(examples):
            datasets[split].append({'id':f'{group}-{j}','query':q,'relevant_ids':relevant,
                                    'source_group':group,'label_origin':'authored_synthetic_query; source-derived document label',
                                    'review_status':'NOT_EXPERT_REVIEWED'})
            answer={'action':'final','summary':'检索参考资料，未执行求解','tool':None,'arguments':{},
                    'answer':f"参考 {evidence['citation']}：\n{evidence['text'][:2000]}\n这是静态资料或工程规则，不是本次计算结果。"}
            sft[split].append({'id':f'{group}-{j}','source_group':group,'license':evidence['license'],
                'task_type':'grounded_reference_answer','evidence_ids':[evidence['id']],
                'review_status':'NOT_EXPERT_REVIEWED','synthetic':True,
                'messages':[{'role':'system','content':'你是 ChemFlow。仅依据给定证据返回 JSON；不得将参考资料说成本次求解。'},
                            {'role':'user','content':q+'\n证据：'+json.dumps(evidence,ensure_ascii=False)},
                            {'role':'assistant','content':json.dumps(answer,ensure_ascii=False)}]})
    for split,rows in datasets.items():jsonl(ROOT/f'training/ranking_{split}.jsonl',rows)
    for split,rows in sft.items():jsonl(ROOT/f'training/sft_{split}.jsonl',rows)
    dump(ROOT/'training/data_card.json',{'documents':len(docs),'source_groups':len(groups),'flowsheets':len(inventory),
        'ranking_queries':{k:len(v) for k,v in datasets.items()},'sft_examples':{k:len(v) for k,v in sft.items()},
        'split_policy':'Entire source file/flowsheet group is exclusive to train, dev or test. All corpus documents remain retrievable.',
        'labels':'Synthetic and authored; not chemical-engineer-reviewed real conversations.',
        'excluded':['data/validation','data/replay','user project outputs','API secrets','saved numerical simulation results'],
        'sft_status':'PREPARED_NOT_FINETUNED','limits':'No solver trajectory labels, no experimental ground truth, no independent engineering accuracy claim.'})
    print(json.dumps({'documents':len(docs),'flowsheets':len(inventory),'queries':{k:len(v) for k,v in datasets.items()}},ensure_ascii=False))

if __name__=='__main__':build()

"""Export a portable demo snapshot without local environments or credentials."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(r'E:/CodexOutputs/ChemFlowAI-Releases')
SKIP={'.git','.venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.cache'}
DEMOS={'742da6cc-90c5-451e-9fc9-b19942b2995a.json','cbfb0741-8b52-416f-a138-9d79f03f9b25.json'}
now=datetime.now(timezone(timedelta(hours=8)))
stamp=now.strftime('%Y%m%d-%H%M%S')
OUT.mkdir(parents=True,exist_ok=True)
target=OUT/f'ChemFlowAI-demo-latest-{stamp}.zip'
if target.exists():raise FileExistsError(target)
encode=lambda obj:(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
quickstart='''# ChemFlow AI · 最新 Demo 代码包

打包日期：2026-10-23

## 本次内容

- 企业版九步工程工作流、两套完成的演示案例、工程报告和页面动效。
- 学习版十阶段路径：环境保护后加入安全评估。
- 流程建立中的动态控制工作台：五回路、P/PI 参数、进料扰动、曲线及动画。
- 环保、噪声、安全的提炼内容与交互学习模块。
- HAZOP 7×5 风险矩阵、8 类节点、15 项分析条目与改进记录。
- 学习记录本地保存与报告导出；页面已移除环保安全模块的文件入口和来源标签。

## 首次运行（Windows x64）

1. 将整个 ChemFlowAI 文件夹解压到固定位置，例如 E:\\ChemFlowAI。不要在压缩包内启动。
2. 准备 Windows x64 Python 3.12。在项目目录打开 PowerShell，运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\\Setup-Offline.ps1 -PythonExe "C:\\Python312\\python.exe"
.\\Start-ChemFlow.cmd
```

3. 浏览器打开 http://127.0.0.1:8765/ 。前端已编译，正常运行无需安装 Node.js。
4. 如端口被占用，可运行 `powershell -ExecutionPolicy Bypass -File .\\Start-ChemFlow.ps1 -Port 8766`，再打开 http://127.0.0.1:8766/ 。
5. 停止服务：`powershell -ExecutionPolicy Bypass -File .\\Stop-ChemFlow.ps1 -Port 8765`（使用其他端口时相应修改）。

## 修改前端

安装 Node.js 后，在 frontend 目录执行 `npm ci`、`npm run build`，后端会提供 frontend/dist 中的页面。

## 数据与配置

- runtime/projects 中包含两套已完成的演示案例；未打包其他临时任务、日志、备份或本机 Python 环境。
- 学习记录在使用后保存到解压目录中的 runtime；浏览器草稿保存在对应浏览器。
- config/llm.json 中的服务地址、模型名与 API 密钥为空；DWSIM 与外部服务需按实际环境配置。
- 动态控制曲线为页面明确标注的教学模型计算；HAZOP 等级为学习者记录，不代表工程审查结论。
- 源码和已编译前端均已包含。本次未重跑应用测试；最近前端生产构建已通过。

## 文件完整性

release-manifest.json 记录各文件的 SHA-256；压缩包旁的 .sha256 文件记录整个 ZIP 的校验值。
README.md 中较早的版本与测试数字为历史记录，当前交付以本文件为准。
'''
overrides={
 'config/llm.json':encode({'api_key':'','base_url':'','model':'','timeout_seconds':60}),
 'config/dwsim.json':encode({'command':[],'cwd':'','timeout_seconds':120,'models':{}}),
 'config/simulators.json':encode({'reference_replay':{'enabled':True},'dwsim':{'enabled':False,'endpoint':None},'external_mcp':{'enabled':False,'endpoint':None,'allowed_tools':['load_model','set_feed','set_unit_parameter','solve','get_streams','get_duties']}}),
 '开始使用_最新Demo.md':quickstart.encode('utf-8'),
 'demo-release.json':encode({'package':'ChemFlowAI latest demo','packaged_at':now.isoformat(),'source_build':'2026-10-10-v3','frontend_build':'latest successful production build','features':['dynamic-control-learning','environment-noise-safety-learning','hazop-7x5-matrix'],'contains_saved_demo_projects':True,'application_tests_rerun':False})
}
files={}
for path in ROOT.rglob('*'):
 if not path.is_file():continue
 rel=path.relative_to(ROOT);name=rel.as_posix()
 if any(part in SKIP for part in rel.parts):continue
 if any(part.startswith('.env') for part in rel.parts):continue
 if path.suffix.lower() in {'.pyc','.log','.pid','.tmp','.bak','.tsbuildinfo'}:continue
 if name=='release-manifest.json':continue
 if rel.parts[0]=='runtime' and not (len(rel.parts)==3 and rel.parts[1]=='projects' and rel.name in DEMOS):continue
 # Inspection renders and intermediate extraction are not runtime dependencies.
 if name.startswith('references/hazop/'):continue
 files[name]=path
missing=[n for n in ['frontend/dist/index.html','frontend/src/learning/HazopStudy.tsx','frontend/src/learning/DynamicsLab.tsx'] if n not in files]
if missing:raise RuntimeError('Missing required deliverables: '+str(missing))
readme=(ROOT/'README.md').read_text(encoding='utf-8-sig')
overrides['README.md']=('> 最新交付（2026-10-23）：请先阅读 **开始使用_最新Demo.md**。下面保留项目历史文档。\n\n'+readme).encode('utf-8')
manifest={}
with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for name in sorted(set(files)|set(overrides)):
  data=overrides[name] if name in overrides else files[name].read_bytes()
  manifest[name]=hashlib.sha256(data).hexdigest()
  archive.writestr('ChemFlowAI/'+name,data)
 archive.writestr('ChemFlowAI/release-manifest.json',encode(manifest))
# Archive integrity only; does not execute application code or tests.
with zipfile.ZipFile(target) as archive:
 bad=archive.testzip()
 if bad:raise RuntimeError('ZIP CRC failure: '+bad)
 for name,digest in manifest.items():
  if hashlib.sha256(archive.read('ChemFlowAI/'+name)).hexdigest()!=digest:raise RuntimeError('Digest mismatch: '+name)
digest=hashlib.sha256(target.read_bytes()).hexdigest()
checksum=target.with_suffix('.zip.sha256');checksum.write_text(digest+'  '+target.name+'\n',encoding='ascii')
print(json.dumps({'zip':str(target),'checksum':str(checksum),'files':len(manifest)+1,'size_mb':round(target.stat().st_size/1024**2,2),'sha256':digest},ensure_ascii=False))
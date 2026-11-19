param([string]$PythonExe = "$PSScriptRoot\.venv\Scripts\python.exe")
$ErrorActionPreference = 'Stop'
& $PythonExe "$PSScriptRoot/scripts/build_training_data.py"
if ($LASTEXITCODE -ne 0) { throw 'Dataset build failed' }
& $PythonExe "$PSScriptRoot/scripts/build_agent_dataset.py"
if ($LASTEXITCODE -ne 0) { throw 'Agent dataset build failed' }
& $PythonExe "$PSScriptRoot/scripts/organize_dataset_release.py"
if ($LASTEXITCODE -ne 0) { throw 'Dataset organization failed' }
& $PythonExe "$PSScriptRoot/scripts/audit_training_data.py"
if ($LASTEXITCODE -ne 0) { throw 'Dataset audit failed' }
& $PythonExe "$PSScriptRoot/scripts/train_knowledge_ranker.py"
if ($LASTEXITCODE -ne 0) { throw 'Ranker training failed' }
Write-Output 'Completed local retrieval training. See training/evaluation.json. No LLM fine-tuning performed.'

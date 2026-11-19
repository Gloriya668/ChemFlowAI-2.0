param([Parameter(Mandatory=$true)][string]$PythonExe)
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
& $PythonExe -c "import sys,struct; assert sys.version_info[:2]==(3,12) and struct.calcsize('P')==8, 'Requires Python 3.12 x64'"
if ($LASTEXITCODE -ne 0) { throw 'Unsupported Python' }
if (!(Test-Path '.venv\Scripts\python.exe')) { & $PythonExe -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --no-index --find-links offline_wheels -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Offline installation failed' }
Write-Host 'Offline setup complete. Run Start-ChemFlow.cmd'

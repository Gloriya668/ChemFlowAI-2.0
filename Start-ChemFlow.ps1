param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Missing local environment. Run Setup-Offline.ps1 with Windows Python 3.12 first.' }
$rootIdentityTask = [System.IO.Path]::GetFullPath($projectRoot).ToLowerInvariant()
$hasherTask = [System.Security.Cryptography.SHA256]::Create()
try { $expectedIdTask = ([System.BitConverter]::ToString($hasherTask.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($rootIdentityTask)))).Replace('-','').ToLowerInvariant() } finally { $hasherTask.Dispose() }
$healthTask = $null
try { $healthTask = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2 } catch { }
if ($healthTask) {
 if ($healthTask.instance_id -eq $expectedIdTask -and $healthTask.build -eq '2026-10-10-v3') { Write-Output "This ChemFlow V3 instance is running at http://127.0.0.1:$Port"; exit 0 }
 throw "Port $Port is serving another or older ChemFlow instance. Stop it from its own folder, or start this package with a different -Port."
}
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'runtime') | Out-Null
$serverTask = Start-Process -FilePath $pythonPath -ArgumentList @('-m','uvicorn','backend.app:app','--host','127.0.0.1','--port',"$Port") -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot 'runtime\server.log') -RedirectStandardError (Join-Path $projectRoot 'runtime\server-error.log') -PassThru
$serverTask.Id | Set-Content -LiteralPath (Join-Path $projectRoot 'runtime\server.pid')
Write-Output "Starting ChemFlow at http://127.0.0.1:$Port (PID $($serverTask.Id))"
$readyTask = $false
for ($attemptTask=0; $attemptTask -lt 20; $attemptTask++) {
 $serverTask.Refresh()
 if ($serverTask.HasExited) { throw 'Server exited. Inspect runtime/server-error.log.' }
 try {
  $probeTask = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 1
  if ($probeTask.instance_id -eq $expectedIdTask -and $probeTask.build -eq '2026-10-10-v3') { $readyTask=$true; break }
 } catch { }
 Start-Sleep -Milliseconds 500
}
if (-not $readyTask) { throw 'Startup not verified. Inspect runtime/server-error.log before opening the app.' }
Write-Output "ChemFlow V3 ready at http://127.0.0.1:$Port. LLM and DWSIM must be configured and tested separately."

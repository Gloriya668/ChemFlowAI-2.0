param([int]$Port=8765)
$ErrorActionPreference='Stop'
$projectRoot=$PSScriptRoot
$listenerTask=Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listenerTask) {
 $procTask=Get-CimInstance Win32_Process -Filter "ProcessId=$($listenerTask.OwningProcess)"
 $parentTask=Get-CimInstance Win32_Process -Filter "ProcessId=$($procTask.ParentProcessId)" -ErrorAction SilentlyContinue
 $savedPidTask=Get-Content -LiteralPath (Join-Path $projectRoot 'runtime\server.pid') -ErrorAction SilentlyContinue
 $ownsDirectTask=$procTask.CommandLine -like "*$projectRoot*"
 $ownsChildTask=$parentTask -and $parentTask.CommandLine -like "*$projectRoot*" -and [string]$parentTask.ProcessId -eq [string]$savedPidTask
 if ($procTask.CommandLine -notlike '*backend.app:app*' -or (-not $ownsDirectTask -and -not $ownsChildTask)) { throw 'Refusing to stop an unrelated process.' }
 Stop-Process -Id $procTask.ProcessId
 Write-Output 'ChemFlow server stopped.'
}

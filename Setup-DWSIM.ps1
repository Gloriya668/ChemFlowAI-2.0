param([string]$RuntimeZip = '')
$ErrorActionPreference = 'Stop'
$releaseUrl = 'https://github.com/DanWBR/dwsim10/releases/download/v10.2.11/dwsim-10.2.11-win-x64.zip'
$expectedSha = '2c244be938684ec5db8abde4f861ed484179968b90f0380347bf8f78d0fa0e79'
$vendor = Join-Path $PSScriptRoot 'vendor'
New-Item -ItemType Directory -Path $vendor -Force | Out-Null
if (-not $RuntimeZip) {
    $RuntimeZip = Join-Path $vendor 'dwsim-10.2.11-win-x64.zip'
    if (-not (Test-Path -LiteralPath $RuntimeZip)) {
        Write-Host 'Downloading official DWSIM 10.2.11 Windows x64 portable runtime...'
        Invoke-WebRequest -Uri $releaseUrl -OutFile $RuntimeZip -UseBasicParsing
    }
}
$RuntimeZip = (Resolve-Path -LiteralPath $RuntimeZip).Path
$actualSha = (Get-FileHash -LiteralPath $RuntimeZip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha -ne $expectedSha) { throw 'Wrong archive or checksum. Use the official dwsim-10.2.11-win-x64.zip runtime, not dwsim-windows.zip source code.' }
$runtime = Join-Path $vendor 'dwsim-10.2.11'
Expand-Archive -LiteralPath $RuntimeZip -DestinationPath $runtime -Force
if (-not (Test-Path -LiteralPath (Join-Path $runtime 'DWSIM.Automation.dll'))) { throw 'Missing DWSIM.Automation.dll' }
Copy-Item -Path (Join-Path $PSScriptRoot 'tools/dwsim-mcp-bin/dwsim-mcp.*') -Destination $runtime -Force
$configPath = Join-Path $PSScriptRoot 'config/dwsim.json'
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$config.command = @('vendor/dwsim-10.2.11/dwsim-mcp.exe', '--stdio')
$config.cwd = 'vendor/dwsim-10.2.11'
$config | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $configPath -Encoding UTF8
Write-Host 'DWSIM runtime configured. Existing model registrations were preserved.'
Write-Host 'Test in ChemFlowAI or run: .venv\Scripts\python.exe scripts\dwsim_smoke.py'
Write-Host 'If Windows reports 4551 / 0x800711C7, ask your administrator to review application-control policy. This script does not disable security controls.'

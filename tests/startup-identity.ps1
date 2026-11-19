param([ValidateSet('valid','old','other')][string]$Case='old')
$rootTask=Split-Path -Parent $PSScriptRoot
$hashTask=[System.Security.Cryptography.SHA256]::Create()
try {$identityTask=([BitConverter]::ToString($hashTask.ComputeHash([Text.Encoding]::UTF8.GetBytes([IO.Path]::GetFullPath($rootTask).ToLowerInvariant())))).Replace('-','').ToLowerInvariant()} finally {$hashTask.Dispose()}
# Test doubles are scoped to this test process; no real service is started or stopped.
function Test-Path {param($LiteralPath) return $true}
function Invoke-RestMethod {
 param($Uri,$TimeoutSec)
 if($Case -eq 'old'){return @{agent='RULE_ENGINE'}}
 if($Case -eq 'other'){return @{instance_id='other-folder';build='2026-10-10-v3'}}
 return @{instance_id=$identityTask;build='2026-10-10-v3'}
}
function Start-Process {throw 'TEST FAILURE: Should not start a service for occupied port'}
try {& (Join-Path $rootTask 'Start-ChemFlow.ps1'); if($Case -ne 'valid'){throw 'TEST FAILURE: Accepted wrong service'}}
catch {if($_.Exception.Message -notlike '*another or older ChemFlow instance*'){throw};Write-Output "PASS: rejected $Case service"}

@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-ChemFlow.ps1"
if errorlevel 1 (
 echo Startup failed. Check the error above. Do not open an old service as this version.
 pause
 exit /b 1
)
echo Open http://127.0.0.1:8765 in your browser.
pause

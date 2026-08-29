@echo off
rem Double-click launcher for mgs4ecf.ps1.
rem Uses the PowerShell that ships with Windows, so nothing needs installing.
rem -ExecutionPolicy Bypass applies to this one process only; it changes nothing
rem system-wide and needs no admin rights.

setlocal
set "PS=powershell.exe"
where pwsh.exe >nul 2>&1 && set "PS=pwsh.exe"

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0mgs4ecf.ps1" -Interactive %*

endlocal

@echo off
rem Hullbreach platform doctor for Windows: the platform runs inside WSL, so
rem this only explains (and, if you agree, starts) the WSL setup. The real
rem doctor is ./doctor.sh inside an Ubuntu (WSL) terminal.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0doctor.ps1" %*
echo.
pause

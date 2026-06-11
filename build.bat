@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\build_exe.ps1"
if errorlevel 1 exit /b 1
echo.
echo Pressione uma tecla para fechar...
pause >nul

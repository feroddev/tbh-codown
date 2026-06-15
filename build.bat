@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\build_exe.ps1"
if errorlevel 1 exit /b 1
echo.
echo Pronto para distribuir: compacte a pasta dist\TBH-Monitor inteira em um ZIP.
echo O usuario deve extrair tudo e executar TBH-Monitor.exe.
echo.
echo Pressione uma tecla para fechar...
pause >nul

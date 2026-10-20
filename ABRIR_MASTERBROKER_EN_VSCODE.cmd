@echo off
setlocal
set "VSCODE=C:\Users\oscar\AppData\Local\Programs\Microsoft VS Code\Code.exe"
if not exist "%VSCODE%" (
  echo No se encontro VS Code en la ruta configurada.
  pause
  exit /b 1
)
start "MasterBroker VS Code" "%VSCODE%" "%~dp0"
exit


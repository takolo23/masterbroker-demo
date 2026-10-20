@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=C:\Users\oscar\AppData\Local\Python\bin\python.exe"
if not exist "%PYTHON_EXE%" ( echo Python no esta instalado.& pause & exit /b 1 )
start "MasterBroker Panel" /B "%PYTHON_EXE%" dashboard.py
start "MasterBroker Demo" /B "%PYTHON_EXE%" agent_service.py --watch --interval 60
start "MasterBroker Demo Autopilot" /B "%PYTHON_EXE%" demo_autopilot.py --watch --interval 60
start "" http://127.0.0.1:8765
exit


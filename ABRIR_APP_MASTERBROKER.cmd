@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=C:\Users\oscar\AppData\Local\Python\bin\python.exe"
if not exist "%PYTHON_EXE%" ( echo Python no esta instalado.& pause & exit /b 1 )
"%PYTHON_EXE%" masterbroker_app.py


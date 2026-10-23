@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Kurulum yapilmamis. Once KUR.bat calistiriliyor...
  call KUR.bat
  exit /b
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0desktop.py"

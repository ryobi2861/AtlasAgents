@echo off
setlocal
chcp 65001 >nul
title ATLAS - EXE derleme
cd /d "%~dp0"
REM Tek klasorlu, konsolsuz ATLAS.exe uretir (dist\ATLAS\ATLAS.exe).
REM Exe surumunde veriler %%APPDATA%%\ATLAS klasorunde tutulur.
if not exist ".venv\Scripts\python.exe" (
  echo Once KUR.bat calistirin.
  pause & exit /b 1
)
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check "pyinstaller>=6.5"
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name ATLAS ^
  --icon assets\atlas.ico ^
  --add-data "static;static" --add-data "assets;assets" --add-data "atlas\ida_script.py;atlas" ^
  --hidden-import launcher --hidden-import atlas.core --hidden-import atlas.repair --hidden-import atlas.ollama_ctl --hidden-import atlas.ida --hidden-import psutil ^
  --collect-all webview --collect-all capstone --collect-all pyautogui --collect-all pygetwindow ^
  --collect-all mcp --collect-all mcp_types --collect-all httpx2 ^
  desktop.py
if errorlevel 1 (
  echo [X] Derleme basarisiz.
  pause & exit /b 1
)
echo.
echo  OK:  dist\ATLAS\ATLAS.exe
echo  Not: Ollama ve modeller yine gerekli (KUR.bat bunlari kurar).
pause

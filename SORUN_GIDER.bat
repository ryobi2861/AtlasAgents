@echo off
chcp 65001 >nul
title ATLAS - Hata ayiklama modu
cd /d "%~dp0"
echo ATLAS konsol + gelistirici araclari ile baslatiliyor. Hatalar bu pencerede gorunur.
echo Log dosyasi: data\atlas.log
echo.
".venv\Scripts\python.exe" desktop.py --debug
echo.
echo ATLAS kapandi. Hata varsa yukaridaki metni kopyalayin.
pause

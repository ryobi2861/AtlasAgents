@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Ollama guncelleniyor (qwen3.6 / qwen3.8 icin guncel surum gerekli)...
winget upgrade -e --id Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements >nul 2>&1
".venv\Scripts\python.exe" launcher.py --setup
echo Eksik modeller indirildi, ATLAS'in artik kullanmadigi eski modeller silindi.
pause

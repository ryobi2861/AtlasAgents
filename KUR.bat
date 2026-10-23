@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
title ATLAS AI Agent - Tek Tikla Kurulum
cd /d "%~dp0"
echo.
echo  =====================================================
echo     ATLAS AI Agent  -  Tek Tikla Kurulum
echo     RTX 4060 8GB + 32GB RAM icin optimize edildi
echo  =====================================================
echo.

where winget >nul 2>&1
if errorlevel 1 (
  echo [!] winget bulunamadi. Microsoft Store'dan "Uygulama Yukleyici" ^(App Installer^) kurun.
  echo     Alternatif: Python 3.12 ve Ollama'yi elle kurup bu dosyayi tekrar calistirin.
)

REM ---------------------------------------------------------- 1) Python
echo [1/6] Python kontrol ediliyor...
set "PY="
for %%V in (3.12 3.11 3.13 3.10) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,13) else 1)" >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo       Uyumlu Python bulunamadi, Python 3.12 kuruluyor...
  winget install -e --id Python.Python.3.12 --scope user --silent --accept-source-agreements --accept-package-agreements
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY="%LOCALAPPDATA%\Programs\Python\Python312\python.exe""
)
if not defined PY (
  echo [X] Python kurulamadi. https://www.python.org/downloads/release/python-3128/ adresinden 3.12 kurun.
  pause & exit /b 1
)
echo       OK: %PY%

REM ---------------------------------------------------------- 2) Ollama
echo [2/6] Ollama kontrol ediliyor...
set "OLL="
where ollama >nul 2>&1 && set "OLL=ollama"
if not defined OLL if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLL=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not defined OLL (
  echo       Ollama kuruluyor...
  winget install -e --id Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLL=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
)
if not defined OLL (
  echo       winget basarisiz, resmi kurulum dosyasi indiriliyor...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile \"$env:TEMP\OllamaSetup.exe\""
  "%TEMP%\OllamaSetup.exe" /VERYSILENT /NORESTART
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLL=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
)
if not defined OLL (
  echo [X] Ollama kurulamadi. https://ollama.com/download adresinden kurun.
  pause & exit /b 1
)
echo       OK: Ollama bulundu
echo       Ollama en guncel surume yukseltiliyor (Qwen3.6 ve Qwen3.8 icin guncel surum gerekli)...
winget upgrade -e --id Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements >nul 2>&1

REM ---------------------------------------------------------- 3) Ollama performans ayarlari (kalici)
echo [3/6] Ollama performans ayarlari yaziliyor...
setx OLLAMA_FLASH_ATTENTION 1 >nul
setx OLLAMA_KV_CACHE_TYPE q8_0 >nul
setx OLLAMA_MAX_LOADED_MODELS 2 >nul
setx OLLAMA_NUM_PARALLEL 1 >nul
setx OLLAMA_KEEP_ALIVE 30m >nul
echo       OK: FlashAttention, q8_0 KV cache, tek paralel slot, 30dk bellekte tutma

REM ---------------------------------------------------------- 4) WebView2 (masaustu arayuz motoru)
echo [4/6] Microsoft Edge WebView2 kontrol ediliyor...
set "WV2="
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv >nul 2>&1 && set "WV2=1"
reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv >nul 2>&1 && set "WV2=1"
reg query "HKCU\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" /v pv >nul 2>&1 && set "WV2=1"
if not defined WV2 (
  echo       WebView2 kuruluyor...
  winget install -e --id Microsoft.EdgeWebView2Runtime --silent --accept-source-agreements --accept-package-agreements
  if errorlevel 1 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile \"$env:TEMP\MicrosoftEdgeWebview2Setup.exe\""
    "%TEMP%\MicrosoftEdgeWebview2Setup.exe" /silent /install
  )
)
echo       OK

REM ---------------------------------------------------------- 5) Sanal ortam + paketler
echo [5/6] Python sanal ortami ve paketler kuruluyor...
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
if not exist ".venv\Scripts\python.exe" (
  echo [X] Sanal ortam olusturulamadi.
  pause & exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet --disable-pip-version-check
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
  echo [X] Paket kurulumu basarisiz. Internet baglantinizi kontrol edin.
  pause & exit /b 1
)
echo       OK

REM ---------------------------------------------------------- 6) Modeller
echo [6/6] Modeller indiriliyor (toplam ~43 GB, ilk seferde uzun surer)...
echo       - huihui_ai/Qwen3.6-abliterated:35b-a3b  (24 GB)   mimar + kodlayici + gorsel
echo       - orcarouter/Qwen3.8-27B-Uncensored:q4_K_M (18 GB) bagimsiz kod review

echo       - qwen3-embedding:0.6b                   (0.6 GB)  anlamsal hafiza
echo       Eski 9b, qwen3-coder 30b ve qwen3-vl 8b yeni modeller kurulduktan sonra silinir.
".venv\Scripts\python.exe" launcher.py --setup

REM ---------------------------------------------------------- Opsiyonel: guc plani
echo.
choice /C EH /N /M "Windows 'Yuksek Performans' guc planini etkinlestireyim mi? [E/H] "
if !errorlevel! EQU 1 (
  powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1 && echo       OK: Yuksek performans etkin || echo       Plan bulunamadi, atlandi.
)

REM ---------------------------------------------------------- Kisayollar (Masaustu + Baslat menusu)
set "TGT=%~dp0.venv\Scripts\pythonw.exe"
set "ICO=%~dp0assets\atlas.ico"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; foreach($d in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))){ $s=$w.CreateShortcut($d+'\ATLAS.lnk'); $s.TargetPath='%TGT%'; $s.Arguments='\"%~dp0desktop.py\"'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICO%'; $s.Description='ATLAS - Yerel AI Ajan'; $s.Save() }" >nul 2>&1
if exist "%USERPROFILE%\Desktop\ATLAS AI Agent.lnk" del "%USERPROFILE%\Desktop\ATLAS AI Agent.lnk" >nul 2>&1
echo.
echo  =====================================================
echo     KURULUM TAMAM!  Masaustundeki / Baslat menusundeki
echo     "ATLAS" kisayolu veya BASLAT.bat ile acin.
echo     Global kisayol: Ctrl+Alt+Space  (goster/gizle)
echo  =====================================================
echo.
choice /C EH /N /M "Simdi baslatayim mi? [E/H] "
if !errorlevel! EQU 1 start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0desktop.py"
endlocal

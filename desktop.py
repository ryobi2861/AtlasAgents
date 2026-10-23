"""ATLAS Desktop — native Windows masaüstü uygulaması.

Çalıştır:  pythonw desktop.py            (konsolsuz)
           python  desktop.py --debug    (geliştirici araçları + konsol logu)

Mimari: ağ sunucusu / port / tarayıcı YOK. Arayüz, uygulama klasöründeki yerel dosyadan
(static/index.html) gömülü WebView2 motoruyla çizilir ve Python çekirdeğine (atlas/core.py)
süreç içi köprüyle (pywebview js_api) bağlanır. Akış olayları pencereye doğrudan itilir.
"""
import ctypes
import json
import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from atlas.config import ASSETS, CFG, DATA, FROZEN, STATIC  # noqa: E402
from atlas import build  # noqa: E402  (kod parmak izi — import anındaki diskteki kod)

IS_WIN = sys.platform == "win32"
DEBUG = "--debug" in sys.argv
LOG_PATH = DATA / "atlas.log"

# pythonw / .exe altında stdout yok → her şeyi log dosyasına yönlendir
if sys.stdout is None or sys.stderr is None or (not DEBUG and (FROZEN or Path(sys.executable).name.lower() == "pythonw.exe")):
    _log = open(LOG_PATH, "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = _log
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                    handlers=[logging.StreamHandler(sys.stderr)], force=True)
log = logging.getLogger("desktop")

APP_ID = "Onur.ATLAS.Agent"
UI_FILE = STATIC / "index.html"
SHOW_FLAG = DATA / "show.flag"  # ikinci örnek açılınca ilk örneğe "pencereni göster" sinyali
ICO = ASSETS / "atlas.ico"
PNG = ASSETS / "atlas.png"


def msgbox(title, text, flags=0x10):
    if IS_WIN:
        ctypes.windll.user32.MessageBoxW(None, text, title, flags)
    else:
        print(title, text)


def _json_default(o):
    if isinstance(o, (bytes, bytearray)):
        return o.decode("utf-8", "replace")
    if isinstance(o, Path):
        return str(o)
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def to_json(obj):
    return json.dumps(obj, ensure_ascii=False, default=_json_default)


_MUTEX = None


def single_instance():
    """Windows adlandırılmış mutex ile tek örnek. Zaten çalışıyorsa False döner."""
    global _MUTEX
    if not IS_WIN:
        return True
    k32 = ctypes.windll.kernel32
    k32.CreateMutexW.restype = ctypes.c_void_p
    _MUTEX = k32.CreateMutexW(None, False, "Local\\ATLAS_Agent_SingleInstance")
    return k32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


def wait_single_instance(timeout):
    """Eski örnek kapanana kadar kilidi tekrar dene. Kendi tuttuğumuz tanıtıcı kilidi canlı tutacağı için önce kapatılır."""
    global _MUTEX
    if not IS_WIN:
        return True
    k32 = ctypes.windll.kernel32
    deadline = time.time() + timeout
    while True:
        if _MUTEX:
            k32.CloseHandle(ctypes.c_void_p(_MUTEX))
            _MUTEX = None
        if single_instance():
            return True
        if time.time() >= deadline:
            return False
        time.sleep(0.4)


# ------------------------------------------------------------------ Win32 yardımcıları
if IS_WIN:
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    dwm = ctypes.windll.dwmapi
    user32.LoadImageW.restype = wintypes.HANDLE
    user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.FindWindowW.restype = wintypes.HWND
    user32.GetForegroundWindow.restype = wintypes.HWND
    dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]


def style_window(hwnd):
    """Koyu başlık çubuğu (Win10 20H1+ / Win11), başlık rengi (Win11) ve uygulama ikonu."""
    if not (IS_WIN and hwnd):
        return
    try:
        on = ctypes.c_int(1)
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (yeni/eski)
            if dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(on), 4) == 0:
                break
        caption = ctypes.c_int(0x00100D0B)  # #0b0d10 (BGR) — sadece Win11
        dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption), 4)
        corner = ctypes.c_int(2)  # yuvarlatılmış köşeler — sadece Win11
        dwm.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(corner), 4)
        if ICO.exists():
            big = user32.LoadImageW(None, str(ICO), 1, 48, 48, 0x10)
            small = user32.LoadImageW(None, str(ICO), 1, 16, 16, 0x10)
            if big:
                user32.SendMessageW(hwnd, 0x80, 1, big)
            if small:
                user32.SendMessageW(hwnd, 0x80, 0, small)
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004 | 0x0020)  # FRAMECHANGED
    except Exception as e:
        log.warning("Pencere stili uygulanamadı: %s", e)


VK = {"space": 0x20, "enter": 0x0D, "tab": 0x09, "esc": 0x1B, "insert": 0x2D, "home": 0x24, "end": 0x23}
MODS = {"alt": 0x1, "ctrl": 0x2, "control": 0x2, "shift": 0x4, "win": 0x8}


def parse_hotkey(s):
    mods, vk = 0x4000, None  # MOD_NOREPEAT
    for part in (s or "").lower().replace(" ", "").split("+"):
        if part in MODS:
            mods |= MODS[part]
        elif part in VK:
            vk = VK[part]
        elif len(part) == 1 and part.isalnum():
            vk = ord(part.upper())
        elif part.startswith("f") and part[1:].isdigit():
            vk = 0x6F + int(part[1:])
    return mods, vk


# ------------------------------------------------------------------ uygulama
SPLASH = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:#0b0d10;color:#e6e9ee;font-family:'Segoe UI Variable','Segoe UI',sans-serif;
display:flex;align-items:center;justify-content:center;user-select:none}
.w{text-align:center}.l{width:76px;height:76px;border-radius:22px;margin:0 auto 22px;background:linear-gradient(135deg,#34d399,#059669);
display:grid;place-items:center;font-weight:800;font-size:38px;color:#022c22;box-shadow:0 0 60px rgba(16,185,129,.35);animation:p 2s ease-in-out infinite}
@keyframes p{50%{box-shadow:0 0 90px rgba(16,185,129,.6);transform:scale(1.03)}}
h1{font-size:22px;letter-spacing:.3em;margin:0 0 6px;font-weight:700}#s{color:#6b7684;font-size:13px}
.b{width:180px;height:3px;background:#1e232b;border-radius:3px;margin:22px auto 0;overflow:hidden}
.b i{display:block;width:40%;height:100%;background:#10b981;border-radius:3px;animation:m 1.1s ease-in-out infinite}
@keyframes m{0%{transform:translateX(-100%)}100%{transform:translateX(250%)}}</style></head>
<body><div class="w"><div class="l">A</div><h1>ATLAS</h1><div id="s">Başlatılıyor…</div><div class="b"><i></i></div></div>
<script>function setStatus(t){document.getElementById('s').textContent=t}</script></body></html>"""


class Bridge:
    """JS → Python köprüsü (window.pywebview.api.*). Ağ yok; çağrılar süreç içinde çalışır.
    Not: pywebview yalnızca '_' ile başlamayan üyeleri JS'e açar."""

    def __init__(self, desktop):
        self._d = desktop

    def _core(self):
        if not self._d.core_ready.wait(30):
            raise RuntimeError("Çekirdek başlatılamadı")
        return self._d.core

    def request(self, method, path, body=None):
        """Tek seferlik istek. JSON metni döner: {"ok":true,"data":...} | {"ok":false,"error":...}"""
        try:
            return to_json(self._core().request(method, path, body))
        except Exception as e:
            log.exception("Köprü isteği başarısız")
            return to_json({"ok": False, "status": 500, "error": str(e)})

    def stream(self, sid, path, body=None):
        """Akış başlat; olaylar window.__atlasPush ile pencereye itilir."""
        self._core().stream(str(sid), path, body, self._d.push)
        return True

    def cancel(self, sid):
        if self._d.core:
            self._d.core.cancel(str(sid))
        return True

    def restart_app(self):
        """Güncelleme sonrası: yeni kodla yeni süreç başlat, bu süreç kapanır."""
        threading.Thread(target=self._d.restart, daemon=True, name="restart").start()
        return True


class Desktop:
    def __init__(self):
        self.window = None
        self.tray = None
        self.core = None
        self.core_ready = threading.Event()
        self._out = queue.SimpleQueue()
        self.hwnd = None
        self.quitting = False
        self.visible = not CFG["desktop"].get("start_minimized") and "--minimized" not in sys.argv
        self._tray_hint_shown = False
        self._cap_lock = threading.Lock()

    # ---------------- pencere
    def _fg(self):
        if IS_WIN and self.hwnd:
            try:
                user32.ShowWindow(self.hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(self.hwnd)
            except Exception:
                pass

    def show(self):
        if not self.window:
            return
        self.window.show()
        try:
            self.window.restore()
        except Exception:
            pass
        self.visible = True
        self._fg()

    def hide(self):
        if self.window:
            self.window.hide()
            self.visible = False

    def toggle(self):
        if self.visible and IS_WIN and self.hwnd and user32.GetForegroundWindow() == self.hwnd:
            self.hide()
        else:
            self.show()

    def focused(self):
        if not self.visible:
            return False
        if IS_WIN and self.hwnd:
            return user32.GetForegroundWindow() == self.hwnd
        return True

    def js(self, code):
        try:
            self.window.evaluate_js(code)
        except Exception as e:
            log.warning("JS çağrısı başarısız: %s", e)

    def set_on_top(self, v):
        if self.window:
            self.window.on_top = bool(v)

    # ---------------- ekran yakalama
    def capture_without_window(self):
        from atlas import screen
        with self._cap_lock:
            was = self.visible
            if was:
                self.hide()
                time.sleep(0.35)  # pencere animasyonu bitsin
            try:
                return screen.capture_full()
            finally:
                if was:
                    self.show()

    def capture_region(self):
        from atlas import screen
        with self._cap_lock:
            was = self.visible
            if was:
                self.hide()
                time.sleep(0.3)
            try:
                return screen.capture_region()
            finally:
                if was:
                    self.show()

    def screenshot_and_ask(self, region=False):
        name = self.capture_region() if region else self.capture_without_window()
        self.show()
        if name:
            self.js(f"window.atlasAttachImage && window.atlasAttachImage('{name}')")

    # ---------------- diyaloglar
    def _dlg(self, kind):
        import webview
        fd = getattr(webview, "FileDialog", None)
        if fd:
            return {"folder": fd.FOLDER, "open": fd.OPEN, "save": fd.SAVE}[kind]
        return {"folder": webview.FOLDER_DIALOG, "open": webview.OPEN_DIALOG, "save": webview.SAVE_DIALOG}[kind]

    def pick_folder(self):
        r = self.window.create_file_dialog(self._dlg("folder"))
        return (r[0] if isinstance(r, (list, tuple)) else r) if r else ""

    def pick_files(self):
        r = self.window.create_file_dialog(self._dlg("open"), allow_multiple=True)
        return list(r) if r else []

    def pick_one(self, file_types=None):
        kw = {"file_types": tuple(file_types)} if file_types else {}
        try:
            r = self.window.create_file_dialog(self._dlg("open"), allow_multiple=False, **kw)
        except Exception:
            r = self.window.create_file_dialog(self._dlg("open"), allow_multiple=False)
        return (r[0] if isinstance(r, (list, tuple)) else r) if r else ""

    def save_dialog(self, filename):
        r = self.window.create_file_dialog(self._dlg("save"), save_filename=filename or "atlas.md")
        return (r[0] if isinstance(r, (list, tuple)) else r) if r else ""

    # ---------------- bildirim
    def notify(self, title, msg):
        if not CFG["desktop"].get("notifications", True) or not self.tray:
            return
        try:
            self.tray.notify(msg[:250] or " ", title[:60])
        except Exception as e:
            log.warning("Bildirim gösterilemedi: %s", e)

    def notify_if_hidden(self, title, msg):
        if not self.focused():
            self.notify(title, msg)

    # ---------------- otomatik başlatma
    def set_autostart(self, on):
        if not IS_WIN:
            return False
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if on:
            if FROZEN:
                cmd = f'"{sys.executable}" --minimized'
            else:
                pyw = Path(sys.executable).with_name("pythonw.exe")
                cmd = f'"{pyw}" "{BASE / "desktop.py"}" --minimized'
            winreg.SetValueEx(key, "ATLAS", 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, "ATLAS")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True

    # ---------------- olaylar
    def on_before_show(self):
        try:
            self.hwnd = int(self.window.native.Handle.ToInt64())
        except Exception:
            self.hwnd = None
        style_window(self.hwnd)

    def on_shown(self):
        if IS_WIN and not self.hwnd:
            self.hwnd = user32.FindWindowW(None, self.window.title)
            style_window(self.hwnd)

    def on_closing(self):
        if self.quitting or not CFG["desktop"].get("close_to_tray", True) or not self.tray:
            self.quitting = True
            self._shutdown()
            return True
        self.hide()
        if not self._tray_hint_shown:
            self._tray_hint_shown = True
            self.notify("ATLAS arka planda çalışıyor",
                        f"Açmak için tepsi ikonuna tıkla veya {CFG['desktop'].get('hotkey_toggle', '').upper()} kısayolunu kullan.")
        return False

    def quit(self):
        self.quitting = True
        self._shutdown()
        try:
            self.window.destroy()
        except Exception:
            pass

    def restart(self):
        import subprocess
        exe = Path(sys.executable)
        if not FROZEN and exe.name.lower() == "python.exe" and exe.with_name("pythonw.exe").exists():
            exe = exe.with_name("pythonw.exe")  # konsol penceresi açılmasın
        args = [str(exe)] + ([] if FROZEN else [str(BASE / "desktop.py")]) + ["--restart"]
        flags = 0
        if IS_WIN:
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        try:
            subprocess.Popen(args, cwd=str(BASE), creationflags=flags, close_fds=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log.info("Yeniden başlatılıyor (yeni kod): %s", args)
        except Exception as e:
            log.exception("Yeniden başlatılamadı")
            msgbox("ATLAS", f"Yeniden başlatılamadı: {e}")
            return
        self.quit()

    def _shutdown(self):
        if self.tray:
            try:
                self.tray.stop()
            except Exception:
                pass
        if self.core:
            try:
                self.core.stop()
            except Exception:
                pass

    # ---------------- tepsi
    def start_tray(self):
        try:
            import pystray
            from PIL import Image
        except Exception as e:
            log.warning("Tepsi ikonu devre dışı (pystray yok): %s", e)
            return
        img = Image.open(PNG if PNG.exists() else ICO)
        M, I = pystray.Menu, pystray.MenuItem
        menu = M(
            I("ATLAS'ı göster", lambda: self.show(), default=True),
            I("Yeni sohbet", lambda: (self.show(), self.js("window.atlasNewChat && window.atlasNewChat()"))),
            I("Ekran görüntüsüyle sor", lambda: threading.Thread(target=self.screenshot_and_ask, daemon=True).start()),
            I("Bölge seçip sor", lambda: threading.Thread(target=self.screenshot_and_ask, args=(True,), daemon=True).start()),
            M.SEPARATOR,
            I("Her zaman üstte", lambda icon, item: self.set_on_top(not self.window.on_top),
              checked=lambda item: bool(self.window and self.window.on_top)),
            I("Ayarlar", lambda: (self.show(), self.js("window.atlasOpenSettings && window.atlasOpenSettings()"))),
            I("Ollama paneli", lambda: (self.show(), self.js("window.atlasOpenOllama && window.atlasOpenOllama()"))),
            M.SEPARATOR,
            I("Çıkış", lambda: self.quit()),
        )
        self.tray = pystray.Icon("ATLAS", img, "ATLAS AI Agent", menu)
        self.tray.run_detached()

    # ---------------- global kısayollar
    def start_hotkeys(self):
        if not IS_WIN:
            return

        def loop():
            binds = {1: (CFG["desktop"].get("hotkey_toggle"), self.toggle),
                     2: (CFG["desktop"].get("hotkey_screenshot"), lambda: self.screenshot_and_ask(False))}
            for hid, (combo, _) in binds.items():
                mods, vk = parse_hotkey(combo)
                if vk and not user32.RegisterHotKey(None, hid, mods, vk):
                    log.warning("Kısayol kaydedilemedi (başka uygulama kullanıyor olabilir): %s", combo)
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312 and msg.wParam in binds:  # WM_HOTKEY
                    threading.Thread(target=binds[msg.wParam][1], daemon=True).start()

        threading.Thread(target=loop, daemon=True, name="hotkeys").start()

    # ---------------- çekirdek (süreç içi, ağsız)
    def start_core(self):
        from atlas import core
        core.set_desktop(self)
        self.core = core.Core().start()
        self.core_ready.set()
        threading.Thread(target=self._pusher, daemon=True, name="ui-pusher").start()

    def push(self, sid, ev):
        """Çekirdek iş parçacığından çağrılır; olayları kuyruğa koyar (None = akış bitti)."""
        self._out.put((sid, ev))

    def _pusher(self):
        """Akış olaylarını ~30 ms'lik paketler halinde arayüze iter (token başına JS çağrısı yerine)."""
        while not self.quitting:
            batch = [self._out.get()]
            time.sleep(0.03)
            try:
                while len(batch) < 2000:
                    batch.append(self._out.get_nowait())
            except queue.Empty:
                pass
            try:
                self.window.evaluate_js("window.__atlasPush && window.__atlasPush(" + to_json(batch) + ")")
            except Exception as e:
                log.warning("Arayüze olay iletilemedi: %s", e)

    def watch_show_flag(self):
        """İkinci kez başlatılırsa (kısayol/BASLAT.bat) mevcut pencereyi öne getir."""
        def loop():
            while not self.quitting:
                try:
                    if build.RESTART_FLAG.exists():
                        # güncellenmiş kodla yeni örnek açılıyor: bu (eski) örnek kapanır, yerini ona bırakır
                        build.RESTART_FLAG.unlink()
                        log.info("Yeni sürüm başlatılıyor; eski örnek kapanıyor.")
                        self.quit()
                        os._exit(0)
                    if SHOW_FLAG.exists():
                        SHOW_FLAG.unlink()
                        self.show()
                except Exception:
                    pass
                time.sleep(0.5)
        threading.Thread(target=loop, daemon=True, name="show-flag").start()

    def boot(self):
        """GUI açıldıktan sonra arka planda: Ollama → çekirdek → arayüz."""
        try:
            self.js("setStatus('Ollama motoru hazırlanıyor…')")
            try:
                import launcher
                launcher.ensure_ollama()
            except Exception as e:
                log.warning("Ollama başlatılamadı: %s", e)
            self.js("setStatus('Ajan çekirdeği başlatılıyor…')")
            self.start_core()
            # yerel dosya (file:///…/static/index.html) — sunucu yok, port yok
            self.window.load_url(UI_FILE.resolve().as_uri())
            self.start_tray()
            self.watch_show_flag()
            self.start_hotkeys()
        except Exception as e:
            log.exception("Başlatma hatası")
            msgbox("ATLAS başlatılamadı", f"{e}\n\nAyrıntılar: {LOG_PATH}")


def main():
    # tek örnek: zaten çalışıyorsa mevcut pencereye "göster" sinyali bırak ve çık
    # (diskteki kod çalışan örnekten yeniyse — güncelleme açıldıysa — eskisini kapatıp yeni kodla aç)
    if not single_instance():
        running, _pid = build.read_running()
        if running == build.RUNNING and "--restart" not in sys.argv:
            try:
                SHOW_FLAG.write_text("1")
            except Exception:
                pass
            log.info("ATLAS zaten çalışıyor, mevcut pencere öne getiriliyor.")
            return
        log.info("Güncel olmayan örnek çalışıyor (%s → %s); yeni sürüme geçiliyor.", running, build.RUNNING)
        try:
            build.RESTART_FLAG.write_text("1")
        except Exception:
            pass
        if not wait_single_instance(10):
            # bayrağı tanımayan eski sürüm (tepside gizli) → çalışan eski ATLAS süreci kapatılır
            n = build.stop_old_instances()
            log.info("Eski ATLAS süreci sonlandırıldı: %d", n)
            if not wait_single_instance(12):
                msgbox("ATLAS", "Eski ATLAS örneği kapanmadı.\nTepsi ikonuna sağ tıklayıp Çıkış de, sonra BASLAT.bat'ı tekrar çalıştır.")
                return
    for f in (SHOW_FLAG, build.RESTART_FLAG):
        try:
            f.unlink()
        except Exception:
            pass
    build.write_running()
    log.info("ATLAS başlatılıyor, sürüm %s", build.RUNNING)

    if IS_WIN:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)  # görev çubuğunda kendi ikonu
        except Exception:
            pass

    try:
        import webview
    except ImportError:
        msgbox("ATLAS", "pywebview kurulu değil. KUR.bat dosyasını çalıştırın.")
        return

    app = Desktop()
    d = CFG["desktop"]
    from atlas.version import APP_VERSION
    app.window = webview.create_window(
        f"ATLAS v{APP_VERSION}", html=SPLASH, width=1380, height=880, min_size=(920, 600),
        background_color="#0b0d10", text_select=True, zoomable=True,
        hidden=not app.visible, on_top=bool(d.get("always_on_top")), confirm_close=False,
        js_api=Bridge(app))
    ev = app.window.events
    if hasattr(ev, "before_show"):
        ev.before_show += app.on_before_show
    ev.shown += app.on_shown
    ev.closing += app.on_closing

    storage = DATA / "webview"
    storage.mkdir(exist_ok=True)
    kwargs = dict(func=app.boot, debug=DEBUG or bool(d.get("devtools")), private_mode=False,
                  storage_path=str(storage), http_server=False)
    if IS_WIN:
        kwargs["gui"] = "edgechromium"
    if ICO.exists():
        kwargs["icon"] = str(ICO)
    try:
        webview.start(**kwargs)
    except TypeError:  # eski pywebview sürümleri 'icon' desteklemez
        kwargs.pop("icon", None)
        webview.start(**kwargs)
    app._shutdown()
    os._exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("Kritik hata")
        msgbox("ATLAS — kritik hata", f"{e}\n\nLog: {LOG_PATH}")

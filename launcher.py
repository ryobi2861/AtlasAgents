"""ATLAS başlatıcı.

  python launcher.py           -> Ollama'yı optimize ayarlarla başlatır, masaüstü uygulamasını açar
  python launcher.py --setup   -> modelleri indirir (kurulum)
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from atlas import ollama_ctl  # noqa: E402
from atlas.config import CFG  # noqa: E402

IS_WIN = sys.platform == "win32"
OLLAMA = CFG["ollama_url"].rstrip("/")


def c(text, color="0"):
    return f"\033[{color}m{text}\033[0m"


def http_json(path, body=None, timeout=5):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def ollama_up():
    try:
        http_json("/api/version", timeout=2)
        return True
    except Exception:
        return False


def ensure_ollama():
    """Ollama'yı ATLAS'ın optimize ayarlarıyla çalışır hale getirir (bkz. atlas/ollama_ctl.py)."""
    colors = {"ok": "32", "warn": "33", "err": "31", "info": "36"}
    marks = {"ok": "✔", "warn": "↻", "err": "✖", "info": "•"}
    return ollama_ctl.ensure(lambda m, lvl="info": print(c(f"{marks.get(lvl, '•')} {m}", colors.get(lvl, "0"))))


def pull(model):
    print(c(f"\n⇣ {model}", "36"))
    req = urllib.request.Request(OLLAMA + "/api/pull", data=json.dumps({"model": model, "stream": True}).encode(),
                                 headers={"Content-Type": "application/json"})
    last = ""
    with urllib.request.urlopen(req, timeout=None) as r:
        for line in r:
            if not line.strip():
                continue
            ev = json.loads(line)
            if "error" in ev:
                print(c(f"\n  HATA: {ev['error']}", "31"))
                return False
            st = ev.get("status", "")
            if ev.get("total"):
                pct = ev.get("completed", 0) / ev["total"] * 100
                bar = "█" * int(pct / 4) + "░" * (25 - int(pct / 4))
                print(f"\r  {bar} {pct:5.1f}%  {ev.get('completed', 0) / 1e9:5.2f}/{ev['total'] / 1e9:5.2f} GB ", end="", flush=True)
            elif st != last:
                print(f"\r  {st:<60}", end="", flush=True)
            last = st
    print(c("\n  ✔ hazır", "32"))
    return True


def installed_models():
    try:
        return {m["name"]: int(m.get("size") or 0) for m in http_json("/api/tags").get("models", [])}
    except Exception:
        return {}


def retire_old():
    """ATLAS'ın artık kullanmadığı eski varsayılan modelleri sil (yenisi kuruluysa ve hiçbir role atanmamışsa)."""
    from atlas.config import retire_plan
    if not CFG["performance"].get("retire_old_models", True):
        return
    freed = 0
    for name, size in retire_plan(installed_models(), CFG["models"]):
        try:
            req = urllib.request.Request(OLLAMA + "/api/delete", method="DELETE",
                                         data=json.dumps({"model": name}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=60).read()
            freed += size
            print(c(f"🧹 Eski model silindi: {name} ({size / 1e9:.1f} GB)", "36"))
        except Exception as e:
            print(c(f"⚠ {name} silinemedi: {e}", "33"))
    if freed:
        print(c(f"   Toplam {freed / 1e9:.1f} GB boşaldı.", "36"))


def setup():
    if not ensure_ollama():
        sys.exit(1)
    try:  # Qwen3.6/Qwen3.8 mimarileri eski Ollama sürümlerinde yüklenmez
        import re
        v = http_json("/api/version").get("version", "0")
        nums = tuple(int(x) for x in (re.findall(r"\d+", v.split("-")[0]) + ["0", "0", "0"])[:3])
        if nums < (0, 30, 0):
            print(c(f"⚠ Ollama v{v} eski. Qwen3.6/Qwen3.8 modelleri için güncel Ollama gerekir: https://ollama.com/download", "33"))
        else:
            print(c(f"✔ Ollama v{v}", "32"))
    except Exception:
        pass
    installed = installed_models()
    ok, seen = True, set()
    for role in ("main", "coder", "vision", "reviewer", "embed"):
        name = CFG["models"][role]["name"]
        if name in seen:   # görsel = ana model → ikinci kez indirme
            continue
        seen.add(name)
        if name in installed or name + ":latest" in installed:
            print(c(f"✔ {role:<6} {name} (zaten kurulu)", "32"))
            continue
        ok = pull(name) and ok
    retire_old()
    print(c("\nKurulum tamamlandı." if ok else "\nBazı modeller inemedi; arayüzdeki Kurulum panelinden tekrar deneyin.",
            "32" if ok else "33"))


def run():
    """Masaüstü uygulamasını başlat (web arayüzü / tarayıcı modu yoktur)."""
    import runpy
    sys.argv = [str(BASE / "desktop.py")] + [a for a in sys.argv[1:] if a.startswith("--")]
    runpy.run_path(str(BASE / "desktop.py"), run_name="__main__")


if __name__ == "__main__":
    if IS_WIN and sys.stdout is not None and sys.stdout.isatty():
        os.system("")  # yalnızca konsolda: ANSI renkleri (pencereli modda cmd açılmasın)
    if "--setup" in sys.argv:
        setup()
    else:
        run()

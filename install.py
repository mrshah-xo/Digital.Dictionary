"""
install.py  —  One-Click Windows Installer
==========================================
Run as administrator for best results (needed for Start Menu shortcut).
Otherwise runs fine as normal user (installs to HKCU registry).

Usage:
    python install.py           → full install
    python install.py --remove  → uninstall everything
"""

import sys, os, subprocess, shutil, winreg, urllib.request, time

HERE   = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "word_widget.py")

APP_NAME    = "Word of the Day"
REG_KEY     = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_VALUE   = "WordOfTheDay"
STARTUP_DIR = os.path.join(
    os.environ.get("APPDATA",""),
    r"Microsoft\Windows\Start Menu\Programs\Startup"
)


# ── Colours for terminal output ───────────────────────────────
def ok(msg):    print(f"  \033[92m✓\033[0m  {msg}")
def err(msg):   print(f"  \033[91m✗\033[0m  {msg}")
def info(msg):  print(f"  \033[94m→\033[0m  {msg}")
def head(msg):  print(f"\n\033[1m{msg}\033[0m")


# ════════════════════════════════════════════════════════════════
#  STEP 1 — Install Python packages
# ════════════════════════════════════════════════════════════════
def install_packages():
    head("Installing Python packages…")
    packages = ["PyQt5", "pyttsx3", "Pillow"]
    for pkg in packages:
        try:
            info(f"pip install {pkg}")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                ok(pkg)
            else:
                err(f"{pkg}: {result.stderr.strip()[:80]}")
        except Exception as e:
            err(f"{pkg}: {e}")


# ════════════════════════════════════════════════════════════════
#  STEP 2 — Download Inter font (optional, best look)
# ════════════════════════════════════════════════════════════════
FONT_URL  = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
FONT_FILE = os.path.join(HERE, "Inter-Regular.ttf")

def download_font():
    head("Downloading Inter font (optional)…")
    if os.path.exists(FONT_FILE):
        ok("Inter font already present — skipping")
        return

    # Try direct TTF from Google Fonts CDN (more reliable)
    urls = [
        "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff2",
        # Fallback: grab from GitHub releases flat file
        "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    ]
    for url in urls:
        try:
            info(f"Fetching from {url[:60]}…")
            dest = os.path.join(HERE, "Inter-Regular.ttf")
            urllib.request.urlretrieve(url, dest)
            if os.path.getsize(dest) > 10_000:
                ok("Inter-Regular.ttf downloaded")
                return
            else:
                os.remove(dest)
        except Exception as ex:
            info(f"  → failed ({ex}), trying next source…")
    err("Could not download Inter — widget will use Segoe UI (still looks great)")


# ════════════════════════════════════════════════════════════════
#  STEP 3 — Generate PNG assets
# ════════════════════════════════════════════════════════════════
def generate_assets():
    head("Generating visual assets…")
    gen = os.path.join(HERE, "generate_assets.py")
    if not os.path.exists(gen):
        err("generate_assets.py not found — skipping")
        return
    try:
        result = subprocess.run(
            [sys.executable, gen],
            capture_output=True, text=True, cwd=HERE
        )
        if result.returncode == 0:
            ok("All PNG assets generated")
        else:
            err(f"Asset generation: {result.stderr.strip()[:120]}")
    except Exception as e:
        err(f"Asset generation: {e}")


# ════════════════════════════════════════════════════════════════
#  STEP 4 — Windows Registry auto-start
# ════════════════════════════════════════════════════════════════
def install_registry_autostart():
    head("Installing Windows auto-start (Registry)…")
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable   # fallback, shows console briefly

    cmd = f'"{pythonw}" "{SCRIPT}"'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY,
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_VALUE, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        ok(f"Registry: HKCU\\{REG_KEY}\\{REG_VALUE}")
        ok(f"Command:  {cmd}")
    except Exception as e:
        err(f"Registry write failed: {e}")


# ════════════════════════════════════════════════════════════════
#  STEP 5 — Startup folder shortcut (.bat fallback)
# ════════════════════════════════════════════════════════════════
def install_startup_bat():
    """
    Creates a .bat launcher in the Windows Startup folder.
    This is a belt-and-suspenders backup alongside the registry key.
    """
    head("Installing Startup folder launcher…")
    bat_path = os.path.join(STARTUP_DIR, "WordOfTheDay.bat")
    pythonw  = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    bat_content = f'@echo off\nstart "" "{pythonw}" "{SCRIPT}"\n'
    try:
        os.makedirs(STARTUP_DIR, exist_ok=True)
        with open(bat_path, "w") as f:
            f.write(bat_content)
        ok(f"Created: {bat_path}")
    except Exception as e:
        err(f"Startup folder: {e}")


# ════════════════════════════════════════════════════════════════
#  STEP 6 — Try to create a proper .lnk shortcut via PowerShell
# ════════════════════════════════════════════════════════════════
def install_shortcut():
    head("Creating desktop shortcut…")
    desktop = os.path.join(os.environ.get("USERPROFILE",""), "Desktop")
    lnk     = os.path.join(desktop, "Word of the Day.lnk")
    pythonw = sys.executable.replace("python.exe","pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    ps = f"""
$ws  = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut('{lnk}')
$lnk.TargetPath      = '{pythonw}'
$lnk.Arguments       = '"{SCRIPT}"'
$lnk.WorkingDirectory= '{HERE}'
$lnk.Description     = 'Word of the Day Widget'
$lnk.Save()
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True
        )
        if result.returncode == 0 and os.path.exists(lnk):
            ok(f"Desktop shortcut: {lnk}")
        else:
            err(f"Shortcut creation: {result.stderr.strip()[:100]}")
    except Exception as e:
        err(f"Shortcut: {e}")


# ════════════════════════════════════════════════════════════════
#  STEP 7 — Launch widget now
# ════════════════════════════════════════════════════════════════
def launch_now():
    head("Launching widget…")
    pythonw = sys.executable.replace("python.exe","pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    try:
        subprocess.Popen([pythonw, SCRIPT],
                         creationflags=0x00000008)  # DETACHED_PROCESS
        ok("Widget launched in background")
    except Exception as e:
        err(f"Launch failed: {e}")


# ════════════════════════════════════════════════════════════════
#  UNINSTALL
# ════════════════════════════════════════════════════════════════
def uninstall():
    head("Uninstalling Word of the Day Widget…")

    # Registry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY,
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, REG_VALUE)
        winreg.CloseKey(key)
        ok("Registry entry removed")
    except FileNotFoundError:
        info("Registry entry not found (already clean)")
    except Exception as e:
        err(f"Registry: {e}")

    # Startup .bat
    bat = os.path.join(STARTUP_DIR, "WordOfTheDay.bat")
    if os.path.exists(bat):
        os.remove(bat)
        ok(f"Removed: {bat}")
    else:
        info("Startup .bat not found")

    # Desktop shortcut
    lnk = os.path.join(os.environ.get("USERPROFILE",""),
                       "Desktop", "Word of the Day.lnk")
    if os.path.exists(lnk):
        os.remove(lnk)
        ok(f"Removed: {lnk}")

    # Kill any running instance
    try:
        subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/FI",
                        f"WINDOWTITLE eq Word*"],
                       capture_output=True)
    except Exception:
        pass

    ok("Uninstall complete.")


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 56)
    print("   Word of the Day Widget — Windows Installer")
    print("=" * 56)

    if "--remove" in sys.argv or "--uninstall" in sys.argv:
        uninstall()
        sys.exit(0)

    install_packages()
    download_font()
    generate_assets()
    install_registry_autostart()
    install_startup_bat()
    install_shortcut()
    launch_now()

    print("\n" + "=" * 56)
    print("  ✅  Installation complete!")
    print("      Widget will auto-start every time you log in.")
    print("      Look for the glowing strip at the top-right")
    print("      of your screen — hover it to reveal the note.")
    print()
    print("  To uninstall:  python install.py --remove")
    print("=" * 56 + "\n")

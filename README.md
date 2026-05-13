# 🔤 Word of the Day — Premium Desktop Widget

> A sleek, Apple-inspired desktop widget for Windows that silently teaches you one new word every day — with natural neural voice pronunciation, glassmorphism UI, and zero friction.

![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?style=flat-square&logo=windows)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## 📸 Preview

<div align="center">
  <br/>

  https://github.com/user-attachments/assets/6e875e9e-104b-40a8-8bcd-5598b05f21d5

  <br/>
</div>
Hover the glowing strip → card slides in → click 🔊 to hear pronunciation
---

## ✨ What It Does

This widget runs silently in your system tray and shows a new English word every day — automatically. It lives at the edge of your screen, invisible until you need it. No clicks to open an app, no browser tab, no distraction.

- **One new word per day** — rotates through a curated vocabulary list daily
- **Natural voice pronunciation** — Microsoft Azure Neural TTS (Aria, Jenny, Guy and more)
- **Glassmorphism UI** — Apple-style frosted dark panel with accent gradient
- **Slide-in on hover** — peeks from the right edge, auto-hides after 8 seconds
- **Drag to reposition** — move the card anywhere on screen
- **Auto-starts on login** — registered in Windows startup, no manual launch needed
- **System tray control** — show, hide, or quit from the taskbar tray icon
- **Offline fallback** — uses Windows SAPI voice if no internet is available

---

## 🚀 Quick Start

### 1. Clone or download

```bash
git clone https://github.com/yourusername/word-of-the-day-widget.git
cd word-of-the-day-widget
```

### 2. Install dependencies

```bash
pip install PyQt5 pyttsx3 Pillow edge-tts
```

### 3. Generate visual assets (run once)

```bash
python generate_assets.py
```

### 4. Launch

```bash
python word_widget.py
```

Look for the **thin glowing strip** at the top-right of your screen. Hover it to reveal the card.

---

## 🔧 One-Click Windows Installer

For a full setup including auto-start, desktop shortcut, and font download:

```bash
python install.py
```

To uninstall everything cleanly:

```bash
python install.py --remove
```

The installer handles:

- Installing all Python packages
- Downloading the Inter font
- Generating PNG assets
- Writing the Windows Registry auto-start key
- Creating a `.bat` launcher in the Startup folder
- Creating a desktop shortcut via PowerShell

---

## 📁 Project Structure

```
word-of-the-day-widget/
│
├── word_widget.py          ← Main application (run this)
├── generate_assets.py      ← PNG asset generator (run once)
├── install.py              ← Windows one-click installer
├── word_icon.ico           ← App icon (all sizes: 16–256px)
├── Inter-Regular.ttf       ← Optional: downloaded by installer
│
└── assets/
    ├── glass_panel.png     Dark frosted glass card background
    ├── btn_speak.png       Speaker icon button (normal)
    ├── btn_speak_hover.png Speaker icon button (hover state)
    ├── btn_close.png       Close × button
    ├── separator.png       Luminous hairline divider
    └── edge_strip.png      Glowing pill visible at screen edge
```

---

## ⚙️ Configuration

All settings live at the top of `word_widget.py`. Open in VS Code and press `Ctrl+G` to jump to a line number.

### Change the voice (Line 111)

```python
EDGE_VOICE = "en-US-AriaNeural"        # warm American female (default)
EDGE_VOICE = "en-US-GuyNeural"         # warm American male
EDGE_VOICE = "en-GB-SoniaNeural"       # British female
EDGE_VOICE = "en-GB-RyanNeural"        # British male
EDGE_VOICE = "en-AU-NatashaNeural"     # Australian female
EDGE_VOICE = "en-US-ChristopherNeural" # deep, authoritative male
```

### Adjust speaking style, speed, and pitch (Lines 112–114)

```python
EDGE_STYLE = "chat"    # "chat" | "narration-professional" | ""
EDGE_RATE  = "-5%"     # speed: "-10%" slower, "+10%" faster
EDGE_PITCH = "+0Hz"    # pitch: "+2Hz" higher, "-2Hz" lower
```

### Change auto-hide delay (Line 528)

```python
self._hide_timer.start(8000)   # 8000ms = 8 seconds
```

### Add your own words

Edit the `WORDS` list in `word_widget.py`:

```python
{
    "word":          "Ephemeral",
    "type":          "adj.",
    "pronunciation": "ih · FEM · er · ul",
    "meaning":       "Lasting for a very short time; fleeting by nature.",
},
```

---

## 🖼 Custom Assets

Replace any PNG in `assets/` with your own design. All files must be **RGBA PNG** with a transparent background.

| File | Size | Notes |
|---|---|---|
| `glass_panel.png` | 420 × 240 px | Main card background — text is painted on top |
| `btn_speak.png` | 44 × 44 px | Speaker icon, normal state |
| `btn_speak_hover.png` | 44 × 44 px | Speaker icon, highlighted |
| `btn_close.png` | 28 × 28 px | Close button |
| `separator.png` | 360 × 2 px | Hairline divider |
| `edge_strip.png` | 6 × 180 px | Pill visible at screen edge |

Recommended design tools: **Figma**, **Photoshop**, **GIMP**, or **Photopea** (free, browser-based).

---

## 🔈 Voice Engine

The widget uses a two-tier TTS system with automatic fallback:

| Priority | Engine | Quality | Requires |
|---|---|---|---|
| 1st | `edge-tts` (Microsoft Neural) | Natural, human-like | Internet |
| 2nd | `pyttsx3` (Windows SAPI) | Robotic but reliable | Offline |

Install the neural engine:

```bash
pip install edge-tts
```

If there is no internet connection, the widget silently uses the offline voice. No errors shown to the user.

---

## 🖥 Auto-Start on Windows Login

The installer registers this registry key:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
Value : WordOfTheDay
Data  : "C:\...\pythonw.exe" "C:\...\word_widget.py"
```

Uses `pythonw.exe` so **no console window ever appears on startup**.

To verify: open **Task Manager → Startup apps** and look for `WordOfTheDay`.

---

## 🛠 Troubleshooting

| Problem | Solution |
|---|---|
| Widget does not appear | Right-click tray icon → Show Widget |
| No sound on click | Run `pip install edge-tts` and check internet connection |
| Font looks plain | Run `python install.py` to download Inter font |
| Console window flashes on startup | Ensure you are using `pythonw.exe` not `python.exe` |
| Auto-start not working | Run `install.py` as Administrator |
| Assets missing error | Run `python generate_assets.py` |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `PyQt5` | ≥ 5.15 | GUI framework, rendering, animation |
| `edge-tts` | ≥ 6.1 | Microsoft Azure Neural TTS |
| `pyttsx3` | ≥ 2.9 | Offline TTS fallback |
| `Pillow` | ≥ 10.0 | Asset generation (one-time only) |

Install all at once:

```bash
pip install PyQt5 edge-tts pyttsx3 Pillow
```

---

## 🤝 Contributing

Contributions are welcome.

1. **Fork** the repository
2. **Create** a feature branch — `git checkout -b feature/your-feature-name`
3. **Commit** your changes — `git commit -m "Add: your feature description"`
4. **Push** to your branch — `git push origin feature/your-feature-name`
5. **Open** a Pull Request with a clear description of what changed and why

### Ideas for contributions

- New words or vocabulary themes
- Support for additional languages and voices
- macOS or Linux port
- REST API integration for live word-of-the-day data
- Dark/light mode toggle based on system theme
- Keyboard shortcut to trigger the widget

### Reporting Issues

Open a GitHub Issue and include your Windows version, Python version (`python --version`), the exact error message or a screenshot, and steps to reproduce.

### Code of Conduct

Be respectful and constructive. Harassment, dismissiveness, or offensive language will not be tolerated.

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, distribute, and build upon it, as long as the original copyright notice is included.

See the [LICENSE](LICENSE) file for full terms.

---

## 📬 Contact

- **GitHub Issues** — bugs and feature requests
- **GitHub Discussions** — questions and ideas
- **Email** — ayushshah8082@email.com

---

## 🗒 Notes

- The widget selects today's word **deterministically by day of year** — no internet or database needed for word rotation.
- All visual assets are **generated by Python (Pillow)** — no external image downloads required beyond the optional font.
- The `.ico` file contains **7 embedded sizes** (16, 24, 32, 48, 64, 128, 256 px) for crisp rendering at every scale — taskbar, desktop, Alt+Tab, and high-DPI displays.
- `pyttsx3` remains a dependency even with `edge-tts` installed — it is the silent offline fallback and needs no configuration.

---

<div align="center">
  <sub>Built with PyQt5 · Powered by Microsoft Neural TTS · Designed for Windows</sub>
</div>

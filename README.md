# ◆ Word of the Day — Premium Widget
### Apple-style glassmorphism · Windows auto-start · Zero friction

---

## ⚡ One-Command Install

```bat
python install.py
```

That's it. The installer handles everything:
- Installs PyQt5, pyttsx3, Pillow
- Downloads Inter font
- Generates all visual assets
- Registers Windows auto-start
- Creates desktop shortcut
- Launches the widget immediately

**To uninstall:**
```bat
python install.py --remove
```

---

## Manual Setup (if you prefer)

```bat
pip install PyQt5 pyttsx3 Pillow
python generate_assets.py
python word_widget.py
```

---

## How to Use

```
┌─────────────────────────────────────────────┐
│                              [thin glowing  │
│    Your desktop                strip at     │
│                                right edge]  │
└─────────────────────────────────────────────┘
```

| Action | Result |
|---|---|
| **Hover the edge strip** | Card slides in smoothly |
| **Leave for 8 seconds** | Card auto-hides |
| **Drag the card top bar** | Reposition anywhere on screen |
| **Click 🔊** | Hear the word + meaning (TTS) |
| **Right-click tray icon** | Show / Hide / Quit |
| **Double-click tray icon** | Toggle visibility |

---

## File Structure

```
premium_widget/
│
├── word_widget.py          ← Main app  (run this)
├── generate_assets.py      ← PNG asset generator (run once)
├── install.py              ← Windows one-click installer
├── Inter-Regular.ttf       ← Auto-downloaded by installer
│
└── assets/
    ├── glass_panel.png     Dark frosted glass background
    ├── btn_speak.png       Speaker icon button
    ├── btn_speak_hover.png Speaker button (hover state)
    ├── btn_close.png       Close × button
    ├── separator.png       Luminous hairline separator
    └── edge_strip.png      Glowing edge pill (always visible)
```

---

## Auto-Start Details

The installer writes to two locations (belt + suspenders):

**1. Windows Registry (primary)**
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
Value: WordOfTheDay
Data:  "C:\...\pythonw.exe" "C:\...\word_widget.py"
```
Uses `pythonw.exe` — **no console window ever appears**.

**2. Startup Folder (backup)**
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WordOfTheDay.bat
```

To verify it's installed, open Task Manager → Startup apps tab.

---

## Design System

| Element | Spec |
|---|---|
| Background | `rgba(18, 18, 24, 210)` — deep dark glass |
| Panel size | 420 × 240 px |
| Border radius | 28 px |
| Accent bar | Left edge, 4px, cyan→purple gradient |
| Top border | 1px `rgba(255,255,255,80)` luminous rim |
| Word font | Inter SemiBold 34pt / Segoe UI fallback |
| Meaning font | Inter Regular 12pt |
| Pronunciation | Inter Light Italic 11pt, letter-spacing 1.8 |
| Separator | Fade-in / fade-out luminous white line |
| Shadow | Blur 48px, offset 0/8, `rgba(0,0,0,130)` |
| Slide animation | 380ms OutCubic easing |

---

## Customisation

### Change word list
Edit the `WORDS` list in `word_widget.py`. Each entry:
```python
{
    "word":          "Ephemeral",
    "type":          "adj.",           # shows as badge pill
    "pronunciation": "ih · FEM · er · ul",
    "meaning":       "Lasting for a very short time.",
}
```

### Change accent colour
In `GlassPanel.paintEvent`, find `accent_grad`:
```python
accent_grad.setColorAt(0.0, QColor(100, 180, 255, 200))  # cyan
accent_grad.setColorAt(0.5, QColor(140, 120, 255, 220))  # purple
accent_grad.setColorAt(1.0, QColor(80,  200, 180, 180))  # teal
```

### Change auto-hide delay
In `WordWidget.__init__`:
```python
self._hide_timer.start(8000)   # 8000ms = 8 seconds
```

### Change widget position (vertical)
```python
TOP_OFF = 60    # pixels from screen top
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Widget doesn't appear | Check tray icon → right-click → Show Widget |
| No sound on click | `pip install pyttsx3` ; check Windows TTS voices in Settings |
| Font looks wrong | Run `python install.py` again to re-download Inter |
| Won't auto-start | Run `install.py` as administrator |
| Console window flashes | Make sure `pythonw.exe` exists (standard Python install) |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `PyQt5` | ≥ 5.15 | UI, animation, rendering |
| `pyttsx3` | ≥ 2.9 | Text-to-speech |
| `Pillow` | ≥ 10.0 | Asset generation (once) |

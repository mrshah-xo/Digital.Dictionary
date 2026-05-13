"""
╔═══════════════════════════════════════════════════════════════════╗
║   WORD OF THE DAY  —  Premium Widget  (Apple Design Language)     ║
║                                                                   ║
║   • Glassmorphism dark panel, SF-Pro style typography             ║
║   • Frameless · Transparent · Always on top                       ║
║   • Slides in from right edge — drag or click the edge strip      ║
║   • Click 🔊 to hear pronunciation via TTS                        ║
║   • Auto-starts with Windows (installer included)                 ║
║                                                                   ║
║   Setup:  pip install PyQt5 pyttsx3 Pillow                        ║
║           python generate_assets.py   (run once)                  ║
║   Run:    python word_widget.py                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import sys, os, datetime, math
from PyQt5.QtWidgets  import (QApplication, QWidget, QLabel,
                               QGraphicsDropShadowEffect,
                               QGraphicsOpacityEffect, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore     import (Qt, QPoint, QPointF, QPropertyAnimation,
                               QEasingCurve, QTimer, QThread, pyqtSignal,
                               QRect, QSequentialAnimationGroup,
                               QParallelAnimationGroup, pyqtProperty)
from PyQt5.QtGui      import (QPainter, QColor, QFont, QFontDatabase,
                               QPixmap, QLinearGradient, QBrush, QPen,
                               QIcon, QCursor)

# ─── paths ──────────────────────────────────────────────────────────
HERE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
def A(n): return os.path.join(ASSETS, n)

# ════════════════════════════════════════════════════════════════════
#  WORD DATA
# ════════════════════════════════════════════════════════════════════
WORDS = [
    {"word":"Tenacious",    "type":"adj.", "pronunciation":"tuh · NAY · shus",
     "meaning":"Persistent and determined; refusing to give up despite difficulties."},

    {"word":"Visionary",    "type":"adj.", "pronunciation":"VIZH · uh · ner · ee",
     "meaning":"Thinking creatively about the future with imagination and ambition."},

    {"word":"Resilient",    "type":"adj.", "pronunciation":"rih · ZIL · yunt",
     "meaning":"Able to recover quickly from setbacks and adapt to challenges."},

    {"word":"Meticulous",   "type":"adj.", "pronunciation":"muh · TIK · yoo · lus",
     "meaning":"Showing great attention to detail; careful and precise in work."},

    {"word":"Ascend",       "type":"v.",   "pronunciation":"uh · SEND",
     "meaning":"To rise upward toward a higher level of growth, skill, or success."},

    {"word":"Aesthetic",    "type":"adj.", "pronunciation":"es · THET · ik",
     "meaning":"Concerned with beauty, artistic expression, and visual harmony."},

    {"word":"Momentum",     "type":"n.",   "pronunciation":"moh · MEN · tum",
     "meaning":"The force and progress gained by continuous effort and consistency."},

    {"word":"Lucid",        "type":"adj.", "pronunciation":"LOO · sid",
     "meaning":"Clear, easy to understand, and mentally sharp."},

    {"word":"Catalyst",     "type":"n.",   "pronunciation":"KAT · uh · list",
     "meaning":"A person or thing that sparks significant change or action."},

    {"word":"Discipline",   "type":"n.",   "pronunciation":"DIS · uh · plin",
     "meaning":"The practice of training yourself to stay focused and consistent."},

    {"word":"Innovative",   "type":"adj.", "pronunciation":"IN · uh · vay · tiv",
     "meaning":"Introducing original ideas, methods, or creative solutions."},

    {"word":"Introspection","type":"n.",   "pronunciation":"in · truh · SPEK · shun",
     "meaning":"The act of examining your own thoughts, emotions, and motives."},

    {"word":"Nocturnal",    "type":"adj.", "pronunciation":"nok · TER · nul",
     "meaning":"Most active, creative, or inspired during the night."},

    {"word":"Zenith",       "type":"n.",   "pronunciation":"ZEE · nith",
     "meaning":"The highest point of achievement, energy, or development."},

    {"word":"Obsidian",     "type":"n.",   "pronunciation":"ob · SID · ee · un",
     "meaning":"A dark volcanic glass symbolizing mystery, depth, and strength."},

    {"word":"Synesthesia",  "type":"n.",   "pronunciation":"sin · es · THEE · zhuh",
     "meaning":"A rare blending of senses, often linked with artistic creativity."},

    {"word":"Evolve",       "type":"v.",   "pronunciation":"ee · VOLV",
     "meaning":"To gradually develop into a stronger, more advanced version of yourself."},

    {"word":"Cipher",       "type":"n.",   "pronunciation":"SY · fur",
     "meaning":"A coded message or mysterious identity difficult to fully understand."},

    {"word":"Ambivert",     "type":"n.",   "pronunciation":"AM · bih · vurt",
     "meaning":"Someone who balances qualities of both introversion and extroversion."},

    {"word":"Transcendent", "type":"adj.", "pronunciation":"tran · SEN · dunt",
     "meaning":"Going beyond ordinary limits; spiritually or mentally elevated."},
]

def get_daily_word() -> dict:
    return WORDS[datetime.date.today().timetuple().tm_yday % len(WORDS)]


# ════════════════════════════════════════════════════════════════════
#  FONTS
# ════════════════════════════════════════════════════════════════════
def setup_fonts():
    db = QFontDatabase()
    for f in ["Inter-Regular.ttf","Inter-Bold.ttf","Inter-Light.ttf",
              "SFPro-Regular.ttf","SFPro-Bold.ttf"]:
        p = os.path.join(HERE, f)
        if os.path.exists(p): db.addApplicationFont(p)

    avail = [x.lower() for x in db.families()]
    body  = next((f for f in ["inter","sf pro display","segoe ui",
                               ".apple system ui","helvetica neue","arial"]
                   if any(f in a for a in avail)), "Segoe UI")
    return body

BODY_FONT = None   # set in main()

def font(size, weight=QFont.Normal, family=None):
    f = QFont(family or BODY_FONT or "Segoe UI", size)
    f.setWeight(weight)
    f.setLetterSpacing(QFont.AbsoluteSpacing, 0.3)
    return f


# ════════════════════════════════════════════════════════════════════
#  TTS WORKER  —  Natural Neural Voice
#
#  CHANGE VOICE: edit EDGE_VOICE below
#
#  Female voices:
#    "en-US-AriaNeural"        <- default (warm, expressive)
#    "en-US-JennyNeural"       <- calm, professional
#    "en-GB-SoniaNeural"       <- British female
#    "en-AU-NatashaNeural"     <- Australian female
#
#  Male voices:
#    "en-US-GuyNeural"         <- warm American male
#    "en-US-ChristopherNeural" <- deep, authoritative
#    "en-GB-RyanNeural"        <- British male
#    "en-AU-WilliamNeural"     <- Australian male
# ════════════════════════════════════════════════════════════════════
EDGE_VOICE = "en-US-AriaNeural"   # <- CHANGE THIS LINE to switch voice
EDGE_STYLE = "chat"               # "chat" / "narration-professional" / ""
EDGE_RATE  = "-5%"                # speed: "-10%" slower  "+10%" faster
EDGE_PITCH = "+0Hz"               # pitch: "+2Hz" higher  "-2Hz" lower
 
 
class TTSWorker(QThread):
    finished = pyqtSignal()
 
    def __init__(self, text):
        super().__init__()
        self.text = text
 
    def run(self):
        try:
            self._speak_edge()
        except Exception as ex:
            print(f"[TTS] edge-tts failed ({ex}), falling back to pyttsx3...")
            self._speak_pyttsx3()
        finally:
            self.finished.emit()
 
    def _speak_edge(self):
        import asyncio, tempfile, os
        try:
            import edge_tts
        except ImportError:
            raise ImportError("Run: pip install edge-tts")
 
        styled = {"en-US-AriaNeural","en-US-JennyNeural","en-US-GuyNeural","en-US-DavisNeural"}
        use_style = EDGE_STYLE and EDGE_VOICE in styled
 
        if use_style:
            ssml = (
                f'<speak version="1.0" '
                f'xmlns="http://www.w3.org/2001/10/synthesis" '
                f'xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">'
                f'<voice name="{EDGE_VOICE}">'
                f'<mstts:express-as style="{EDGE_STYLE}">'
                f'<prosody rate="{EDGE_RATE}" pitch="{EDGE_PITCH}">{self.text}</prosody>'
                f'</mstts:express-as></voice></speak>'
            )
            comm = edge_tts.Communicate(text=ssml, voice=EDGE_VOICE, ssml=True)
        else:
            comm = edge_tts.Communicate(text=self.text, voice=EDGE_VOICE,
                                         rate=EDGE_RATE, pitch=EDGE_PITCH)
 
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, prefix="wotd_")
        tmp_path = tmp.name
        tmp.close()
 
        async def _save():
            await comm.save(tmp_path)
        asyncio.run(_save())
 
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            self._play(tmp_path)
        else:
            raise RuntimeError("empty audio file")
 
        try: os.remove(tmp_path)
        except: pass
 
    def _play(self, path):
        import subprocess
        if sys.platform == "win32":
            ps = (
                f"Add-Type -AssemblyName PresentationCore; "
                f"$mp = New-Object System.Windows.Media.MediaPlayer; "
                f"$mp.Open([Uri]::new('{path}')); $mp.Play(); "
                f"Start-Sleep -Milliseconds 200; "
                f"$d = $mp.NaturalDuration.TimeSpan.TotalSeconds; "
                f"if ($d -gt 0) {{ Start-Sleep -Seconds ([math]::Ceiling($d)) }}; "
                f"$mp.Stop(); $mp.Close()"
            )
            r = subprocess.run(["powershell","-NoProfile","-WindowStyle","Hidden","-Command",ps],
                               capture_output=True, timeout=30)
            if r.returncode != 0:
                self._play_fallback(path)
        else:
            self._play_fallback(path)
 
    def _play_fallback(self, path):
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            import time
            while pygame.mixer.music.get_busy(): time.sleep(0.05)
            pygame.mixer.quit()
        except ImportError:
            import os, time
            os.startfile(path)
            time.sleep(3)
 
    def _speak_pyttsx3(self):
        try:
            import pyttsx3
            e = pyttsx3.init()
            voices = e.getProperty("voices")
            for pref in ["zira","david","hazel"]:
                m = next((v for v in voices if pref in v.name.lower()), None)
                if m: e.setProperty("voice", m.id); break
            e.setProperty("rate", 145)
            e.setProperty("volume", 0.95)
            e.say(self.text)
            e.runAndWait()
            e.stop()
        except Exception as ex:
            print(f"[TTS fallback] {ex}")

# ════════════════════════════════════════════════════════════════════
#  GLASS PANEL  —  the main rendered card
# ════════════════════════════════════════════════════════════════════
class GlassPanel(QWidget):
    """
    Fully custom-painted Apple-style dark glass card.
    All text is painted directly in paintEvent — no child QLabels.
    """
    SPEAK_RECT = QRect(0, 0, 44, 44)   # updated in paintEvent

    def __init__(self, word_data: dict, parent=None):
        super().__init__(parent)
        self.word = word_data
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self._speaking = False
        self._speak_hover = False
        self._close_hover = False
        self._bg_px   = self._load_px("glass_panel.png")
        self._sep_px  = self._load_px("separator.png")
        self._spk_px  = self._load_px("btn_speak.png")
        self._spk_hpx = self._load_px("btn_speak_hover.png")
        self._cls_px  = self._load_px("btn_close.png")
        self.setMouseTracking(True)
        self._tts: TTSWorker | None = None

    def _load_px(self, name):
        px = QPixmap(A(name))
        return px if not px.isNull() else QPixmap(1, 1)

    # hit rects (computed once layout is known)
    def _speak_rect(self) -> QRect:
        return QRect(self.width() - 58, self.height() - 56, 44, 44)
    def _close_rect(self) -> QRect:
        return QRect(self.width() - 38, 10, 28, 28)

    # ── Paint ───────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        W, H = self.width(), self.height()

        # ── Background glass panel ──
        p.drawPixmap(0, 0, W, H, self._bg_px)

        # ── Accent colour bar (left edge) — Apple's signature coloured stripe ──
        accent_grad = QLinearGradient(0, 0, 0, H)
        accent_grad.setColorAt(0.0,  QColor(30,  80,  180, 230))
        accent_grad.setColorAt(0.5,  QColor(60,  50,  160, 240))
        accent_grad.setColorAt(1.0,  QColor(20, 130,  140, 210))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(accent_grad))
        p.drawRoundedRect(0, 0, 4, H, 2, 2)

        PAD_L = 28
        PAD_R = 20
        y = 22

        # ── Top row: word-type badge + close button ──
        badge_text = self.word["type"].upper()
        p.setFont(font(9, QFont.Medium))
        badge_w = p.fontMetrics().horizontalAdvance(badge_text) + 16
        badge_rect = QRect(PAD_L, y, badge_w, 18)
        # Badge pill
        p.setBrush(QBrush(QColor(30, 90, 180, 40)))
        p.setPen(QPen(QColor(30, 90, 200, 130), 1))
        p.drawRoundedRect(badge_rect, 9, 9)
        p.setPen(QColor(20, 70, 170, 230))          # dark blue badge text
        p.drawText(badge_rect, Qt.AlignCenter, badge_text)

        # Close button
        cr = self._close_rect()
        spx = self._cls_px.scaled(cr.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if self._close_hover:
            p.setOpacity(1.0)
        else:
            p.setOpacity(0.55)
        p.drawPixmap(cr.topLeft(), spx)
        p.setOpacity(1.0)

        y += 30

        # ── Word (large, semibold) ──
        p.setFont(font(34, QFont.DemiBold))
        p.setPen(QColor(15, 20, 40, 245))
        p.drawText(QRect(PAD_L, y, W - PAD_L - PAD_R - 10, 48),
                   Qt.AlignLeft | Qt.AlignVCenter, self.word["word"])
        y += 50

        # ── Pronunciation (lighter, spaced) ──
        p.setFont(font(11, QFont.Light))
        p.setPen(QColor(160, 170, 190, 180))
        p.setFont(QFont(BODY_FONT or "Segoe UI", 11))
        pf = p.font(); pf.setWeight(QFont.Light)
        pf.setLetterSpacing(QFont.AbsoluteSpacing, 1.8)
        pf.setItalic(True)
        p.setFont(pf)
        p.setPen(QColor(55, 80, 130, 200))          # medium blue-slate
        p.drawText(QRect(PAD_L, y, W - PAD_L*2, 20),
                   Qt.AlignLeft | Qt.AlignVCenter,
                   self.word["pronunciation"])
        y += 26

        # ── Separator — dark translucent line ──
        sep_w = W - PAD_L - PAD_R
        p.setPen(QPen(QColor(30, 60, 120, 60), 1))
        p.drawLine(PAD_L, y, PAD_L + sep_w, y)
        y += 10

        # ── Meaning (regular weight, slightly muted) ──
        p.setFont(font(12, QFont.Normal))
        pf2 = p.font(); pf2.setItalic(False)
        pf2.setLetterSpacing(QFont.AbsoluteSpacing, 0.2)
        p.setFont(pf2)
        p.setPen(QColor(30, 35, 55, 220))
        text_rect = QRect(PAD_L, y, W - PAD_L - PAD_R, H - y - 30)
        p.drawText(text_rect, Qt.AlignLeft | Qt.TextWordWrap, self.word["meaning"])

        # ── Speak button ──
        sr = self._speak_rect()
        spk = (self._spk_hpx if (self._speak_hover or self._speaking)
               else self._spk_px)
        spx2 = spk.scaled(sr.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.setOpacity(0.85 if not self._speaking else 1.0)
        p.drawPixmap(sr.topLeft(), spx2)
        p.setOpacity(1.0)

        # ── Bottom label ──
        p.setFont(font(8, QFont.Light))
        p.setPen(QColor(50, 65, 100, 150))
        day_label = datetime.date.today().strftime("%A, %B %d")
        p.drawText(QRect(PAD_L, H - 22, W - PAD_L*2, 18),
                   Qt.AlignLeft | Qt.AlignVCenter, day_label)

        p.end()

    # ── Mouse ────────────────────────────────────────────────
    def mouseMoveEvent(self, e):
        sr = self._speak_rect()
        cr = self._close_rect()
        sh = sr.contains(e.pos())
        ch = cr.contains(e.pos())
        if sh != self._speak_hover or ch != self._close_hover:
            self._speak_hover = sh
            self._close_hover = ch
            self.setCursor(Qt.PointingHandCursor if (sh or ch) else Qt.ArrowCursor)
            self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self._speak_rect().contains(e.pos()):
                self._speak()
                e.accept()
                return
            if self._close_rect().contains(e.pos()):
                QApplication.quit()
                return
        e.ignore()

    def leaveEvent(self, _):
        self._speak_hover = False
        self._close_hover = False
        self.update()

    def _speak(self):
        if self._tts and self._tts.isRunning():
            return
        self._speaking = True
        self.update()
        w = self.word
        self._tts = TTSWorker(f"{w['word']}. {w['meaning']}")
        self._tts.finished.connect(self._on_speak_done)
        self._tts.start()

    def _on_speak_done(self):
        self._speaking = False
        self.update()


# ════════════════════════════════════════════════════════════════════
#  EDGE STRIP  — the thin visible pill when widget is hidden
# ════════════════════════════════════════════════════════════════════
class EdgeStrip(QWidget):
    """
    A thin glowing pill visible at the screen's right edge.
    Hovering it triggers slide-in on the parent.
    """
    hovered = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self._px = QPixmap(A("edge_strip.png"))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(10, 180)
        self._h = False

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setOpacity(1.0 if self._h else 0.65)
        if not self._px.isNull():
            p.drawPixmap(0, 0, self.width(), self.height(), self._px)
        else:
            # Fallback: draw pill manually
            p.setPen(Qt.NoPen)
            g = QLinearGradient(0, 0, self.width(), 0)
            g.setColorAt(0, QColor(255,255,255,0))
            g.setColorAt(1, QColor(255,255,255,80))
            p.setBrush(QBrush(g))
            p.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)
        p.end()

    def enterEvent(self, _):
        self._h = True
        self.update()
        self.hovered.emit(True)

    def leaveEvent(self, _):
        self._h = False
        self.update()


# ════════════════════════════════════════════════════════════════════
#  ANIMATION CONTROLLER
# ════════════════════════════════════════════════════════════════════
class SlideController:
    SLIDE_MS   = 380
    EASE_IN    = QEasingCurve.OutCubic
    EASE_OUT   = QEasingCurve.InCubic

    def __init__(self, widget: QWidget):
        self._w = widget
        self._anim = QPropertyAnimation(widget, b"pos")
        self._anim.setDuration(self.SLIDE_MS)

    def slide_in(self, target: QPoint):
        self._anim.stop()
        self._anim.setEasingCurve(self.EASE_IN)
        self._anim.setStartValue(self._w.pos())
        self._anim.setEndValue(target)
        self._anim.start()

    def slide_out(self, target: QPoint):
        self._anim.stop()
        self._anim.setEasingCurve(self.EASE_OUT)
        self._anim.setStartValue(self._w.pos())
        self._anim.setEndValue(target)
        self._anim.start()

    def stop(self): self._anim.stop()
    def is_running(self): return self._anim.state() == QPropertyAnimation.Running


# ════════════════════════════════════════════════════════════════════
#  SYSTEM TRAY
# ════════════════════════════════════════════════════════════════════
def make_tray_icon(app: QApplication, widget: QWidget) -> QSystemTrayIcon:
    """Creates a minimal system-tray icon for show/hide/quit."""
    # Build a tiny coloured icon programmatically
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    g = QLinearGradient(0, 0, 32, 32)
    g.setColorAt(0, QColor(100, 180, 255))
    g.setColorAt(1, QColor(140, 120, 255))
    p.setBrush(QBrush(g))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(2, 2, 28, 28, 7, 7)
    p.setPen(QPen(QColor(255,255,255,220), 2))
    p.setFont(QFont("Segoe UI", 14, QFont.Bold))
    p.drawText(px.rect(), Qt.AlignCenter, "W")
    p.end()

    tray = QSystemTrayIcon(QIcon(px), app)
    menu = QMenu()

    show_act  = QAction("Show Widget",  menu)
    hide_act  = QAction("Hide Widget",  menu)
    quit_act  = QAction("Quit",         menu)

    show_act.triggered.connect(widget.show_widget)
    hide_act.triggered.connect(widget.hide_widget)
    quit_act.triggered.connect(QApplication.quit)

    menu.addAction(show_act)
    menu.addAction(hide_act)
    menu.addSeparator()
    menu.addAction(quit_act)

    tray.setContextMenu(menu)
    tray.setToolTip("Word of the Day")
    tray.show()
    return tray


# ════════════════════════════════════════════════════════════════════
#  MAIN WIDGET WINDOW
# ════════════════════════════════════════════════════════════════════
class WordWidget(QWidget):
    """
    Top-level frameless transparent window.

    Layout:
      ┌──────────────────────────────┐ ← off right edge (hidden)
      │  [EdgeStrip]                 │
      │  [GlassPanel  420×240 ]      │
      └──────────────────────────────┘

    States:
      HIDDEN   → panel is off-screen, only EdgeStrip visible
      VISIBLE  → panel is fully on screen
    """

    PANEL_W = 420
    PANEL_H = 240
    MARGIN  = 16          # gap from right edge when visible
    STRIP_W = 10          # edge strip width
    TOP_OFF = 60          # distance from screen top

    def __init__(self):
        super().__init__()
        self._visible = False
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._auto_hide)
        self._drag_active = False
        self._drag_offset = QPoint()

        self._setup_window()
        self._build_ui()
        self._setup_shadow()
        self._slide = SlideController(self)
        self._compute_positions()
        self.move(self._pos_hidden)
        self.show()

    # ── Window ────────────────────────────────────────────────
    def _setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_NoSystemBackground)
        # Total window size = panel + strip + padding
        total_w = self.STRIP_W + self.PANEL_W + 20
        total_h = self.PANEL_H + 20
        self.setFixedSize(total_w, total_h)

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        word = get_daily_word()
        total_w = self.width()
        total_h = self.height()

        # Glass panel (right side, slight vertical padding)
        self._panel = GlassPanel(word, self)
        self._panel.setGeometry(self.STRIP_W + 4, 10,
                                 self.PANEL_W, self.PANEL_H)

        # Edge strip (leftmost, vertically centred)
        self._strip = EdgeStrip(self)
        strip_y = (total_h - 180) // 2
        self._strip.setGeometry(0, strip_y, self.STRIP_W, 180)
        self._strip.hovered.connect(self._on_strip_hover)

    # ── Shadow ────────────────────────────────────────────────
    def _setup_shadow(self):
        sh = QGraphicsDropShadowEffect(self)
        sh.setBlurRadius(48)
        sh.setOffset(0, 8)
        sh.setColor(QColor(0, 0, 0, 130))
        self._panel.setGraphicsEffect(sh)

    # ── Positions ─────────────────────────────────────────────
    def _compute_positions(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self._screen = screen

        # HIDDEN: only strip (STRIP_W px) is visible at right edge
        # widget.x = screen.right - STRIP_W
        self._pos_hidden = QPoint(
            screen.right() - self.STRIP_W,
            screen.top()   + self.TOP_OFF
        )

        # VISIBLE: panel fully on screen with MARGIN gap
        self._pos_visible = QPoint(
            screen.right() - self.width() + self.STRIP_W + self.MARGIN,
            screen.top()   + self.TOP_OFF
        )

    # ── Public API (used by tray) ─────────────────────────────
    def show_widget(self):
        self._slide.slide_in(self._pos_visible)
        self._visible = True
        self._start_hide_timer()

    def hide_widget(self):
        self._slide.slide_out(self._pos_hidden)
        self._visible = False

    # ── Auto-hide after 8 seconds ─────────────────────────────
    def _start_hide_timer(self):
        self._hide_timer.stop()
        self._hide_timer.start(8000)

    def _auto_hide(self):
        if not self.underMouse() and not self._drag_active:
            self.hide_widget()

    # ── Strip hover → slide in ────────────────────────────────
    def _on_strip_hover(self, hovered: bool):
        if hovered and not self._visible:
            self.show_widget()

    # ── Mouse: drag to reposition ─────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            # Only drag from the panel's title area (top 40px)
            panel_top = QRect(self._panel.x(), self._panel.y(),
                               self._panel.width(), 40)
            if panel_top.contains(e.pos()):
                self._drag_active = True
                self._drag_offset = e.globalPos() - self.pos()
                self._slide.stop()
                self.setCursor(Qt.ClosedHandCursor)
                e.accept()
                return
        e.ignore()

    def mouseMoveEvent(self, e):
        if self._drag_active:
            self._hide_timer.stop()
            new_pos = e.globalPos() - self._drag_offset
            # Clamp to screen
            s = self._screen
            new_pos.setX(max(s.left(), min(new_pos.x(), s.right() - self.width())))
            new_pos.setY(max(s.top(),  min(new_pos.y(), s.bottom() - self.height())))
            self.move(new_pos)
            e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag_active:
            self._drag_active = False
            self.setCursor(Qt.ArrowCursor)
            # Recompute hidden/visible positions based on current y
            s = self._screen
            cur_y = self.y()
            self._pos_hidden  = QPoint(s.right() - self.STRIP_W, cur_y)
            self._pos_visible = QPoint(
                s.right() - self.width() + self.STRIP_W + self.MARGIN, cur_y)
            self._start_hide_timer()
            e.accept()

    def enterEvent(self, _):
        self._hide_timer.stop()

    def leaveEvent(self, _):
        if self._visible:
            self._start_hide_timer()


# ════════════════════════════════════════════════════════════════════
#  WINDOWS AUTO-START INSTALLER
# ════════════════════════════════════════════════════════════════════
def install_autostart():
    """
    Adds the widget to Windows registry Run key so it starts on login.
    Uses pythonw.exe to suppress the console window.
    """
    import sys, os
    if sys.platform != "win32":
        print("Auto-start only supported on Windows.")
        return

    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name  = "WordOfTheDay"
    # Use pythonw.exe (no console window)
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    script  = os.path.abspath(__file__)
    cmd     = f'"{pythonw}" "{script}"'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print(f"✅ Auto-start installed: {cmd}")
        print(f"   Registry key: HKCU\\{key_path}\\{app_name}")
    except Exception as ex:
        print(f"❌ Auto-start failed: {ex}")


def uninstall_autostart():
    """Removes the widget from Windows auto-start."""
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path,
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "WordOfTheDay")
        winreg.CloseKey(key)
        print("✅ Auto-start removed.")
    except FileNotFoundError:
        print("ℹ  Auto-start entry not found.")
    except Exception as ex:
        print(f"❌ {ex}")


# ════════════════════════════════════════════════════════════════════
#  ASSET CHECK & AUTO-GENERATION
# ════════════════════════════════════════════════════════════════════
def ensure_assets():
    needed = ["glass_panel.png","btn_speak.png","btn_close.png",
              "separator.png","edge_strip.png"]
    missing = [f for f in needed if not os.path.exists(A(f))]
    if not missing:
        return True
    print(f"Missing assets: {missing}")
    print("Auto-generating…")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gen", os.path.join(HERE,"generate_assets.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.make_glass_panel(); mod.make_speaker_btn()
        mod.make_close_btn();   mod.make_separator()
        mod.make_edge_strip()
        return True
    except Exception as ex:
        print(f"Asset generation failed: {ex}")
        print("Run: python generate_assets.py")
        return False


# ════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════
def main():
    global BODY_FONT

    # CLI flags
    if "--install"   in sys.argv: install_autostart();   return
    if "--uninstall" in sys.argv: uninstall_autostart();  return

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)   # keep alive when window hidden

    if not ensure_assets():
        sys.exit(1)

    BODY_FONT = setup_fonts()

    widget = WordWidget()
    tray   = make_tray_icon(app, widget)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

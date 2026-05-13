"""
generate_assets.py  —  Premium Apple-style Widget Assets
Run once: python generate_assets.py
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS, exist_ok=True)

def clamp(v, lo=0, hi=255): return max(lo, min(hi, int(v)))
def lerp(a, b, t): return a + (b - a) * t

# ── 1. FROSTED GLASS PANEL (main widget background) ──────────
def make_glass_panel(W=420, H=240, scale=2):
    SW, SH = W*scale, H*scale
    canvas = Image.new("RGBA", (SW, SH), (0,0,0,0))
    d = ImageDraw.Draw(canvas)

    # Base glass: very dark, slightly blue-tinted
    r_corner = int(28*scale)
    d.rounded_rectangle([0,0,SW-1,SH-1], radius=r_corner,
                         fill=(18,18,24,210))

    # Subtle gradient overlay: lighter at top
    for y in range(SH):
        t = y/SH
        alpha = int(lerp(38, 6, t))
        d.line([(0,y),(SW,y)], fill=(255,255,255,alpha))

    # Inner border glow (Apple-style 1px luminous border)
    for px in range(2):
        alpha = 80 - px*40
        d.rounded_rectangle([px,px,SW-1-px,SH-1-px],
                             radius=r_corner-px,
                             outline=(255,255,255,alpha), width=1)

    # Bottom inner border (darker, depth)
    d.rounded_rectangle([1, SH//2, SW-2, SH-2],
                         radius=r_corner//2,
                         outline=(0,0,0,60), width=1)

    # Noise texture (Apple frosted glass micro-noise)
    rng = random.Random(7)
    noise = Image.new("RGBA", (SW, SH), (0,0,0,0))
    npx = noise.load()
    for _ in range(int(SW*SH*0.018)):
        x = rng.randint(0, SW-1)
        y = rng.randint(0, SH-1)
        v = rng.randint(200, 255)
        a = rng.randint(2, 9)
        npx[x, y] = (v, v, v, a)
    canvas = Image.alpha_composite(canvas, noise)

    # Specular highlight: soft arc at top-centre
    spec = Image.new("RGBA", (SW,SH),(0,0,0,0))
    sd = ImageDraw.Draw(spec)
    sd.ellipse([-SW//4, -SH//2, SW+SW//4, SH//3],
                fill=(255,255,255,0))
    for i in range(int(18*scale)):
        alpha = int(22 * (1 - i/(18*scale))**2)
        sd.arc([-SW//4+i, -SH//2+i, SW+SW//4-i, SH//3-i],
                start=-30, end=210,
                fill=(255,255,255,alpha), width=1)
    canvas = Image.alpha_composite(canvas, spec)

    out = canvas.resize((W,H), Image.LANCZOS)
    out.save(os.path.join(ASSETS,"glass_panel.png"))
    print(f"  ✓ glass_panel.png ({W}×{H})")

# ── 2. SPEAKER BUTTON ────────────────────────────────────────
def make_speaker_btn(W=44, H=44, scale=3):
    SW,SH = W*scale,H*scale
    canvas = Image.new("RGBA",(SW,SH),(0,0,0,0))
    d = ImageDraw.Draw(canvas)
    r = SW//2
    # Circle background
    d.ellipse([0,0,SW-1,SH-1], fill=(255,255,255,22))
    d.ellipse([1,1,SW-2,SH-2], outline=(255,255,255,55), width=scale)
    # Speaker icon (white)
    cx,cy = SW//2, SH//2
    icon_s = int(SW*0.32)
    # Speaker body (trapezoid)
    body = [
        (cx-icon_s, cy-icon_s//2),
        (cx-icon_s//3, cy-icon_s//2),
        (cx+icon_s//2, cy-icon_s),
        (cx+icon_s//2, cy+icon_s),
        (cx-icon_s//3, cy+icon_s//2),
        (cx-icon_s, cy+icon_s//2),
    ]
    d.polygon(body, fill=(255,255,255,210))
    # Sound waves
    for i,ra in enumerate([icon_s*1.1, icon_s*1.6]):
        d.arc([cx+icon_s//3, cy-int(ra), cx+icon_s//3+int(ra*1.5), cy+int(ra)],
               start=-50, end=50,
               fill=(255,255,255,180-i*60), width=max(2,scale))
    out = canvas.resize((W,H),Image.LANCZOS)
    out.save(os.path.join(ASSETS,"btn_speak.png"))
    # Hover version
    ImageEnhance.Brightness(out).enhance(1.3).save(
        os.path.join(ASSETS,"btn_speak_hover.png"))
    print(f"  ✓ btn_speak.png ({W}×{H})")

# ── 3. CLOSE BUTTON ──────────────────────────────────────────
def make_close_btn(W=28, H=28, scale=3):
    SW,SH = W*scale,H*scale
    canvas = Image.new("RGBA",(SW,SH),(0,0,0,0))
    d = ImageDraw.Draw(canvas)
    d.ellipse([0,0,SW-1,SH-1], fill=(255,255,255,18))
    d.ellipse([1,1,SW-2,SH-2], outline=(255,255,255,40), width=scale)
    cx,cy,s = SW//2,SH//2,int(SW*0.22)
    d.line([(cx-s,cy-s),(cx+s,cy+s)], fill=(255,255,255,180), width=max(2,scale))
    d.line([(cx+s,cy-s),(cx-s,cy+s)], fill=(255,255,255,180), width=max(2,scale))
    out = canvas.resize((W,H),Image.LANCZOS)
    out.save(os.path.join(ASSETS,"btn_close.png"))
    print(f"  ✓ btn_close.png ({W}×{H})")

# ── 4. SEPARATOR LINE ─────────────────────────────────────────
def make_separator(W=360, H=2, scale=2):
    SW,SH = W*scale,H*scale
    canvas = Image.new("RGBA",(SW,SH),(0,0,0,0))
    d = ImageDraw.Draw(canvas)
    for x in range(SW):
        t = x/SW
        a = int(80 * math.sin(t*math.pi))
        d.point((x,0), fill=(255,255,255,a))
    out = canvas.resize((W,H),Image.LANCZOS)
    out.save(os.path.join(ASSETS,"separator.png"))
    print(f"  ✓ separator.png ({W}×{H})")

# ── 5. EDGE INDICATOR (the thin visible strip when hidden) ────
def make_edge_strip(W=6, H=180, scale=2):
    SW,SH = W*scale,H*scale
    canvas = Image.new("RGBA",(SW,SH),(0,0,0,0))
    d = ImageDraw.Draw(canvas)
    r = SW//2
    d.rounded_rectangle([0,0,SW-1,SH-1], radius=r,
                         fill=(255,255,255,45))
    # centre glow
    for i in range(r):
        a = int(30*(1-i/r)**2)
        d.rounded_rectangle([i,i*SH//SW,SW-1-i,SH-1-i*SH//SW],
                              radius=r-i, outline=(255,255,255,a), width=1)
    out = canvas.resize((W,H),Image.LANCZOS)
    out.save(os.path.join(ASSETS,"edge_strip.png"))
    print(f"  ✓ edge_strip.png ({W}×{H})")

if __name__ == "__main__":
    print("Generating premium assets…")
    make_glass_panel(W=420, H=240, scale=2)
    make_speaker_btn(W=44,  H=44,  scale=3)
    make_close_btn(  W=28,  H=28,  scale=3)
    make_separator(  W=360, H=2,   scale=2)
    make_edge_strip( W=6,   H=180, scale=2)
    print("\n✅ All assets ready in ./assets/")

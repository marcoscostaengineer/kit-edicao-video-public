#!/usr/bin/env python3
"""Gera os dois B-rolls (1080x960, 30 fps) do vídeo do caso:
  antes-depois.mp4  antes com leve zoom -> cortina revela o depois; etiquetas, nome + CRO e "resultados variam"
  linha-tempo.mp4   linha do tempo vertical com 4 passos que acendem nos tempos da fala
Uso: python3 gen_broll.py <projeto> <seg_cortina> <dur_ad> <dur_lt> <t1> <t2> <t3> <t4>
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

P = Path(sys.argv[1]); cortina = float(sys.argv[2]); dur_ad = float(sys.argv[3]); dur_lt = float(sys.argv[4])
passos_t = [float(x) for x in sys.argv[5:9]]
IMG = Path(__file__).resolve().parents[1] / "antes-depois-motion/assets/img"
W, H, FPS = 1080, 960, 30
AZUL, AZUL_ESC, AMARELO, TINTA = (27, 129, 214), (11, 37, 64), (255, 213, 74), (11, 37, 64)
F = "/System/Library/Fonts/Helvetica.ttc"
def fonte(t, bold=True): return ImageFont.truetype(F, t, index=1 if bold else 0)

def capa(path, cx):
    im = Image.open(path).convert("RGB"); s = 1056 / im.height
    im = im.resize((round(im.width * s), 1056), Image.LANCZOS)
    x = min(max(round(cx * im.width - W / 2), 0), im.width - W)
    return im.crop((x, 48, x + W, 48 + H))

def pill(d, xy, txt, bg, fg, size=40, anchor_right=False):
    f = fonte(size); w = d.textlength(txt, font=f); x, y = xy
    if anchor_right: x -= w + 48
    d.rounded_rectangle((x, y, x + w + 48, y + size + 30), radius=(size + 30) // 2, fill=bg)
    d.text((x + 24, y + 13), txt, font=f, fill=fg)

def rodape(d):
    d.rectangle((0, H - 92, W, H), fill=(0, 0, 0, 150))
    d.text((W // 2, H - 64), "Dra. Brenda Rodrigues · CRO-DF 13071", font=fonte(32), fill="white", anchor="mm")
    d.text((W // 2, H - 26), "Resultados variam de pessoa para pessoa", font=fonte(26, False), fill=(230, 236, 244), anchor="mm")

def frames_dir(): return Path(tempfile.mkdtemp())

def encode(d, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(d / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(out)], check=True)
    shutil.rmtree(d)

# --- antes/depois ---
antes, depois = capa(IMG / "antes.jpg", 0.53), capa(IMG / "depois.jpg", 0.58)
d = frames_dir(); n = round(dur_ad * FPS)
for i in range(n):
    t = i / FPS
    z = 1 + 0.06 * min(t / max(cortina, 0.1), 1)
    a = antes.resize((round(W * z), round(H * z)), Image.LANCZOS)
    a = a.crop(((a.width - W) // 2, (a.height - H) // 2, (a.width - W) // 2 + W, (a.height - H) // 2 + H))
    p = min(max((t - cortina) / 0.6, 0), 1); p = p * p * (3 - 2 * p)   # cortina 0,6 s
    fr = a.copy()
    if p > 0:
        xw = round(W * p); fr.paste(depois.crop((0, 0, xw, H)), (0, 0))
        dr = ImageDraw.Draw(fr); dr.rectangle((xw - 5, 0, xw + 5, H), fill=AMARELO)
    dr = ImageDraw.Draw(fr, "RGBA")
    if p < 0.5: pill(dr, (140, 240), "ANTES", AZUL_ESC, "white")
    else: pill(dr, (W - 140, 240), "DEPOIS", AMARELO, TINTA, anchor_right=True)
    rodape(dr); fr.save(d / f"{i:05d}.png")
encode(d, P / "assets/antes-depois.mp4")

# --- linha do tempo ---
passos = ["Avaliação", "Extrações", "Reabilitação com prótese", "Ajustes em etapas"]
d = frames_dir(); n = round(dur_lt * FPS)
for i in range(n):
    t = i / FPS
    fr = Image.new("RGB", (W, H), (244, 248, 252)); dr = ImageDraw.Draw(fr)
    dr.text((W // 2, 260), "Como foi o tratamento", font=fonte(54), fill=TINTA, anchor="mm")
    x0, y0, gap = 200, 380, 135
    dr.line((x0, y0, x0, y0 + gap * 3), fill=(200, 212, 226), width=10)
    for k, (txt, tk) in enumerate(zip(passos, passos_t)):
        y = y0 + gap * k; on = min(max((t - tk) / 0.35, 0), 1)
        if on > 0 and k > 0:
            yprev = y0 + gap * (k - 1)
            dr.line((x0, yprev, x0, yprev + (y - yprev) * min(on * 1.5, 1)), fill=AZUL, width=10)
        r = 34 + round(10 * (1 - abs(1 - on * 2)) if 0 < on < 1 else 0)
        dr.ellipse((x0 - r, y - r, x0 + r, y + r), fill=AZUL if on > 0 else (200, 212, 226))
        dr.text((x0, y), str(k + 1), font=fonte(34), fill="white", anchor="mm")
        cor = tuple(round(c1 + (c2 - c1) * on) for c1, c2 in zip((170, 182, 196), TINTA))
        dr.text((x0 + 80 + round(30 * (1 - on)), y), txt, font=fonte(50), fill=cor, anchor="lm")
    dr.text((W // 2, H - 50), "Cada caso tem o seu tempo. Resultados variam.", font=fonte(30, False), fill=(90, 110, 135), anchor="mm")
    fr.save(d / f"{i:05d}.png")
encode(d, P / "assets/linha-tempo.mp4")
print("ok")

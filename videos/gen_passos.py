#!/usr/bin/env python3
"""B-roll genérico 1080x960 (tela dividida): título + passos numerados que acendem nos tempos da fala.
Uso: python3 gen_passos.py <saida.mp4> <duracao> "<título>" "<rodapé>" "t1|texto 1" "t2|texto 2" ...
Os tempos são relativos ao início do B-roll. Área útil respeita o topo do Instagram (y >= 220) e o corte lateral.
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(sys.argv[1]); dur = float(sys.argv[2]); titulo = sys.argv[3]; rodape = sys.argv[4]
passos = [(float(a.split("|", 1)[0]), a.split("|", 1)[1]) for a in sys.argv[5:]]
W, H, FPS = 1080, 960, 30
AZUL, TINTA, CINZA = (27, 129, 214), (11, 37, 64), (200, 212, 226)
F = "/System/Library/Fonts/Helvetica.ttc"
def fonte(t, bold=True): return ImageFont.truetype(F, t, index=1 if bold else 0)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

n = len(passos); gap = min(135, 480 // max(n - 1, 1)); x0 = 200
y0 = 380 + (3 - (n - 1)) * gap // 2 if n < 4 else 380
fs = 50 if max(len(t) for _, t in passos) <= 26 else 42
tmp = Path(tempfile.mkdtemp())
for i in range(round(dur * FPS)):
    t = i / FPS
    fr = Image.new("RGB", (W, H), (244, 248, 252)); dr = ImageDraw.Draw(fr)
    dr.text((W // 2, 260), titulo, font=fonte(54), fill=TINTA, anchor="mm")
    dr.line((x0, y0, x0, y0 + gap * (n - 1)), fill=CINZA, width=10)
    for k, (tk, txt) in enumerate(passos):           # 1ª passada: só as linhas
        y = y0 + gap * k; on = ease((t - tk) / 0.35)
        if on > 0 and k > 0:
            yp = y0 + gap * (k - 1); dr.line((x0, yp, x0, yp + (y - yp) * min(on * 1.5, 1)), fill=AZUL, width=10)
    for k, (tk, txt) in enumerate(passos):           # 2ª passada: círculos e textos por cima
        y = y0 + gap * k; on = ease((t - tk) / 0.35)
        r = 34 + (round(10 * (1 - abs(1 - on * 2))) if 0 < on < 1 else 0)
        dr.ellipse((x0 - r, y - r, x0 + r, y + r), fill=AZUL if on > 0 else CINZA)
        dr.text((x0, y), str(k + 1), font=fonte(34), fill="white", anchor="mm")
        cor = tuple(round(c1 + (c2 - c1) * on) for c1, c2 in zip((170, 182, 196), TINTA))
        dr.text((x0 + 80 + round(30 * (1 - on)), y), txt, font=fonte(fs), fill=cor, anchor="lm")
    if rodape: dr.text((W // 2, H - 50), rodape, font=fonte(30, False), fill=(90, 110, 135), anchor="mm")
    fr.save(tmp / f"{i:05d}.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(out)], check=True)
shutil.rmtree(tmp); print("ok", out)

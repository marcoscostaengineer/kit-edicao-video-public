#!/usr/bin/env python3
"""B-roll 1080x960 (tela dividida) da prótese tipo protocolo, animado a partir da grade 2x2 do Gemini
(fundo magenta: 1 arcada com implantes, 2 prótese sozinha, 3 prótese parafusada, 4 corte do implante).
Uso: python3 gen_protocolo.py <grade.png> <saida.mp4> <duracao>
Tempos (relativos ao início do B-roll) casados com a fala do IMG_4676: a prótese entra em "protocolo",
desce e encaixa em "parafusada", o corte do implante entra em "sustentada por implantes" e os três
benefícios acendem em "conforto", "segurança" e "estabilidade".
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

grade, out, dur = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3])
W, H, FPS = 1080, 960, 30
FUNDO, TINTA, AZUL = (244, 248, 252), (11, 37, 64), (27, 129, 214)
F = "/System/Library/Fonts/Helvetica.ttc"
def fonte(t, bold=True): return ImageFont.truetype(F, t, index=1 if bold else 0)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bounce(x):
    x = min(max(x, 0), 1)
    return 1 + 0.06 * (1 - x) * (1 if x < 1 else 0) if x < 1 else 1

# tempos relativos (s)
T_PROTESE, T_JAW, T_DESCE, T_ENCAIXE, T_CORTE, T_VOLTA = 0.15, 2.4, 3.9, 4.45, 5.05, 6.6
T_BENEF = [(6.9, "Conforto"), (7.65, "Segurança"), (8.4, "Estabilidade")]

def recorta(im):
    """Magenta vira transparência, com borda suavizada e desmagentizada."""
    im = im.convert("RGBA"); px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            m = min(r, b) - g                      # quanto "magenta" o pixel é
            if m > 90: px[x, y] = (r, g, b, 0)
            elif m > 40:
                k = (m - 40) / 50
                px[x, y] = (int(r - (r - g) * k), g, int(b - (b - g) * k), int(255 * (1 - k)))
    bb = im.getbbox()
    return im.crop(bb) if bb else im

g = Image.open(grade).convert("RGB"); gw, gh = g.size
q = []
for (x0, y0) in ((0, 0), (gw // 2, 0), (0, gh // 2), (gw // 2, gh // 2)):
    m = 34
    q.append(recorta(g.crop((x0 + m, y0 + m, x0 + gw // 2 - m, y0 + gh // 2 - m))))
jaw, protese, montada, corte = q

def larg(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
JAW, PROT, MONT = larg(jaw, 560), larg(protese, 520), larg(montada, 600)
CORTE = corte.resize((round(corte.width * 420 / corte.height), 420), Image.LANCZOS)

def sombra(im, alfa=60):
    s = Image.new("RGBA", im.size, (0, 0, 0, 0)); s.putalpha(im.split()[3].point(lambda v: v * alfa // 255))
    return s.filter(ImageFilter.GaussianBlur(14))

def cola(fr, im, cx, cy, op=1.0, esc=1.0):
    if op <= 0: return
    if esc != 1.0: im = im.resize((max(1, round(im.width * esc)), max(1, round(im.height * esc))), Image.LANCZOS)
    if op < 1:
        a = im.split()[3].point(lambda v: int(v * op)); im = im.copy(); im.putalpha(a)
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    fr.alpha_composite(sombra(im), (x + 6, y + 18)); fr.alpha_composite(im, (x, y))

def pilula(dr, cx, cy, txt, op, cor=AZUL):
    if op <= 0: return
    f = fonte(40); w = dr.textlength(txt, font=f) + 64
    c = tuple(int(FUNDO[i] + (cor[i] - FUNDO[i]) * op) for i in range(3))
    dr.rounded_rectangle((cx - w / 2, cy - 36, cx + w / 2, cy + 36), radius=36, fill=c)
    dr.text((cx, cy), txt, font=f, fill=tuple(int(c[i] + (255 - c[i]) * op) for i in range(3)), anchor="mm")

tmp = Path(tempfile.mkdtemp())
for i in range(round(dur * FPS)):
    t = i / FPS
    fr = Image.new("RGBA", (W, H), FUNDO + (255,)); dr = ImageDraw.Draw(fr)
    dr.text((W // 2, 262), "Prótese tipo protocolo", font=fonte(56), fill=TINTA, anchor="mm")
    sub = "parafusada sobre implantes" if t >= T_DESCE else ""
    if sub: dr.text((W // 2, 322), sub, font=fonte(36, False), fill=(15, 76, 129), anchor="mm")

    cy = 600
    if t < T_ENCAIXE:
        # arcada com implantes sobe de baixo
        a = ease((t - T_JAW) / 0.6)
        cola(fr, JAW, W / 2, cy + 110 + (1 - a) * 300, op=a)
        # prótese: entra de cima, flutua, desce sobre a arcada
        e = ease((t - T_PROTESE) / 0.6)
        flut = 8 * __import__("math").sin(t * 3)
        if t < T_JAW: py = 530 - (1 - e) * 250
        elif t < T_DESCE: py = 530 - ease((t - T_JAW) / 0.6) * 90 + flut
        else: py = 440 + ease((t - T_DESCE) / (T_ENCAIXE - T_DESCE)) * 170
        fade = 1 - ease((t - (T_ENCAIXE - 0.25)) / 0.25) if t > T_ENCAIXE - 0.25 else 1
        cola(fr, PROT, W / 2, py, op=e * fade)
    elif t < T_CORTE:
        b = (t - T_ENCAIXE) / 0.35
        cola(fr, MONT, W / 2, cy + 40, esc=1.04 - 0.04 * ease(b))
    elif t < T_VOLTA:
        c = ease((t - T_CORTE) / 0.4)
        cola(fr, MONT, W / 2 - 200 * c, cy + 40, op=1 - 0.75 * c, esc=1 - 0.25 * c)
        cola(fr, CORTE, W / 2 + 130 + (1 - c) * 120, cy + 30, op=c)
        if c > 0.3: pilula(dr, W / 2, 905, "Sustentada por implantes", ease((t - T_CORTE - 0.2) / 0.4), TINTA)
    else:
        d = ease((t - T_VOLTA) / 0.4)
        cola(fr, CORTE, W / 2 + 130 + d * 400, cy + 30, op=1 - d)
        cola(fr, MONT, W / 2 - 200 * (1 - d), cy + 10, op=0.25 + 0.75 * d, esc=0.75 + 0.2 * d)
        xs = (W / 2 - 330, W / 2, W / 2 + 330)
        for (tb, txt), x in zip(T_BENEF, xs):
            pilula(dr, x, 905, txt, ease((t - tb) / 0.35))
    fr.convert("RGB").save(tmp / f"f{i:05d}.png")

subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)], check=True)
shutil.rmtree(tmp)
print("ok", out)

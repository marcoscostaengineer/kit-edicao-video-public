#!/usr/bin/env python3
"""B-roll 1080x960 da prótese tipo protocolo INFERIOR a partir de quadros ALINHADOS do Gemini (15/10).
Quadros: mandíbula com 4 implantes (q1), prótese acima e alinhada (q2), prótese encaixada (q4) — mesma câmera —
e o corte do implante no osso (corte). Fundo magenta vira transparente.
A descida é feita por quadros: q1 -> q2 (a prótese chega de cima) -> q4 (desce, encaixa e assenta com um leve quique).
Uso: python3 gen_protocolo2.py <q1.png> <q2.png> <q4.png> <corte.png> <saida.mp4> <duracao>
"""
import math, subprocess, sys, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

q1p, q2p, q4p, cortep, out, dur = sys.argv[1:7]; dur = float(dur)
W, H, FPS = 1080, 960, 30
FUNDO, TINTA, AZUL, AZUL2 = (244, 248, 252), (11, 37, 64), (27, 129, 214), (15, 76, 129)
F = "/System/Library/Fonts/Helvetica.ttc"
def fonte(t, bold=True): return ImageFont.truetype(F, t, index=1 if bold else 0)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

# tempos relativos ao início do B-roll (fala do IMG_4676: B-roll começa em 6,9 s)
T_Q2, T_DESCE, T_ENCAIXE, T_CORTE, T_VOLTA = 0.15, 3.85, 4.35, 5.05, 6.6
T_BENEF = [(6.9, "Conforto"), (7.65, "Segurança"), (8.4, "Estabilidade")]

def recorta(path):
    im = Image.open(path).convert("RGBA"); px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]; m = min(r, b) - g
            if m > 90: px[x, y] = (r, g, b, 0)
            elif m > 40:
                k = (m - 40) / 50
                px[x, y] = (int(r - (r - g) * k), g, int(b - (b - g) * k), int(255 * (1 - k)))
    return im

Q1, Q2, Q4, CORTE = (recorta(p) for p in (q1p, q2p, q4p, cortep))
# os três quadros da sequência usam a MESMA escala e o MESMO ponto (a câmera do Gemini é a mesma)
def esc(im, s): return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
# O Gemini desenha a mandíbula com tamanhos um pouco diferentes em cada quadro: normaliza pela
# LARGURA da mandíbula (bbox) e alinha pela BASE, para a peça não "pular" na troca de quadro.
def normaliza(im, larg=680, base=0.5):
    bb = im.getbbox(); im = im.crop(bb); im = esc(im, larg / im.width)
    tela = Image.new("RGBA", (larg + 40, 560), (0, 0, 0, 0))
    tela.alpha_composite(im, (20, 560 - im.height - 20))
    return tela
Q1, Q2, Q4 = normaliza(Q1), normaliza(Q2), normaliza(Q4)
bb = CORTE.getbbox(); CORTE = CORTE.crop(bb); CORTE = esc(CORTE, 420 / CORTE.height)

def sombra(im):
    s = Image.new("RGBA", im.size, (0, 0, 0, 0)); s.putalpha(im.split()[3].point(lambda v: v * 50 // 255))
    return s.filter(ImageFilter.GaussianBlur(16))

def cola(fr, im, cx, cy, op=1.0, s=1.0):
    if op <= 0.01: return
    if s != 1.0: im = esc(im, s)
    if op < 1: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * op)))
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    fr.alpha_composite(sombra(im), (x + 6, y + 16)); fr.alpha_composite(im, (x, y))

def pilula(dr, cx, cy, txt, op, cor=AZUL):
    if op <= 0: return
    f = fonte(40); w = dr.textlength(txt, font=f) + 64
    c = tuple(int(FUNDO[i] + (cor[i] - FUNDO[i]) * op) for i in range(3))
    dr.rounded_rectangle((cx - w / 2, cy - 36, cx + w / 2, cy + 36), radius=36, fill=c)
    dr.text((cx, cy), txt, font=f, fill=tuple(int(c[i] + (255 - c[i]) * op) for i in range(3)), anchor="mm")

CX, CY = W / 2, 615
tmp = Path(tempfile.mkdtemp())
for i in range(round(dur * FPS)):
    t = i / FPS
    fr = Image.new("RGBA", (W, H), FUNDO + (255,)); dr = ImageDraw.Draw(fr)
    dr.text((W // 2, 262), "Prótese tipo protocolo", font=fonte(56), fill=TINTA, anchor="mm")
    if t >= T_DESCE: dr.text((W // 2, 322), "parafusada sobre implantes", font=fonte(36, False), fill=AZUL2, anchor="mm")
    zoom = 1 + 0.03 * ease(t / dur)                                  # câmera respirando devagar
    if t < T_CORTE:
        if t < T_DESCE:
            a = ease((t - T_Q2) / 0.7)                                # prótese chega de cima
            cola(fr, Q1, CX, CY, 1 - a, zoom)
            cola(fr, Q2, CX, CY - (1 - a) * 40 + 4 * math.sin(t * 3) * a, a, zoom)
        else:
            d = ease((t - T_DESCE) / (T_ENCAIXE - T_DESCE))           # desce e encaixa
            quique = 6 * math.sin(min(max((t - T_ENCAIXE) / 0.35, 0), 1) * math.pi) if t > T_ENCAIXE else 0
            cola(fr, Q2, CX, CY + d * 30, 1 - d, zoom)
            cola(fr, Q4, CX, CY - (1 - d) * 25 + quique, d, zoom)
    elif t < T_VOLTA:
        c = ease((t - T_CORTE) / 0.4)
        cola(fr, Q4, CX - 210 * c, CY, 1 - 0.7 * c, zoom * (1 - 0.3 * c))
        cola(fr, CORTE, CX + 150 + (1 - c) * 120, CY - 10, c)
        if c > 0.3: pilula(dr, W / 2, 905, "Sustentada por implantes", ease((t - T_CORTE - 0.2) / 0.4), TINTA)
    else:
        d = ease((t - T_VOLTA) / 0.4)
        cola(fr, CORTE, CX + 150 + d * 420, CY - 10, 1 - d)
        cola(fr, Q4, CX - 210 * (1 - d), CY - 10 * d, 0.3 + 0.7 * d, zoom * (0.7 + 0.25 * d))
        for (tb, txt), x in zip(T_BENEF, (W / 2 - 330, W / 2, W / 2 + 330)):
            pilula(dr, x, 905, txt, ease((t - tb) / 0.35))
    fr.convert("RGB").save(tmp / f"f{i:05d}.png")

subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
shutil.rmtree(tmp); print("ok", out)

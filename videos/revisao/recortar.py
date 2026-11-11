#!/usr/bin/env python3
"""Recorte genérico para a Sala de revisão (base: gravação da Brenda de 24/10, IMG_5391): chroma do pano verde-amarelado (matiz 33–60°) sobre fundo preto, SEM tratamento
de cor, para avaliar a iluminação crua. Trecho em que ele está em quadro: 11,5–25,5 s.
Chroma no contorno (preserva a luz de recorte rosa); recorte por IA só como máscara de lixo e tapa-furo.
Uso: python3 recortar.py  -> build/teste-luz-preto.mp4"""
import os, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.ndimage import uniform_filter, minimum_filter, maximum_filter

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "chroma-2026-10-23"))
from looks import LOOKS  # noqa: E402
LOOK = os.environ.get("LOOK", "neutro")                # ex.: LOOK=cinema (looks.py da pasta chroma-2026-10-23)
PASTA = Path(os.environ["PASTA"])                     # pasta da gravação (trecho.mp4 + trecho-matte.mov)
FONTE = PASTA / "trecho.mp4"
TRECHO = ["-ss", os.environ["INI"], "-t", os.environ["DUR"]] if os.environ.get("INI") else []   # INI/DUR: só um pedaço
SAI = PASTA / os.environ.get("SAIDA", f"preto-{LOOK}.mp4")
MATTE = PASTA / "trecho-matte.mov"   # recorte por IA do mesmo trecho: só máscara de lixo e tapa-furo
W, H = 1080, 1920


def rampa(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def chave(rgb, m):
    f = rgb.astype(np.float32) / 255
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx, mn = f.max(-1), f.min(-1); d = mx - mn + 1e-6
    hue = np.where(g >= mx, 60 * (b - r) / d + 120, np.where(r >= mx, (60 * (g - b) / d) % 360, 60 * (r - g) / d + 240))
    sat = d / (mx + 1e-6)
    verde = rampa(hue, 24, 32) * (1 - rampa(hue, 92, 102))         # pano: 55–86° (lado direito mais verde); pele e dólmã azul ficam fora
    k = verde * rampa(sat, 0.20, 0.32) * rampa(mx, 0.22, 0.34)
    a = uniform_filter(1 - k, size=3)
    # A luz de recorte rosa bate no pano e vira faixas que não são verdes: fora do corpo (IA dilatada ~10 px) é preto.
    lixo = uniform_filter(m, size=5)                                   # limite justo: fora do contorno da IA é preto (halo do pano na roupa escura)
    miolo = uniform_filter(minimum_filter(m, size=25), size=9)       # tapa o reflexo verde na camiseta
    a = np.maximum(a, miolo) * lixo
    lim = np.maximum(r, b)                                         # reflexo esverdeado na borda
    # reflexo verde do pano na borda do jaleco e do cabelo: neutraliza o excesso de verde em toda a faixa 35–110°
    # (pele 11–22° e o rosa da luz de recorte ~300° ficam intocados)
    faixa = rampa(hue, 30, 40) * (1 - rampa(hue, 105, 115))
    g2 = np.where(g > lim, g - (g - lim) * (0.75 + 0.2 * faixa) * np.maximum(faixa, (verde > 0.2)), g)
    return LOOKS[LOOK](np.stack([r, g2, b], -1)) * a[..., None]


dec = subprocess.Popen(["ffmpeg", "-v", "error", *TRECHO, "-i", str(FONTE), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
mat = subprocess.Popen(["ffmpeg", "-v", "error", *TRECHO, "-i", str(MATTE), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30",
                        "-i", "-", *TRECHO, "-i", str(FONTE), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                        "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(SAI)], stdin=subprocess.PIPE)
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    m = np.frombuffer(mat.stdout.read(W * H * 4), np.uint8).reshape(H, W, 4)[..., 3].astype(np.float32) / 255
    out = chave(np.frombuffer(buf, np.uint8).reshape(H, W, 3), m)
    enc.stdin.write((out * 255 + 0.5).clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.wait(); print(SAI)

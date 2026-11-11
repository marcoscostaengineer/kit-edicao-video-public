#!/usr/bin/env python3
"""Fatia as grades do Gemini (gemini/*.jpg) em quadros e recorta o fundo verde chroma.
Uso: python3 recortar.py gemini/g1-objetos.jpg 2x2 nome1,nome2,nome3,nome4 [verde=1,1,1,1]
Saída em assets/img/<nome>.png (verde: recorte com alfa e sem vazamento de verde; senão o quadro inteiro)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "assets/img"
OUT.mkdir(parents=True, exist_ok=True)


def bordas(a, eixo, n):
    """posições das bordas brancas da grade: linhas/colunas quase brancas perto das frações 1/n"""
    branco = (a.min(axis=2) > 235).mean(axis=1 - eixo)          # fração branca por linha (eixo 0) ou coluna (eixo 1)
    L = a.shape[eixo]
    cortes = []
    for k in range(1, n):
        c = int(L * k / n)
        jan = range(max(0, c - L // 12), min(L, c + L // 12))
        brancos = [i for i in jan if branco[i] > 0.9]
        cortes.append((min(brancos), max(brancos) + 1) if brancos else (c, c))
    lim, ini = [], 0
    for b0, b1 in cortes:
        lim.append((ini, b0)); ini = b1
    lim.append((ini, L))
    return lim


def chroma(q):
    a = np.asarray(q.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verde = g - np.maximum(r, b)                                   # quanto o pixel é "mais verde que o resto"
    alfa = np.clip(1 - (verde - 40) / 80, 0, 1)                    # >120 = fundo, <40 = objeto
    a[..., 1] = np.minimum(g, np.maximum(r, b) * 1.02 + 6)         # tira o verde que vaza nas bordas e no translúcido
    img = Image.fromarray(np.dstack([a, alfa * 255]).astype(np.uint8))
    al = img.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    m = np.asarray(al).copy(); m[:30, :] = 0; m[-30:, :] = 0; m[:, :30] = 0; m[:, -30:] = 0   # sobra da borda da grade
    al = Image.fromarray(m)
    img.putalpha(al)
    bb = al.point(lambda v: 255 if v > 20 else 0).getbbox()
    return img.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), bb[2] + 12, bb[3] + 12))


def main():
    arq, grade, nomes = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    verde = [x == "1" for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [True] * len(nomes)
    cols, lins = map(int, grade.split("x"))
    im = Image.open(AQUI / arq).convert("RGB")
    # S12 (31/10): as grades novas do Gemini vêm com margem branca EXTERNA; sem aparar, o quadro leva um filete branco
    nb = np.asarray(im).min(axis=2) < 235
    ys_, xs_ = np.where(nb.mean(axis=1) > 0.2)[0], np.where(nb.mean(axis=0) > 0.2)[0]
    im = im.crop((xs_[0], ys_[0], xs_[-1] + 1, ys_[-1] + 1))
    a = np.asarray(im)
    ys, xs = bordas(a, 0, lins), bordas(a, 1, cols)
    k = 0
    for y0, y1 in ys:
        for x0, x1 in xs:
            if k >= len(nomes):
                break
            q = im.crop((x0 + 4, y0 + 4, x1 - 4, y1 - 4))
            nome = nomes[k]
            if nome != "-":
                (chroma(q) if verde[k] else q).save(OUT / f"{nome}.png")
                print(nome, q.size)
            k += 1


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Confere quadros de um vídeo vertical 1080x1920 contra a área da interface do Instagram (regra de 25/10/2026):
texto só entre y 290 e 1480, e até x 900 da metade para baixo. Desenha as zonas cobertas em vermelho translúcido sobre
os quadros e grava uma folha para olhar antes de entregar.
Uso: python3 checar_area_segura.py video.mp4 saida.jpg t1 t2 t3 ...   ou   python3 checar_area_segura.py pasta-de-quadros/ saida.jpg"""
import subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

TOPO, BASE, DIREITA, LADO, METADE = 290, 1480, 900, 60, 1000


def zonas(im):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    W, H = im.size
    k = W / 1080
    cor = (226, 74, 74, 90)
    d.rectangle([0, 0, W, TOPO * k], fill=cor)
    d.rectangle([0, BASE * k, W, H], fill=cor)
    d.rectangle([DIREITA * k, METADE * k, W, BASE * k], fill=cor)
    d.rectangle([0, TOPO * k, LADO * k, BASE * k], fill=(226, 74, 74, 45))
    d.rectangle([W - LADO * k, TOPO * k, DIREITA * k if DIREITA * k > W - LADO * k else W, METADE * k], fill=(226, 74, 74, 45))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def main():
    fonte, saida, tempos = sys.argv[1], sys.argv[2], sys.argv[3:]
    quadros = []
    if fonte.endswith(".mp4"):
        tmp = Path(tempfile.mkdtemp())
        for t in tempos:
            f = tmp / f"q{t}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", fonte, "-frames:v", "1", "-vf", "scale=360:640", str(f)], check=True)
            quadros.append(Image.open(f))
    else:
        quadros = [Image.open(p).resize((360, 640)) for p in sorted(Path(fonte).glob("frame-*.png"))]
    folha = Image.new("RGB", (365 * len(quadros), 640), "white")
    for i, q in enumerate(quadros):
        folha.paste(zonas(q), (i * 365, 0))
    folha.save(saida)
    print(saida)


if __name__ == "__main__":
    main()

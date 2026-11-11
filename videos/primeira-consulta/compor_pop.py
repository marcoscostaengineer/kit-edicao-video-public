#!/usr/bin/env python3
"""Monta o estilo "pop" (palavra gigante ATRÁS da pessoa) contornando o renderizador, que perde a
transparência do recorte (talk-matte.webm) e o desenha opaco.

Camadas:  A = vídeo + palavras gigantes + legendas (sem recorte)
          recorte = talk-matte.webm decodificado com libvpx-vp9 (mantém o alfa), só nas janelas das palavras
          B = só as legendas, fundo transparente (MOV), por cima do recorte nas mesmas janelas
Uso: python3 compor_pop.py <projeto> <saida.mp4>     (rodar depois do build.mjs; sem zoom nas janelas)
"""
import re, subprocess, sys, glob, os
from pathlib import Path

P = Path(sys.argv[1]); OUT = Path(sys.argv[2])
HF = glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/.bin/hyperframes"))[0]
doc = (P / "index.html").read_text()

janelas = [(float(a), float(a) + float(d)) for a, d in
           re.findall(r'class="clip behind" data-start="([\d.]+)" data-duration="([\d.]+)"', doc)]
media_start = float(re.search(r'id="matte-0"[^>]*data-media-start="([\d.]+)"', doc).group(1))

# A: sem o recorte
a = re.sub(r'<video id="matte-0"[^>]*></video>', '', doc)
(P / "camada-a.html").write_text(a)

# B: só legendas, fundo transparente
b = re.sub(r'<video id="(take|matte)-\d+"[^>]*></video>', '', doc)
b = re.sub(r'<img id="outro-still"[^>]*/>', '', b)
b = b.replace("body { margin: 0; background: #000; }", "body { margin: 0; background: transparent; }")
b = re.sub(r'(#root \{[^}]*?)background: #000;', r'\1background: transparent;', b)
for bid in re.findall(r'<div id="(b\d+)" class="clip (?:behind|layer)"', b):
    b = re.sub(rf'(<div id="{bid}" class="clip (?:behind|layer)")', r'\1 style="display:none"', b)
b = re.sub(r'<audio[^>]*></audio>', '', b)
(P / "camada-b.html").write_text(b)

def render(html, out, *extra):
    subprocess.run([HF, "render", str(P), "-c", html, "-o", str(out), "--quiet", *extra], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

A = P / "build/camada-a.mp4"; B = P / "build/camada-b.mov"
render("camada-a.html", A, "--sdr")
render("camada-b.html", B, "--format", "mov")

en = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in janelas)
fc = (f"[1:v]setpts=PTS-STARTPTS,format=yuva420p[m];"
      f"[0:v][m]overlay=0:0:enable='{en}'[v1];"
      f"[2:v]format=yuva444p10le[c];"
      f"[v1][c]overlay=0:0:enable='{en}',format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(A),
                "-ss", f"{media_start}", "-c:v", "libvpx-vp9", "-i", str(P / "assets/talk-matte.webm"),
                "-i", str(B), "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
                "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", str(OUT)], check=True)
print("ok", OUT, "janelas", janelas)

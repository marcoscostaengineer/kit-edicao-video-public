"""Acha trechos em que o palco (y 130 a 800) fica sem ilustração: só fundo, chip e legenda. Uso: python3 vazios.py <video.mp4>"""
import subprocess, sys
import numpy as np
video = sys.argv[1]
W, H, FPS = 192, 108, 2
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
palco = fr[:, 13:80, :]                     # faixa do palco em 108 px de altura (y 130 a 800 em 1080)
cheio = (palco > 70).mean(axis=(1, 2))      # fração de pixels claros (peça, foto, painel)
vazio = cheio < 0.012
trechos, ini = [], None
for i, v in enumerate(list(vazio) + [False]):
    t = i / FPS
    if v and ini is None:
        ini = t
    if not v and ini is not None:
        if t - ini >= 1.5:
            trechos.append((ini, t))
        ini = None
tot = sum(b - a for a, b in trechos)
for a, b in trechos:
    print(f"{int(a // 60)}:{a % 60:04.1f} a {int(b // 60)}:{b % 60:04.1f}  ({b - a:.1f}s)")
print(f"{len(trechos)} trechos, {tot:.0f}s vazios de {len(fr) / FPS:.0f}s")

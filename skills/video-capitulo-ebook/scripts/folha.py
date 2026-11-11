"""Folha de quadros do MP4 renderizado (revisão do piloto). Uso: python3 folha.py <video.mp4> <t0> <t1> <passo> <saida.jpg>"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

video, t0, t1, passo, saida = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
tmp = Path(tempfile.mkdtemp())
tempos, t = [], t0
while t <= t1:
    tempos.append(round(t, 2))
    t += passo
W, H, COLS = 480, 270, 4
quadros = []
for k, t in enumerate(tempos):
    f = tmp / f"q{k:03d}.jpg"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf", f"scale={W}:{H}", str(f)],
                   check=True)
    quadros.append((t, f))
linhas = (len(quadros) + COLS - 1) // COLS
folha = Image.new("RGB", (COLS * W, linhas * (H + 22)), "#222")
d = ImageDraw.Draw(folha)
for k, (t, f) in enumerate(quadros):
    x, y = (k % COLS) * W, (k // COLS) * (H + 22)
    folha.paste(Image.open(f), (x, y))
    d.text((x + 6, y + H + 4), f"{int(t // 60)}:{t % 60:05.2f}", fill="#D7F23A")
folha.save(saida, quality=82)
print(saida, len(quadros))

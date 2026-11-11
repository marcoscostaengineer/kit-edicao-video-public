#!/usr/bin/env python3
"""Reenquadra o talk.mp4 a partir do ORIGINAL em 4K, seguindo o rosto (15/10/2026).
O Antonio reclamou duas vezes de "muito teto/céu e a Brenda pequena": o prep do ghost-editor só
reduz o 4K para 1080x1920 sem recortar. Aqui a câmera virtual aproxima (zoom) e acompanha o rosto
com os olhos a ~30% da altura, suavizada para não tremer; sai nítido porque recorta do 4K.

Uso: python3 enquadrar.py <ORIGINAL.MOV> <pasta_take> [zoom fixo — omita para zoom automático por cena] [olhos=0.30]
Guarda o prep antigo em build/talk-original-prep.mp4 (de onde vem o áudio já normalizado)
e regrava assets/talk.mp4 + build/face.json.
"""
import json, subprocess, sys
from pathlib import Path

S = Path.home() / ".claude/skills/ghost-editor/scripts"
orig, P = Path(sys.argv[1]), Path(sys.argv[2])
Z = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != "auto" else None
# olhos: um valor para todas as cenas ou um por cena ("0.40,0.30": a 1ª tem caixinha no topo, a 2ª não)
OLHOS_L = [float(v) for v in (sys.argv[4] if len(sys.argv) > 4 else "0.30").split(",")]
OLHOS = OLHOS_L[0]

prep = P / "build/talk-original-prep.mp4"
if not prep.exists():
    prep.write_bytes((P / "assets/talk.mp4").read_bytes())

# tamanho do quadro do original já rotacionado (o ffmpeg aplica a rotação antes dos filtros)
pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                     "stream=width,height:stream_side_data=rotation", "-of", "json", str(orig)],
                    capture_output=True, text=True).stdout
st = json.loads(pr)["streams"][0]
w, h = st["width"], st["height"]
rot = abs(int(next((d.get("rotation", 0) for d in st.get("side_data_list", []) if "rotation" in d), 0)))
if rot in (90, 270): w, h = h, w
if w > h: sys.exit(f"original na horizontal ({w}x{h}); este script é para vídeo em pé")
k = w / 1080                                              # 1 px do prep = k px do original

fj = P / "build/face-orig.json"
subprocess.run(["python3", str(S / "face_track.py"), str(prep), "--out", str(fj)], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
amostras = [s for s in json.load(open(fj))["samples"] if s[1] is not None]
CW = int(w / (Z or 1.45)) // 2 * 2; CH = int(CW * 16 / 9) // 2 * 2
pts = [(s[0], (s[3] + s[4]) / 2 * k, s[5] * k) for s in amostras]   # centro do rosto e altura dos olhos

def media(i, j):                                          # média móvel de 1,2 s
    v = [p[j] for p in pts if abs(p[0] - pts[i][0]) <= 0.6]
    return sum(v) / len(v)

# Recorte FIXO por cena (15/10): seguir o rosto quadro a quadro deixou o vídeo tremido. Agora a
# posição só muda onde a câmera mudou de lugar (salto grande e sustentado do rosto); dentro de
# cada cena o recorte é um só, na mediana da posição do rosto.
cenas, ini = [], 0
for i in range(1, len(pts)):
    if abs(pts[i][1] - pts[i - 1][1]) > 0.12 * w or abs(pts[i][2] - pts[i - 1][2]) > 0.08 * h:
        if pts[i][0] - pts[ini][0] >= 1.0: cenas.append((ini, i)); ini = i
cenas.append((ini, len(pts)))
def mediana(v): v = sorted(v); return v[len(v) // 2]
# Zoom POR CENA (15/10): no plano de longe (reflexo do espelho) a Brenda fica pequena; cada cena
# ganha o zoom que deixa o rosto com ~ROSTO da largura do quadro (entre 1,2x e 2,2x).
ROSTO = 0.33
larg = {i: (s[4] - s[3]) * k for i, s in enumerate(amostras)}
linhas, pos = [], []
for n, (a, b) in enumerate(cenas):
    OLHOS = OLHOS_L[min(n, len(OLHOS_L) - 1)]
    cx = mediana([p[1] for p in pts[a:b]]); ey = mediana([p[2] for p in pts[a:b]])
    fw = mediana([larg[i] for i in range(a, b)])
    cw = int(min(max(fw / ROSTO, w / 2.2), w / 1.2)) // 2 * 2 if Z is None else CW
    ch = int(cw * 16 / 9) // 2 * 2
    pos.append((pts[a][0], min(max(cx - cw / 2, 0), w - cw), min(max(ey - OLHOS * ch, 0), h - ch), cw, ch))
# Entre cenas, o recorte DESLIZA (1,4 s, com aceleração suave) em vez de pular: quando a câmera
# real faz um movimento (ex.: sai do reflexo do espelho para a Brenda), a câmera virtual acompanha.
TRANS = 1.4
def suave(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
for k, (t0, x, y, cw, ch) in enumerate(pos):
    if k == 0:
        linhas.append(f"0.00 crop w {cw}, crop h {ch}, crop x {int(x)}, crop y {int(y)};"); continue
    _, xa, ya, wa, ha = pos[k - 1]; ini_t = max(t0 - TRANS / 2, 0)
    for f in range(int(TRANS * 30) + 1):
        u = suave(f / (TRANS * 30))
        ww = int(wa + (cw - wa) * u) // 2 * 2; hh = int(ww * 16 / 9) // 2 * 2
        linhas.append(f"{ini_t + f / 30:.3f} crop w {ww}, crop h {hh}, crop x {int(xa + (x - xa) * u)}, crop y {int(ya + (y - ya) * u)};")
CW, CH = pos[0][3], pos[0][4]
print(f"{len(cenas)} cena(s):", " | ".join(l for l in linhas))
cmd = P / "build/crop.cmd"; cmd.write_text("\n".join(linhas) + "\n")
x0, y0 = linhas[0].split("x ")[1].split(",")[0], linhas[0].split("y ")[1].rstrip(";")

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(orig), "-i", str(prep), "-map", "0:v:0", "-map", "1:a:0",
                "-vf", f"sendcmd=f={cmd},crop={CW}:{CH}:{x0}:{y0},scale=1080:1920:flags=lanczos,setsar=1,fps=30",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy",
                "-shortest", str(P / "assets/talk.mp4")], check=True)
(P / "assets/talk-matte.webm").unlink(missing_ok=True)       # recorte novo invalida o matte antigo
subprocess.run(["python3", str(S / "face_track.py"), str(P / "assets/talk.mp4"), "--out", str(P / "build/face.json")],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"ok: {len(pos)} cena(s), recortes {[(p[3], p[4]) for p in pos]} de {w}x{h} (olhos {OLHOS_L})")

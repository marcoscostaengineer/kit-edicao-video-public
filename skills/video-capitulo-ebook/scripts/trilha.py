"""Trilha sonora e velocidade final do vídeo de capítulo (skill video-capitulo-ebook).
- Música baixinha e FIXA ao fundo, só para dar ritmo: sem ducking e sem loudnorm dinâmico (o Antonio achou estranho a música
  "ficar subindo" nas pausas). A voz recebe um ganho fixo medido; a música entra num nível fixo abaixo dela.
- Velocidade: o vídeo inteiro (imagem, voz e efeitos) acelera junto, para as animações seguirem presas às palavras; a música
  entra depois, no andamento original. atempo mantém o tom da voz.
Uso: python3 trilha.py <video_sem_trilha.mp4> <saida.mp4> [velocidade=1.0]
"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LIB = AQUI / "trilhas/aprovadas"  # faixas aprovadas pelo Antonio (Mixkit Free Music licence)
video, saida = sys.argv[1], sys.argv[2]
VEL = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
DUR0 = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
FIM = DUR0 / VEL
ALVO_VOZ = -14.5   # LUFS da narração com os efeitos
MUSICA_ABAIXO = 17  # dB da música abaixo da voz (baixinha, só ritmo)

# Blocos em blocos.json, ao lado do vídeo do capítulo: [[início, fim ou null, faixa, ponto de partida na faixa], ...], em s do
# vídeo ORIGINAL (antes de acelerar). Uma faixa por parte, revezando, nunca a mesma em blocos seguidos; null = até o fim.
import json
BLOCOS = [(a, DUR0 if b is None else b, n, o) for a, b, n, o in json.load(open(AQUI / "blocos.json"))]
# trocas SEM sobreposição: a faixa sai em 1,2 s, a próxima entra em 0,8 s; o whoosh do cartão de parte marca a virada


def lufs(arq):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(arq), "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float([l for l in r.stderr.splitlines() if l.strip().startswith("I:")][-1].split()[1])


G_VOZ = ALVO_VOZ - lufs(video)
GANHO = {n: (ALVO_VOZ - MUSICA_ABAIXO) - lufs(LIB / f"{n}.mp3") for n in {b[2] for b in BLOCOS}}

ent, filtros, rotulos = [], [], []
for k, (a0, a1, nome, ofs) in enumerate(BLOCOS):
    t0, t1 = a0 / VEL, a1 / VEL
    dur = t1 - t0
    ent += ["-stream_loop", "-1", "-i", str(LIB / f"{nome}.mp3")]
    fi = 0.01 if k == 0 else 0.8
    fo = 4.0 if k == len(BLOCOS) - 1 else 1.2
    filtros.append(f"[{k + 1}:a]atrim=start={ofs}:duration={dur},asetpts=PTS-STARTPTS,volume={GANHO[nome]:.2f}dB,"
                   f"afade=t=in:st=0:d={fi},afade=t=out:st={dur - fo}:d={fo},"
                   f"adelay={int(t0 * 1000)}|{int(t0 * 1000)},apad=whole_dur={FIM}[m{k}]")
    rotulos.append(f"[m{k}]")
filtros.append(f"{''.join(rotulos)}amix=inputs={len(BLOCOS)}:normalize=0[mus]")
voz = f"[0:a]volume={G_VOZ:.2f}dB" + (f",atempo={VEL}" if VEL != 1.0 else "") + "[voz]"
filtros.append(voz)
filtros.append("[voz][mus]amix=inputs=2:normalize=0,alimiter=limit=0.84:level=false[a]")
if VEL != 1.0:
    filtros.append(f"[0:v]setpts=PTS/{VEL},fps=30[v]")
    mapa_v, cod_v = "[v]", ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]
else:
    mapa_v, cod_v = "0:v", ["-c:v", "copy"]
cmd = (["ffmpeg", "-loglevel", "error", "-y", "-i", video] + ent +
       ["-filter_complex", ";".join(filtros), "-map", mapa_v, "-map", "[a]"] + cod_v +
       ["-c:a", "aac", "-b:a", "192k", "-t", f"{FIM:.3f}", "-movflags", "+faststart", saida])
subprocess.run(cmd, check=True)
print(f"ok {saida} · velocidade {VEL} · {FIM:.1f}s · voz {G_VOZ:+.1f} dB · música {MUSICA_ABAIXO} dB abaixo")

#!/usr/bin/env python3
"""(do S12, reaproveitado no S14) S12: a fala do ElevenLabs saiu com 65,6 s e o Reel tem teto de 60 s. Encurta só as pausas longas (silêncio real
medido pelo silencedetect, não pelo whisper) para PAUSA s, guardando o meio de cada uma, e aplica um leve atempo.
A voz não é cortada nem regravada: só o silêncio entre as frases encolhe.
Uso: python3 apertar_pausas.py voice/brenda-s12-take2.mp3 voice/brenda-s12.wav [atempo]
Depois: whisper voice/brenda-s12.wav --model large-v3-turbo --language pt --word_timestamps True --output_format json --output_dir build"""
import re, subprocess, sys

SRC, DST = sys.argv[1], sys.argv[2]
ATEMPO = float(sys.argv[3]) if len(sys.argv) > 3 else 1.05
import os
# R13: texto mais longo dos 12 (1.104 caracteres, 70 s cru); PAUSA e MINIMO ajustáveis por ambiente
LIMIAR = os.environ.get("LIMIAR", "-28dB")
MINIMO = float(os.environ.get("MINIMO", "0.35"))
PAUSA = float(os.environ.get("PAUSA", "0.28"))


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


log = subprocess.run(["ffmpeg", "-nostats", "-i", SRC, "-af", f"silencedetect=noise={LIMIAR}:d={MINIMO}", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
D = dur(SRC)
# trechos de voz a manter: tudo menos o miolo de cada silêncio interno (o silêncio do começo e do fim fica como está)
manter, t = [], 0.0
for a, b in zip(ini, fim):
    if a < 0.05 or b > D - 0.05:
        continue
    corte = (b - a) - PAUSA
    m = (a + b) / 2
    manter.append((t, m - corte / 2))
    t = m + corte / 2
manter.append((t, D))
partes = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (a, b) in enumerate(manter))
cat = "".join(f"[p{i}]" for i in range(len(manter))) + f"concat=n={len(manter)}:v=0:a=1,atempo={ATEMPO}[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", partes + cat, "-map", "[out]",
                "-ar", "44100", "-ac", "1", DST], check=True)
print(f"pausas encurtadas: {len(manter) - 1}; {D:.2f} s -> {dur(DST):.2f} s (atempo {ATEMPO})")

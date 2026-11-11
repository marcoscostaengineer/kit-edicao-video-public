#!/bin/bash
# Fecho do áudio das animações (25/10): normaliza para -14 LUFS (pico -1 dB) e baixa a música no último 1,2 s,
# para o vídeo não terminar com a trilha cortada seca. Vídeo copiado sem recodificar.
# Uso: bash finalizar_audio.sh entrada.mp4 saida.mp4
set -euo pipefail
in="$1"; out="$2"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
st=$(python3 -c "print(max(0, $dur - 1.2))")
FADE="afade=t=out:st=${st}:d=1.2"
medida=$(ffmpeg -nostats -i "$in" -af "${FADE},loudnorm=I=-14:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
read I TP LRA TH OFF <<< "$(echo "$medida" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")"
ffmpeg -v error -y -i "$in" -c:v copy -af "${FADE},loudnorm=I=-14:TP=-1:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true,aresample=48000" -c:a aac -b:a 192k -movflags +faststart "$out"

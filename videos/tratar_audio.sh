#!/bin/bash
# Tratamento de voz para Reels (15/10): limpa grave, tira chiado leve, dá presença, comprime e
# normaliza para -14 LUFS (volume de Reels/TikTok), pico verdadeiro -1 dB. Vídeo é copiado sem recodificar.
# Uso: bash tratar_audio.sh entrada.mp4 saida.mp4
set -euo pipefail
in="$1"; out="$2"
CADEIA="highpass=f=80,afftdn=nf=-25,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2"
medida=$(ffmpeg -nostats -i "$in" -af "$CADEIA,loudnorm=I=-14:TP=-1:LRA=9:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
mi=$(echo "$medida" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
read I TP LRA TH OFF <<< "$mi"
ffmpeg -v error -y -i "$in" -c:v copy -af "$CADEIA,loudnorm=I=-14:TP=-1:LRA=9:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" -c:a aac -b:a 192k -movflags +faststart "$out"

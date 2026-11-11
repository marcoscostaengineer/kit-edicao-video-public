#!/bin/bash
# "Whoosh visual" num movimento de câmera (15/10): rastro de movimento horizontal + desfoque lateral
# forte no meio do giro + leve zoom de impulso, com o som de whoosh junto. Não corta nem muda a duração.
# Uso: bash whoosh_visual.sh entrada.mp4 saida.mp4 <início_do_giro> <fim_do_giro>
set -euo pipefail
in="$1"; out="$2"; A="$3"; B="$4"
M=$(python3 -c "print(($A+$B)/2)"); MD=$(python3 -c "print(($B-$A)/2)")
WH="$(cd "$(dirname "$0")/.." && pwd)/.claude/skills/ghost-editor/library/sfx/whoosh-2.wav"
Z="1+0.10*max(0\,1-abs(t-$M)/$MD)"
DL=$(python3 -c "print(int(($A-0.05)*1000))")
ffmpeg -v error -y -i "$in" -i "$WH" -filter_complex "
[0:v]format=gbrp,
avgblur=sizeX=36:sizeY=1:enable='between(t,$M-0.12,$M+0.12)',
avgblur=sizeX=14:sizeY=1:enable='between(t,$A,$B)',
scale=w='trunc(iw*($Z)/2)*2':h='trunc(ih*($Z)/2)*2':eval=frame,crop=1080:1920,format=yuv420p[v];
[1:a]volume=0.45,adelay=$DL|$DL[w];
[0:a][w]amix=inputs=2:duration=first:normalize=0[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k "$out"

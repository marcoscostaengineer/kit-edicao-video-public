#!/bin/bash
# Transição de "zoom com flash" num corte de câmera (15/10): ±0,15 s em volta do corte a imagem
# avança num zoom rápido com desfoque e um clarão, e volta já no ângulo novo; whoosh baixinho junto.
# Não muda a duração nem a sincronia com a voz.  Uso: bash transicao_zoom.sh entrada.mp4 saida.mp4 <segundo_do_corte>
set -euo pipefail
in="$1"; out="$2"; T="$3"; D=0.15
WH="$(cd "$(dirname "$0")/.." && pwd)/.claude/skills/ghost-editor/library/sfx/whoosh-2.wav"
Z="1+0.28*max(0\,1-abs(t-$T)/$D)"
ffmpeg -v error -y -i "$in" -i "$WH" -filter_complex "
[0:v]scale=w='trunc(iw*($Z)/2)*2':h='trunc(ih*($Z)/2)*2':eval=frame,crop=1080:1920,
gblur=sigma=14:enable='between(t,$T-$D,$T+$D)',
eq=brightness='0.22*max(0\,1-abs(t-$T)/0.09)':eval=frame[v];
[1:a]volume=0.35,adelay=$(python3 -c "print(int(($T-0.18)*1000))")|$(python3 -c "print(int(($T-0.18)*1000))")[w];
[0:a][w]amix=inputs=2:duration=first:normalize=0[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k "$out"

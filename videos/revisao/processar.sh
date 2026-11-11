#!/bin/bash
# Gravação nova -> Sala de revisão, de ponta a ponta.
# Uso: bash processar.sh <arquivo.MOV> <CODIGO do roteiro, ex. P1> [look, padrão cinema]
#  1) HDR do iPhone -> SDR 1080x1920 (avconvert)   2) recorte de apoio por IA   3) chroma + fundo preto + look
#  4) os seis looks num trecho de 15 s             5) transcrição               6) importa para projeto.json
set -euo pipefail
MOV="$1"; COD="$2"; LOOK="${3:-cinema}"
AQUI="$(cd "$(dirname "$0")" && pwd)"; RAIZ="$(dirname "$AQUI")"
NOME="$(basename "${MOV%.*}")"; PASTA="$RAIZ/gravacoes/$COD-$NOME"; mkdir -p "$PASTA/looks"
KIT="$(cd "$AQUI/../.." && pwd)"; HF="$KIT/node_modules/.bin/hyperframes"; [ -x "$HF" ] || HF=$(ls ~/.npm/_npx/*/node_modules/.bin/hyperframes 2>/dev/null | tail -1)
echo "1/6 convertendo para SDR";   nice -n 10 avconvert --source "$MOV" --preset Preset1920x1080 --output "$PASTA/sdr.mov" --replace >/dev/null
ffmpeg -v error -y -i "$PASTA/sdr.mov" -vf "scale=1080:1920,fps=30" -c:v libx264 -crf 14 -preset veryfast -c:a aac "$PASTA/trecho.mp4"
echo "2/6 recorte de apoio (IA)";  nice -n 10 "$HF" remove-background "$PASTA/trecho.mp4" -o "$PASTA/trecho-matte.mov" >/dev/null 2>&1
echo "3/6 chroma + preto + $LOOK"; PASTA="$PASTA" LOOK="$LOOK" nice -n 10 python3 "$AQUI/recortar.py" >/dev/null
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$PASTA/trecho.mp4"); INI=$(python3 -c "print(max(0, round($DUR/2 - 7.5, 1)))")
echo "4/6 seis looks (15 s a partir de $INI s)"
for L in neutro comercial dourado cinema clinico editorial; do
  PASTA="$PASTA" LOOK=$L INI=$INI DUR=15 SAIDA="looks/$L.mp4" nice -n 10 python3 "$AQUI/recortar.py" >/dev/null &
done; wait
echo "5/6 transcrevendo";          python3 "$KIT/.claude/skills/ghost-editor/scripts/transcribe.py" "$PASTA/trecho.mp4" --out "$PASTA/words.json" --lang pt >/dev/null 2>&1
echo "6/6 importando para a Sala"; REL="${PASTA#$RAIZ/}"
python3 "$AQUI/importar.py" "$COD" "$REL/preto-$LOOK.mp4" --palavras "$REL/words.json" --looks "$REL/looks"
echo "Pronto: http://localhost:8797/revisao/"

#!/bin/bash
# SessionStart: checagem rápida (sem rede) do que o kit precisa. A saída entra no contexto do Claude.
K="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
GE="$K/.claude/skills/ghost-editor"
falta=()
command -v ffmpeg >/dev/null || falta+=("ffmpeg")
command -v node   >/dev/null || falta+=("node")
[ -x "$K/node_modules/.bin/hyperframes" ] || falta+=("hyperframes/puppeteer (npm install)")
command -v whisper >/dev/null || [ -n "$WHISPER" ] || falta+=("whisper")
python3 -c "import cv2, numpy, PIL" 2>/dev/null || falta+=("opencv/numpy/pillow (pip)")
[ -f "$GE/library/models/face_detection_yunet_2023mar.onnx" ] || falta+=("modelo de rosto YuNet")
n=$(ls "$GE"/library/sfx/*.wav 2>/dev/null | wc -l | tr -d ' '); [ "$n" -ge 30 ] || falta+=("biblioteca de SFX ($n arquivos)")
ls "$GE"/library/music/*.mp3 >/dev/null 2>&1 || falta+=("trilhas de música")

if [ ${#falta[@]} -eq 0 ]; then
  echo "Kit de vídeo: ambiente completo (ffmpeg, HyperFrames, whisper, OpenCV, SFX, música, YuNet)."
else
  lista=$(printf "%s, " "${falta[@]}"); echo "Kit de vídeo: FALTA ${lista%, }. Antes de editar, rode /setup (ou bash setup.sh) e avise a pessoa."
fi
chaves=""
grep -qs '^GEMINI_API_KEY=.' "$GE/.env" || [ -n "$GEMINI_API_KEY" ] || chaves+=" Gemini"
grep -qs '^ELEVENLABS_API_KEY=.' "$GE/.env" || [ -n "$ELEVENLABS_API_KEY" ] || chaves+=" ElevenLabs"
[ -n "$chaves" ] && echo "Chaves opcionais ausentes:$chaves (só b-roll/estudo de referência e voz por API precisam)."
proj=$(find "$K/videos" -mindepth 1 -maxdepth 1 -type d -newer "$K/CLAUDE.md" 2>/dev/null | grep -vE '/(revisao|modelo-take|primeira-consulta|caso-antes-depois)$' | xargs -n1 basename 2>/dev/null | head -5 | tr '\n' ' ')
[ -n "$proj" ] && echo "Projetos em videos/: $proj"
exit 0

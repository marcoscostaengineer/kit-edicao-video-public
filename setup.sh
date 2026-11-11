#!/bin/bash
# Puxa tudo que o kit precisa numa máquina nova (macOS). Idempotente: pode rodar de novo à vontade.
# Uso: bash setup.sh            (tudo)
#      bash setup.sh --global   (também liga as skills em ~/.claude/skills, para usar fora deste repo)
set -uo pipefail
K="$(cd "$(dirname "$0")" && pwd)"; cd "$K"
GE="$K/.claude/skills/ghost-editor"
passo() { printf "\n== %s\n" "$1"; }
aviso=()

passo "1/6 ferramentas do sistema (Homebrew)"
if command -v brew >/dev/null; then
  for f in ffmpeg node yt-dlp; do command -v "$f" >/dev/null || brew install "$f"; done
else
  for f in ffmpeg node; do command -v "$f" >/dev/null || aviso+=("$f ausente e sem Homebrew: instale o brew em https://brew.sh e rode de novo"); done
fi

passo "2/6 pacotes Python"
PIP=(python3 -m pip install -q -r requirements.txt)
"${PIP[@]}" 2>/dev/null || "${PIP[@]}" --user 2>/dev/null || {
  echo "pip recusou (ambiente gerenciado). Criando .venv do kit."
  python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt \
    && aviso+=("pacotes Python ficaram em .venv: rode 'source .venv/bin/activate' antes do claude (ou use o python da .venv)")
}
command -v whisper >/dev/null || [ -x .venv/bin/whisper ] || {
  ub="$(python3 -m site --user-base 2>/dev/null)/bin"
  [ -x "$ub/whisper" ] && aviso+=("whisper instalado em $ub: ponha no PATH (export PATH=\"$ub:\$PATH\")") || aviso+=("whisper não ficou no PATH")
}

passo "3/6 HyperFrames + puppeteer (npm, local no repo)"
npm install --silent --no-audit --no-fund || aviso+=("npm install falhou")
./node_modules/.bin/hyperframes --version >/dev/null 2>&1 || aviso+=("hyperframes não respondeu")
# o render baixa o chrome-headless-shell em ~/.cache/hyperframes na primeira vez; forçamos agora
[ -d ~/.cache/hyperframes/chrome ] || ./node_modules/.bin/hyperframes doctor >/dev/null 2>&1 || true

passo "4/6 biblioteca do ghost-editor (SFX, música, memes)"
python3 "$GE/scripts/library_restore.py" || aviso+=("library_restore falhou: rode python3 $GE/scripts/library_restore.py")

passo "5/6 modelo de rosto (YuNet)"
M="$GE/library/models/face_detection_yunet_2023mar.onnx"
[ -f "$M" ] || { mkdir -p "$(dirname "$M")"; curl -fsSL -o "$M" \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx || aviso+=("download do YuNet falhou"); }

passo "6/6 chaves e skills globais"
[ -f "$GE/.env" ] || { cp .env.example "$GE/.env"; echo "criado $GE/.env (preencha as chaves que for usar)"; }
if [ "${1:-}" = "--global" ]; then
  mkdir -p ~/.claude/skills
  for s in "$K"/.claude/skills/*/; do n=$(basename "$s"); d=~/.claude/skills/$n
    if [ -e "$d" ] && [ ! -L "$d" ]; then aviso+=("$d já existe como pasta real: mantido"); else ln -sfn "${s%/}" "$d"; echo "ligado $d"; fi
  done
fi

echo; bash "$GE/scripts/doctor.sh"
if [ ${#aviso[@]} -gt 0 ]; then echo; echo "Atenção:"; printf '  - %s\n' "${aviso[@]}"; fi
echo; echo "Pronto. Abra o Claude Code nesta pasta: cd \"$K\" && claude"

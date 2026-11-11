#!/bin/bash
# Liga o kit no Claude Code e restaura a biblioteca de mídia do ghost-editor.
set -euo pipefail
K="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.claude/skills
for par in "ghost-editor:$K/ghost-editor" "video-capitulo-ebook:$K/skills/video-capitulo-ebook"; do
  nome="${par%%:*}"; alvo="${par#*:}"; dest=~/.claude/skills/$nome
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then echo "já existe $dest (pasta real) — mantido; apague ou renomeie para ligar o kit"; continue; fi
  ln -sfn "$alvo" "$dest"; echo "ligado $dest -> $alvo"
done
python3 "$K/ghost-editor/scripts/library_restore.py" || echo "aviso: library_restore falhou (SFX/música); rode de novo depois"
bash "$K/ghost-editor/scripts/doctor.sh" || true

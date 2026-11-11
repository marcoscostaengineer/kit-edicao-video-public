#!/usr/bin/env python3
"""PreToolUse (Bash): bloqueia comando que apaga ou sobrescreve gravação original ou voz gerada.

A gravação de câmera (.MOV em fonte/) é o único arquivo que não se regenera; voz do ElevenLabs custa crédito.
Mover para a Lixeira (mv ... ~/.Trash/) continua permitido.
"""
import json, re, sys

try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    sys.exit(0)

APAGA = r"(\brm\b|\bunlink\b|\btruncate\b|find\b[^|;]*-delete|git\s+clean)"
PROTEGIDO = r"(\.mov\b|/fonte(/|\b)|/voice(/|\b)|\bfonte/|\bvoice/)"
SOBRESCREVE = r"(>\s*\S*(\.mov|/fonte/|/voice/)|ffmpeg[^;|&]*-y[^;|&]*\s\S*/fonte/\S+\s*$)"

for parte in re.split(r"&&|\|\||;|\n", cmd):
    p = parte.strip()
    if "~/.Trash" in p or "/.Trash/" in p:
        continue
    if (re.search(APAGA, p) and re.search(PROTEGIDO, p, re.I)) or re.search(SOBRESCREVE, p, re.I):
        print("Bloqueado pelo kit: este comando apaga ou sobrescreve gravação original (fonte/, .MOV) ou voz gerada (voice/). "
              "Se for mesmo para descartar, mova para a Lixeira (mv <arquivo> ~/.Trash/) ou peça para a pessoa apagar.",
              file=sys.stderr)
        sys.exit(2)
sys.exit(0)

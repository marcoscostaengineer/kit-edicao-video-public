---
description: Instala e confere tudo que o kit precisa (ffmpeg, Node, Python, HyperFrames, whisper, SFX, modelo de rosto)
---
Rode `bash setup.sh` na raiz do repo (em segundo plano se demorar) e depois `bash .claude/skills/ghost-editor/scripts/doctor.sh`.
Mostre só o que ficou faltando e o comando para resolver cada item. Não instale nada com `sudo`.
Se faltar chave (Gemini/ElevenLabs), diga que é opcional e onde fica (`.claude/skills/ghost-editor/.env`, modelo em `.env.example`) — nunca peça a chave no chat.

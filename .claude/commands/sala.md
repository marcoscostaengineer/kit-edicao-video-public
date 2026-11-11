---
description: Abre a Sala de revisão (timeline das tomadas para marcar fica/sai/ajuste)
---
Suba `python3 videos/revisao/servidor.py` (config `sala-revisao` em `.claude/launch.json`, porta 8797) e abra http://localhost:8797/revisao/.
Se `videos/revisao/projeto.json` não existir, diga que a Sala está vazia e que `bash videos/revisao/processar.sh <MOV> <CÓDIGO>` a alimenta.
Depois que a pessoa marcar, leia `videos/revisao/decisoes.json` e resuma por vídeo o que fica, o que sai e os ajustes.

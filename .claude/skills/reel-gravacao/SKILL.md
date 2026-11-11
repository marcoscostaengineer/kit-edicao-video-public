---
name: reel-gravacao
description: Fluxo completo de Reels/Shorts a partir de gravação real de celular (pessoa falando para a câmera) — do .MOV à Sala de revisão, take com story/facts, reenquadramento seguindo o rosto, montagem, tratamento de áudio e conferência. Use quando chegar uma gravação nova, quando pedirem "edita esse vídeo", "monta o Reels", "recorta as tomadas" ou para refazer um take reprovado.
---

# Reel a partir de gravação real

Motor por baixo: skill `ghost-editor` (transcrição, `prep.sh`, `build.mjs`, legenda, SFX). Este fluxo soma o que a casa
aprendeu: recorte do 4K seguindo o rosto, Sala de revisão, travas de qualidade. Regras em `docs/regras.md`.

## Pastas

```
videos/<projeto>/fonte/        .MOV original (nunca apagar; o hook bloqueia)
videos/<projeto>/take-<n>/     reel.json, story.md, facts.json, assets/, build/
videos/<projeto>/saida/        MP4 aprovado, nome com data
```

## Passo a passo

1. **Entrada.** Copie o `.MOV` para `videos/<projeto>/fonte/`.
2. **Sala de revisão** (quando houver várias tomadas): `bash videos/revisao/processar.sh videos/<projeto>/fonte/<arq>.MOV <CÓDIGO>`
   → SDR, recorte de apoio, 6 looks, transcrição e importação. Suba a Sala (`/sala`) e peça para marcar fica/sai/ajuste.
   **Leia `videos/revisao/decisoes.json` antes de montar** — o ajuste escrito ali é pedido.
3. **História primeiro.** Delegue ao agente `diretor-de-video`: `story.md` + `facts.json` no take (modelo em `videos/modelo-take/`).
4. **Prep do take** (ghost-editor): `bash .claude/skills/ghost-editor/scripts/prep.sh <fonte> <take>` e transcrição
   (`scripts/transcribe.py ... --lang pt`). Escolha das tomadas: `references/take-selection.md` do ghost-editor.
5. **Enquadrar do 4K:** `python3 videos/enquadrar.py <ORIGINAL.MOV> <take>` — olhos a ~0,30 (0,40 com caixa no topo).
   Confira uma folha de quadros do `assets/talk.mp4` antes de seguir; apague `assets/talk-matte.webm` se existir.
6. **reel.json:** estilo, legenda (`{"style":"clean","group":1,"y":0,"size":74,"highlight":"#FFFFFF"}`), beats e cenas.
   Formato em `.claude/skills/ghost-editor/references/reel-json.md`.
7. **Montar:** `python3 videos/montar.py <take> <nome> "<pergunta da caixa>" <segundo>` (série caixa de perguntas) ou, fora
   da série, `node .claude/skills/ghost-editor/scripts/build.mjs <take>` + render HyperFrames + `bash videos/tratar_audio.sh in out`.
   O `montar.py` já roda render → áudio (−14 LUFS) → `conferir.py` e só copia para `saida/` o que passa.
8. **Travas:** agente `conferente` (mecânico) e agente `leitor-sem-som` com **só** `build/conferir.jpg`. Frase dele ≠
   "Em uma frase" do `story.md` → volta ao passo 6.
9. **Entrega:** caminho absoluto do MP4 em `saida/`, a folha de quadros e a tabela do conferente.

## Armadilhas que já custaram retrabalho
- Prep do ghost-editor sozinho deixa teto demais e a pessoa pequena: sempre `enquadrar.py`.
- Copiar posição de outro take (y fixo) põe o queixo onde entra a caixa: medir olhos e queixo em cada gravação.
- `concat` com trechos mono e estéreo deixa a voz em câmera lenta: tudo `-ac 2 -ar 48000`.
- Legenda com `group` 3 vira duas linhas no peito: é `group` 1, colada ao queixo.

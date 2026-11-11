# Kit de edição de vídeo

Tudo que roda a edição de Reels, animações e vídeos de capítulo do jeito que fazemos no Cleef: o motor
(ghost-editor), as ferramentas de enquadramento, montagem e conferência, a Sala de revisão, o molde de
animação e a skill de vídeo de capítulo de ebook. Só código e regras — nenhuma gravação, voz clonada,
foto de pessoa ou chave de API entra aqui.

## O que tem

| Pasta | O que faz |
|---|---|
| `ghost-editor/` | Motor de edição (fork local de [kurbaitaev/ghost-editor](https://github.com/kurbaitaev/ghost-editor), MIT) com os ajustes da casa: área segura do Instagram (`scripts/lib/safezone.mjs`), cenas em camadas (`references/layered-scenes.md`, `scripts/cut_parts.py`) e a receita mármore (`recipes/marble-explainer/`). Lê `SKILL.md` e `docs/PLAYBOOK.md`. |
| `videos/` | Ferramentas da linha de Reels com gravação real. Mesmo layout da pasta original, para os caminhos relativos funcionarem. |
| `videos/revisao/` | Sala de revisão: HTML local com timeline por vídeo (porta 8797). `processar.sh` leva um `.MOV` do celular até a Sala. |
| `videos/modelo-take/` | `story.md` + `facts.json`: todo take abre por eles; o `montar.py` recusa take sem os dois. |
| `molde-animacao/` | Molde de animação narrada (ElevenLabs) presa à palavra: `build.py` → `index.html` → render pelo HyperFrames. Exemplo real (R13); os `assets/`, `voice/` e `gemini/` ficam fora — gere os seus. |
| `skills/video-capitulo-ebook/` | Skill de vídeo 16:9 de capítulo de ebook no estilo mármore: `scripts/novo_capitulo.py` monta a pasta do capítulo. |
| `docs/regras.md` | As regras que viraram lei depois de vídeo reprovado (área segura, enquadramento, legenda, mixagem, camadas). **Leia antes de editar.** |
| `docs/framework-diretor-de-motion-2026.md` | Framework de direção de motion (story → fatos → quadro → som → leitura sem som). |

## Instalação (macOS)

```bash
brew install ffmpeg node python@3.12
pip3 install opencv-python numpy openai-whisper google-genai
bash install.sh
```

`install.sh` liga `ghost-editor/` e `skills/video-capitulo-ebook/` em `~/.claude/skills/` (symlink), restaura a
biblioteca de SFX e música (`ghost-editor/scripts/library_restore.py`) e roda o `doctor.sh` do ghost-editor.
O modelo de rosto (YuNet) baixa sozinho no primeiro `face_track.py`. O HyperFrames (render) roda via `npx hyperframes`
e baixa o próprio Chrome headless.

Chaves opcionais, em `ghost-editor/.env` (ignorado pelo git):

```
GEMINI_API_KEY=...       # b-roll e estudo de referência
ELEVENLABS_API_KEY=...   # narração dos explainers
```

## Fluxos

**Reel com gravação real (talking head)**

1. `bash videos/revisao/processar.sh <arquivo.MOV> <CÓDIGO>` → SDR, recorte, looks, transcrição e importação para a Sala.
2. `python3 videos/revisao/servidor.py` e abra `http://localhost:8797/revisao/`; marque fica/sai/ajuste (vai para `decisoes.json`).
3. Copie `videos/modelo-take/` para o take e preencha `story.md` e `facts.json`.
4. `python3 videos/enquadrar.py <original-4K> <take>` — recorte seguindo o rosto, olhos a ~30% da altura.
5. `python3 videos/montar.py <take> <nome> "<pergunta>" <saida>` — build → render → `tratar_audio.sh` (−14 LUFS) → `conferir.py`. Só copia o que passa.
6. Antes de entregar: leitura sem som (alguém que não viu o roteiro reconta o vídeo só pela folha `build/conferir.jpg`).

**Animação narrada** — copie `molde-animacao/`, gere a voz, transcreva com
`whisper --model large-v3-turbo --language pt --word_timestamps True`, ajuste `build.py` (cada entrada presa a uma
palavra), rode e confira a área segura com `node area_segura_dom.mjs`.

**Vídeo de capítulo** — `python3 skills/video-capitulo-ebook/scripts/novo_capitulo.py <ebook> <NN> "<TÍTULO>"` e siga o `SKILL.md`.

## Estrutura de saída de um projeto

```
<projeto>/fonte/   gravação original (.MOV) — nunca apagar
<projeto>/build/   intermediários — descartável
<projeto>/saida/   MP4 final: <id>-<tema>-<variante>-AAAA-MM-DD.mp4
```

Mídia (`.mov`, `.mp4`, `.wav`, `.mp3`…) não entra no git: o `.gitignore` barra.

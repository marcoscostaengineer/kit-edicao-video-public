# Kit de edição de vídeo — harness

Neste repo você é o **editor de vídeo**: transforma gravação de celular, roteiro ou capítulo em vídeo
pronto para postar (Reels/Shorts 1080×1920 ou 16:9), com o padrão de qualidade das regras abaixo. Responda em
português do Brasil, direto: o que vai fazer, o que fez, o que reprovou.

@docs/regras.md

## O que já está carregado

| Peça | Onde | Para quê |
|---|---|---|
| Skill `ghost-editor` | `.claude/skills/ghost-editor/` | Motor: transcrição, melhor tomada, legenda por palavra, cenas, SFX, render (HyperFrames) |
| Skill `reel-gravacao` | `.claude/skills/reel-gravacao/` | Fluxo da gravação real: `.MOV` → Sala → take → enquadrar → montar → conferir |
| Skill `animacao-narrada` | `.claude/skills/animacao-narrada/` | Vídeo sem câmera: voz gerada + peças que se movem na palavra |
| Skill `video-capitulo-ebook` | `.claude/skills/video-capitulo-ebook/` | Capítulo de livro em 16:9, estilo mármore |
| Agente `diretor-de-video` | `.claude/agents/` | Storyboard, `story.md` e `facts.json` antes do primeiro quadro |
| Agente `conferente` | `.claude/agents/` | Roda as travas mecânicas (conferir.py, área segura, LUFS) e devolve passa/reprova |
| Agente `leitor-sem-som` | `.claude/agents/` | Olho novo: reconta o vídeo só pela folha de quadros |
| Comandos | `.claude/commands/` | `/setup`, `/novo-reel`, `/animacao`, `/capitulo`, `/conferir`, `/sala` |
| Hooks | `.claude/settings.json` | Checagem do ambiente ao abrir; trava contra apagar gravação original |

## Como trabalhar

1. **O quê antes do como.** Todo vídeo abre por `story.md` ("Em uma frase", gancho, blocos, final) e `facts.json`
   (cada frase da tela com origem). Sem os dois, `montar.py` recusa — e você também.
2. **Escolha o fluxo pela matéria-prima:** gravação de câmera → `reel-gravacao`; só roteiro/voz → `animacao-narrada`;
   capítulo de livro → `video-capitulo-ebook`; referência de edição que a pessoa gostou → `ghost-editor` (estudo de referência).
3. **Piloto antes do lote.** Um vídeo aprovado antes de replicar o molde para os outros.
4. **Nada chega à pessoa sem passar pelo `conferente` e pelo `leitor-sem-som`.** "Parece pronto" não é sinal; o
   script que sai 0 é. Reprovou: corrija e rode de novo, não entregue com ressalva.
5. **Entrega:** caminho absoluto do MP4 em `<projeto>/saida/`, a folha `build/conferir.jpg` e o que cada trava disse.

## Onde mora cada coisa

- Projetos de vídeo: `videos/<projeto>/` com `fonte/` (original, **nunca apagar**), `build/` (descartável) e `saida/` (final).
  Projetos ficam fora do git (só as ferramentas são versionadas).
- Roteiros e textos aprovados: `videos/<projeto>/roteiro.md`. Voz gerada: `<projeto>/anim/voice/` (custa crédito, não apagar).
- Chaves: `.claude/skills/ghost-editor/.env` (modelo em `.env.example`). Nunca em código, nunca no chat.

## Limites

- Não invente fato, número, depoimento, preço ou promessa na tela: tudo vem da fala gravada ou de fonte citada.
- Não gere imagem de pessoa real sem foto de referência aprovada; foto real só de pessoa e capa de livro.
- Não suba mídia para o git (o `.gitignore` barra; não force).
- Gerar voz ou imagem em serviço pago (ElevenLabs, Gemini): diga quanto vai gerar antes.

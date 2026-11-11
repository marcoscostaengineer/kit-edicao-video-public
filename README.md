# Kit de edição de vídeo

Harness de Claude Code para editar vídeo: abra o Claude Code nesta pasta e ele já carrega o editor, as skills, os
agentes, os comandos e as travas de qualidade. Reels/Shorts de gravação real, animação narrada presa à palavra e vídeo
de capítulo de ebook — com as regras que a gente aprendeu reprovando vídeo.

## Começar (máquina nova)

```bash
gh repo clone antonioddiniz/kit-edicao-video && cd kit-edicao-video && bash setup.sh && claude
```

O `setup.sh` instala ffmpeg/Node/yt-dlp (Homebrew), os pacotes Python (`requirements.txt`), o HyperFrames e o puppeteer
(`package.json`, local no repo), restaura SFX e trilhas, baixa o modelo de rosto e cria o `.env` das chaves. Pode rodar de novo
quando quiser. `bash setup.sh --global` também liga as skills em `~/.claude/skills/` para usar fora do repo.

Ao abrir o Claude Code aqui, o hook de início confere o ambiente e avisa o que falta.

## O que carrega sozinho

| Peça | Onde | Faz |
|---|---|---|
| `CLAUDE.md` + `docs/regras.md` | raiz | Persona do editor, fluxo e as regras (área segura, enquadramento, legenda, áudio, animação) |
| Skill `ghost-editor` | `.claude/skills/` | Motor: transcrição, tomadas, legenda por palavra, cenas, SFX, render. Fork de [kurbaitaev/ghost-editor](https://github.com/kurbaitaev/ghost-editor) (MIT) com os ajustes da casa |
| Skill `reel-gravacao` | `.claude/skills/` | `.MOV` → Sala de revisão → take → enquadrar do 4K → montar → conferir |
| Skill `animacao-narrada` | `.claude/skills/` | Voz + peças geradas que se movem na palavra, render em HTML |
| Skill `video-capitulo-ebook` | `.claude/skills/` | Capítulo inteiro em 16:9, estilo mármore |
| Agentes | `.claude/agents/` | `diretor-de-video` (história e fatos antes do quadro), `conferente` (travas mecânicas), `leitor-sem-som` (olho novo) |
| Comandos | `.claude/commands/` | `/setup`, `/novo-reel`, `/animacao`, `/capitulo`, `/conferir`, `/sala` |
| Hooks | `.claude/settings.json` | Início: checa o ambiente. Bash: bloqueia apagar `.MOV`, `fonte/` e `voice/` |
| Permissões | `.claude/settings.json` | ffmpeg, whisper, HyperFrames e os scripts do kit sem pedir confirmação |
| Sala de revisão | `.claude/launch.json` | `sala-revisao` na porta 8797 |

## Ferramentas

| Pasta | O quê |
|---|---|
| `videos/` | `enquadrar.py`, `montar.py`, `conferir.py`, `tratar_audio.sh`, `finalizar_audio.sh`, medidores de área segura, transições |
| `videos/revisao/` | Sala de revisão (servidor, importação de tomadas, `processar.sh`) |
| `videos/modelo-take/` | `story.md` + `facts.json` — todo vídeo começa por eles |
| `molde-animacao/` | Molde de animação narrada (`build.py`, recorte de grades, pausas, área segura no DOM) |
| `docs/` | Regras e framework de direção de motion |

## Onde ficam os vídeos

```
videos/<projeto>/fonte/   original da câmera — nunca apagar (o hook bloqueia)
videos/<projeto>/build/   intermediários — descartável
videos/<projeto>/saida/   MP4 final: <id>-<tema>-<variante>-AAAA-MM-DD.mp4
```

Projetos e mídia ficam fora do git; só ferramentas e regras são versionadas. Chaves (Gemini, ElevenLabs) em
`.claude/skills/ghost-editor/.env`, nunca no repo.

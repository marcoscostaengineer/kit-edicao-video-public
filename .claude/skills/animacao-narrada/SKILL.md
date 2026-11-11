---
name: animacao-narrada
description: Vídeo vertical sem câmera — voz gerada (ElevenLabs) ou gravada, com imagens geradas recortadas em partes que se movem presas a cada palavra da fala, renderizado em HTML pelo HyperFrames. Use para "faz uma animação", explicação de procedimento, curiosidade, vídeo derivado de comentário, ou quando não há gravação da pessoa.
---

# Animação narrada presa à palavra

Molde em `molde-animacao/` (exemplo real: `build.py` de um Reel de 60 s). Receitas irmãs no ghost-editor:
`recipes/marble-explainer/` (estátuas de mármore) e `references/layered-scenes.md` (cena em camadas).

## Passo a passo

1. **Projeto:** `mkdir -p videos/<projeto> && cp -R molde-animacao videos/<projeto>/anim` e `mkdir -p videos/<projeto>/anim/{assets/img,voice,gemini,build}`.
2. **História:** agente `diretor-de-video` → `story.md`, `facts.json`, storyboard (palavra que dispara · peça · texto) e lista de peças.
3. **Voz:** gere no ElevenLabs (`.claude/skills/ghost-editor/scripts/tts_elevenlabs.py`, chave no `.env`) ou pelo site; salve em `anim/voice/`.
   Passou do teto de 60 s? `python3 apertar_pausas.py voice/in.mp3 voice/out.wav [atempo]` encolhe só os silêncios.
4. **Palavras:** `whisper voice/out.wav --model large-v3-turbo --language pt --word_timestamps True --output_format json --output_dir build`.
5. **Peças:** gere grades no Gemini (várias variações numa imagem, fundo verde chroma) em `gemini/`; fatie com
   `python3 recortar.py gemini/<grade>.jpg 2x2 nome1,nome2,nome3,nome4` → `assets/img/`. Partes de um objeto: `cut_parts.py` do ghost-editor.
6. **build.py:** troque o JSON de palavras e os elementos. Cada entrada usa `W("palavra")` — nunca segundos fixos. Imagem
   nunca parada; cada slide com gesto próprio; ✓/✕ com texto (nunca só cor).
7. **Render:** `python3 build.py && npx hyperframes lint && node area_segura_dom.mjs index.html && npx hyperframes render -o build/<id>.mp4`.
8. **Áudio final:** `bash videos/finalizar_audio.sh build/<id>.mp4 ../saida/<id>-<tema>-AAAA-MM-DD.mp4` (−14 LUFS, fade de 1,2 s).
9. **Travas:** `conferente` (área segura + LUFS + formato) e `leitor-sem-som` com uma folha de quadros
   (`ffmpeg -i <mp4> -vf "fps=1/2,scale=270:-1,tile=6x4" -frames:v 1 build/folha.jpg`).

## Ritmo e som
- Música fixa ~17 dB abaixo da voz, sem ducking. Um SFX por entrada é bem-vindo; duas músicas sobrepostas, não.
- Velocidade: acelerar o vídeo inteiro (`setpts`/`atempo`) e só depois pôr a música no andamento original.
- O fecho respira ~1,4 s e volta ao quadro de abertura (loop).

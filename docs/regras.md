# Regras de edição (cada uma nasceu de vídeo reprovado)

## Quadro vertical 1080×1920 — área segura do Instagram
- **Topo:** nenhum texto acima de y 290 (cabeçalho centrado em ~335). A barra do app cobre até ~270.
- **Base:** legenda e chips terminam até y 1480 (legenda centrada em ~1420). O perfil começa em ~1565.
- **Direita:** abaixo de y 1000, nenhum texto além de x 900 (coluna de curtir/comentar). Chip longo quebra em duas linhas (max-width 720).
- **Laterais:** 60 px de folga.
- Imagem pode passar por baixo da interface; **texto não**.
- **Medir, não olhar:** `area_segura_dom.mjs` percorre a timeline de 0,1 em 0,1 s e sai 1 se algo invadir. Legenda que passou: `.cap { left: 480px; max-width: 840px; font-size: 56px }`, grupo quebra antes de 22 caracteres.

## Enquadramento de gravação real
- Sempre reenquadrar do **original 4K** seguindo o rosto (`enquadrar.py`) antes de montar: zoom ~1,4–1,6, olhos a ~30% da altura (~40% quando há caixa de pergunta no topo).
- Pessoa grande sem cena: olhos ~30%, caixas de texto no peito com folga abaixo do queixo. Medir olhos e queixo com o YuNet em cada gravação.
- A pessoa aparece no 1º segundo e meio e na capa (1º quadro). `conferir.py` reprova capa sem rosto ou chapada.

## Legenda
- Centro, colada logo abaixo do queixo, **uma palavra por vez**: `captions = {"style": "clean", "group": 1, "y": 0, "size": 74, "highlight": "#FFFFFF"}`.
- Roupa branca: trocar sombra por contorno preto de 12 px (`-webkit-text-stroke` + `paint-order`).

## Áudio
- Voz final a **−14 LUFS** (`tratar_audio.sh`).
- Música baixa e **fixa** (~17 dB abaixo da voz), sem ducking nem loudnorm dinâmico.
- Concat do ffmpeg: todos os trechos com `-ac 2 -ar 48000`; mono com estéreo faz a voz tocar em câmera lenta.
- Gravação real com voz gerada: limpar a real (Voice Isolator) e igualar volume por trecho.
- Acelerar (ex.: 1,15×) com `setpts`/`atempo` no vídeo inteiro e só depois pôr a música no andamento original.

## Animação
- Imagem gerada **nunca fica parada**: gerar em vista explodida, recortar com `cut_parts.py`, cada parte se move numa palavra da fala (`ghost-editor/references/layered-scenes.md`).
- Ilustração muda de gesto por slide; a mesma peça no mesmo canto em todo quadro vira careta.
- Storyboard e lista de peças primeiro, um piloto antes do lote.
- Foto real só de pessoa e capa de livro; objeto e cena ficam no estilo gerado.

## Antes de entregar
1. `story.md` e `facts.json` preenchidos: cada frase da tela tem origem (fala ou fonte), sem promessa nem preço inventado.
2. `conferir.py` aprovado (enquadramento, capa, legenda, área segura, LUFS).
3. **Leitura sem som:** alguém que não viu o roteiro reconta a mensagem só pela folha de quadros; se não bater com "Em uma frase" do `story.md`, volta.
4. Nunca informação só por cor: ✓/✕, texto ou padrão junto.

## Pastas
- `fonte/` (.MOV original, nunca apagar) · `build/` (descartável) · `saida/` (MP4 final com data no nome).
- Mídia fora do git: o repo do Cleef chegou a 36 GB de pacotes temporários por vídeo versionado.

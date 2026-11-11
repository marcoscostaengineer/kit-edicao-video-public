---
name: video-capitulo-ebook
description: "Transformar um capítulo de ebook do Antonio em vídeo 16:9 narrado com a voz dele (ElevenLabs) e animado no estilo mármore da convexa, peças que se movem na palavra. Use para: 'faz o vídeo do capítulo N', vídeo do ebook para YouTube, refazer ou ajustar versão de vídeo de capítulo, mesmo processo do cap. 01 do Inovação Antifrágil."
argument-hint: "ebook + número do capítulo (ex.: inovacao-antifragil 02)"
user-invocable: true
---
# Vídeo de capítulo de ebook (mármore 16:9)

O vídeo é o capítulo em outro formato, não um teaser. Exemplo resolvido, fonte de verdade do código:
`vida/negocios/conteudo-lai/ebooks/inovacao-antifragil/video/cap01/` (v10 entregue, 9min15). Leia o `storyboard.md` dele
antes do primeiro vídeo da sessão.

## Quando usar
- Antonio pede o vídeo de um capítulo de ebook (Inovação Antifrágil ou outro livro dele).
- Nova versão de um vídeo de capítulo já feito (roteiro, peças, trilha, ritmo).
- Short vertical saído do capítulo: o roteiro nasce aqui; a montagem vertical segue `ghost-editor`.

## Procedimento
1. **Pasta.** `python3 .github/skills/video-capitulo-ebook/scripts/novo_capitulo.py <ebook> <NN> "<TÍTULO>"` cria
   `<ebook>/video/capNN/` com o motor, capa e fecho prontos. Ele não sobrescreve pasta existente.
2. **Roteiro** (`roteiro.txt`): o capítulo inteiro, parte por parte, com os casos completos e "Parte um." falado como
   cartão. Voz professor próximo (`perfil/voz-escrita-publica.md`, seção Voz falada; objeção "Ah, Antonio, mas..."),
   número por extenso. Cole o roteiro inteiro no chat num bloco só. Fontes vão para `fontes.md`.
3. **Voz:** Antonio gera no ElevenLabs (voz clonada dele) e salva `audio/antonio-original.mp3`. Ele faz; você espera.
4. **Whisper:** `whisper audio/antonio-original.mp3 --model medium --language pt --word_timestamps True --output_format json --output_dir audio`
   e renomeie para `audio/antonio-original.json`. Erro de grafia recorrente entra no `JUNTA` do `build.py`.
5. **Storyboard** (`storyboard.md`): tabela fala → âncoras → camadas e movimento → chip, uma linha a cada 2 a 5 s.
   Liste as peças novas; o resto vem do acervo `vida/negocio-dentistas/marca-convexa/marmore/elementos/v2/`.
6. **Peças:** Gemini web, modelo Pro, conversa nova, cartela em grade em vista explodida
   (`references/pecas-e-gramatica.md`); recorte com `marmore/recortar_partes.py`. Pessoa real e capa de livro: foto de
   biblioteca em `fotos/` com crédito em `fotos/creditos.json`.
7. **Cenas** (`cenas.py`): na ordem da fala, âncora `D("palavra")` com cursor. Ajudantes e vocabulário em
   `references/pecas-e-gramatica.md`.
8. **Render:** `python3 build.py`, depois em `anim/`: `npx hyperframes lint && npx hyperframes render -q draft -o build/draft.mp4`.
   Final sem `-q draft`, nome `build/capNN-vK.mp4`.
9. **Revisão:** `python3 vazios.py <mp4>` (palco vazio ≥ 1,5 s), `python3 folha.py <mp4> t0 t1 passo saida.jpg`
   (folha de quadros) e **teste sem som por agente novo**: ele reconta o argumento só pelas imagens e chips.
10. **Trilha e ritmo:** preencha `blocos.json` (uma faixa por parte, revezando) e rode
    `python3 trilha.py anim/build/capNN-vK.mp4 <ebook>-capNN-vK.mp4 1.15`. Antes da primeira mixagem, mande amostra.
11. **Entrega:** caminho absoluto do MP4, `fontes.md` como descrição, capítulos do YouTube com minutagem já em 1,15×
    (modelo: `cap01/shorts/youtube.md`). Quem sobe é o Antonio. Atualize o `storyboard.md` (seção Estado).

## Saída padrão
- MP4 1920×1080 em `<ebook>/video/capNN/<ebook>-capNN-vK.mp4`, caminho absoluto na resposta.
- Roteiro colado no chat; `fontes.md` pronto para a descrição; `youtube.md` com título, descrição e minutagem.
- Status: vazios.py (nº de trechos), teste sem som (passou ou não) e o que ficou pendente.

## Regras
- Cobrir o capítulo todo. A tese central fica, mesmo que o vídeo passe de 10 min.
- Peça gerada sempre se move: vista explodida, cada parte numa palavra. Revelação no ritmo da fala, nunca antes.
- Certo e errado = carimbo ✓/✕ mais chip, nunca só cor (Antonio é daltônico).
- Foto real só de pessoa e capa de livro, em quadro de papel com crédito; objeto e cena ficam no mármore.
- Música baixa e fixa, 17 dB abaixo da voz, sem ducking; uma faixa por vez, sem sobreposição; todos os efeitos ficam.
- Velocidade 1,15× no vídeo inteiro (imagem, voz e efeitos juntos); a música entra depois, no andamento original.
- Versão nova = arquivo novo (`-vK`); nunca sobrescreva a entregue.

## Armadilhas
- v1 de 4 min do cap. 01 cortou a tese (o cientista) e foi recusada: "quero ele bem documentado".
- Âncora em número, sigla ou nome estrangeiro falha (o whisper escreve "12%" ou "Shilhart"): ancore na palavra comum vizinha.
- Whisper pula fala curta como "Parte cinco": use `lacuna("palavra")` para achar o buraco.
- Dois `tl.set` no mesmo seletor em t=0 quebram o render: use `init()` uma vez.
- Música revezando com sobreposição soou como "várias músicas uma em cima da outra"; ducking soou como música "subindo" nas pausas.
- Trilha de lo-fi, drone e piano misturados e eletrônica genérica foram recusadas; a aprovada é o trio funk do Mixkit em `trilhas/aprovadas/`.
- Cortar efeitos sonoros (226 → 27) foi revertido a pedido dele.
- Gemini grudou parte na peça (lacre no frasco) e o download travou: refaça a parte por código (`.lacre` desenhado) em vez de insistir.
- 15 trechos vazios (59 s) na v2: rode `vazios.py` antes de mostrar; cartão de parte leva a peça da parte.

---
Status: experimental
Versao: v1
Ultima revisao: 2026-11-04

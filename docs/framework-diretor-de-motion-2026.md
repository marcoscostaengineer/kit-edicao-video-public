# Framework — diretor de motion em código (2026)

**Fonte:** prompt de "motion director" que circulou no X em out/2026, na linha do estúdio de vídeo em
código descrito por @francescoinweb3 (post de 2026-10-15, artigo "Build Your Own AI Production
Studio With Claude", 2026-10-10). Imagem trazida pelo Antonio em 2026-10-17. **Paráfrase própria**;
o texto original não está copiado aqui.

**Ressalva:** feito para filme de produto, showreel e explicador com motion pesado. Para o Reel de
falar para a câmera da Brenda, só as partes marcadas ★ se pagam; o resto é para peça de motion de
verdade (antes e depois animado, abertura da LAI, explicador).

---

## A ideia central
Um filme só está pronto quando se sustenta **ao lado da melhor referência do gênero**. Sem erro não
basta. Quem constrói não julga o próprio trabalho: um crítico de contexto limpo julga.

## 1. Briefing antes de tudo
Modo (showreel · produto · história de lançamento · explicador), assunto, quem assiste, **o que a
pessoa deve sentir/saber/fazer no último segundo**, duração e formatos, quadros por segundo (60 UI,
30 personagem, 24 artesanal), marca, **fonte dos fatos**, assets, estilo/referência, som, autonomia
(com ou sem parada nos marcos), ferramenta e assinatura final. Campo em branco: decidir e anotar o
porquê em `brief.md`.

## 2. Ofício (as regras de imagem)
1. ★ **O primeiro quadro é uma imagem pronta,** que funciona parada no feed; o gancho entra no 1º segundo.
2. **Continuidade:** um elemento atravessa as transições, e a transição é feita do próprio conteúdo;
   corte seco só quando tudo casa e no beat.
3. **Movimento vivo:** um movimento líder com secundários, velocidade que varia (chega devagar, sai
   rápido), nada parado de vez, toda ação com resultado visível.
4. ★ **Texto que se lê:** ~0,3 s por palavra (mínimo 0,7 s), com placa sobre imagem carregada; se a
   imagem já diz, corta a palavra.
5. **Via negativa:** layout que não se repete, 3D só onde explica espaço, nenhum efeito decorativo.

## 3. Áudio primeiro, imagem cortada nele
Música no clima e baixa; beats detectados num `timing.json` que comanda toda animação; efeito sonoro
só para evento real na tela; vozes com duas opções por personagem; ★ **mix a −14 LUFS, pico real ≤ −1 dBTP.**

## 4. Build
Tudo em código numa linha do tempo, fontes e assets locais, render quadro a quadro. Teste de 3–5 s
de ponta a ponta antes do trabalho real. Todo valor é função do número do quadro (sem timer, sem
aleatório sem semente). Recompor cada formato em vez de recortar. ★ 9:16 longe das zonas de interface.

## 5. Fluxo
Fatos travados (`facts.json`: cada frase, a frase exata da fonte, o link) → estudo das referências
→ 2–3 conceitos, escolher um, nomear três momentos-assinatura → storyboard que **se lê sem som** →
bíblia de estilo (≤ 6 cores) e três quadros de estilo → mapa de áudio → build + loop de crítica → entrega.

### A cadeia de arquivos (post de @francescoinweb3, 2026-10-17)
Não pedir "faça um vídeo". Seis trabalhos pequenos, **cada um gera um arquivo e o próximo começa dele**:
referência → `spec.md` (por que o vídeo de referência funciona: ritmo, primeiro movimento, cortes) ·
dados → `data.json` (cada número com a fonte ao lado) · história → `story.md` (uma ideia, um número
herói, três batidas, antes de qualquer movimento) · movimento → a cena em código · direção → notas em
português viram uma linha de timing · entrega → quadros parados conferidos contra o `spec` e os dados,
e só sai com aprovação. Ganho: cada etapa se confere sozinha, o defeito tem endereço (o arquivo), e
nada é sorteado de novo.

Na casa (take do Reel): `spec.md` ≈ `reference_study.py` do ghost-editor · `data.json` = `facts.json` ·
`story.md` = a pergunta da caixa + as 3 batidas · cena = `reel.json` + `index.html` (HyperFrames, não
Remotion) · direção = edição do `reel.json` · entrega = `conferir.py` + leitura sem som + seu ok.

## 6. Loop de crítica (o coração)
Um crítico **novo, que não viu nada da construção,** tira os próprios quadros (a cada 0,2 s, mais
denso nas transições), mede e devolve os problemas em ordem, com tempo, terminando em "publica" ou
"mais uma volta". Em todo render completo:
- ★ **Leitura sem som:** o crítico vê só uma folha de quadros muda e reconta a história.
- **Sincronia:** cada batida e cada frase a ≤ 1 quadro do `timing.json`.
- ★ **Checagem de fatos:** cada palavra rastreada até o `facts.json`.
- **Revisão do diretor:** crítica dura do que parece montado, lento ou genérico.

Corrige o maior problema, renderiza de novo, e um crítico novo reconfere tudo. Registro em
`ledger.md` com o número de antes e depois.

## 7. Régua de qualidade
Medido: duração, tamanho e fps exatos; primeiro quadro pronto; ≤ 1 s congelado a cada 30 s e nenhum
trecho parado > 0,5 s; contraste de texto ≥ 4,5:1, sem colisão, dentro das margens; cores da marca;
cortes a ≤ 1 quadro do beat; −14 LUFS sem clipping; entendido sem som; **nenhum fato inventado**
(depoimento, nota, preço, resultado, gente real) e todo gerado rotulado.
Julgado: um crítico poria ao lado da referência sem que parecesse mais fraco.

---

## Como a casa aplica (2026-10-17)

| ★ Item | Onde vive |
|---|---|
| Primeiro quadro pronto | `vida/consultorio-brenda/videos/conferir.py`: reprova a capa sem a Brenda ou em branco |
| −14 LUFS / pico real | `tratar_audio.sh` + `conferir.py` |
| Texto e zonas seguras | `conferir.py` (legenda × rosto, área segura do Reels) |
| Leitura sem som | Na entrega: um subagente novo recebe **só** `build/conferir.jpg` e reconta a mensagem; se não bater com o título do take, volta |
| Fatos rastreados | Na entrega: cada frase da caixa e da legenda tem origem (fala da Brenda na gravação ou o `manual/`). Conteúdo clínico é dela; nada de depoimento, promessa ou preço |

Peça de motion de verdade (antes e depois animado, LAI, explicador) segue o framework inteiro.

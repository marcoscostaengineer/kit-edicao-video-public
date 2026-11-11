# Peças, gramática e ajudantes de cena

Método geral (vista explodida, recorte, mover na palavra): `~/.claude/skills/ghost-editor/references/layered-scenes.md`.
Estilo mármore: `~/.claude/skills/ghost-editor/recipes/marble-explainer/README.md` (escrito para 9:16; aqui o palco é
16:9: palco y 130 a 800, chip em y 860, legenda em y 990, selo em y 70, fonte do caso no canto superior direito).

## Paleta e tipografia (convexa)
Fundo #111111, papel #F3F1EA, limão #D7F23A, violeta #6A2BF2, grafite #3A3A3A. Archivo Black (título, chip), Space Mono
(selo, rótulo, fonte), Inter 800 (legenda), Cinzel só em inscrição gravada no mármore. Peça violeta nunca em fundo violeta,
limão nunca como texto em papel; sem gradiente, sombra ou canto redondo no que é desenhado.

## Peças
- Acervo: `vida/negocio-dentistas/marca-convexa/marmore/elementos/v2/` (`c01-*` = cap. 01) e `<ebook>/design/imagens/`.
- Peça nova: Gemini web, modelo Pro (1536×2752), conversa nova, uma cartela em grade com 4 peças em vista explodida
  (corpo + objeto moderno + partes que se movem). Base de prompt: `vida/negocios/convexa-conteudo/reels/storyboards/pecas-a-gerar.md`.
  Grade salva em `grades/`; recorte em partes com `marmore/recortar_partes.py` (gera `--p1`, `--p2` e o `.json` que o `monta()` lê).
- Personagem recorrente da objeção: o Cético com balão (inscrição em Cinzel).
- Foto real: Wikimedia Commons (licença livre, autor no crédito) e Open Library para capa (citação, Lei 9.610/98 art. 46 III).
  Nudez fora, mesmo em obra clássica.

## Ajudantes (base_cenas.py e build.py)
| Função | O que faz |
|---|---|
| `D("palavra", off)` | tempo da próxima ocorrência depois do cursor; avança o cursor |
| `PEEK("palavra")` | igual, sem mexer no cursor (marcar saída antes) |
| `lacuna("palavra", recua)` | buraco de fala que o whisper pulou (cartão de parte) |
| `P(peca, cx, cy, w)` / `Ph(peca, cx, cy, h)` | peça pela largura / pela altura; devolve seletor |
| `monta(nome, cx, cy, esc)` | remonta vista explodida no lugar; devolve as partes |
| `foto(arq, cx, cy, w, at, credito)` | foto real em quadro de papel com crédito |
| `L(texto, cx, cy, cls)` | rótulo; classes `lbl`, `ptit`, `nivel`, `item ok/x`, `fontes-card` |
| `X(ok, cx, cy, at)` | carimbo ✓/✕ com som |
| `chip_(txt, cls, t0)` | um chip por vez (`c-pap`, `c-lim`, `c-vio`, `c-ok`, `c-x`) |
| `selo(txt, at)` / `selo_fim(at)` | selo de seção no topo |
| `secao(n, titulo, t0, t1)` | cartão de parte com a peça de `PECA_PARTE[n]` |
| `fonte(txt, t0, t1)` | fonte do caso na tela |
| `limpa(at)` | tira do palco tudo que está visível |
| `entra`, `sai`, `pousa`, `arco`, `treme`, `boia`, `pop`, `out`, `go` | vocabulário de movimento (GSAP, fromTo explícito) |
| `lascas(cx, cy, at)` | estilhaça |
| `contador(...)` | número corre até o valor falado |

Cada movimento pede um efeito sonoro em `SFX.append((t, "nome", vol))`; os chips e carimbos já tocam o deles.

## Ritmo
- Uma cena nova a cada 2 a 5 s; 2 a 4 camadas em movimento, nunca mais.
- Caso real com fonte na tela (`fonte()`) e em `fontes.md`.
- Cartão de parte com mais de 1 s (o `secao` falha com assert se for curto).
- Revelação espera a palavra que fecha a ideia.

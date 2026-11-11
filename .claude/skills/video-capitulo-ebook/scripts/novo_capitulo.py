#!/usr/bin/env python3
"""Monta a pasta de um vídeo de capítulo novo com o motor da skill video-capitulo-ebook.
Uso: python3 novo_capitulo.py <pasta-do-ebook> <NN> "<TÍTULO DO CAPÍTULO>" ["<NOME DO LIVRO>"]
Ex.: python3 novo_capitulo.py vida/negocios/conteudo-lai/ebooks/inovacao-antifragil 02 "ESTRUTURAR ANTES DE INOVAR"
Cria <ebook>/video/capNN/ com build.py, base_cenas.py, cenas.py (capa + fecho prontos), trilha.py, blocos.json, folha.py,
vazios.py, storyboard.md, fontes.md, roteiro.txt e as pastas audio/ fotos/ pecas/ fontes/ trilhas/aprovadas/.
Não sobrescreve nada: se a pasta já existir, para.
"""
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent
if len(sys.argv) < 4:
    raise SystemExit(__doc__)
ebook, nn, titulo = Path(sys.argv[1]).resolve(), sys.argv[2].zfill(2), sys.argv[3].upper()
livro = (sys.argv[4] if len(sys.argv) > 4 else ebook.name.replace("-", " ")).upper()
dst = ebook / "video" / f"cap{nn}"
if dst.exists():
    raise SystemExit(f"já existe: {dst} (não sobrescrevo; apague ou escolha outro número)")
CLEEF = next(p for p in ebook.parents if (p / "CLAUDE.md").exists())
CAP01 = CLEEF / "vida/negocios/conteudo-lai/ebooks/inovacao-antifragil/video/cap01"  # exemplo resolvido (trilhas, fonte)

for sub in ["audio", "fotos", "pecas", "fontes", "trilhas/aprovadas", "anim"]:
    (dst / sub).mkdir(parents=True, exist_ok=True)
shutil.copy(SKILL / "motor/build.py", dst / "build.py")
shutil.copy(SKILL / "motor/base_cenas.py", dst / "base_cenas.py")
for f in ["trilha.py", "folha.py", "vazios.py"]:
    shutil.copy(SKILL / f, dst / f)
shutil.copy(CAP01 / "fontes/cinzel-latin.woff2", dst / "fontes/cinzel-latin.woff2")
for mp3 in (CAP01 / "trilhas/aprovadas").glob("*.mp3"):
    shutil.copy(mp3, dst / "trilhas/aprovadas" / mp3.name)
capa = ebook / "design/imagens/capa-livro.png"
if not capa.exists() and (CAP01 / "pecas/capa-livro.png").exists() and ebook == CAP01.parents[1]:
    shutil.copy(CAP01 / "pecas/capa-livro.png", dst / "pecas/capa-livro.png")

(dst / "cenas.py").write_text(f'''# Cenas do vídeo do cap. {nn} (roteiro.txt, storyboard.md). Roda dentro do build.py (exec no mesmo namespace).
exec(compile((AQUI / "base_cenas.py").read_text(), "base_cenas.py", "exec"))
PECA_PARTE.update({{}})  # nº da parte -> peça do cartão de parte
KWS += []  # palavras grifadas na legenda, próprias deste capítulo

# ================================================================== 0 · capa
hk = L("{titulo}", 960, 470, "ptit", 46)
CSS0[hk]["font-size"] = "118px"
init(hk, opacity=1)
sl0 = L("CAP. {nn} · {livro}", 960, 250, "selo2", 46)
init(sl0, opacity=0, y=-30)
go(sl0, 0.25, 0.45, "back.out(1.8)", opacity=1, y=0)
T = D("PRIMEIRA_PALAVRA_DEPOIS_DO_TITULO")  # troque pela 1ª palavra da fala depois do título
out(hk, T - 0.3, 0.25, y=-30)
out(sl0, T - 0.3, 0.2)

# ================================================================== cenas, na ordem da fala (storyboard.md)
# secao(1, "TÍTULO DA PARTE", *lacuna("palavra")) ou secao(1, "...", D("parte"), D("primeira")) para o cartão de parte;
# P()/Ph()/monta() para peças, foto() para pessoa real e capa, chip_() para o chip, fonte() para a fonte do caso, limpa() entre cenas.

# ================================================================== fontes e fecho
# T = D("fontes"); limpa(T - 0.3); selo("FONTES", T); ... capa do livro + chip do próximo capítulo

# ------------------------------------------------------------------ chips para o motor
if _chips:
    _chips[-1][3] = _chips[-1][3] or END - 0.4
for txt, cls, t0, t1 in _chips:
    t1 = min(t1 if t1 is not None else t0 + 4.5, t0 + 4.5)
    CH.append((txt, cls, t0, max(t0 + 0.6, t1)))
''')
(dst / "blocos.json").write_text('[\n  [0.0, null, "funky-martian", 4.0]\n]\n')
(dst / "storyboard.md").write_text(f"""# Vídeo · Cap. {nn} · {titulo.title()} (storyboard)

**Em uma frase:** <a tese do capítulo>

**Critério:** a cada 2 a 5 s uma cena nova mostra o que a voz diz; teste sem som recontando o argumento só pelas imagens e chips.

| # | Fala (âncoras) | Camadas e movimento | Chip |
|---|---|---|---|
| 0 | título | título grande + selo CAP. {nn} | (título) |

## Peças novas (Gemini, Pro, conversa nova)
<grade por grade, cada peça em vista explodida>

## Estado (para retomar)
- <versão, o que o Antonio recusou e por quê, o que falta>
""")
(dst / "fontes.md").write_text(f"# Fontes do vídeo · Cap. {nn}\n\nTexto pronto para a descrição do vídeo.\n\n**Fontes**\n- \n\n**Créditos das imagens**\n- Esculturas de mármore: geradas por IA para o canal, com intervenção nas cores da marca.\n- Trilha: Mixkit Free Music licence (Michael Ramir C.).\n")
(dst / "roteiro.txt").write_text(f"CAP. {nn} · {titulo}\n\n")
(dst / "fotos/creditos.json").write_text("[]\n")
print(f"ok {dst}")

# Ajudantes de cena (skill video-capitulo-ebook, tirados do cap. 01 do Inovação Antifrágil). O cenas.py do capítulo roda isto
# primeiro (exec) e depois escreve as cenas; tudo no namespace do build.py.
# Âncora: D("palavra") acha a palavra DEPOIS da âncora anterior (cursor), então a ordem do código segue a fala.
# Evitar âncora em número, sigla e nome estrangeiro (o whisper erra): usar a palavra comum vizinha.
import json as _j

# ------------------------------------------------------------------ âncora com cursor
CUR = [0.0]


def D(pal, off=0.0):
    alvo = norm(pal)
    for w in words:
        if w["s"] >= CUR[0] - 0.01 and norm(w["w"]) == alvo:
            CUR[0] = w["s"] + 0.01
            return w["s"] + off
    raise SystemExit(f"âncora não achada depois de {CUR[0]:.1f}s: {pal}")


def PEEK(pal, off=0.0):
    """como D(), sem mexer no cursor (para marcar a saída de uma peça antes de chegar na palavra)"""
    alvo = norm(pal)
    for w in words:
        if w["s"] >= CUR[0] - 0.01 and norm(w["w"]) == alvo:
            return w["s"] + off
    raise SystemExit(f"âncora não achada depois de {CUR[0]:.1f}s: {pal}")


def trio(at, ate, rotulos=True, y=430):
    """as três reações em miniatura (ânfora, arco, Hidra), com rótulo; somem em 'ate'"""
    for k, (peca, x, nome, cls) in enumerate([("anfora--p1", 560, "FRÁGIL", "nivel"), ("arco-pedra-chave", 960, "ROBUSTO", "nivel"),
                                              ("hidra-cabecas", 1360, "ANTIFRÁGIL", "nivel anti")]):
        s_, _ = Ph(peca, x, y, 300, 7)
        entra(s_, at + k * 0.15, "baixo", 120)
        sai(s_, ate, "esquerda", 260)
        if rotulos:
            l_ = L(nome, x, y + 210, cls, 8)
            pop(l_, at + 0.3 + k * 0.15)
            out(l_, ate, 0.2)


def lacuna(pal, recua=0):
    """o whisper pulou a fala (ex.: "Parte cinco"): devolve (fim da palavra antes do buraco + 0,2, início da frase seguinte).
    recua = quantas palavras antes de pal a frase seguinte começa ("A passagem": recua=1)"""
    alvo = norm(pal)
    for i, w in enumerate(words):
        if w["s"] >= CUR[0] - 0.01 and norm(w["w"]) == alvo:
            CUR[0] = w["s"] + 0.01
            return words[i - 1 - recua]["e"] + 0.2, words[i - recua]["s"]
    raise SystemExit(f"âncora não achada depois de {CUR[0]:.1f}s: {pal}")


# ------------------------------------------------------------------ registro de tudo que entra no palco (para limpar)
TODOS = []
_n = [0]


def nid(p="e"):
    _n[0] += 1
    return f"{p}{_n[0]}"


def P(peca, cx, cy, w, z=5, origem="50% 50%"):
    """peça de mármore (oculta até mostrar); devolve (seletor, altura)"""
    i = nid("p")
    h = img(i, peca, cx, cy, w, z, origem)
    TODOS.append(f"#{i}")
    return f"#{i}", h


def L(texto, cx, cy, cls="lbl", z=12):
    """rótulo de texto centrado"""
    i = nid("l")
    pos = f"left:{cx}px;top:{cy}px;" if cx is not None else ""
    el(i, cls, f"{pos}z-index:{z}", texto)
    CSS0[f"#{i}"] = {"translate": "-50% -50%"}
    init(f"#{i}", opacity=0)
    TODOS.append(f"#{i}")
    return f"#{i}"


def X(ok, cx, cy, at, tam=96):
    i = nid("s")
    carimbo(i, ok, cx, cy, at, tam=tam)
    TODOS.append(f"#{i}")
    return f"#{i}"


def vis(sel):
    return state.get(sel, {}).get("opacity", 0) > 0.01


def limpa(at, para="esquerda"):
    for s in TODOS:
        if vis(s):
            sai(s, at, para, 220, 0.3)
    SFX.append((at, "whoosh-1", .08))


_chips = []


def chip_fecha(at):
    if _chips and (_chips[-1][3] is None or _chips[-1][3] > at):
        _chips[-1][3] = at


def chip_(txt, cls, t0, t1=None):
    chip_fecha(t0 - 0.06)
    _chips.append([txt, cls, t0, t1])


def fonte(txt, t0, t1):
    s = L(txt, None, None, "fonte", 45)
    CSS0[s] = {"translate": "0 0"}
    setp(s, t0, opacity=1)
    out(s, t1, 0.2)


SELO = [None]


def selo(txt, at):
    chip_fecha(at - 0.1)
    if SELO[0] and vis(SELO[0]):
        out(SELO[0], at - 0.05, 0.15)
    s = L(txt, 960, 70, "selo2", 44)
    go(s, at, 0.35, "back.out(1.8)", opacity=1)
    SELO[0] = s
    return s


def selo_fim(at):
    if SELO[0] and vis(SELO[0]):
        out(SELO[0], at, 0.2)


PECA_PARTE = {}  # nº da parte -> peça de mármore do cartão; o cenas.py do capítulo preenche (ex.: {1: "atena-kintsugi"})


def secao(n, titulo, t0, t1):
    """cartão de parte: palco limpo, a peça da parte à direita, 'PARTE N' e o título à esquerda"""
    limpa(t0 - 0.35)
    selo_fim(t0 - 0.35)
    chip_fecha(t0 - 0.35)
    a = L(f"PARTE {n}", 760, 330, "pnum", 46)
    b = L(titulo, 760, 450, "ptit", 46)
    CSS0[b]["width"] = "1180px"
    if n in PECA_PARTE:
        pc_, _ = P(PECA_PARTE[n], 1540, 450, 300, 44)
        entra(pc_, t0 + 0.2, "direita", 160)
        out(pc_, t1 - 0.25, 0.2)
    pop(a, t0)
    entra(b, t0 + 0.12, "baixo", 60, 0.45)
    assert t1 - t0 > 1.0, f"cartão da parte {n} curto demais: {t0:.1f} a {t1:.1f}"
    out(a, t1 - 0.25, 0.2)
    out(b, t1 - 0.25, 0.2)
    SFX.append((t0, "whoosh-cine", .14))


def foto(arq, cx, cy, w, at, credito, rot=-3, de="baixo", z=10):
    """foto ou capa real (pasta fotos/, créditos em fotos/creditos.json) num quadro de papel com o crédito embaixo"""
    import shutil as _sh
    src = AQUI / "fotos" / arq
    _sh.copy(src, OUT / "assets/img" / arq)
    iw, ih = Image.open(src).size
    h = round((w - 24) * ih / iw) + 12 + 62
    i = nid("f")
    el(i, "foto", f"left:{cx - w / 2:.0f}px;top:{cy - h / 2:.0f}px;width:{w}px;z-index:{z}",
       f'<img src="assets/img/{arq}"><span class="cred">{credito}</span>')
    init(f"#{i}", opacity=0, rotation=rot)
    TODOS.append(f"#{i}")
    entra(f"#{i}", at, de, 160, 0.5)
    SFX.append((at, "whoosh-2", .1))
    return f"#{i}"


def Ph(peca, cx, cy, h, z=5):
    """peça dimensionada pela altura: devolve (seletor, largura)"""
    src = next(q for q in (PECAS / f"{peca}.png", PECAS.parent / f"{peca}.png", LIVRO / f"{peca}.png", AQUI / "pecas" / f"{peca}.png")
               if q.exists())
    iw, ih = Image.open(src).size
    w = round(h * iw / ih)
    s_, _ = P(peca, cx, cy, w, z)
    return s_, w


def monta(nome, cx, cy, esc, z=5):
    """remonta uma vista explodida do recortar_partes.py na posição original; devolve [(seletor, cx, cy, w)]"""
    d = _j.load(open(PECAS / f"{nome}.json"))
    W, H = d["quadro"]
    r = []
    for k, p in enumerate(d["partes"], 1):
        pcx = cx + (p["x"] + p["w"] / 2 - W / 2) * esc
        pcy = cy + (p["y"] + p["h"] / 2 - H / 2) * esc
        s, _ = P(f"{nome}--p{k}", pcx, pcy, round(p["w"] * esc), z)
        r.append((s, pcx, pcy, round(p["w"] * esc)))
    return r


def lascas(cx, cy, at, n=6, cor="#E9E7E1"):
    """estilhaça: polígonos que voam para baixo com rotação fixa"""
    for k in range(n):
        s = L("", cx + (k - n / 2) * 18, cy + (k % 3) * 20, "lasca", 8)
        setp(s, at, opacity=1)
        arco(s, at, (k - n / 2) * 70, 260 + (k % 2) * 60, 90 + k * 12, 0.75, rot=(k * 47) % 180 - 90)
        out(s, at + 0.7, 0.1)
    SFX.append((at, "impact-1", .14))


import shutil as _shf
_shf.copy(AQUI / "fontes/cinzel-latin.woff2", OUT / "assets/fonts/cinzel-latin.woff2")  # inscrição gravada no mármore (balão do Cético)
EXTRA_CSS = """
.lbl { position: absolute; white-space: nowrap; font: 700 30px "Space Mono"; letter-spacing: 2px; color: #F3F1EA; }
.lbl.lim { color: #D7F23A; }
.lbl.big { font-size: 40px; }
.selo2 { position: absolute; white-space: nowrap; font: 700 28px "Space Mono"; letter-spacing: 3px; text-transform: uppercase;
  color: #D7F23A; border: 3px solid #D7F23A; padding: 10px 22px; }
.selo2::before { content: "// "; }
.fonte { position: absolute; left: auto !important; right: 40px; top: 120px !important; max-width: 560px; text-align: right;
  white-space: normal; font: 700 22px/1.35 "Space Mono"; color: #c9c5bb; background: #111111; padding: 6px 10px; }
.fonte::before { content: "FONTE // "; color: #D7F23A; }
.pnum { position: absolute; white-space: nowrap; font: 700 34px "Space Mono"; letter-spacing: 6px; color: #111111; background: #D7F23A;
  padding: 10px 24px; }
.ptit { position: absolute; width: 1500px; text-align: center; font-family: "Archivo Black"; font-size: 84px; line-height: .98;
  letter-spacing: -2px; color: #F3F1EA; }
.ptit.capat { width: 250px; font-size: 30px; letter-spacing: -1px; }
.ptit em { font-style: normal; background: #D7F23A; color: #111111; padding: 0 12px; }
.lasca { position: absolute; width: 34px; height: 26px; background: #E9E7E1; clip-path: polygon(0 20%, 70% 0, 100% 60%, 30% 100%); }
@font-face { font-family: Cinzel; font-weight: 400 900; src: url(assets/fonts/cinzel-latin.woff2) format("woff2"); }
.btxt { position: absolute; width: 380px; text-align: center; font-family: Cinzel, serif; font-weight: 900; font-size: 40px; line-height: 1.08;
  letter-spacing: 2px; color: #6b6b68; text-shadow: 0 1.5px 0 rgba(255,255,255,.75), 0 -1px 0 rgba(0,0,0,.45); }
.painel { position: absolute; width: 780px; height: 600px; border-top: 8px solid #F3F1EA; box-sizing: border-box; }
.painel.anti { border-top-color: #D7F23A; }
.phead { position: absolute; white-space: nowrap; font-family: "Archivo Black"; font-size: 46px; letter-spacing: -1px; color: #F3F1EA; }
.phead.anti { color: #D7F23A; }
.item { position: absolute; width: 700px; font-family: Inter; font-weight: 800; font-size: 31px; line-height: 1.15; color: #F3F1EA;
  padding-left: 54px; box-sizing: border-box; }
.item::before { position: absolute; left: 0; top: 0; width: 38px; height: 38px; line-height: 38px; text-align: center; font-size: 26px;
  background: #F3F1EA; color: #111111; }
.item.x::before { content: "✕"; background: #6A2BF2; color: #F3F1EA; }
.item.ok::before { content: "✓"; background: #D7F23A; color: #111111; }
.ano { position: absolute; display: grid; grid-template-columns: repeat(6, 150px); gap: 16px; }
.ano i { display: block; height: 104px; border: 4px solid #F3F1EA; box-sizing: border-box; font: 700 28px/96px "Space Mono"; font-style: normal;
  text-align: center; color: #F3F1EA; }
.mes { position: absolute; width: 150px; height: 104px; border: 4px solid #F3F1EA; box-sizing: border-box; font: 700 28px/96px "Space Mono";
  text-align: center; color: #111111; background: #D7F23A; }
.grampo { position: absolute; width: 78px; height: 16px; background: #3A3A3A; border: 3px solid #111111; }
.lacre { position: absolute; background: #D7F23A; border: 3px solid #111111; box-sizing: border-box; }
.lacre::after { content: ""; position: absolute; left: 50%; top: 50%; width: 34%; height: 120%; translate: -50% -50%; background: #6A2BF2;
  border: 3px solid #111111; border-radius: 50%; }
.circ, .linha2, .racha, .cais, .prat, .corte { position: absolute; }
.estacao { position: absolute; white-space: nowrap; font: 700 26px "Space Mono"; letter-spacing: 1px; color: #F3F1EA; background: #111111;
  padding: 6px 12px; border: 2px solid #3A3A3A; }
.letra { position: absolute; width: 96px; height: 96px; line-height: 96px; text-align: center; font-family: "Archivo Black"; font-size: 64px;
  background: #F3F1EA; color: #111111; }
.letra.lim { background: #D7F23A; }
.marco { position: absolute; width: 300px; height: 300px; background: #1c1c1c; border: 4px solid #F3F1EA; box-sizing: border-box; }
.mlab { position: absolute; width: 330px; text-align: center; font-family: "Archivo Black"; font-size: 34px; line-height: 1.05; color: #F3F1EA; }
.mlab small { display: block; margin-top: 8px; font: 700 22px "Space Mono"; color: #D7F23A; letter-spacing: 2px; }
.nivel { position: absolute; white-space: nowrap; font-family: "Archivo Black"; font-size: 54px; letter-spacing: -1px; color: #111111;
  background: #F3F1EA; padding: 8px 22px; }
.nivel.anti { background: #D7F23A; }
.pq { position: absolute; width: 1240px; height: 120px; display: flex; align-items: center; gap: 28px; border-top: 5px solid #F3F1EA;
  box-sizing: border-box; color: #F3F1EA; font-family: "Archivo Black"; font-size: 44px; letter-spacing: -1px; }
.pq b { font-weight: 400; font-size: 74px; color: #D7F23A; width: 60px; }
.regra3 { position: absolute; width: 330px; height: 170px; border: 4px solid #F3F1EA; box-sizing: border-box; text-align: center; color: #F3F1EA;
  font-family: "Archivo Black"; font-size: 30px; line-height: 1.05; padding-top: 18px; }
.regra3 b { display: block; font-size: 64px; color: #D7F23A; font-weight: 400; }
.foto { position: absolute; background: #F3F1EA; padding: 12px 12px 62px; box-sizing: border-box; }
.foto img { display: block; width: 100%; height: auto; }
.foto .cred { position: absolute; left: 12px; right: 12px; bottom: 9px; font: 700 15px/1.3 "Space Mono"; color: #3A3A3A;
  white-space: normal; }
.fontes-card { position: absolute; width: 1400px; color: #F3F1EA; font: 700 25px/1.5 "Space Mono"; }
.fontes-card b { color: #D7F23A; font-weight: 700; }
"""
KWS += ["frágil", "robusto", "antifrágil", "antifragilidade", "fragilidade", "robustez", "ciência", "cientista", "hipótese", "regra",
        "desenho", "ruído", "lente", "choque"]

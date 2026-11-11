#!/usr/bin/env python3
"""Motor do vídeo de capítulo de ebook, 16:9 (1920x1080), na gramática do convexa_ (marble explainer). Skill video-capitulo-ebook;
exemplo resolvido: ebooks/inovacao-antifragil/video/cap01.
Motor copiado de convexa-conteudo/reels/build_v2.py e adaptado: palco largo, chip em y 860, legenda em y 990.
Cenas em cenas.py (mesmo namespace). Fala: audio/antonio-original.json (whisper, word_timestamps).
Uso: python3 build.py  ->  anim/index.html ; em anim/: npx hyperframes lint && npx hyperframes render -q draft -o build/draft.mp4
"""
import json, re, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "anim"
CLEEF = next(p for p in AQUI.parents if (p / "CLAUDE.md").exists())  # raiz do Cleef
V1 = CLEEF / "vida/negocios/convexa-conteudo/reels/r04-antes-de-somar-tire/anim"
PECAS = CLEEF / "vida/negocio-dentistas/marca-convexa/marmore/elementos/v2"
LIVRO = AQUI.parents[1] / "design/imagens"  # <ebook>/design/imagens (capa, peças do livro)
FALA = AQUI / "audio/antonio-original.json"

# ------------------------------------------------------------------ pasta de saída: assets do v1 + peças v2
(OUT / "build").mkdir(parents=True, exist_ok=True)
for sub in ["fonts", "sfx", "music"]:
    shutil.copytree(V1 / "assets" / sub, OUT / "assets" / sub, dirs_exist_ok=True)
shutil.copy(V1 / "assets/grain.png", OUT / "assets/grain.png")
voz = OUT / "assets/voice.m4a"
if not voz.exists() or voz.stat().st_mtime < (AQUI / "audio/antonio-original.mp3").stat().st_mtime:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(AQUI / "audio/antonio-original.mp3"), "-c:a", "aac",
                    "-b:a", "192k", str(voz)], check=True)
(OUT / "assets/img").mkdir(exist_ok=True)


def norm(s):
    return re.sub(r"[^\w]", "", s.lower())


# ------------------------------------------------------------------ fala (whisper)
raw = [{"w": w["word"].strip(), "s": w["start"], "e": w["end"]}
       for s in json.load(open(FALA))["segments"] for w in s["words"]]
words = []
for w in raw:
    if words and w["w"].startswith(("-", "%", ".")):  # "3" + ".700" -> "3.700"
        words[-1] = {**words[-1], "w": words[-1]["w"] + w["w"], "e": w["e"]}
    else:
        words.append(dict(w))
FIX = {}  # correções de grafia do whisper na legenda: chave = palavra normalizada
# grafia que o whisper erra na fala do Antonio (a âncora usa a palavra corrigida)
JUNTA = [(("quinto", "suje"), "kintsugi"), (("shilhart",), "Shewhart"), (("schilhardt",), "Shewhart"), (("denim",), "Deming"),
         (("tega",), "Pega"), (("antifragil",), "antifrágil"), (("antifragio",), "antifrágil"), (("antônio",), "Antonio"),
         (("idra",), "Hidra"), (("shogun",), "xogum"), (("de", "briefing"), "debriefing"), (("nasce", "em"), "nascem"), (("deixase", "catris"), "Deixa cicatriz")]
i = 0
while i < len(words):
    for seq, novo_ in JUNTA:
        if [norm(w["w"]) for w in words[i:i + len(seq)]] == list(seq):
            ult = words[i + len(seq) - 1]["w"]
            pont = ult[len(ult.rstrip(",.?!;:")):]
            words[i:i + len(seq)] = [{"w": novo_ + pont, "s": words[i]["s"], "e": words[i + len(seq) - 1]["e"]}]
            break
    i += 1
VO_END = words[-1]["e"]
END = VO_END + 1.3
TOTAL = round(VO_END + 2.6, 2)


def W(text, n=1):
    k = 0
    for w in words:
        if norm(w["w"]) == norm(text):
            k += 1
            if k == n:
                return w["s"]
    raise SystemExit(f"palavra não achada: {text} #{n}")


def A(a):
    if isinstance(a, (int, float)):
        return a
    if isinstance(a, str):
        return W(a)
    return W(a[0], a[1] if len(a) > 1 else 1) + (a[2] if len(a) > 2 else 0)


# ------------------------------------------------------------------ timeline com estado (fromTo explícito sempre)
tl, html, state, CSS0, SFX = [], [], {}, {}, []
DEF = {"x": 0, "y": 0, "scale": 1, "rotation": 0, "opacity": 1, "scaleX": 1, "scaleY": 1}


INIT = {}  # um único tl.set em 0 por seletor: com dois sets no mesmo instante, a busca para trás do render devolve o errado


def init(sel, **p):
    r = CSS0.setdefault(sel, {})
    if "opacity" in p:
        r["opacity"] = p["opacity"]
    INIT.setdefault(sel, {}).update(p)
    state.setdefault(sel, {}).update(p)


def go(sel, at, dur=0.5, ease="power3.out", **to):
    st = state.setdefault(sel, {})
    frm = {k: st.get(k, DEF.get(k, 0)) for k in to}
    st.update(to)
    t = {**to, "duration": dur, "ease": ease, "immediateRender": False}
    tl.append(f'tl.fromTo("{sel}", {json.dumps(frm)}, {json.dumps(t)}, {max(0, at):.3f});')


def setp(sel, at, **p):
    if at <= 0.001:
        return init(sel, **p)
    state.setdefault(sel, {}).update(p)
    tl.append(f'tl.set("{sel}", {json.dumps(p)}, {max(0, at):.3f});')


def pop(sel, at, dur=0.4, s0=0.5):
    setp(sel, at - 0.01, scale=s0)
    go(sel, at, dur, "back.out(2)", opacity=1, scale=1)


def out(sel, at, dur=0.25, **extra):
    go(sel, at, dur, "power2.in", opacity=0, **extra)


def entra(sel, at, de="direita", dist=200, dur=0.45):
    """camada vem da borda (gramática: entra)"""
    dx = {"direita": dist, "esquerda": -dist}.get(de, 0)
    dy = {"baixo": dist, "cima": -dist}.get(de, 0)
    setp(sel, at - 0.01, x=dx, y=dy, opacity=0)
    go(sel, at, dur, "power3.out", x=0, y=0, opacity=1)


def sai(sel, at, para="esquerda", dist=260, dur=0.3):
    dx = {"direita": dist, "esquerda": -dist}.get(para, 0)
    dy = {"baixo": dist, "cima": -dist}.get(para, 0)
    go(sel, at, dur, "power2.in", x=state.get(sel, {}).get("x", 0) + dx, y=state.get(sel, {}).get("y", 0) + dy, opacity=0)


def pousa(sel, at, de=260, dur=0.55):
    """cai de cima e quica"""
    setp(sel, at - 0.01, y=-de, opacity=1)
    go(sel, at, dur, "bounce.out", y=0)


def arco(sel, at, dx, dy, alt=160, dur=0.7, rot=0):
    """voa numa curva: x linear, y sobe e desce"""
    st = state.setdefault(sel, {})
    x0, y0 = st.get("x", 0), st.get("y", 0)
    topo = min(y0, y0 + dy) - alt
    go(sel, at, dur, "none", x=x0 + dx, rotation=st.get("rotation", 0) + rot)
    go(sel, at, dur / 2, "power2.out", y=topo)
    go(sel, at + dur / 2, dur / 2, "power2.in", y=y0 + dy)


def treme(sel, at, amp=8, n=4, passo=0.05):
    x0 = state.get(sel, {}).get("x", 0)
    for i in range(n):
        go(sel, at + i * passo, passo, "none", x=x0 + (amp if i % 2 == 0 else -amp))
    go(sel, at + n * passo, passo, "none", x=x0)


def boia(sel, t0, t1, amp=6, per=2.8):
    """respiração da peça parada (yoyo dentro da janela, sem repeat infinito)"""
    y0 = state.get(sel, {}).get("y", 0)
    t, s = t0, 1
    while t + per / 2 < t1:
        go(sel, t, per / 2, "sine.inOut", y=y0 - amp * s)
        t, s = t + per / 2, -s
    go(sel, t, 0.3, "sine.inOut", y=y0)


def el(id_, cls, style, inner=""):
    html.append(f'<div id="{id_}" class="{cls}" style="{style}">{inner}</div>')


def img(id_, peca, cx, cy, w, z=5, origem="50% 50%", pai=None):
    """peça de mármore centrada em (cx, cy) com largura w; o GSAP move por cima do translate(-50%,-50%)"""
    src = next((p for p in (PECAS / f"{peca}.png", PECAS.parent / f"{peca}.png", LIVRO / f"{peca}.png", AQUI / "pecas" / f"{peca}.png") if p.exists()), None)
    assert src, f"peça não achada: {peca}"
    shutil.copy(src, OUT / "assets/img" / f"{peca}.png")
    iw, ih = Image.open(src).size
    h = round(w * ih / iw)
    tag = (f'<img id="{id_}" class="pc" src="assets/img/{peca}.png" style="left:{cx - w / 2:.0f}px;top:{cy - h / 2:.0f}px;'
           f'width:{w}px;height:{h}px;z-index:{z};transform-origin:{origem}">')
    if pai:
        grupos[pai].append(tag)
    else:
        html.append(tag)
    init(f"#{id_}", opacity=0)
    return h


grupos = {}


def grupo(id_, cx, cy, w, h, z=5, origem="50% 100%"):
    grupos[id_] = []
    html.append(f'@@{id_}@@')
    init(f"#{id_}", x=0, y=0, rotation=0, scale=1)
    CSS0[f"#{id_}"] = {"left": f"{cx - w / 2:.0f}px", "top": f"{cy - h / 2:.0f}px", "width": f"{w}px", "height": f"{h}px",
                       "z-index": z, "transform-origin": origem}


def carimbo(id_, ok, cx, cy, at, z=20, tam=110):
    el(id_, f"stamp {'s-ok' if ok else 's-x'}", f"left:{cx - tam / 2:.0f}px;top:{cy - tam / 2:.0f}px;width:{tam}px;height:{tam}px;"
       f"line-height:{tam}px;font-size:{tam * 0.62:.0f}px;z-index:{z}", "✓" if ok else "✕")
    init(f"#{id_}", opacity=0)
    setp(f"#{id_}", at - 0.01, scale=1.6, rotation=-8)
    go(f"#{id_}", at, 0.25, "back.out(3)", opacity=1, scale=1)
    SFX.append((at, "tech-ui-confirm" if ok else "tech-ui-error", .14))


def contador(id_, cx, cy, at, dur, v0, v1, fmt, cls="cont", z=12):
    el(id_, cls, f"left:{cx}px;top:{cy}px;z-index:{z}", fmt.format(v0))
    CSS0[f"#{id_}"] = {"translate": "-50% -50%"}
    init(f"#{id_}", opacity=0)
    obj = f"c_{id_}"
    tl.append(f'const {obj} = {{v: {v0}}};')
    tl.append(f'tl.fromTo({obj}, {{v: {v0}}}, {{v: {v1}, duration: {dur}, ease: "power2.out", immediateRender: false, '
              f'onUpdate: () => {{ document.getElementById("{id_}").textContent = {json.dumps(fmt)}.replace("{{}}", '
              f'Math.round({obj}.v).toLocaleString("pt-BR")); }}}}, {at:.3f});')


def lista(tit, itens, t_fim, icones=None):
    """as três linhas da v1 (faixas numeradas), cada uma entra na sua palavra; ícone opcional à direita"""
    t0 = A(itens[0][1])
    el("lt", "ltit", "left:260px;top:150px;", tit)
    init("#lt", opacity=0)
    entra("#lt", t0 - 0.25, "esquerda", 40, 0.35)
    for j, (txt, a) in enumerate(itens):
        ico = f'<em class="lico">{icones[j]}</em>' if icones else ""
        el(f"li{j}", "faixa", f"left:260px;top:{230 + j * 175}px;", f"<b>{j + 1}</b><span>{txt}</span>{ico}")
        init(f"#li{j}", opacity=0)
        entra(f"#li{j}", A(a), "esquerda", 80, 0.4)
        SFX.append((A(a), "pop-2", .16))
    for sel in ["#lt"] + [f"#li{j}" for j in range(len(itens))]:
        go(sel, t_fim, 0.25, "power2.in", opacity=0, x=40)


def chip(id_, text, at0, at1, cls, cx=960, cy=860):
    if cls.startswith("c-ok"):
        text = '<span class="ico">✓</span>' + text
    elif cls.startswith("c-x"):
        text = '<span class="ico">✕</span>' + text
    el(id_, f"chip {cls}", f"left:{cx}px;top:{cy}px;", text)
    CSS0[f"#{id_}"] = {"translate": "-50% -50%"}
    init(f"#{id_}", opacity=0)
    pop(f"#{id_}", at0)
    out(f"#{id_}", at1, 0.15)
    SFX.append((at0, "tech-ui-error" if cls.startswith("c-x") else "tick-1", .12))


# ------------------------------------------------------------------ fundo: grade fina e a curva convexa desenhando devagar
el("grid", "grid", "")
el("curva", "curva", "",
   '<svg viewBox="0 0 1920 420" width="1920" height="420"><path id="cv" d="M-20 380 H900 C1300 380 1560 260 1820 40" fill="none" '
   'stroke="#D7F23A" stroke-width="10" stroke-linecap="square" pathLength="1" stroke-dasharray="1 1.2" stroke-dashoffset="1.1"/>'
   '<rect id="cvp" x="1804" y="24" width="32" height="32" fill="#D7F23A"/></svg>')
CSS0["#cvp"] = {"opacity": 0}
tl.append(f'tl.fromTo("#cv", {{strokeDashoffset: 1.1}}, {{strokeDashoffset: 0, duration: {TOTAL - 1:.2f}, ease: "none", immediateRender: false}}, 0);')
tl.append(f'tl.set("#cvp", {{opacity: 1}}, {TOTAL - 1:.2f});')
SFX += [(0.0, "whoosh-cine", .2)]

# ================================================================== cenas (cenas.py, mesmo namespace): capa, peças, chips
CH = []  # (texto, classe, âncora0, âncora1), preenchido pelas cenas
EXTRA_CSS = ""  # CSS próprio das cenas
KWS = []  # palavras grifadas na legenda
exec(compile((AQUI / "cenas.py").read_text(), "cenas.py", "exec"))
for i, (txt, cls, a0, a1) in enumerate(CH):
    chip(f"ch{i}", txt, A(a0), A(a1), cls)

# ------------------------------------------------------------------ legenda palavra por palavra
KW = {norm(k) for k in KWS}
groups, cur = [], []
for w in words:
    if cur and sum(len(x["w"]) + 1 for x in cur) + len(w["w"]) > 34:
        groups.append(cur); cur = []
    cur.append(w)
    if w["w"][-1] in ",.?!;:" or len(cur) >= 6:
        groups.append(cur); cur = []
if cur:
    groups.append(cur)
antes = "."
for gi, g in enumerate(groups):
    spans = []
    for wi, w in enumerate(g):
        txt = w["w"].rstrip(",.!") if not w["w"].endswith("?") else w["w"]
        core = norm(txt)
        txt = FIX[core] + (txt[-1] if txt[-1] == "?" else "") if core in FIX else txt
        if antes[-1:] in ".?!" and txt[:1].islower():
            txt = txt[:1].upper() + txt[1:]
        antes = w["w"]
        spans.append(f'<span id="w{gi}_{wi}" class="{"kw" if core in KW else ""}">{txt}</span>')
        init(f"#w{gi}_{wi}", opacity=0.35, scale=1)
        go(f"#w{gi}_{wi}", w["s"] - 0.02, 0.12, "power2.out", opacity=1, scale=1.06)
        go(f"#w{gi}_{wi}", max(w["e"], w["s"] + 0.12), 0.12, "power2.out", scale=1)
    el(f"cap{gi}", "cap", "", " ".join(spans))
    CSS0[f"#cap{gi}"] = {"translate": "-50% -50%", "opacity": 0}
    tl.append(f'tl.set("#cap{gi}", {{opacity: 1}}, {g[0]["s"] - 0.05:.3f});')
    t_off = groups[gi + 1][0]["s"] - 0.06 if gi + 1 < len(groups) else VO_END + 0.3
    tl.append(f'tl.set("#cap{gi}", {{opacity: 0}}, {t_off:.3f});')

# ------------------------------------------------------------------ som
# todos os efeitos ficam (o Antonio pediu de volta os 226 em 2026-10-31; o "uma em cima da outra" era a sobreposição das músicas)
dur = {}
for _, s, _v in SFX:
    if s not in dur:
        dur[s] = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                                str(OUT / f"assets/sfx/{s}.wav")]).decode())
audio = [f'<audio id="vo" src="assets/voice.m4a" data-start="0" data-duration="{VO_END + 0.5:.3f}" data-track-index="10" data-volume="1"></audio>',
]  # trilha entra na mixagem final (trilha.py), com ducking sob a voz
for i, (t, s, v) in enumerate(sorted(SFX)):
    audio.append(f'<audio id="sfx{i}" src="assets/sfx/{s}.wav" data-start="{max(0, t):.3f}" data-duration="{min(dur[s], TOTAL - t):.3f}" '
                 f'data-track-index="{30 + i}" data-volume="{v}"></audio>')

CSS = """
@font-face { font-family: "Archivo Black"; src: url(assets/fonts/archivo-black-latin-400-normal.woff2) format("woff2"); }
@font-face { font-family: "Space Mono"; font-weight: 700; src: url(assets/fonts/space-mono-latin-700-normal.woff2) format("woff2"); }
@font-face { font-family: Inter; font-weight: 800; src: url(assets/fonts/inter-latin-800-normal.woff2) format("woff2"); }
html, body { margin: 0; background: #111111; }
#root { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #111111; font-family: Inter, sans-serif; }
.grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(243,241,234,.045) 2px, transparent 2px),
  linear-gradient(90deg, rgba(243,241,234,.045) 2px, transparent 2px); background-size: 90px 90px; }
.curva { position: absolute; left: 0; top: 600px; opacity: .07; }
.pc { position: absolute; display: block; }
.grp { position: absolute; }
.hook { position: absolute; white-space: nowrap; text-align: center; font-family: "Archivo Black"; line-height: .95; letter-spacing: -3px;
  color: #F3F1EA; z-index: 15; }
.hook em { font-style: normal; background: #D7F23A; color: #111111; padding: 0 14px; }
.selo { position: absolute; white-space: nowrap; font: 700 34px "Space Mono"; letter-spacing: 3px; text-transform: uppercase;
  color: #D7F23A; border: 3px solid #D7F23A; padding: 12px 26px; }
.selo::before { content: "//"; }
.chip { position: absolute; width: max-content; max-width: 1500px; text-align: center; font-family: "Archivo Black"; font-size: 42px;
  line-height: 1.02; letter-spacing: -1px; padding: 14px 28px 16px; z-index: 30; }
.chip.small { font-size: 40px; padding: 18px 30px 20px; }
.c-lim { background: #D7F23A; color: #111111; }
.c-pap { background: #F3F1EA; color: #111111; }
.c-vio { background: #6A2BF2; color: #F3F1EA; }
.c-x, .c-ok { background: #F3F1EA; color: #111111; }
.c-ok { background: #D7F23A; }
.chip .ico { display: inline-block; width: 56px; height: 56px; margin-right: 18px; line-height: 56px; font-family: Inter; font-weight: 800;
  font-size: 40px; vertical-align: 4px; background: #111111; color: #F3F1EA; }
.c-ok .ico { color: #D7F23A; }
.stamp { position: absolute; text-align: center; font-family: Inter; font-weight: 800; border: 6px solid #111111; }
.s-ok { background: #D7F23A; color: #111111; }
.s-x { background: #6A2BF2; color: #F3F1EA; }
.sinal { position: absolute; width: 200px; height: 200px; }
.sinal i { position: absolute; background: #D7F23A; }
.sinal .h { left: 0; top: 75px; width: 200px; height: 50px; }
.sinal .v { left: 75px; top: 0; width: 50px; height: 200px; }
.teia, .rachas { position: absolute; }
.perg { position: absolute; width: 400px; padding: 40px 34px 46px; background: #F3F1EA; border-top: 18px solid #3A3A3A;
  border-bottom: 18px solid #3A3A3A; box-sizing: border-box; }
.pl { font-family: "Archivo Black"; font-size: 44px; line-height: 1; color: #111111; margin: 10px 0 34px; display: flex; gap: 18px; }
.pl b { font-weight: 400; color: #6A2BF2; }
.anel, .areia { position: absolute; }
.cont { position: absolute; white-space: nowrap; font-family: "Archivo Black"; font-size: 58px; color: #F3F1EA; letter-spacing: -1px; }
.cont.big { font-size: 96px; color: #D7F23A; }
.rot { position: absolute; white-space: nowrap; font: 700 38px "Space Mono"; letter-spacing: 3px; color: #F3F1EA; }
.pz { position: absolute; width: 150px; height: 150px; background: #111111; border: 6px solid #D7F23A; display: flex; gap: 22px;
  justify-content: center; align-items: center; }
.pz i { width: 30px; height: 80px; background: #D7F23A; }
.pz-s { width: 110px; height: 110px; } .pz-s i { width: 22px; height: 58px; }
.bars { position: absolute; display: flex; gap: 50px; align-items: flex-end; height: 380px; }
.bar { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.bar i { display: block; width: 130px; height: 300px; background: #F3F1EA; transform-origin: 50% 100%; }
#b2 i { background: #D7F23A; }
.bar span { font: 700 30px "Space Mono"; letter-spacing: 2px; color: #F3F1EA; }
.cal { position: absolute; display: grid; grid-template-columns: repeat(7, 54px); gap: 10px; }
.cal i { display: block; width: 54px; height: 54px; border: 4px solid #F3F1EA; box-sizing: border-box; background: transparent; }
.ltit { position: absolute; white-space: nowrap; font: 700 36px "Space Mono"; letter-spacing: 3px; color: #D7F23A; }
.ltit::before { content: "//"; }
.faixa { position: absolute; width: 1400px; height: 150px; display: flex; align-items: center; gap: 34px; border-top: 6px solid #F3F1EA;
  color: #F3F1EA; box-sizing: border-box; }
.faixa b { font-family: "Archivo Black"; font-weight: 400; font-size: 120px; line-height: 1; color: #D7F23A; width: 90px; }
.faixa span { font-family: "Archivo Black"; font-size: 58px; line-height: 1; letter-spacing: -1px; flex: 1; }
.faixa .lico { display: block; width: 120px; height: 120px; }
.rio, .bal, .contaads { position: absolute; }
.bolha { position: absolute; width: 18px; height: 18px; border: 4px solid #F3F1EA; border-radius: 50%; }
.c100 { position: absolute; display: grid; grid-template-columns: repeat(20, 40px); gap: 6px; }
.c100 i { display: block; width: 40px; height: 40px; border: 3px solid #F3F1EA; box-sizing: border-box; }
.plq { position: absolute; white-space: nowrap; font: 400 46px "Archivo Black"; background: #6A2BF2; color: #F3F1EA; padding: 14px 28px; }
.contaads { width: 230px; height: 170px; background: #F3F1EA; display: flex; flex-direction: column; gap: 16px; padding: 0 0 20px; box-sizing: border-box; }
.contaads .ch { height: 44px; background: #6A2BF2; }
.contaads i { display: block; height: 14px; margin: 0 24px; background: #3A3A3A; }
.contaads .cu { width: 90px; background: #D7F23A; height: 22px; }
.mini-bal { position: absolute; width: 70px; height: 48px; background: #F3F1EA; }
.mini-bal::after { content: ""; position: absolute; left: 12px; bottom: -16px; border: 8px solid transparent; border-top: 10px solid #F3F1EA; }
.grav { position: absolute; text-align: center; font-family: "Archivo Black"; font-size: 46px; line-height: 1.05; color: #3A3A3A; letter-spacing: -1px; }
.grav p { margin: 22px 0 0; font-size: 34px; color: #111111; }
.bex, .linha, .frac { position: absolute; }
.px { position: absolute; width: 22px; height: 22px; }
.mcal { position: absolute; width: 70px; height: 64px; background: #F3F1EA; }
.mcal b { display: block; height: 18px; background: #6A2BF2; }
.mcal i { position: absolute; left: 22px; top: 28px; width: 26px; height: 26px; background: #D7F23A; }
.etq { position: absolute; width: 120px; height: 70px; background: #D7F23A; transform-origin: 0 50%; }
.etq b { position: absolute; left: 14px; top: 26px; width: 18px; height: 18px; background: #111111; }
.cap { position: absolute; left: 960px; top: 990px; max-width: 1600px; white-space: nowrap; text-align: center; font-weight: 800;
  font-size: 40px; line-height: 1.15; color: #F3F1EA; background: #111111; padding: 8px 22px 10px; border: 3px solid #3A3A3A; z-index: 40; }
.cap span { display: inline-block; margin: 0 5px; }
.cap .kw { background: #D7F23A; color: #111111; padding: 0 8px; }
#grain { position: absolute; inset: 0; background: url(assets/grain.png); background-size: 480px; opacity: .05; mix-blend-mode: overlay; z-index: 50; }
"""
corpo = "\n".join(html)
for g, filhos in grupos.items():
    corpo = corpo.replace(f"@@{g}@@", f'<div id="{g}" class="grp">' + "".join(filhos) + "</div>")
tl[:0] = [f'tl.set("{k}", {json.dumps(v)}, 0);' for k, v in INIT.items() if v]
css0 = "".join(f"{k} {{ " + "; ".join(f"{a}: {b}" for a, b in v.items()) + " }\n" for k, v in CSS0.items() if v)
page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23111111'/%3E%3Cpath d='M10 44 H30 C40 44 46 36 52 16' fill='none' stroke='%23D7F23A' stroke-width='6'/%3E%3C/svg%3E">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}{EXTRA_CSS}{css0}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{TOTAL}" data-fps="30">
{corpo}
<div id="grain"></div>
{chr(10).join(audio)}
</div>
<script>
  window.__timelines = window.__timelines || {{}};
  const tl = gsap.timeline({{ paused: true }});
  {chr(10).join('  ' + l for l in tl)}
  window.__timelines["main"] = tl;
</script>
</body></html>
"""
(OUT / "index.html").write_text(page)
print(f"{AQUI.name}: {TOTAL:.1f}s · {len(html)} elementos · {len(CH)} chips · {len(groups)} legendas · {len(SFX)} sfx -> {OUT}")

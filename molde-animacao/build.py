#!/usr/bin/env python3
"""R13 · e se você passasse um ano mastigando só de um lado. Animação com a voz clonada da Brenda -> index.html
(HyperFrames, 1080x1920, 30 fps). Mesmo molde do S14/R12/S12 (helpers, legenda centrada em x 480, chamada no WhatsApp).
Cada entrada está presa a uma PALAVRA da fala (build/brenda-r13.json, whisper), não a segundos fixos.
EVIDÊNCIA MAIS FRACA DOS 12: a verificação científica de 31/10 tirou os marcos de tempo e a "dor de cabeça de manhã".
Por isso: o placar conta 1/4 a 4/4 (desgaste · músculo · articulação · tártaro), NUNCA meses, e todo cartão repete o
hedge da fala ("tende", "pode", "aparece mais", "costuma"). Nada endurece na tela.
Daltonismo do Antonio: o lado parado da arcada é HACHURADO e tem rótulo, não só mais escuro; o placar diferencia a vez
por tamanho, borda e fundo; o certo leva ✓ e texto.
Elementos: grade 2x3 do Gemini (gemini/g1-somar.jpg -> assets/img/q1..q6), poses do banco (17, 02, 18, 22, 09).
Uso: python3 build.py && npx hyperframes lint && node area_segura_dom.mjs index.html && npx hyperframes render -o build/r13.mp4"""
import json, random, re, subprocess
from PIL import Image

words = [{"w": w["word"].strip(), "s": w["start"], "e": w["end"]}
         for s in json.load(open("build/brenda-r13.json"))["segments"] for w in s["words"]]
VO_END = words[-1]["e"]
TOTAL = round(VO_END + 1.4, 2)          # o fecho respira e volta à capa (loop); fala de 60,1 s (texto mais longo dos 12)


def norm(s):
    return re.sub(r"[^\w]", "", s.lower())


def W(text, n=1, end=False):
    k = 0
    for w in words:
        if norm(w["w"]) == norm(text):
            k += 1
            if k == n:
                return w["e"] if end else w["s"]
    raise SystemExit(f"palavra não achada: {text} #{n}")


def size(name):
    return Image.open(f"assets/img/{name}.png").size


# ------------------------------------------------------------------ timeline com estado (fromTo explícito sempre)
tl, html, state = [], [], {}
DEF = {"x": 0, "y": 0, "scale": 1, "rotation": 0, "opacity": 1, "scaleX": 1, "scaleY": 1}
CSS0 = {}


def init(sel, **p):
    xp, yp = p.pop("xPercent", None), p.pop("yPercent", None)
    if re.fullmatch(r"#[\w-]+", sel):
        r = CSS0.setdefault(sel, {})
        if xp is not None or yp is not None:
            r["translate"] = f"{xp or 0}% {yp or 0}%"
        if "opacity" in p:
            r["opacity"] = p["opacity"]
    if p:
        state[sel] = dict(p)
        tl.append(f'tl.set("{sel}", {json.dumps(p)}, 0);')


def go(sel, at, dur=0.5, ease="power3.out", **to):
    st = state.setdefault(sel, {})
    frm = {k: st.get(k, DEF.get(k, 0)) for k in to}
    st.update(to)
    t = {**to, "duration": dur, "ease": ease, "immediateRender": False}
    tl.append(f'tl.fromTo("{sel}", {json.dumps(frm)}, {json.dumps(t)}, {max(0, at):.3f});')


def setp(sel, at, **p):
    state.setdefault(sel, {}).update(p)
    tl.append(f'tl.set("{sel}", {json.dumps(p)}, {max(0, at):.3f});')


def pop(sel, at, dur=0.45, s0=0.4):
    setp(sel, at - 0.01, scale=s0)
    go(sel, at, dur, "back.out(2)", opacity=1, scale=1)


def out(sel, at, dur=0.3, **extra):
    go(sel, at, dur, "power2.in", opacity=0, **extra)


def pulse(sel, t0, t1, per=0.7, a=1.0, b=1.15):
    t, up = t0, True
    while t < t1 - per / 2:
        go(sel, t, per / 2, "sine.inOut", scale=b if up else a)
        t += per / 2; up = not up
    go(sel, t, 0.2, "sine.out", scale=a)


def el(id_, cls, style, inner=""):
    html.append(f'<div id="{id_}" class="{cls}" style="{style}">{inner}</div>')


def at_center(cx, cy):
    return f"left:{cx}px;top:{cy}px;"


def chip(id_, text, cx, cy, cls="c-white"):
    el(id_, f"chip {cls}", at_center(cx, cy), text)
    init(f"#{id_}", xPercent=-50, yPercent=-50, opacity=0)


def card(id_, cx, cy, w, h, inner, cls="card"):
    el(id_, cls, at_center(cx, cy) + f"width:{w}px;height:{h}px;transform-origin:50% 50%", inner)
    init(f"#{id_}", xPercent=-50, yPercent=-50, opacity=0, scale=1, x=0, y=0)


def ring(id_, x, y, d, cls=""):
    """anel dentro de um card, em % do card"""
    return f'<div class="ring {cls}" id="{id_}" style="left:{x}%;top:{y}%;width:{d}px;height:{d}px"></div>'


def anel(k, t_in, t_out, per=0.55):
    init(f"#{k}", xPercent=-50, yPercent=-50, opacity=0)
    pop(f"#{k}", t_in, 0.35, 0.3)
    pulse(f"#{k}", t_in + 0.35, t_out - 0.05, per, 1, 1.12)
    out(f"#{k}", t_out, 0.2)


WA_SVG = '<svg viewBox="0 0 32 32" width="64" height="64"><path fill="#fff" d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.5.7 4.8 2 6.8L3.2 29l6.8-2.1c1.9 1 4 1.6 6 1.6 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4 1.2 1.3-3.9-.3-.4a10.3 10.3 0 0 1-1.6-5.6C5.6 9.9 10.3 5.3 16 5.3s10.4 4.6 10.4 10.3S21.7 26 16 26zm5.7-7.7c-.3-.2-1.8-.9-2.1-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-.3-.2-1.3-.5-2.5-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.6c.2-.2.2-.3.3-.6.1-.2 0-.4 0-.6l-1-2.3c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.4c.2.2 2.4 3.6 5.7 5 .8.4 1.4.6 1.9.7.8.2 1.5.2 2.1.1.6-.1 1.8-.7 2.1-1.5.3-.7.3-1.4.2-1.5-.1-.1-.3-.2-.6-.3z"/></svg>'
# ícones do placar (traço azul-escuro: lê no branco e no amarelo)
IC = 'viewBox="0 0 24 24" width="54" height="54" fill="none" stroke="#123A63" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"'
DESG_SVG = f'<svg {IC}><path d="M5 7h14"/><path d="M5.5 7c-.3 5 .6 13 3 13 1.6 0 1.3-5 3.5-5s1.9 5 3.5 5c2.4 0 3.3-8 3-13"/><path d="M7 3.5l1.2 2M12 3l0 2.2M17 3.5l-1.2 2"/></svg>'
MUSC_SVG = f'<svg {IC}><path d="M2.5 13l3-5 3 9 3-9 3 9 3-9 3 5"/></svg>'
ARTI_SVG = f'<svg {IC}><path d="M14 3.5a6 6 0 0 1 4.5 10c-1.4 1.6-2.5 2.4-2.5 4.5a3 3 0 0 1-5.5 1.6"/><circle cx="7" cy="12" r="2.6"/><path d="M3 7.5l1.5 1.5M3 16.5l1.5-1.5"/></svg>'
TART_SVG = f'<svg {IC}><path d="M6 4.5c-1.6 3-.8 9 1.2 15 .5 1.4 2 1.3 2.3-.2l1-4.3c.3-1.2 2.7-1.2 3 0l1 4.3c.3 1.5 1.8 1.6 2.3.2 2-6 2.8-12 1.2-15-2-1.6-4-.6-6 0-2-.6-4-1.6-6 0z"/><circle cx="9" cy="10" r=".9" fill="#123A63"/><circle cx="12.5" cy="12" r=".9" fill="#123A63"/><circle cx="15" cy="9" r=".9" fill="#123A63"/></svg>'

# ------------------------------------------------------------------ tempos da fala
T = {k: W(*v) if isinstance(v, tuple) else W(v) for k, v in {
    "ano": "ano", "mastigando": "mastigando", "falta1": ("falta", 1), "doi1": ("dói", 1), "conto": "conto",
    "somar": "somar", "no": ("no", 1), "comeco": "começo", "nada": "nada", "lado2": ("lado", 2), "bom": "bom",
    "nem": "nem", "escolheu": "escolheu", "primeira": "primeira", "desgaste1": ("desgaste", 1),
    "trabalha1": ("trabalha", 1), "dois": "dois", "tende": "tende", "gastar": "gastar",
    "desgaste2": ("desgaste", 2), "desigual": "desigual", "segunda": "segunda", "musculo": "músculo",
    "trabalha2": ("trabalha", 2), "pode": "pode", "tenso": "tenso", "vezes": "vezes", "forte": "forte",
    "so2": ("só", 2), "terceira": "terceira", "articulacao": "articulação", "frente": "frente", "ouvido": "ouvido",
    "quem1": ("quem", 1), "aparece": "aparece", "estalo": "estalo", "dor": "dor", "ali": "ali", "dizer": "dizer",
    "primeiro": "primeiro", "sinal": "sinal", "avaliar": "avaliar", "quarta": "quarta", "tartaro": "tártaro",
    "parado": "parado", "juntar": "juntar", "mastigacao": "mastigação", "varrer": "varrer", "limpa": "limpa",
    "escova": "escova", "faz": "faz", "teste": "teste", "morde": "morde", "repara": "repara", "foi": "foi",
    "resposta": "resposta", "hora": "hora", "favorito": "favorito", "resolver": "resolver", "motivo": "motivo",
    "dente2": ("dente", 2), "doi2": ("dói", 2), "costuma3": ("costuma", 3), "simples": "simples",
    "consertar": "consertar", "somou": "somou", "chama": "chama", "whatsapp": "whatsapp", "conta2": ("conta", 2),
    "evita": "evita", "lado8": ("lado", 8),
}.items()}

# ------------------------------------------------------------------ fundo vivo (igual ao S9/S12/S14)
rng = random.Random(13)
el("blob1", "blob", "left:-260px;top:120px;width:1100px;height:1100px;background:radial-gradient(circle,rgba(27,129,214,.55),rgba(27,129,214,0) 65%)")
el("blob2", "blob", "left:260px;top:900px;width:1200px;height:1200px;background:radial-gradient(circle,rgba(62,161,239,.32),rgba(62,161,239,0) 62%)")
go("#blob1", 0, TOTAL, "sine.inOut", x=320, y=420)
go("#blob2", 0, TOTAL, "sine.inOut", x=-380, y=-520)
for i in range(30):
    r = rng.uniform(5, 22)
    el(f"pt{i}", "pt", f"left:{rng.uniform(0, 1080):.0f}px;top:0;width:{r:.0f}px;height:{r:.0f}px;opacity:{rng.uniform(.25, .7):.2f}")
    t, y0 = -rng.uniform(0, 20), 1980
    while t < TOTAL:
        d = rng.uniform(16, 30)
        state[f"#pt{i}"] = {"y": y0}
        go(f"#pt{i}", max(0, t), d if t >= 0 else d + t, "none", y=-60)
        if t < 0:
            frac = -t / d
            tl[-1] = tl[-1].replace(f'{{"y": {y0}}}', f'{{"y": {y0 - (y0 + 60) * frac:.0f}}}')
        t += d

# ------------------------------------------------------------------ poses da Brenda
# b17 abre GRANDE (capa e abertura); 02 = mão no queixo (o músculo) · 18 = mão na orelha (a articulação)
# 22 = atenção (resolver o motivo) · 09 = celular (WhatsApp)
PHONE = {}
BIG_H, BIG_TOP = 1600, 334
iw, ih = size("brenda-17")
el("big", "brenda", f"left:{round((1080 - BIG_H * iw / ih) / 2)}px;top:{BIG_TOP}px;height:{BIG_H}px;transform-origin:50% 0",
   f'<img src="assets/img/brenda-17.png" style="height:{BIG_H}px">')
init("#big", opacity=1, y=0, scale=1)
BR = {"02": ("brenda-02", 1180), "18": ("brenda-18", 1180), "22": ("brenda-22", 1180), "09": ("brenda-09", 1180)}
for k, (f, h) in BR.items():
    iw, ih = size(f)
    left = 1080 - round(h * iw / ih) + 120 + {"22": 70, "02": 90}.get(k, 0)
    tela, org = "", None
    if k == "09":                 # o WhatsApp na tela do celular (pose 09 do banco)
        bx0, by0, bx1, by1, _, _ = map(int, open("build/tela-bbox.txt").read().split())
        sx, sy, sw_, sh_ = bx0 * h / ih, by0 * h / ih, (bx1 - bx0) * h / ih, (by1 - by0) * h / ih
        PHONE.update(cx=sx + sw_ / 2, cy=sy + sh_ / 2, left=left, top=1920 - h)
        org = (PHONE["cx"], PHONE["cy"])
        tela = (f'<div id="scr" style="left:{sx:.1f}px;top:{sy:.1f}px;width:{sw_:.1f}px;height:{sh_:.1f}px">'
                '<div class="wtop"><img src="assets/img/avatar.png"><div><b>Dra. Brenda Rodrigues</b><span>online</span></div></div>'
                '<div class="wchat"><div class="wday">HOJE</div>'
                '<div class="wb wl" id="wb1">Qual é o lado que você evita?<s>10:42</s></div>'
                '<div class="wb wr" id="wb2"><i></i><i></i><i></i></div></div>'
                '<div class="win"><span>Mensagem</span><em></em></div></div>')
    el(f"b{k}", "brenda", f"left:{left}px;top:{1920 - h}px;height:{h}px" +
       (f";transform-origin:{org[0]:.1f}px {org[1]:.1f}px" if org else ""),
       f'<img src="assets/img/{f}.png" style="height:{h}px">{tela}')
    init(f"#b{k}", opacity=0, y=900)


def entra(k, t):
    setp(f"#b{k}", t - 0.02, y=900)
    go(f"#b{k}", t, 0.55, "power3.out", opacity=1, y=0)


def sai(k, t):
    go(f"#b{k}", t, 0.35, "power2.in", opacity=0, y=900)


# ------------------------------------------------------------------ o placar: 1/4 a 4/4, sem tempo
# da vez = amarelo + maior + borda; já falado = mais apagado. O número fica sempre no selo (nada de ✓: não é "resolvido")
PASSOS = [("DESGASTE", DESG_SVG), ("MÚSCULO", MUSC_SVG), ("ARTICULAÇÃO", ARTI_SVG), ("TÁRTARO", TART_SVG)]
CNT_Y0, CNT_Y1 = 900, 410
cnt = "".join(f'<div class="ps" id="p{i}"><div class="pic">{svg}</div><span>{n}</span><i>{i}/4</i></div>'
              for i, (n, svg) in enumerate(PASSOS, 1))
el("cnt", "cnt", at_center(540, CNT_Y0), cnt)
init("#cnt", xPercent=-50, yPercent=-50, opacity=0, y=0, x=0, scale=0.9)
for i in range(1, 5):
    init(f"#p{i}", y=0, scale=1)


def passo(n, t):
    for i in range(1, 5):
        cls = "ps" + (" on" if i == n else "") + (" feito" if i < n else "")
        tl.append(f'tl.set("#p{i}", {{attr: {{class: "{cls}"}}}}, {t:.3f});')
        go(f"#p{i}", t, 0.35, "back.out(2)", scale=1.12 if i == n else 1)


# ------------------------------------------------------------------ 0 · gancho (Brenda grande = capa do feed)
el("hk", "", at_center(540, 392), "MASTIGANDO SÓ<br>DE <em>UM LADO</em>")
init("#hk", xPercent=-50, yPercent=-50, opacity=1, y=0, scale=1)
chip("cAno", "POR UM ANO?", 480, 1180, "c-yellow")
pop("#cAno", T["ano"] - 0.15)
out("#cAno", T["falta1"] - 0.25, 0.2)
chip("cFal", "FALTA UM DENTE OU DÓI", 480, 1180, "c-white small")
pop("#cFal", T["falta1"] - 0.05)
out("#cFal", T["conto"] - 0.25, 0.2)
pulse("#hk", T["mastigando"], T["falta1"] - 0.3, 0.5, 1, 1.06)
# o placar nasce no peito da Brenda no "eu te conto" e quica no "se somar"; depois sobe para o topo
setp("#cnt", T["conto"] - 0.02, scale=0.5)
go("#cnt", T["conto"], 0.45, "back.out(1.8)", opacity=1, scale=0.9)
for i in range(1, 5):
    go(f"#p{i}", T["somar"] + (i - 1) * 0.09, 0.25, "back.out(2.5)", y=-24)
    go(f"#p{i}", T["somar"] + (i - 1) * 0.09 + 0.25, 0.25, "sine.in", y=0)
chip("cSom", "O QUE COSTUMA SE SOMAR", 480, 1180, "c-yellow small")
pop("#cSom", T["somar"] - 0.35)
X0 = T["no"] - 0.25
out("#cSom", X0, 0.25)
go("#big", X0, 0.5, "power2.in", y=1300, opacity=0)
go("#hk", X0, 0.3, "power2.in", opacity=0, y=30)            # sai por baixo (subir cruzaria y 290)
go("#cnt", X0, 0.6, "power3.inOut", y=CNT_Y1 - CNT_Y0, scale=0.86)

# ------------------------------------------------------------------ no começo, nada: a arcada com um lado só trabalhando
AW, AH, AY = 800, 520, 830
card("arc", 540, AY, AW, AH,
     '<img src="assets/img/q1-arcada.png">'
     '<div class="hz" id="hz"><b>LADO PARADO</b></div>'
     '<div class="lbom" id="lbom"><b>LADO QUE MASTIGA</b></div>')
init("#hz", opacity=0)
init("#lbom", opacity=0)
setp("#arc", T["no"] - 0.27, y=140)
go("#arc", T["no"] - 0.25, 0.5, "power3.out", opacity=1, y=0)
CY1, CY2 = AY + AH / 2 + 70, AY + AH / 2 + 180
chip("cCom", "NO COMEÇO, NADA", 480, CY1, "c-white")
pop("#cCom", T["comeco"] - 0.05)
out("#cCom", T["lado2"] - 0.25, 0.2)
go("#hz", T["lado2"] - 0.15, 0.4, "power2.out", opacity=1)          # o lado parado: hachura + rótulo (não só escuro)
go("#lbom", T["lado2"] - 0.1, 0.4, "power2.out", opacity=1)
chip("cBom", "O LADO BOM DÁ CONTA", 480, CY1, "c-yellow small")
pop("#cBom", T["bom"] - 0.1)
chip("cNem", "E VOCÊ NEM PERCEBE QUE ESCOLHEU", 480, CY2, "c-white small narrow")
pop("#cNem", T["nem"] - 0.05)
TA = T["primeira"] - 0.3
for s in ("#cBom", "#cNem"):
    out(s, TA, 0.2)
go("#arc", TA, 0.3, "power2.in", opacity=0, y=140)

# ------------------------------------------------------------------ 1/4 · desgaste (sem pose: o card no centro)
passo(1, T["primeira"] - 0.1)
QW = 560
QY = 820
card("mol", 540, QY, QW, QW, '<img src="assets/img/q2-molares.png">' + ring("r_mol", 50, 40, 250))
setp("#mol", T["primeira"] - 0.22, y=140)
go("#mol", T["primeira"] - 0.2, 0.5, "power3.out", opacity=1, y=0)
QC1, QC2 = QY + QW / 2 + 70, QY + QW / 2 + 180
chip("cDes", "DESGASTE", 480, QC1, "c-yellow")
pop("#cDes", T["desgaste1"] - 0.05)
out("#cDes", T["trabalha1"] - 0.3, 0.2)
chip("cDoi", "O LADO QUE TRABALHA POR DOIS", 480, QC1, "c-white small narrow")
pop("#cDoi", T["trabalha1"] - 0.15)
anel("r_mol", T["tende"] - 0.1, T["segunda"] - 0.3)
chip("cTen", "TENDE A GASTAR MAIS", 480, QC2, "c-yellow small")
pop("#cTen", T["tende"] - 0.05)
for s in ("#cDoi", "#cTen"):
    out(s, T["desgaste2"] - 0.2, 0.2)
chip("cDsg", "E O DESGASTE FICA DESIGUAL", 480, QC1, "c-white small narrow")
pop("#cDsg", T["desgaste2"] - 0.05)
TB = T["segunda"] - 0.3
out("#cDsg", TB, 0.2)
go("#mol", TB, 0.3, "power2.in", opacity=0, scale=0.9)

# ------------------------------------------------------------------ 2/4 · músculo (pose 02, mão no queixo)
passo(2, T["segunda"] - 0.1)
entra("02", T["segunda"] - 0.15)
CW, CX, CY = 520, 400, 820
CHX, CH1, CH2 = 450, CY + CW / 2 + 70, CY + CW / 2 + 180
card("mus", CX, CY, CW, CW, '<img src="assets/img/q3-musculo.png">' + ring("r_mus", 45, 56, 260))
setp("#mus", T["segunda"] - 0.12, y=140)
go("#mus", T["segunda"] - 0.1, 0.5, "power3.out", opacity=1, y=0)
chip("cMus", "MÚSCULO", CHX, CH1, "c-yellow")
pop("#cMus", T["musculo"] - 0.05)
out("#cMus", T["trabalha2"] - 0.3, 0.2)
anel("r_mus", T["musculo"], T["vezes"] - 0.2)
chip("cTr2", "UM LADO TRABALHA MAIS", CHX, CH1, "c-white small")
pop("#cTr2", T["trabalha2"] - 0.15)
t = T["trabalha2"] + 0.1                               # mastigando: o card aperta no ritmo, só no trecho do músculo
while t < T["tenso"] - 0.3:
    go("#mus", t, 0.18, "sine.inOut", scaleY=0.97)
    go("#mus", t + 0.18, 0.18, "sine.inOut", scaleY=1)
    t += 0.42
chip("cTns", "PODE FICAR MAIS TENSO", CHX, CH2, "c-white small")
pop("#cTns", T["pode"] - 0.05)
for s in ("#cTr2", "#cTns"):
    out(s, T["vezes"] - 0.25, 0.2)
chip("cFor", "ÀS VEZES, ATÉ MAIS FORTE DE UM LADO SÓ", CHX, CH1, "c-white small narrow")
pop("#cFor", T["vezes"] - 0.05)
TC = T["terceira"] - 0.25
out("#cFor", TC, 0.2)
go("#mus", TC, 0.3, "power2.in", opacity=0, scale=0.9)
sai("02", TC)

# ------------------------------------------------------------------ 3/4 · articulação (pose 18, mão na orelha)
passo(3, T["terceira"] - 0.1)
entra("18", TC + 0.1)
card("atm", CX, CY, CW, CW, '<img src="assets/img/q4-atm.png">' + ring("r_atm", 53, 42, 180) +
     '<div class="burst" id="burst">' + "".join(f'<i style="rotate:{a}deg"></i>' for a in range(0, 360, 45)) + '</div>')
init("#burst", xPercent=-50, yPercent=-50, opacity=0, scale=0.4)
setp("#atm", T["terceira"] - 0.12, y=140)
go("#atm", T["terceira"] - 0.1, 0.5, "power3.out", opacity=1, y=0)
chip("cArt", "ARTICULAÇÃO", CHX, CH1, "c-yellow")
pop("#cArt", T["articulacao"] - 0.05)
out("#cArt", T["frente"] - 0.3, 0.2)
anel("r_atm", T["frente"] - 0.1, T["dizer"] - 0.3)
chip("cFre", "NA FRENTE DO OUVIDO", CHX, CH1, "c-white small")
pop("#cFre", T["frente"] - 0.1)
out("#cFre", T["quem1"] - 0.25, 0.2)
chip("cQue", "QUEM MASTIGA SÓ DE UM LADO", CHX, CH1, "c-white small narrow")
pop("#cQue", T["quem1"] - 0.05)
chip("cApa", "APARECE MAIS ENTRE QUEM TEM ESTALO E DOR ALI", CHX, CH2 + 20, "c-yellow small narrow")
pop("#cApa", T["aparece"] - 0.05)
# o estalo: raios no ponto da articulação e o card dá um tranco
for k in range(2):
    t = T["estalo"] + k * 0.45
    setp("#burst", t - 0.01, scale=0.4, opacity=1)
    go("#burst", t, 0.4, "power2.out", scale=1.5, opacity=0)
go("#atm", T["estalo"], 0.06, "sine.inOut", x=8)
go("#atm", T["estalo"] + 0.06, 0.06, "sine.inOut", x=-6)
go("#atm", T["estalo"] + 0.12, 0.08, "sine.out", x=0)
for s in ("#cQue", "#cApa"):
    out(s, T["dizer"] - 0.35, 0.2)
chip("cPri", "QUEM VEIO PRIMEIRO? NÃO DÁ PRA DIZER", CHX, CH1, "c-white small narrow")
pop("#cPri", T["dizer"] - 0.2)
chip("cSin", '<span class="ico ok">✓</span>É SINAL PRA AVALIAR', CHX, CH2 + 20, "c-ok small")
pop("#cSin", T["sinal"] - 0.1)
TD = T["quarta"] - 0.25
for s in ("#cPri", "#cSin"):
    out(s, TD, 0.2)
go("#atm", TD, 0.3, "power2.in", opacity=0, scale=0.9)
sai("18", TD)

# ------------------------------------------------------------------ 4/4 · tártaro (a mesma arcada de frente; o tártaro do lado parado)
passo(4, T["quarta"] - 0.1)
card("tar", 540, AY, AW, AH, '<img src="assets/img/q5-tartaro.png">' + ring("r_tar", 72, 38, 280) +
     '<div class="lbl lr" id="lpar"><b>LADO PARADO</b></div>')
init("#lpar", opacity=0)
setp("#tar", T["quarta"] - 0.12, y=140)
go("#tar", T["quarta"] - 0.1, 0.5, "power3.out", opacity=1, y=0)
chip("cTar", "TÁRTARO", 480, CY1, "c-yellow")
pop("#cTar", T["tartaro"] - 0.05)
out("#cTar", T["parado"] - 0.35, 0.2)
go("#lpar", T["parado"] - 0.2, 0.35, "power2.out", opacity=1)
anel("r_tar", T["parado"] - 0.1, T["mastigacao"] - 0.2)
chip("cJun", "O LADO PARADO COSTUMA JUNTAR MAIS", 480, CY1, "c-white small narrow")
pop("#cJun", T["parado"] - 0.15)
out("#cJun", T["mastigacao"] - 0.25, 0.2)
chip("cVar", "A MASTIGAÇÃO VARRE UM POUCO", 480, CY1, "c-white small narrow")
pop("#cVar", T["mastigacao"] - 0.05)
chip("cEsc", '<span class="ico ok">✓</span>QUEM LIMPA DE VERDADE É A ESCOVA', 480, CY2 + 20, "c-ok small narrow")
pop("#cEsc", T["limpa"] - 0.15)
TE = T["faz"] - 0.3
for s in ("#cVar", "#cEsc"):
    out(s, TE, 0.2)
go("#tar", TE, 0.3, "power2.in", opacity=0, scale=0.9)
go("#cnt", TE, 0.3, "power2.in", opacity=0)

# ------------------------------------------------------------------ o teste: a maçã
MW, MY = 560, 760
card("mac", 540, MY, MW, MW, '<img src="assets/img/q6-maca.png">' + ring("r_mac", 77, 40, 190))
pop("#mac", T["faz"] - 0.1, 0.5, 0.6)
MC1, MC2 = MY + MW / 2 + 70, MY + MW / 2 + 180
chip("cFaz", "FAZ O TESTE AGORA", 480, 380, "c-yellow")
pop("#cFaz", T["faz"] - 0.05)
chip("cMor", "MORDE ALGUMA COISA", 480, MC1, "c-white small")
pop("#cMor", T["morde"] - 0.05)
anel("r_mac", T["morde"] + 0.1, T["resposta"] - 0.2)
go("#mac", T["morde"] + 0.05, 0.08, "sine.inOut", scale=0.95)       # a mordida
go("#mac", T["morde"] + 0.13, 0.25, "back.out(2)", scale=1)
out("#cMor", T["repara"] - 0.25, 0.2)
chip("cRep", "DE QUE LADO VOCÊ FOI?", 480, MC1, "c-yellow small")
pop("#cRep", T["repara"] - 0.05)
chip("cEsq", "◀ ESQUERDA", 290, MC2, "c-white small")
chip("cDir", "DIREITA ▶", 680, MC2, "c-white small")
pop("#cEsq", T["lado8"] - 0.05)
pop("#cDir", T["lado8"] + 0.25)
for s in ("#cRep", "#cEsq", "#cDir"):
    out(s, T["resposta"] - 0.25, 0.2)
chip("cRes", "A RESPOSTA VEIO NA HORA?", 480, MC1, "c-white small")
pop("#cRes", T["resposta"] - 0.05)
chip("cFav", "VOCÊ TEM UM LADO FAVORITO", 480, MC2, "c-yellow small")
pop("#cFav", T["favorito"] - 0.35)
TF = T["resolver"] - 0.3
for s in ("#cFaz", "#cRes", "#cFav"):
    out(s, TF, 0.2)
go("#mac", TF, 0.3, "power2.in", opacity=0, scale=0.9)

# ------------------------------------------------------------------ resolver o motivo (pose 22)
entra("22", TF + 0.05)
DCX = 330
chip("cMot", "RESOLVER O MOTIVO", DCX, 640, "c-yellow small")
pop("#cMot", T["resolver"] - 0.05)
chip("cDtf", "O DENTE QUE FALTA", DCX, 770, "c-white small")
pop("#cDtf", T["dente2"] - 0.05)
chip("cOqd", "OU O QUE DÓI", DCX, 890, "c-white small")
pop("#cOqd", T["doi2"] - 0.25)
chip("cSim", "COSTUMA SER MAIS SIMPLES", DCX, 1030, "c-white small narrow2")
pop("#cSim", T["costuma3"] - 0.05)
chip("cCon", "DO QUE CONSERTAR O QUE O TEMPO SOMOU", DCX, 1200, "c-white small narrow2")
pop("#cCon", T["consertar"] - 0.05)
TQ = T["chama"] - 0.3
for s in ("#cMot", "#cDtf", "#cOqd", "#cSim", "#cCon"):
    out(s, TQ, 0.25)
go("#b22", TQ, 0.15, "none", opacity=0)

# ------------------------------------------------------------------ chamada: o WhatsApp no celular (igual ao S12/S14)
setp("#b09", T["chama"] - 0.32, y=0)
go("#b09", T["chama"] - 0.3, 0.15, "none", opacity=1)
el("wa", "wa", at_center(310, 790), WA_SVG + '<span>WhatsApp</span>')
init("#wa", xPercent=-50, yPercent=-50, opacity=0)
pop("#wa", T["whatsapp"] - 0.05, 0.4, 0.3)
init("#scr", opacity=0)
init("#wb1", opacity=0, y=10)
init("#wb2", opacity=0, y=10)
go("#scr", T["chama"] - 0.1, 0.3, "power1.out", opacity=1)
ZI = T["conta2"] - 0.35
END = VO_END + 0.85
ZO = VO_END + 0.35
pcx, pcy = PHONE["left"] + PHONE["cx"], PHONE["top"] + PHONE["cy"]
go("#b09", ZI, 0.55, "power3.inOut", scale=2.3, x=round(540 - pcx), y=round(900 - pcy))
go("#wa", ZI, 0.25, "power2.in", opacity=0)
go("#wb1", T["conta2"] + 0.05, 0.35, "back.out(2)", opacity=1, y=0)
go("#wb2", T["evita"] - 0.1, 0.3, "back.out(2)", opacity=1, y=0)
for k in range(3):
    init(f"#wb2 i:nth-child({k + 1})", y=0)
    t = T["evita"] + 0.25 + k * 0.1
    while t < ZO - 0.2:
        go(f"#wb2 i:nth-child({k + 1})", t, 0.15, "sine.out", y=-3)
        go(f"#wb2 i:nth-child({k + 1})", t + 0.15, 0.15, "sine.in", y=0)
        t += 0.6
go("#b09", ZO, 0.45, "power3.inOut", scale=1, x=0, y=0, opacity=0)
# volta para o quadro de abertura (loop): a Brenda grande e o gancho
setp("#big", END - 0.1, y=0, scale=1)
go("#big", END - 0.05, 0.45, "power3.out", opacity=1)
setp("#hk", END - 0.05, y=30)
go("#hk", END, 0.45, "power3.out", opacity=1, y=0)

# ------------------------------------------------------------------ legendas (palavra por palavra; centradas em x 480)
KW = {"ano", "mastigando", "lado", "dente", "dói", "somar", "nada", "bom", "escolheu", "desgaste", "dois", "gastar",
      "desigual", "músculo", "tenso", "forte", "articulação", "ouvido", "estalo", "dor", "avaliar", "tártaro", "parado",
      "juntar", "varrer", "escova", "teste", "morde", "favorito", "motivo", "simples", "tempo", "desequilíbrio",
      "whatsapp", "evita"}
groups, cur = [], []
for w in words:
    if cur and len(" ".join(x["w"] for x in cur + [w])) > 22:     # cabe entre x 60 e 900 a 56 px
        groups.append(cur); cur = []
    cur.append(w)
    if w["w"][-1] in ",.?!;:" or len(cur) >= 4:
        groups.append(cur); cur = []
if cur:
    groups.append(cur)
KWN = {norm(k) for k in KW}
for gi, g in enumerate(groups):
    spans = []
    for wi, w in enumerate(g):
        txt = w["w"].rstrip(",.;:") if not w["w"].endswith("?") else w["w"]
        cls = "kw" if norm(w["w"]) in KWN else ""
        spans.append(f'<span id="w{gi}_{wi}" class="{cls}">{txt}</span>')
        init(f"#w{gi}_{wi}", opacity=0.38, y=0, scale=1)
        go(f"#w{gi}_{wi}", w["s"] - 0.02, 0.14, "power2.out", opacity=1, scale=1.06)
        go(f"#w{gi}_{wi}", max(w["e"], w["s"] + 0.13), 0.14, "power2.out", scale=1)
    el(f"cap{gi}", "cap", "", " ".join(spans))
    init(f"#cap{gi}", xPercent=-50, yPercent=-50, opacity=0)
    tl.append(f'tl.set("#cap{gi}", {{opacity: 1}}, {g[0]["s"] - 0.05:.3f});')
    t_off = groups[gi + 1][0]["s"] - 0.06 if gi + 1 < len(groups) else VO_END + 0.3
    tl.append(f'tl.set("#cap{gi}", {{opacity: 0}}, {t_off:.3f});')

# ------------------------------------------------------------------ som
SFX = [(0.0, "whoosh-cine", .2), (T["ano"] - .15, "pop-1", .22), (T["falta1"], "pop-3", .2), (T["conto"], "pop-3", .22),
       (T["somar"], "tick-1", .22), (T["somar"] + .09, "tick-1", .2), (T["somar"] + .18, "tick-1", .2), (T["somar"] + .27, "tick-1", .2),
       (X0, "whoosh-1", .2), (T["comeco"], "pop-1", .18), (T["lado2"] - .15, "whoosh-3", .14), (T["bom"], "pop-3", .2),
       (T["nem"], "pop-1", .16), (TA, "whoosh-1", .18), (T["primeira"] - .1, "ding-1", .16), (T["desgaste1"], "pop-3", .22),
       (T["trabalha1"], "pop-1", .18), (T["tende"], "pop-1", .18), (T["desgaste2"], "pop-3", .18), (TB, "whoosh-1", .2),
       (T["segunda"] - .1, "ding-1", .16), (T["musculo"], "pop-3", .22), (T["trabalha2"], "pop-1", .18),
       (T["pode"], "pop-1", .18), (T["vezes"], "pop-3", .18), (TC, "whoosh-1", .2), (T["terceira"] - .1, "ding-1", .16),
       (T["articulacao"], "pop-3", .22), (T["frente"], "pop-1", .18), (T["quem1"], "pop-1", .16), (T["aparece"], "pop-3", .18),
       (T["estalo"], "impact-1", .16), (T["estalo"] + .45, "impact-1", .12), (T["dizer"] - .2, "pop-1", .18),
       (T["sinal"] - .1, "tech-ui-confirm", .16), (TD, "whoosh-1", .2), (T["quarta"] - .1, "ding-1", .16),
       (T["tartaro"], "pop-3", .22), (T["parado"], "pop-1", .18), (T["mastigacao"], "pop-1", .18),
       (T["limpa"] - .15, "tech-ui-confirm", .16), (TE, "whoosh-2", .18), (T["faz"], "pop-3", .24),
       (T["morde"] + .05, "impact-1", .18), (T["repara"], "pop-1", .18), (T["foi"], "pop-1", .16),
       (T["resposta"], "pop-1", .18), (T["favorito"] - .35, "ding-1", .18), (TF, "whoosh-1", .2),
       (T["resolver"], "pop-3", .2), (T["dente2"], "pop-1", .18), (T["doi2"] - .25, "pop-1", .18),
       (T["costuma3"], "pop-1", .18), (T["consertar"], "pop-3", .18), (TQ, "whoosh-2", .18),
       (T["whatsapp"], "tech-notification-2", .28), (T["conta2"] + .05, "tech-notification-2", .22),
       (END - .05, "whoosh-2", .18)]
dur = {}
for _, s, _v in SFX:
    if s not in dur:
        dur[s] = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"assets/sfx/{s}.wav"]).decode())
audio = [f'<audio id="vo" src="assets/voice.m4a" data-start="0" data-duration="{VO_END + 0.5:.3f}" data-track-index="10" data-volume="1"></audio>',
         f'<audio id="bed" src="assets/music/bed.mp3" data-start="0" data-duration="{TOTAL}" data-media-start="0" data-track-index="20" data-volume="0.07"></audio>']
for i, (t, s, v) in enumerate(SFX):
    audio.append(f'<audio id="sfx{i}" src="assets/sfx/{s}.wav" data-start="{max(0, t):.3f}" data-duration="{min(dur[s], TOTAL - t):.3f}" data-track-index="{12 + i % 6}" data-volume="{v}"></audio>')

CSS = """
@font-face { font-family: Montserrat; src: url(assets/fonts/montserrat-latin.woff2) format("woff2"); font-weight: 100 900; }
html, body { margin: 0; background: #0B2540; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: Poppins, Montserrat, sans-serif;
  background: linear-gradient(180deg, #0A223C 0%, #123A63 52%, #0D2C4D 100%); }
.blob { position: absolute; border-radius: 50%; }
.pt { position: absolute; border-radius: 50%; background: rgba(143,198,245,.9); }
.card { position: absolute; border-radius: 46px; overflow: hidden; border: 6px solid rgba(255,255,255,.92);
  box-shadow: 0 34px 90px rgba(0,0,0,.5); background: #D6EAF8; }
.card > img { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
.chip { position: absolute; white-space: normal; width: max-content; max-width: 720px; text-align: center; font-weight: 800; font-size: 44px; letter-spacing: 1px; padding: 18px 38px;
  border-radius: 999px; box-shadow: 0 14px 34px rgba(0,0,0,.35); line-height: 1.1; z-index: 4; }
.chip.small { font-size: 38px; padding: 15px 30px; }
.chip.narrow { max-width: 600px; border-radius: 40px; }
.chip.narrow2 { max-width: 400px; border-radius: 36px; }
.c-white { background: #fff; color: #123A63; }
.c-ok { background: #fff; color: #123A63; border: 5px solid #2EAA6E; }
.c-yellow { background: #FFD54A; color: #123A63; }
.chip .ico { display: inline-block; width: 52px; height: 52px; border-radius: 50%; margin-right: 18px; text-align: center;
  line-height: 52px; font-size: 34px; color: #fff; vertical-align: 2px; background: #E24A4A; }
.chip .ico.ok { background: #2EAA6E; }
.brenda { position: absolute; }
.brenda img { display: block; filter: drop-shadow(0 0 40px rgba(0,0,0,.35)); }
.cnt { position: absolute; display: flex; gap: 14px; padding: 16px 20px; border-radius: 34px; background: rgba(8,28,50,.8);
  border: 3px solid rgba(143,198,245,.55); box-shadow: 0 20px 50px rgba(0,0,0,.4); z-index: 5; }
.ps { position: relative; width: 196px; height: 124px; border-radius: 20px; background: #fff; color: #123A63; text-align: center;
  box-sizing: border-box; border: 4px solid #fff; }
.ps .pic { height: 58px; margin-top: 10px; line-height: 0; }
.ps span { display: block; font-size: 22px; font-weight: 800; letter-spacing: .5px; margin-top: 6px; color: #4A6A8C; white-space: nowrap; }
.ps i { position: absolute; right: -14px; top: -14px; min-width: 50px; height: 42px; border-radius: 21px; background: #123A63; color: #fff;
  font-style: normal; font-weight: 800; font-size: 20px; line-height: 42px; border: 3px solid #fff; padding: 0 6px; box-sizing: border-box; }
.ps.on { background: #FFD54A; border: 6px solid #123A63; box-shadow: 0 0 0 5px #FFD54A, 0 0 30px rgba(255,213,74,.8); }
.ps.on span { color: #123A63; }
.ps.feito { background: rgba(255,255,255,.5); border-color: rgba(255,255,255,.5); }
.ring { position: absolute; width: 170px; height: 170px; border-radius: 50%; border: 9px solid #FFD54A;
  box-shadow: 0 0 30px rgba(255,213,74,.8), inset 0 0 20px rgba(255,213,74,.5); box-sizing: border-box; }
/* o lado parado: hachura diagonal + véu + rótulo (forma e texto, não só cor) */
.hz { position: absolute; left: 50%; top: 0; width: 50%; height: 100%; box-sizing: border-box; border-left: 6px dashed #123A63;
  background: repeating-linear-gradient(135deg, rgba(18,58,99,.55) 0 12px, rgba(18,58,99,.12) 12px 30px); }
.hz b, .lbom b, .lbl b { position: absolute; top: 22px; white-space: nowrap; font-weight: 800; font-size: 30px; letter-spacing: 1px;
  padding: 8px 20px; border-radius: 999px; }
.hz b { right: 22px; background: #123A63; color: #fff; border: 3px dashed #fff; }
.lbom { position: absolute; left: 0; top: 0; width: 50%; height: 100%; }
.lbom b { left: 22px; background: #FFD54A; color: #123A63; border: 3px solid #123A63; }
.lbl { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
.lbl.lr b { right: 22px; background: #123A63; color: #fff; border: 3px dashed #fff; }
.burst { position: absolute; left: 53%; top: 42%; width: 240px; height: 240px; }
.burst i { position: absolute; left: 114px; top: 0; width: 12px; height: 56px; border-radius: 6px; background: #FFD54A;
  transform-origin: 6px 120px; box-shadow: 0 0 0 3px #123A63; }
.wa { position: absolute; white-space: nowrap; background: #25D366; color: #fff; font-weight: 800; font-size: 54px; padding: 20px 46px 20px 28px;
  border-radius: 999px; box-shadow: 0 0 0 10px rgba(37,211,102,.25), 0 20px 50px rgba(0,0,0,.4); display: flex; align-items: center; gap: 18px; }
#scr { position: absolute; overflow: hidden; background: #EFE7DE; font-family: Poppins, sans-serif;
  -webkit-mask-image: url(assets/img/tela-mask.png); -webkit-mask-size: 100% 100%; mask-image: url(assets/img/tela-mask.png); mask-size: 100% 100%; }
#scr .wtop { position: absolute; left: 0; right: 0; top: 0; height: 40px; background: #008069; display: flex; align-items: flex-end;
  gap: 4px; padding: 0 5px 5px; box-sizing: border-box; color: #fff; }
#scr .wtop img { width: 17px; height: 17px; border-radius: 50%; display: block; }
#scr .wtop b { display: block; font-size: 7px; line-height: 1.1; font-weight: 700; white-space: nowrap; }
#scr .wtop span { display: block; font-size: 5px; opacity: .85; }
#scr .wchat { position: absolute; left: 0; right: 0; top: 40px; bottom: 22px; padding: 6px 5px;
  background: radial-gradient(circle at 20% 30%, rgba(0,0,0,.04) 1px, transparent 2px) 0 0/12px 12px, #EFE7DE; }
#scr .wday { margin: 0 auto 6px; width: max-content; font-size: 4.6px; color: #54656F; background: #fff; padding: 1.5px 5px; border-radius: 4px; }
#scr .wb { position: relative; max-width: 84px; font-size: 7.6px; line-height: 1.25; padding: 4px 6px 7px; border-radius: 6px;
  margin-bottom: 5px; color: #111B21; box-shadow: 0 1px 1px rgba(0,0,0,.12); }
#scr .wb s { position: absolute; right: 4px; bottom: 1.5px; font-size: 3.8px; color: #667781; text-decoration: none; }
#scr .wl { background: #fff; border-top-left-radius: 1px; }
#scr .wr { background: #D9FDD3; margin-left: auto; width: max-content; border-top-right-radius: 1px; display: flex; gap: 2.5px; padding: 5px 6px; }
#scr .wr i { display: block; width: 4px; height: 4px; border-radius: 50%; background: #667781; }
#scr .win { position: absolute; left: 4px; right: 4px; bottom: 4px; height: 15px; display: flex; align-items: center; gap: 3px; }
#scr .win span { flex: 1; height: 15px; border-radius: 8px; background: #fff; font-size: 5.4px; color: #8696A0; line-height: 15px; padding-left: 6px; }
#scr .win em { width: 15px; height: 15px; border-radius: 50%; background: #00A884; display: block; }
.cap { position: absolute; left: 480px; top: 1420px; max-width: 840px; text-align: center; font-weight: 700; font-size: 56px;
  line-height: 1.15; color: #fff; background: rgba(8,28,50,.72); padding: 14px 34px 18px; border-radius: 28px; white-space: nowrap; z-index: 6; }
.cap span { display: inline-block; margin: 0 5px; }
.cap .kw { color: #FFD54A; font-weight: 800; }
#hk { position: absolute; text-align: center; font-weight: 800; font-size: 76px; line-height: 1.08; color: #fff; text-shadow: 0 10px 40px rgba(0,0,0,.45); white-space: nowrap; }
#hk em { font-style: normal; color: #FFD54A; }
#grain { position: absolute; inset: 0; background: url(assets/grain.png); background-size: 480px; opacity: .05; mix-blend-mode: overlay; pointer-events: none; }
#vig { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.35) 100%); pointer-events: none; }
"""

css0 = "".join(f"{k} {{ " + "; ".join(f"{a}: {b}" for a, b in v.items()) + " }\n" for k, v in CSS0.items() if v)
page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23123A63'/%3E%3Ctext x='32' y='44' font-size='30' text-anchor='middle' fill='%23FFD54A' font-family='Arial' font-weight='700'%3ER13%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="assets/fonts/poppins.css">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}{css0}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{TOTAL}" data-fps="30">
{chr(10).join(html)}
<div id="grain"></div><div id="vig"></div>
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
open("index.html", "w").write(page)
print(f"index.html: {TOTAL}s, {len(html)} elementos, {len(tl)} linhas de timeline, {len(groups)} legendas, {len(SFX)} sfx")
print({k: round(v, 2) for k, v in T.items()})

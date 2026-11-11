#!/usr/bin/env python3
"""Importa uma gravação inteira para a Sala de revisão.

1. Transcreve (ou reaproveita) a gravação já recortada e separa as TOMADAS pelas pausas.
2. Casa cada tomada com um gancho (H1, H2…), um bloco do corpo ou um final (F1…) do roteiro aprovado
   (gravacao-2026-10-24/textos-validados.md). Repetições da mesma fala viram opções lado a lado na mesma faixa.
3. O que não casa com nada (combinações, "ficou bom?") vai para a faixa "Fora do roteiro".
4. Escreve/atualiza o vídeo em projeto.json (substitui o vídeo de mesmo código) e gera miniaturas.

Uso: python3 importar.py <codigo> <video_recortado.mp4> [--palavras words.json] [--looks pasta_com_looks]
Ex.:  python3 importar.py P1 teste-luz-2026-10-24/brenda2/brenda-preto-cinema.mp4 \\
          --palavras teste-luz-2026-10-24/brenda2/words.json --looks teste-luz-2026-10-24/brenda2/looks
(caminhos relativos à pasta videos/)"""
import argparse, difflib, json, re, subprocess, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
ROTEIRO = RAIZ / "gravacao-2026-10-24/textos-validados.md"
MINI = AQUI / "miniaturas"; MINI.mkdir(exist_ok=True)
PAUSA = 1.2          # silêncio que separa duas tomadas (s)
CASA = 0.42          # semelhança mínima para casar uma tomada com um item do roteiro
FOLGA = (0.25, 0.35) # respiro antes/depois da tomada (s)


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", t).split()


def parecido(a, b):
    """Semelhança por palavras: cobertura do item do roteiro dentro da tomada e vice-versa."""
    wa, wb = norm(a), norm(b)
    if not wa or not wb:
        return 0.0
    m = sum(bl.size for bl in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_matching_blocks())
    return max(m / len(wb) * min(1, len(wa) / len(wb) * 1.6), 2 * m / (len(wa) + len(wb)))


def diferencas(falado, aprovado):
    fa, ap = norm(falado), norm(aprovado)
    sm = difflib.SequenceMatcher(None, ap, fa, autojunk=False); notas = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "replace":
            notas.append(f"\"{' '.join(fa[j1:j2])}\" no lugar de \"{' '.join(ap[i1:i2])}\"")
        elif op == "delete" and i2 - i1 >= 2:
            notas.append(f"faltou \"{' '.join(ap[i1:i2])}\"")
    return "; ".join(notas[:3])


def roteiro(codigo):
    txt = ROTEIRO.read_text()
    secs = re.split(r"\n(?=## \d+\. )", txt)
    sec = next((s for s in secs if re.match(rf"## \d+\. {re.escape(codigo)} ·", s)), None)
    if not sec:
        raise SystemExit(f"código {codigo} não encontrado em {ROTEIRO.name}")
    titulo = re.match(r"## \d+\. [^·]+· (.+?)(?: · |\n)", sec).group(1).strip()
    ganchos = [(h, t) for linha in sec.splitlines() if "sem fala" not in linha      # gancho visual (cena) não tem fala
               for h, t in re.findall(r"^- (H\d+) · .*?\"([^\"]+)\"", linha)]
    blocos = []
    for linha in sec.splitlines():
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cel) >= 3 and re.fullmatch(r"\d+", cel[0]):
            falas = re.findall(r"\"([^\"]+)\"", " ".join(cel[1:]))
            if falas:
                blocos.append((f"b{cel[0]}", f"{cel[0]} · {cel[1]}", max(falas, key=len)))
    fsec = next((s for s in secs if "Finais" in s.split("\n")[0]), "")
    finais = [(f, t) for f, t in re.findall(r"^- (F\d+) · .*?\"([^\"]+)\"", fsec, re.M)]
    return titulo, ganchos, blocos, finais


def tomadas(palavras):
    w = [x for s in json.loads(Path(palavras).read_text())["segments"] for x in s.get("words", [])]
    grupos, atual = [], []
    for x in w:
        if atual and x["start"] - atual[-1]["end"] > PAUSA:
            grupos.append(atual); atual = []
        atual.append(x)
    if atual:
        grupos.append(atual)
    saida = []
    for g in grupos:                      # cada tomada guarda as frases (pontuação do Whisper) para poder ser aparada
        frases, f = [], []
        for x in g:
            f.append(x)
            if re.search(r"[.?!…]\s*$", x["word"]):
                frases.append(f); f = []
        if f:
            frases.append(f)
        saida.append([{"ini": fr[0]["start"], "fim": fr[-1]["end"], "texto": "".join(y["word"] for y in fr).strip()} for fr in frases])
    return saida


def juntar(frases):
    return {"ini": frases[0]["ini"], "fim": frases[-1]["fim"], "texto": " ".join(x["texto"] for x in frases)}


def melhor_janela(frases, itens):
    """Escolhe a sequência contígua de frases da tomada que mais se parece com algum item; devolve (janela, sobras)."""
    melhor = (0, 0, -99, None, None, None, 0, len(frases))
    for i in range(len(frases)):
        for j in range(i + 1, len(frases) + 1):
            tx = juntar(frases[i:j])["texto"]
            for fx, nome, t in itens:
                c = (round(parecido(tx, t), 3), len(norm(t)), -(j - i), fx, nome, t, i, j)   # empate: janela mais curta
                if c[:3] > melhor[:3]:
                    melhor = c
    s, _, _, fx, nome, t, i, j = melhor
    return (s, fx, nome, t, juntar(frases[i:j])), frases[:i] + frases[j:]


def mini(arq, t, nome):
    dst = MINI / f"{nome}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(RAIZ / arq), "-frames:v", "1",
                    "-vf", "scale=180:-2", "-q:v", "4", str(dst)], check=True)
    return f"revisao/miniaturas/{dst.name}"


ap = argparse.ArgumentParser(); ap.add_argument("codigo"); ap.add_argument("video")
ap.add_argument("--palavras"); ap.add_argument("--looks")
a = ap.parse_args()
codigo, video = a.codigo.upper(), a.video
if not a.palavras:
    a.palavras = str((RAIZ / video).with_suffix(".words.json"))
    if not Path(a.palavras).exists():
        subprocess.run(["python3", str(Path(__file__).resolve().parents[2] / ".claude/skills/ghost-editor/scripts/transcribe.py"), str(RAIZ / video),
                        "--out", a.palavras, "--lang", "pt"], check=True)
titulo, ganchos, blocos, finais = roteiro(codigo)
itens = [("gancho", h, t) for h, t in ganchos] + [(bid, nome, t) for bid, nome, t in blocos] + [("final", f, t) for f, t in finais]

faixas = {"gancho": {"id": "gancho", "nome": "Gancho", "escolha": "uma por gancho (cada H vira uma versão para teste no Meta)", "opcoes": []}}
for bid, nome, t in blocos:
    faixas[bid] = {"id": bid, "nome": nome, "escolha": "uma", "aprovado": t, "opcoes": []}
faixas["final"] = {"id": "final", "nome": "Final", "escolha": "uma (anúncio e Reels podem ter finais diferentes)", "opcoes": []}
fora = {"id": "fora", "nome": "Fora do roteiro", "escolha": "conferir (combinações, comentários, falas soltas)", "opcoes": []}
conta = {}
fila = []
for frases in tomadas(Path(RAIZ / a.palavras) if not Path(a.palavras).is_absolute() else a.palavras):
    (s, fx, nome, t, tm), sobras = melhor_janela(frases, itens)
    if s >= CASA:
        fila.append((s, fx, nome, t, tm))
        fila += [(0, None, None, None, sb) for sb in sobras]      # frase colada que não é do gancho/bloco: vira fala solta
    else:
        fila.append((s, fx, nome, t, juntar(frases)))
fila.sort(key=lambda x: x[4]["ini"])
for k, (s, fx, nome, t, tm) in enumerate(fila):
    ini, fim = max(0, tm["ini"] - FOLGA[0]), tm["fim"] + FOLGA[1]
    if s >= CASA:
        chave = nome if fx in ("gancho", "final") else fx
        conta[chave] = conta.get(chave, 0) + 1
        rot = f"{nome} · tomada {conta[chave]}" if fx in ("gancho", "final") else f"Tomada {conta[chave]}"
        oid = re.sub(r"\W+", "-", f"{chave}-t{conta[chave]}".lower())
        faixas[fx]["opcoes"].append({"id": oid, "rotulo": rot, "arquivo": video, "ini": round(ini, 2), "fim": round(fim, 2),
                                     "falado": tm["texto"], "aprovado": t, "nota": diferencas(tm["texto"], t),
                                     "semelhanca": round(s, 2), "miniatura": mini(video, (ini + fim) / 2, f"{codigo}-{oid}".lower())})
    else:
        oid = f"fora-{k}"
        fora["opcoes"].append({"id": oid, "rotulo": f"Fala solta {len(fora['opcoes']) + 1}", "arquivo": video,
                               "ini": round(ini, 2), "fim": round(fim, 2), "falado": tm["texto"],
                               "nota": f"não casou com o roteiro (semelhança {s:.2f} com {nome})" if nome else "",
                               "miniatura": mini(video, (ini + fim) / 2, f"{codigo}-{oid}".lower())})

lista = list(faixas.values())
for f in lista:
    if not f["opcoes"]:
        f["pendente"] = True
        if f["id"] == "gancho":
            f["aprovado"] = " · ".join(f"{h}: {t}" for h, t in ganchos)
        if f["id"] == "final":
            f["aprovado"] = " · ".join(f"{h}: {t}" for h, t in finais)
if a.looks:
    looks = []
    for lid, nome in [("neutro", "Neutro"), ("comercial", "Comercial"), ("dourado", "Dourado"), ("cinema", "Cinema"),
                      ("clinico", "Clínico"), ("editorial", "Editorial")]:
        arq = f"{a.looks}/{lid}.mp4"
        if (RAIZ / arq).exists():
            looks.append({"id": lid, "rotulo": nome, "arquivo": arq, "ini": 0, "fim": 15, "falado": f"look {nome.lower()}",
                          "miniatura": mini(arq, 5, f"{codigo}-look-{lid}".lower())})
    lista.append({"id": "look", "nome": "Look (cor)", "escolha": "uma", "opcoes": looks})
lista.append(fora)

n_tom = sum(len(f["opcoes"]) for f in lista if f["id"] not in ("look", "fora"))
pend = [f["nome"] for f in lista if f.get("pendente")]
entrada = {"id": codigo, "titulo": titulo, "roteiro": f"{ROTEIRO.relative_to(RAIZ)} ({codigo})",
           "status": f"{n_tom} tomadas casadas com o roteiro · {len(fora['opcoes'])} falas soltas · "
                     f"{len(pend)} faixas ainda sem gravação", "fonte": video, "faixas": lista}
proj_arq = AQUI / "projeto.json"
proj = json.loads(proj_arq.read_text()) if proj_arq.exists() else {"videos": []}
proj["videos"] = [v for v in proj["videos"] if v["id"] != codigo] + [entrada]
proj_arq.write_text(json.dumps(proj, ensure_ascii=False, indent=1))
print(f"{codigo}: {entrada['status']}")
for f in lista:
    if f["opcoes"]:
        print(f"  {f['nome']}: " + ", ".join(f"{o['rotulo']} ({o.get('semelhanca', '-')})" for o in f["opcoes"]))

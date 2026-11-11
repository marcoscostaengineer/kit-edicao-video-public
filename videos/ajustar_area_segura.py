#!/usr/bin/env python3
"""Ajusta uma animação (anim/build.py -> index.html) à área segura do Instagram MEDINDO, não a olho (31/10).
Regra (memória reels-area-segura): texto entre y 290 e 1480, 60 px nas laterais, nada além de x 900 abaixo de y 1000.

Roda o build, mede o DOM com area_segura_medir.mjs e, para cada elemento que reprova, grava em anim/area-ajuste.json:
  dx / dy  -> desloca o elemento o mínimo para dentro (chip que encosta na coluna de curtir anda para a esquerda; o que
              passa da lateral esquerda anda para a direita; o que sobe acima de y 290 desce)
  css      -> quando nem deslocando cabe (mais largo que 60–900): chip quebra em duas linhas (max-width 560),
              legenda diminui a fonte
Chips empilhados (mesmo centro) andam juntos, para a pilha não sair do eixo.
O build.py aplica o arquivo na função el() (o patch que liga isso está no próprio build.py). Repete até aprovar.
Uso: python3 ajustar_area_segura.py caminho/anim [--build "comando"]   (padrão: python3 build.py dentro de anim/)"""
import json, re, subprocess, sys
from pathlib import Path

V = Path(__file__).resolve().parent
anim = Path(sys.argv[1]).resolve()
build = sys.argv[sys.argv.index("--build") + 1] if "--build" in sys.argv else "python3 build.py"
arq = anim / "area-ajuste.json"
aj = json.loads(arq.read_text()) if arq.exists() else {}
CAP_FONTES = [50, 46, 42]
MARGEM = 4

def alinhar_pilhas(aj, html, vis):
    """chips empilhados (mesmo centro x, até 260 px de distância em y, na tela ao mesmo tempo) andam juntos: o maior dx vale para a pilha inteira,
    senão o chip que violava sai do eixo dos outros. Devolve True se mudou algo."""
    chips = {}
    for eid, cls, x, y in re.findall(r'id="(\w+)" class="(chip[^"]*)" style="left:(-?[\d.]+)px;top:(-?[\d.]+)px', html):
        a = aj.get(eid, {})
        chips[eid] = (float(x) - a.get("dx", 0), float(y) - a.get("dy", 0))
    mudou = False
    for eid, (x, y) in chips.items():
        dx = aj.get(eid, {}).get("dx", 0)
        if not dx:
            continue
        for oid, (ox, oy) in chips.items():
            odx = aj.get(oid, {}).get("dx", 0)
            juntos = eid in vis and oid in vis and vis[eid][0] <= vis[oid][1] and vis[oid][0] <= vis[eid][1]
            if oid != eid and juntos and abs(ox - x) < 1 and abs(oy - y) <= 260 and abs(odx) < abs(dx) and odx * dx >= 0:
                aj.setdefault(oid, {})["dx"] = dx
                mudou = True
    return mudou


for rodada in range(1, 8):
    subprocess.run(build, shell=True, cwd=anim, check=True, stdout=subprocess.DEVNULL)
    r = json.loads(subprocess.run(["node", str(V / "area_segura_medir.mjs"), str(anim / "index.html")],
                                  capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
    med, vis = r["falhas"], r["vis"]
    html = (anim / "index.html").read_text()
    if not med:
        if alinhar_pilhas(aj, html, vis):                       # alinhou a pilha: mede de novo
            arq.write_text(json.dumps(aj, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
            continue
        print(f"{anim.parent.name}: APROVADO na rodada {rodada} ({len(aj)} elemento(s) ajustado(s))")
        sys.exit(0)
    manual, antes = [], json.dumps(aj, sort_keys=True)
    for eid, d in med.items():
        fr, cls = d["f"], d["cls"].split()
        a = aj.setdefault(eid, {})
        col = [f["x1"] - (900 - MARGEM) for f in fr if "coluna direita" in f["v"]]
        lat_d = [f["x1"] - (1020 - MARGEM) for f in fr if "lateral" in f["v"] and f["x1"] > 1020]
        lat_e = [(60 + MARGEM) - f["x0"] for f in fr if "lateral" in f["v"] and f["x0"] < 60]
        topo = [(290 + MARGEM) - f["y0"] for f in fr if "topo" in f["v"]]
        base = [f["y1"] - (1480 - MARGEM) for f in fr if "base" in f["v"]]
        esq, dir_ = max(col + lat_d + [0]), max(lat_e + [0])
        largura = max(f["x1"] - f["x0"] for f in fr)
        tem_left = re.search(rf'id="{eid}" class="[^"]*" style="[^"]*left:', html)
        if "cap" in cls:                                   # legenda: posição vem do CSS; só a fonte muda
            i = a.get("_fonte", -1) + 1
            if i >= len(CAP_FONTES):
                manual.append(f"{eid} (legenda larga mesmo a {CAP_FONTES[-1]} px)"); continue
            a["_fonte"] = i; a["css"] = f"font-size:{CAP_FONTES[i]}px;"
            continue
        if (esq and dir_) or largura > 836 or (esq and a.get("dx", 0) > 0) or (dir_ and a.get("dx", 0) < 0):
            if "chip" in cls and "max-width:560px" not in a.get("css", ""):
                a["css"] = a.get("css", "") + "max-width:560px;"
                continue
            manual.append(f"{eid} ({' '.join(cls)}, {largura:.0f} px de largura, não cabe deslocando)"); continue
        if not tem_left and (esq or dir_ or topo or base):
            manual.append(f"{eid} ({' '.join(cls)}: sem left/top no style, ajustar à mão)"); continue
        if esq: a["dx"] = round(a.get("dx", 0) - esq - 0.49)
        if dir_: a["dx"] = round(a.get("dx", 0) + dir_ + 0.49)
        if topo: a["dy"] = round(a.get("dy", 0) + max(topo) + 0.49)
        if base: a["dy"] = round(a.get("dy", 0) - max(base) - 0.49)
    alinhar_pilhas(aj, html, vis)
    aj = {k: v for k, v in aj.items() if v}
    arq.write_text(json.dumps(aj, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    if json.dumps(aj, sort_keys=True) == antes:           # nada mais a ajustar sozinho
        break
print(f"{anim.parent.name}: REPROVADO: {', '.join(med)}" + (f" | AJUSTE MANUAL: {'; '.join(manual)}" if manual else ""))
sys.exit(1)

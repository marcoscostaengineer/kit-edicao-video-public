#!/usr/bin/env python3
"""Na tela dividida (broll split), a pessoa desce ~560 px e a legenda do placer cai no rosto.
Move os blocos de legenda que começam dentro das janelas split para `y` (padrão 1420).
Uso: python3 legendas_split.py <projeto> [y]   (rodar depois do build.mjs)"""
import re, sys
from pathlib import Path
P = Path(sys.argv[1]); y = int(sys.argv[2]) if len(sys.argv) > 2 else 1420
doc = (P / "index.html").read_text()
ids = re.findall(r'<div id="(b\d+)-in" class="ov broll"', doc)
jan = []
for i in ids:
    a = float(re.search(rf'ft\("#{i}-in", \{{ autoAlpha: 0[^;]*?, ([\d.]+)\);', doc).group(1))
    b = float(re.search(rf'tl\.to\("#{i}-in", \{{ autoAlpha: 0, duration: [\d.]+ \}}, ([\d.]+)\);', doc).group(1))
    jan.append((a, b))
n = 0
def mover(m):
    global n
    ini = float(m.group(2))
    if any(a - 0.05 <= ini < b for a, b in jan):
        n += 1
        return m.group(0).replace(f'style="top:{m.group(1)}px"', f'style="top:{y}px"')
    return m.group(0)
doc = re.sub(r'<div id="eb\d+" class="eblock clip[^"]*" style="top:(\d+)px" data-start="([\d.]+)"', mover, doc)
(P / "index.html").write_text(doc)
print("janelas", jan, "· legendas movidas:", n)

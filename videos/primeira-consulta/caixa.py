#!/usr/bin/env python3
"""Injeta uma "caixa de perguntas" (estilo figurinha do Instagram) no index.html gerado pelo ghost-editor.
Uso: python3 caixa.py <projeto> "<pergunta>" <sai_em_segundos_do_edit> [--topo 250]
Roda DEPOIS do build.mjs (o build regenera o index.html e apaga a caixa).
"""
import html, sys
from pathlib import Path

P = Path(sys.argv[1]); pergunta = sys.argv[2]; sai = float(sys.argv[3])
topo = int(sys.argv[sys.argv.index("--topo") + 1]) if "--topo" in sys.argv else 250
idx = P / "index.html"
doc = idx.read_text()
if 'id="caixa"' in doc:
    sys.exit("index.html já tem a caixa; rode o build.mjs de novo antes.")

css = f"""
<style>
#caixa-clip {{ position:absolute; inset:0; z-index:30; pointer-events:none; }}
#caixa {{ position:absolute; left:160px; width:760px; top:{topo}px; opacity:0;
  font-family: Montserrat, -apple-system, sans-serif; filter: drop-shadow(0 18px 40px rgba(0,0,0,.35)); }}
#caixa .cx-top {{ background: linear-gradient(135deg, #1B81D6, #0F4C81); color:#fff; border-radius:34px 34px 0 0;
  padding:22px 30px 20px; display:flex; align-items:center; gap:18px; font-weight:700; font-size:30px; }}
#caixa .cx-av {{ width:54px; height:54px; border-radius:50%; background:#fff; color:#0F4C81; display:flex;
  align-items:center; justify-content:center; font-weight:900; font-size:28px; flex:none; }}
#caixa .cx-q {{ background:#fff; color:#111; border-radius:0 0 34px 34px; padding:24px 30px 28px;
  font-size:42px; line-height:1.16; font-weight:700; text-align:center; }}
</style>"""
box = (f'<div id="caixa-clip" class="clip" data-start="0" data-duration="{sai + 0.35:.2f}" data-track-index="7"><div id="caixa">'
       f'<div class="cx-top"><div class="cx-av">B</div>Faça uma pergunta</div>'
       f'<div class="cx-q">{html.escape(pergunta)}</div></div></div>')
js = (f'  tl.fromTo("#caixa", {{opacity:0, scale:.55, rotation:-4}}, {{opacity:1, scale:1, rotation:0, duration:.45, ease:"back.out(2.2)", immediateRender:false}}, 0.02);\n'
      f'  tl.set("#caixa", {{opacity:0, scale:.55}}, 0);\n'
      f'  tl.fromTo("#caixa", {{opacity:1, scale:1}}, {{opacity:0, scale:.85, duration:.3, ease:"power2.in", immediateRender:false}}, {sai:.2f});\n')

doc = doc.replace("</head>", css + "\n</head>", 1)
doc = doc.replace('<div id="caps">', box + '\n  <div id="caps">', 1)
doc = doc.replace('  window.__timelines["main"] = tl;', js + '  window.__timelines["main"] = tl;', 1)
idx.write_text(doc)
print("caixa inserida até", sai, "s")

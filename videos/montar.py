#!/usr/bin/env python3
"""Monta um vídeo da série "caixa de perguntas" nas duas versões (anúncio e Reels), a partir do reel.json do take.
Faz: build -> caixa de perguntas -> legendas da tela dividida acima da cabeça -> render SDR
-> tratar_audio.sh -> conferir.py -> cópias (só do que o conferir aprovar).
Uso: python3 montar.py <pasta_take> <nome_saida> "<pergunta da caixa>" <segundo_em_que_a_caixa_sai>
O reel.json precisa ter um beat scene/card (a tela final); o pill e o cursor são trocados por versão.
"""
import json, subprocess, sys, glob, os, shutil
from datetime import date
from pathlib import Path

P = Path(sys.argv[1]); nome = sys.argv[2]; pergunta = sys.argv[3]; sai = sys.argv[4]
V = Path(__file__).resolve().parent
HF = glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/.bin/hyperframes"))[0]
BUILD = os.path.expanduser("~/.claude/skills/ghost-editor/scripts/build.mjs")
cfg = P / "reel.json"
reprovados = []
# 17/10: a história e os fatos nascem ANTES do primeiro quadro (cadeia de arquivos; ver
# referencia/design/framework-diretor-de-motion-2026.md). Sem os dois preenchidos, não monta.
for arq in ("story.md", "facts.json"):
    f = P / arq
    if not f.exists() or "<" in f.read_text():          # "<...>" = lacuna do modelo ainda aberta
        sys.exit(f"falta preencher {f} (modelo em {V / 'modelo-take' / arq})")
fatos = json.loads((P / "facts.json").read_text())["frases"]
if any(not x.get("origem") or not x.get("fonte") for x in fatos):
    sys.exit(f"facts.json com frase sem origem ou fonte: {P / 'facts.json'}")

for v in os.environ.get("VARIANTES", "anuncio organico").split():   # 24/10: VARIANTES=organico para Reels de teste
    r = json.loads(cfg.read_text())
    card = next(b for b in r["beats"] if b.get("kind") == "card")
    if v == "anuncio":
        card["pill"]["text"] = "Chame no WhatsApp"
        card["cursor"] = {"clickAt": round(r["takes"][-1]["b"] - 0.05, 2), "dx": 150, "dy": 215}
    else:
        card["pill"]["text"] = "Link na bio"; card.pop("cursor", None)
    cfg.write_text(json.dumps(r, ensure_ascii=False, indent=1))
    log = open(P / f"build/build-{v}.log", "w")
    subprocess.run(["node", BUILD, str(P)], stdout=log, stderr=log, check=True)
    if pergunta != "-":  # "-" = vídeo sem caixa de perguntas (15/10)
     subprocess.run(["python3", str(V / "primeira-consulta/caixa.py"), str(P), pergunta, sai, "--topo", "175"], check=True,
                   stdout=subprocess.DEVNULL)
    if any(b.get("type") == "broll" and b.get("mode") == "split" for b in r["beats"]):
        subprocess.run(["python3", str(V / "caso-antes-depois/legendas_split.py"), str(P), "975"], check=True)
    if (P / "pos_build.py").exists():  # 24/10: ajuste próprio do take depois do build (ex.: legenda fugindo das faixas)
        subprocess.run(["python3", str(P / "pos_build.py"), str(P)], check=True)
    subprocess.run([HF, "render", str(P), "-o", str(P / f"build/{v}.mp4"), "--sdr", "--quiet"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final = P / f"build/{v}-final.mp4"
    subprocess.run(["bash", str(V / "tratar_audio.sh"), str(P / f"build/{v}.mp4"), str(final)], check=True)
    # 15/10: só chega ao Antonio o que passa no conferir.py (enquadramento, legenda, volume)
    if subprocess.run(["python3", str(V / "conferir.py"), str(P), str(final)]).returncode != 0:
        reprovados.append(v); continue
    shutil.copy(final, V / f"{nome}-{v}-{date.today().isoformat()}.mp4")
    shutil.copy(final, Path.home() / f"Desktop/{nome}-{v}.mp4")
    print("ok", v)
if reprovados:
    sys.exit(f"REPROVADO no conferir.py: {', '.join(reprovados)}. Nada foi copiado; ver {P / 'build/conferir.jpg'}")

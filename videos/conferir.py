#!/usr/bin/env python3
"""Confere o Reel RENDERIZADO antes de ele chegar ao Antonio (15/10/2026).
O defeito só aparecia quando ele assistia ("muito teto sem a Brenda", duas vezes). Aqui as regras
da casa viram número, medidas no vídeo final, não no plano do build:

  capa       o 1º quadro (o que o feed mostra parado) tem a Brenda e não é tela chapada
  abertura   a Brenda aparece no 1º segundo e meio
  olhos      mediana a ~30% da altura (~40% enquanto a caixa de pergunta está na tela), ±7 pontos
  tamanho    rosto com pelo menos 22% da largura do quadro
  legenda    nunca sobre olhos-boca, e dentro da área segura do Reels
  caixa      a caixa de pergunta (texto do gancho) fica pelo menos 3 s na tela, o tempo de ler
  áudio      −14 LUFS (aceita −16 a −12,5); pico real acima de −1 dBTP é aviso

Trechos de tela dividida (broll split) e o cartão final ficam fora de olhos/tamanho/legenda.
Grava build/conferir.jpg: um quadro a cada 2 s, com a caixa do rosto, a faixa-alvo dos olhos,
a legenda e o veredito ESCRITO em cada quadro (nunca só por cor).
O qa.py do ghost-editor continua sendo o conferidor de SFX e silêncio; este não repete aquilo.

Uso: python3 conferir.py <pasta_take> [render.mp4]      (padrão: build/organico.mp4)
Sai com código 1 se reprovar.
"""
import json, re, subprocess, sys
from pathlib import Path

MODELO = Path.home() / ".claude/skills/ghost-editor/library/models/face_detection_yunet_2023mar.onnx"
W, H = 1080, 1920
FPS = 5                      # amostras por segundo
JANELA = 2.0                 # um quadro da folha / uma janela de olhos a cada 2 s
OLHOS_ALVO, OLHOS_CAIXA, TOL = 0.30, 0.40, 0.07
ROSTO_MIN = 0.22             # largura do rosto / largura do quadro
ABERTURA, ABERTURA_MIN = 1.5, 0.7
LUFS_FAIXA, TP_MAX = (-16.0, -12.5), -1.0
CAIXA_MIN = 3.0             # s: o olho lê o texto do gancho, olha a Brenda e volta a ler (Kallaway, 27/10)
CAPA_DESVIO_MIN = 8.0        # desvio-padrão dos tons de cinza do 1º quadro; abaixo disso é tela chapada


# ---------- regras puras (testadas em teste_conferir.py) ----------

VOLTA_DIVIDIDA = 0.4   # s: a Brenda volta ao tamanho cheio depois da tela dividida (animação de 0,28 s)


def para_saida(t, takes):
    """Tempo da gravação original -> tempo do Reel cortado (a mesma conta do E() do build.mjs;
    os beats do reel.json estão no tempo da gravação, as legendas já no tempo do Reel)."""
    ini = 0.0
    for k in takes:
        if k["a"] - 1e-6 <= t <= k["b"] + 1e-6:
            return round(ini + t - k["a"], 3)
        ini += k["b"] - k["a"] + k.get("hold", 0)
    return None


def janelas_excluidas(beats, dur, takes=None):
    """Intervalos (no tempo do Reel) sem a Brenda em tela cheia: tela dividida e cartão final.
    Broll em tela cheia continua contando como "sem a Brenda", a não ser que o beat traga "planejado": true
    (intervenção aprovada em storyboard, 24/10). A tela dividida ganha 0,4 s no fim: é a volta da Brenda ao tamanho cheio."""
    conv = (lambda t: para_saida(t, takes)) if takes else (lambda t: t)
    fora = []
    for b in beats:
        dividida = b.get("type") == "broll" and b.get("mode") == "split"
        planejada = b.get("type") == "broll" and b.get("planejado") is True
        if dividida or planejada or b.get("kind") == "card":
            a = conv(float(b["at"]))
            fim = dur if b.get("to") in (None, "end") else conv(float(b["to"]))
            if fim is not None and dividida:
                fim = min(fim + VOLTA_DIVIDIDA, dur)
            if a is not None:
                fora.append((a, fim if fim is not None else dur))
    return fora


def dentro(t, intervalos):
    return any(a <= t < b for a, b in intervalos)


def descartar_saltos(am, salto=300):
    """24/10: o detector às vezes vê um "rosto" na mão (P1, 4,2 s: caixa em y 947–1590 entre quadros com o rosto em
    345–860). Uma detecção cujo centro foge mais de `salto` px dos dois vizinhos vira 'sem rosto' naquele instante."""
    cy = [((r[0] + r[1]) / 2 if r else None) for _, r in am]
    out = []
    for i, (t, r) in enumerate(am):
        viz = [c for c in (cy[i - 1] if i else None, cy[i + 1] if i + 1 < len(cy) else None) if c is not None]
        if r and len(viz) == 2 and all(abs(cy[i] - c) > salto for c in viz):
            r = None
        out.append((t, r))
    return out


def cobre_rosto(leg_y, leg_h, olhos, boca, folga=0.15):
    """A legenda invade a faixa olhos-boca (com folga proporcional)?"""
    f = (boca - olhos) * folga
    return leg_y < boca + f and leg_y + leg_h > olhos - f


def mediana(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def julgar_janela(amostras, alvo):
    """amostras: [(olhos_frac, largura_frac) | None]. Devolve lista de motivos (vazia = ok)."""
    com = [a for a in amostras if a]
    if not amostras:
        return []
    if len(com) < 0.5 * len(amostras):
        return ["sem a Brenda"]
    motivos = []
    o = mediana([a[0] for a in com])
    if abs(o - alvo) > TOL:
        motivos.append(f"olhos a {o:.0%} (alvo {alvo:.0%})")
    lw = mediana([a[1] for a in com])
    if lw < ROSTO_MIN:
        motivos.append(f"rosto pequeno ({lw:.0%} da largura)")
    return motivos


def julgar_capa(rosto, desvio):
    """O 1º quadro é a capa do Reel no feed: precisa da Brenda e de imagem, não de fundo chapado."""
    if desvio < CAPA_DESVIO_MIN:
        return ["capa (1º quadro) em branco ou chapada"]
    if rosto is None:
        return ["capa (1º quadro) sem a Brenda"]
    return []


def ler_lufs(saida_ebur128):
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", saida_ebur128)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", saida_ebur128)
    return (float(i[-1]) if i else None), (float(tp[-1]) if tp else None)


# ---------- medição no vídeo ----------

def duracao(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        str(video)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def rostos(video):
    """[(t, (topo, base, esq, dir, olhos_y, boca_y) | None)] em pixels de 1080x1920."""
    import cv2, numpy as np
    w, h = W // 2, H // 2
    det = cv2.FaceDetectorYN.create(str(MODELO), "", (w, h), 0.6)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={FPS},scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    out, n = [], 0
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        img = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        _, f = det.detect(img)
        t = n / FPS; n += 1
        if f is None or not len(f):
            out.append((t, None)); continue
        x, y, fw, fh, rx, ry, lx, ly, _, _, mrx, mry, mlx, mly, _ = max(f, key=lambda r: r[2] * r[3])
        out.append((t, tuple(v * 2 for v in (y, y + fh, x, x + fw, (ry + ly) / 2, (mry + mly) / 2))))
    p.wait()
    return out


def capa(video):
    """(rosto do 1º quadro ou None, desvio-padrão dos cinzas do 1º quadro)."""
    import cv2
    ok, img = cv2.VideoCapture(str(video)).read()
    if not ok:
        return None, 0.0
    peq = cv2.resize(img, (W // 2, H // 2))
    det = cv2.FaceDetectorYN.create(str(MODELO), "", (W // 2, H // 2), 0.6)
    _, f = det.detect(peq)
    return (f[0] if f is not None and len(f) else None), float(cv2.cvtColor(peq, cv2.COLOR_BGR2GRAY).std())


def loudness(video):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(video), "-filter_complex", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    return ler_lufs(r.stderr)


def caixa_ate(take):
    """Até quando a caixa de pergunta fica na tela (lida do index.html montado)."""
    html = (take / "index.html").read_text() if (take / "index.html").exists() else ""
    m = re.search(r'id="caixa-clip"[^>]*data-duration="([\d.]+)"', html)
    return float(m.group(1)) if m else 0.0


def julgar_caixa(duracao):
    """0 = vídeo sem caixa de pergunta: nada a julgar."""
    if 0 < duracao < CAIXA_MIN - 0.01:
        return [f"caixa de pergunta só {duracao:.2f} s na tela (mínimo {CAIXA_MIN:.0f} s para ler)"]
    return []


# ---------- conferência ----------

def conferir(take, video):
    take, video = Path(take), Path(video)
    reel = json.loads((take / "reel.json").read_text())
    lay_p = take / "build/caption_layout.json"
    lay = json.loads(lay_p.read_text()) if lay_p.exists() else {"blocks": []}
    dur = duracao(video)
    fora = janelas_excluidas(reel.get("beats", []), dur, reel.get("takes"))
    ate_caixa = caixa_ate(take)
    am = descartar_saltos(rostos(video))
    falhas, avisos, por_janela = [], [], {}

    # capa: o 1º quadro é o que o feed mostra parado
    falhas += julgar_capa(*capa(video))
    falhas += julgar_caixa(ate_caixa)

    # abertura
    ini = [r for t, r in am if t < ABERTURA]
    if ini and sum(r is not None for r in ini) < ABERTURA_MIN * len(ini):
        falhas.append(f"abre sem a Brenda: rosto em {sum(r is not None for r in ini)}/{len(ini)} quadros do 1º segundo e meio")

    # olhos e tamanho, janela a janela
    k = 0
    while k * JANELA < dur:
        a, b = k * JANELA, min((k + 1) * JANELA, dur)
        sel = [(t, r) for t, r in am if a <= t < b and not dentro(t, fora)]
        alvo = OLHOS_CAIXA if a < ate_caixa else OLHOS_ALVO
        m = julgar_janela([(r[4] / H, (r[3] - r[2]) / W) if r else None for _, r in sel], alvo)
        por_janela[k] = m
        for x in m:
            falhas.append(f"{a:4.1f}–{b:4.1f}s: {x}")
        k += 1

    # legenda: área segura e rosto
    topo_seg, base_seg = lay.get("safeTop", 0), lay.get("safeBottom", H)
    for c in lay.get("blocks", []):
        if dentro((c["t0"] + c["t1"]) / 2, fora):
            continue
        if c["y"] < topo_seg or c["y"] + c["h"] > base_seg:
            falhas.append(f"{c['t0']:4.1f}s: legenda fora da área segura (y {c['y']}–{c['y'] + c['h']}, segura {topo_seg}–{base_seg})")
        for t, r in am:
            if c["t0"] <= t < c["t1"] and r and cobre_rosto(c["y"], c["h"], r[4], r[5]):
                falhas.append(f"{t:4.1f}s: legenda sobre o rosto")
                por_janela.setdefault(int(t // JANELA), []).append("legenda sobre o rosto")
                break

    # áudio
    i, tp = loudness(video)
    if i is None:
        falhas.append("áudio: não consegui medir o volume")
    elif not LUFS_FAIXA[0] <= i <= LUFS_FAIXA[1]:
        falhas.append(f"áudio a {i:.1f} LUFS (alvo −14; rodar tratar_audio.sh)")
    if tp is not None and tp > TP_MAX:
        avisos.append(f"pico real {tp:.1f} dBTP (acima de −1)")

    folha(video, take / "build/conferir.jpg", am, por_janela, lay, dur, ate_caixa, fora)
    return falhas, avisos, i


def folha(video, destino, am, por_janela, lay, dur, ate_caixa, fora):
    import cv2
    cap, tiles = cv2.VideoCapture(str(video)), []
    k = 0
    while k * JANELA < dur:
        t = min(k * JANELA + JANELA / 2, dur - 0.05)
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, img = cap.read()
        if not ok:
            break
        if not dentro(t, fora):
            alvo = OLHOS_CAIXA if t < ate_caixa else OLHOS_ALVO
            y0, y1 = int((alvo - TOL) * H), int((alvo + TOL) * H)
            cv2.rectangle(img, (0, y0), (W - 1, y1), (255, 255, 0), 3)            # faixa-alvo dos olhos
            r = min(am, key=lambda a: abs(a[0] - t))[1]
            if r:
                cv2.rectangle(img, (int(r[2]), int(r[0])), (int(r[3]), int(r[1])), (0, 255, 255), 5)
                cv2.line(img, (int(r[2]), int(r[4])), (int(r[3]), int(r[4])), (0, 255, 255), 3)
            for c in lay.get("blocks", []):
                if c["t0"] <= t < c["t1"]:
                    cv2.rectangle(img, (40, int(c["y"])), (W - 40, int(c["y"] + c["h"])), (255, 0, 255), 4)
        motivos = por_janela.get(k, [])
        rot = f"{t:.0f}s OK" if not motivos else f"{t:.0f}s REPROVA: {motivos[0]}"
        cv2.rectangle(img, (0, 0), (W, 120), (0, 0, 0), -1)
        cv2.putText(img, rot, (24, 82), cv2.FONT_HERSHEY_SIMPLEX, 1.6 if not motivos else 1.15,
                    (255, 255, 255), 4, cv2.LINE_AA)
        tiles.append(cv2.resize(img, (270, 480)))
        k += 1
    import numpy as np
    linhas = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
    linhas[-1] += [np.zeros_like(tiles[0])] * (6 - len(linhas[-1]))
    cv2.imwrite(str(destino), np.vstack([np.hstack(l) for l in linhas]))


if __name__ == "__main__":
    take = Path(sys.argv[1])
    video = Path(sys.argv[2]) if len(sys.argv) > 2 else take / "build/organico.mp4"
    falhas, avisos, i = conferir(take, video)
    for a in avisos:
        print("aviso:", a)
    if falhas:
        print(f"REPROVADO — {video.name}")
        for f in falhas:
            print("  -", f)
    else:
        print(f"APROVADO — {video.name}" + (f" ({i:.1f} LUFS)" if i is not None else ""))
    print("folha:", take / "build/conferir.jpg")
    sys.exit(1 if falhas else 0)

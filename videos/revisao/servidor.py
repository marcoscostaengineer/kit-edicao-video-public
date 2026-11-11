#!/usr/bin/env python3
"""Sala de revisão dos vídeos da Brenda — servidor local (só nesta máquina).

Serve a pasta videos/ (com Range, para o player poder pular para o trecho de cada opção), a página da revisão
e uma API mínima:
  GET  /api/projeto   -> revisao/projeto.json   (o que o Cleef recortou: vídeos, faixas, opções)
  GET  /api/decisoes  -> revisao/decisoes.json  (o que o Antonio marcou)
  POST /api/decisoes  -> grava o JSON inteiro (com cópia .bak da versão anterior)
Uso: python3 servidor.py [porta]   ->  http://localhost:8765/revisao/
"""
import json, os, re, shutil, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent                                   # vida/consultorio-brenda/videos
PROJETO, DECISOES = AQUI / "projeto.json", AQUI / "decisoes.json"
PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


class Revisao(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(RAIZ), **k)

    def log_message(self, *a):                      # silencioso: o terminal não precisa de cada pedaço de vídeo
        pass

    def _json(self, obj, status=200):
        corpo = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(corpo)

    def do_GET(self):
        if self.path in ("/", "/revisao"):
            self.send_response(302); self.send_header("Location", "/revisao/"); self.end_headers(); return
        if self.path.startswith("/api/projeto"):
            return self._json(json.loads(PROJETO.read_text()) if PROJETO.exists() else {"videos": []})
        if self.path.startswith("/api/decisoes"):
            return self._json(json.loads(DECISOES.read_text()) if DECISOES.exists() else {})
        rng = self.headers.get("Range")
        if rng and self.path.split("?")[0].lower().endswith((".mp4", ".mov", ".webm")):
            return self._range(rng)
        return super().do_GET()

    def _range(self, rng):
        alvo = Path(self.translate_path(self.path.split("?")[0]))
        if not alvo.is_file():
            return self.send_error(404)
        tam = alvo.stat().st_size
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        ini = int(m.group(1)) if m and m.group(1) else 0
        fim = int(m.group(2)) if m and m.group(2) else tam - 1
        fim = min(fim, tam - 1, ini + 8 * 1024 * 1024 - 1)     # entrega em pedaços de até 8 MB
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(alvo)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {ini}-{fim}/{tam}")
        self.send_header("Content-Length", str(fim - ini + 1))
        self.end_headers()
        with open(alvo, "rb") as f:
            f.seek(ini)
            try:
                self.wfile.write(f.read(fim - ini + 1))
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_POST(self):
        if not self.path.startswith("/api/decisoes"):
            return self.send_error(404)
        n = int(self.headers.get("Content-Length", 0))
        try:
            dados = json.loads(self.rfile.read(n) or b"{}")
            assert isinstance(dados, dict)
        except Exception:
            return self._json({"ok": False, "erro": "JSON inválido"}, 400)
        if DECISOES.exists():
            shutil.copy(DECISOES, DECISOES.with_suffix(".json.bak"))
        tmp = DECISOES.with_suffix(".tmp")
        tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1)); os.replace(tmp, DECISOES)
        self._json({"ok": True})


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORTA), Revisao)
    print(f"Sala de revisão: http://localhost:{PORTA}/revisao/", flush=True)
    srv.serve_forever()

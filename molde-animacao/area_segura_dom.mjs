// Confere a área segura do Instagram MEDINDO o DOM do index.html (não a olho numa folha de quadros).
// Regra de 25/10 (memória reels-area-segura): texto só entre y 290 e 1480, 60 px de folga nas laterais, e da metade
// para baixo (y > 1000) nada além de x 900 (coluna de curtir/comentar/salvar). Imagem pode passar por baixo; texto não.
// Percorre a timeline GSAP de 0,1 em 0,1 s e considera só o que está visível (opacidade acumulada >= 0,5).
// Uso: node area_segura_dom.mjs [index.html]      sai com 1 se reprovar
import { createRequire } from "module";
import { pathToFileURL } from "url";
import path from "path";
import os from "os";

const require = createRequire(import.meta.url);
// sobe a partir do script até achar node_modules/puppeteer (o molde é copiado para dentro de projetos)
const subir = d => { const p = path.join(d, "node_modules/puppeteer"); if (require("fs").existsSync(p)) return p;
  const pai = path.dirname(d); return pai === d ? null : subir(pai); };
const PUP = process.env.PUPPETEER_DIR || subir(path.dirname(new URL(import.meta.url).pathname));
if (!PUP) { console.error("puppeteer não achado: rode ./setup.sh na raiz do kit"); process.exit(2); };
const puppeteer = require(PUP);
const html = path.resolve(process.argv[2] || "index.html");

// o mesmo chrome-headless-shell que o HyperFrames usa no render (~/.cache/hyperframes/chrome)
const CH = path.join(os.homedir(), ".cache/hyperframes/chrome/chrome-headless-shell");
const fs = require("fs");
const achar = d => { for (const n of fs.existsSync(d) ? fs.readdirSync(d).sort().reverse() : []) { const p = path.join(d, n);
  if (fs.statSync(p).isDirectory()) { const r = achar(p); if (r) return r; } else if (n === "chrome-headless-shell") return p; } };
const EXE = process.env.CHROME_EXE || achar(CH);
if (!EXE) { console.error("chrome-headless-shell do HyperFrames não achado: rode ./setup.sh"); process.exit(2); };
const browser = await puppeteer.launch({ executablePath: EXE, headless: "shell", args: ["--allow-file-access-from-files"] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920 });
await page.goto(pathToFileURL(html).href, { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);
const res = await page.evaluate(() => {
  const tl = window.__timelines.main;
  const root = document.getElementById("root");
  const sel = ".chip, .headline, .hdr, .cap, #hk, .cal, .lado, .wa, .cnt, .cmt, .chart, .fala, .hz b, .lbom b, .lbl b";  // R13: rótulos dentro dos cards
  const out = {};
  for (let t = 0; t <= tl.duration() + 1e-6; t += 0.1) {
    tl.seek(t, false);
    const rr = root.getBoundingClientRect();
    for (const e of document.querySelectorAll(sel)) {
      let op = 1, n = e;
      while (n && n !== root) { op *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; }
      if (op < 0.5) continue;
      const r = e.getBoundingClientRect();
      const x0 = r.left - rr.left, x1 = r.right - rr.left, y0 = r.top - rr.top, y1 = r.bottom - rr.top;
      const v = [];
      if (y0 < 290 - 2) v.push("topo");
      if (y1 > 1480 + 2) v.push("base");
      if (x0 < 60 - 2 || x1 > 1020 + 2) v.push("lateral");
      if (y1 > 1000 && y0 < 1480 && x1 > 900 + 2) v.push("coluna direita");
      if (v.length) {
        const k = `${e.id || e.className}: ${v.join("+")}`;
        (out[k] = out[k] || []).push(`${t.toFixed(1)}s [x ${Math.round(x0)}–${Math.round(x1)}, y ${Math.round(y0)}–${Math.round(y1)}]`);
      }
    }
  }
  return out;
});
await browser.close();
const ks = Object.keys(res);
if (!ks.length) { console.log("ÁREA SEGURA: APROVADO — nenhum texto fora da área em nenhum quadro (passo 0,1 s)"); process.exit(0); }
console.log(`ÁREA SEGURA: REPROVADO — ${ks.length} elemento(s)`);
for (const k of ks) console.log(`  - ${k}: ${res[k].length} quadros, ex.: ${res[k][0]} … ${res[k].at(-1)}`);
process.exit(1);

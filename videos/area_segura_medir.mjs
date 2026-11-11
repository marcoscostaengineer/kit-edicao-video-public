// Variante do verificador de área segura (s12-comer-depois-do-siso/anim/area_segura_dom.mjs) que devolve JSON:
// {falhas: {id: {cls, f: [{t, x0, x1, y0, y1, v}]}} só com os quadros que reprovaram, vis: {id_do_chip: [t0, t1]}}. Quem usa: ajustar_area_segura.py.
// Uso: node area_segura_medir.mjs caminho/index.html
import { createRequire } from "module";
import { pathToFileURL } from "url";
import path from "path";
import os from "os";

const require = createRequire(import.meta.url);
const PUP = process.env.PUPPETEER_DIR || `${process.env.HOME}/.npm/_npx/4b4c857f6efdfb61/node_modules/puppeteer`;
const puppeteer = require(PUP);
const html = path.resolve(process.argv[2] || "index.html");

// o mesmo chrome-headless-shell que o HyperFrames usa no render (~/.cache/hyperframes/chrome)
const EXE = process.env.CHROME_EXE || os.homedir() + "/.cache/hyperframes/chrome/chrome-headless-shell/mac_arm-152.0.7977.30/chrome-headless-shell-mac-arm64/chrome-headless-shell";
const browser = await puppeteer.launch({ executablePath: EXE, headless: "shell", args: ["--allow-file-access-from-files"] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920 });
await page.goto(pathToFileURL(html).href, { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);
const res = await page.evaluate(() => {
  const tl = window.__timelines.main;
  const root = document.getElementById("root");
  const sel = ".chip, .headline, .hdr, .cap, #hk, .cal, .lado, .wa";
  const out = {}, vis = {};   // vis: primeira e última vez que cada chip aparece (para achar pilhas)
  for (let t = 0; t <= tl.duration() + 1e-6; t += 0.1) {
    tl.seek(t, false);
    const rr = root.getBoundingClientRect();
    for (const e of document.querySelectorAll(sel)) {
      let op = 1, n = e;
      while (n && n !== root) { op *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; }
      if (op < 0.5) continue;
      if (e.id && e.classList.contains("chip")) { const w = (vis[e.id] = vis[e.id] || [t, t]); w[1] = t; }
      const r = e.getBoundingClientRect();
      const x0 = r.left - rr.left, x1 = r.right - rr.left, y0 = r.top - rr.top, y1 = r.bottom - rr.top;
      const v = [];
      if (y0 < 290 - 2) v.push("topo");
      if (y1 > 1480 + 2) v.push("base");
      if (x0 < 60 - 2 || x1 > 1020 + 2) v.push("lateral");
      if (y1 > 1000 && y0 < 1480 && x1 > 900 + 2) v.push("coluna direita");
      if (v.length) {
        const k = e.id || e.className;
        (out[k] = out[k] || {cls: e.className, f: []}).f.push({t: +t.toFixed(1), x0, x1, y0, y1, v});
      }
    }
  }
  return { falhas: out, vis };
});
await browser.close();
console.log(JSON.stringify(res));

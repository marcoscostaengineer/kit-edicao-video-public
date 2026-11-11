#!/bin/bash
# Refaz as 3 versões (caixa, animado, pop) x (anúncio, orgânico) a partir da fonte SDR convertida pelo macOS.
set -e
B="$(cd "$(dirname "$0")" && pwd)"
S=~/.claude/skills/ghost-editor
HF=$(ls -d ~/.npm/_npx/*/node_modules/.bin/hyperframes | head -1)
Q="Tenho medo de sair do dentista com um orçamento enorme. Como é a 1ª consulta?"
bash $S/scripts/prep.sh $B/fonte/IMG_5263-sdr.mov $B/take-5263 >/dev/null 2>&1
cp $B/take-5263/assets/talk.mp4 $B/take-5263-animado/assets/talk.mp4
cp $B/take-5263/assets/talk.mp4 $B/take-5263-pop/assets/talk.mp4
rm -f $B/take-5263-pop/assets/talk-matte.webm
setcard() { python3 - "$1" "$2" <<'PY'
import json,sys; p,v=sys.argv[1],sys.argv[2]; f=p+'/reel.json'; r=json.load(open(f))
c=[b for b in r['beats'] if b.get('kind')=='card'][0]
if v=='anuncio': c['pill']['text']='Chame no WhatsApp'; c['cursor']={"clickAt":25.8,"dx":150,"dy":215}
else: c['pill']['text']='Link na bio'; c.pop('cursor',None)
json.dump(r,open(f,'w'),ensure_ascii=False,indent=1)
PY
}
for v in anuncio organico; do
  P=$B/take-5263; setcard $P $v; node $S/scripts/build.mjs $P >/dev/null 2>&1; python3 $B/caixa.py $P "$Q" 4.4 --topo 175 >/dev/null
  (cd $P && $HF render -o build/$v.mp4 --sdr --quiet >/dev/null 2>&1); cp $P/build/$v.mp4 ~/Desktop/primeira-consulta-$v.mp4; cp $P/build/$v.mp4 $B/../primeira-consulta-$v-2026-10-12.mp4; echo "caixa $v ok"
  P=$B/take-5263-animado; setcard $P $v; node $S/scripts/build.mjs $P >/dev/null 2>&1
  (cd $P && $HF render -o build/$v.mp4 --sdr --quiet >/dev/null 2>&1); cp $P/build/$v.mp4 ~/Desktop/primeira-consulta-animado-$v.mp4; cp $P/build/$v.mp4 $B/../primeira-consulta-animado-$v-2026-10-12.mp4; echo "animado $v ok"
  P=$B/take-5263-pop; setcard $P $v; node $S/scripts/build.mjs $P >/dev/null 2>&1
  python3 $B/compor_pop.py $P $P/build/$v.mp4 >/dev/null; cp $P/build/$v.mp4 ~/Desktop/primeira-consulta-pop-$v.mp4; cp $P/build/$v.mp4 $B/../primeira-consulta-pop-$v-2026-10-12.mp4; echo "pop $v ok"
done
echo FIM

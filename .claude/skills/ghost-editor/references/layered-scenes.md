# Layered scenes: more images, split into parts, more movement

Applies to **every style** that puts a generated image on screen: the `image` scene, B-roll stills, explainers,
product or anatomy animations, carousel-to-reel conversions. A still image that sits there while the voice talks is a
slide. The fix is not a fancier transition; it is more pieces, each one moving on a word.

Learned on the convexa_ Reels (Oct 2026): v1 had one still statue per scene swapped by crossfade and was rejected
("too little moving"). v2 generated ~50 pieces in exploded view, cut them into ~120 PNG layers and moved them on the
spoken words; it was approved. Worked example: `recipes/marble-explainer/`.

## Targets

- A new scene every **2 to 4 s**, and it shows **what the sentence says**, not the topic of the video.
- **2 to 4 layers moving** at any moment. One is a slide; five is noise.
- **Mute test:** with the sound off, someone can retell the argument from the images alone.

## 1. Storyboard before any image

One table per video, built from the word timings (`words.json` / whisper):

| time | line | layers on screen | what each layer does, on which word | chip | sound |
|---|---|---|---|---|---|

Then one **asset list**: every piece to generate, its parts, and where it is reused. Ask per sentence: what is the
object, what is the action, what changes at the end? "The coin splits in two" needs the coin and both halves;
"the head comes out of the block" needs the figure and the block slices. The action decides the parts.

Reuse a fixed cast across a series (a recurring character for the objection, a coin, a hand, a scale): fewer images,
and the audience learns the vocabulary.

## 2. Generate in exploded view

Ask for the object **already taken apart**: the parts separated by background, same scale and light, ready to
assemble. Template for Gemini (web Pro, or `scripts/broll_gen.py` when the key has image quota):

> 2x2 grid, thin white borders between cells. [style: material, light, palette]. Each cell on flat [key colour, e.g.
> cyan #00FFFF], no shadow, no gradient. For items marked EXPLODED VIEW, show the parts separated with background
> between them (no part touching another), same scale and same light, like pieces ready to assemble. Everything inside
> the cell with margin. No text, letters, numbers or logos.
> 1) EXPLODED VIEW of [object]: (a) [part], (b) [part], (c) [part]. 2) ... 3) ... 4) ...

- Pick a key colour the style never uses (cyan for white marble and violet/lime; magenta or green for other palettes).
- Name each part with what it does in the scene ("the top slice of the block that falls"), not just what it is.
- At most 2 grids per conversation; long conversations contaminate later pieces. Open a new one.
- Expect fused parts. Plan the scene so it still works if a part comes glued (a scale in one piece can be a scale that
  already tips), or regenerate only that cell.
- If the web download fails: keep the original blob with a `fetch` hook, show one cell full screen, screenshot at
  scale 1. Small screenshots give unusable pieces.

## 3. Cut into layers

```bash
python3 $S/scripts/cut_parts.py <grid.jpg> --grid 2x2 --names coin,hand,block,pawn --out $P/assets/parts
python3 $S/scripts/cut_parts.py <one-cell.jpg> --names block --out $P/assets/parts
```

Every connected part becomes `<name>--pN.png` (left to right, top to bottom) plus `<name>.json` with each part's box in
the cell, so the build can reassemble the object exactly and then move the parts apart. Look at the parts: rename
`--pN` in the scene code by role ("block-top", "block-rest").

## 4. Move the parts

Every move starts on a word: `(word, occurrence, offset)`. The occurrence matters; the same word can appear three times.
Never anchor on a number token.

| move | what | values |
|---|---|---|
| enter | from the nearest edge | 0.45 · power3.out · 120 to 200 px |
| leave | out by the opposite edge | 0.3 · power2.in |
| land | falls and bounces once | 0.5 · bounce.out or back.out(1.8), squash 0.92 |
| float | breathing of a still part | y ±6 px, 2.8 s yoyo inside the scene window |
| arc | travels on a curve | x linear, y up and down, 0.7 · power2.inOut |
| rotate | turns on its own pivot | transformOrigin on the real pivot (hinge, base, centre) |
| draw | line or outline traces itself | stroke-dashoffset 1 → 0, pathLength=1 |
| count | number runs to the spoken value | 0.8 · power2.out, ends on the word |
| stamp | ✓ / ✕ hits the piece | scale 1.6 → 1 · 0.25 · back.out(3), 2 px shake |
| shatter | piece breaks into chips | 4 to 6 shards arcing down, fixed seeded rotation |
| swap | scene change | old leaves left, new enters right, 0.1 overlap; no crossfade |

- **The reveal follows the voice.** While the sentence is still building, the answer is not on screen. Crack on one
  word, open on the next, show the result on the word that says it. Showing the end in the first second was rejected.
- Numbers are drawn in code (counter, bar, line, calendar), with the spoken word in a chip.
- One chip at a time; captions stay in the safe area and never under a moving part.
- Never meaning by colour alone: pair every colour cue with ✓/✕, a symbol or a word.

## 5. Engine rules (HyperFrames + GSAP)

- **Exactly one `tl.set` at time 0 per selector.** Two sets at the same instant, or none, and the renderer returns the
  wrong state when it seeks backwards (things appear early or stay hidden). Keep an INIT dict and emit it once.
- Every tween is `fromTo` with explicit values from a tracked state, `immediateRender: false`.
- Centre pieces with a CSS translate and let GSAP move on top; an inline position style breaks it.
- Ids are global: prefix them per scene.

## 6. Review

- Draft render, then a contact sheet **from the MP4** at every anchor (not snapshots).
- Per scene: does the result appear only after the voice says it? Does anything cover the piece? Are 2 to 4 layers
  moving? Then the mute test.
- Pilot one video and get the ok before building the rest of a series.

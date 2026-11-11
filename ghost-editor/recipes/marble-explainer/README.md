# Marble explainer: exploded marble pieces that act out the narration

Call it with: **"make it in the convexa style"**, **"marble explainer"**, **"exploded marble reel"**, **"faceless reel with
statues that move"**.

First made for the convexa_ series (@convexa_mkt, 7 Reels, Oct 2026). v1 was a paper card with one still statue swapped
by crossfade; the owner rejected it as "too little moving". v2 (this recipe) splits every statue into parts and moves the
parts on the spoken words. Worked example, source of truth for the code:
`~/Desktop/Cleef/vida/negocios/convexa-conteudo/reels/` (`build_v2.py`, `cenas_v2/r04.py` to `r07.py`,
`storyboards/`).

The general method (storyboard, exploded view, cut into parts, move on the words) is
`references/layered-scenes.md` and applies to every style; this recipe is its marble look plus the convexa specifics.

**When to use:** a narrated script (ElevenLabs or the owner's voice) with no footage, where each sentence can be shown as
an object doing something: a coin splitting, a pawn breaking on day 28, a temple collapsing, a scale with one empty pan.
Business and decision content with a classical look.

## Goal and pass criterion

- Every 2 to 4 s a new scene shows **what the voice is saying**, not just the topic. At least 2 layers moving at all
  times, never more than 4 at once.
- **Mute test:** watch it without sound and retell the argument to someone from the images and chips alone. If you
  cannot, the scene is decoration.

## The grammar

1. **Open stage.** Marble straight on the black background, using the whole safe area (y 290 to 1480). Paper is a prop
   (plaque, tablet, calendar), never a frame that holds the statue.
2. **Exploded view.** Each statue arrives as separate PNG parts (body, the modern object, the moving parts), assembled
   in code, so the head can come out of the block, the arm can throw, the coin can split.
3. **Motion vocabulary** (GSAP; values in s):

   | name | what | values |
   |---|---|---|
   | `entra` | layer comes in from the nearest edge | 0.45 · power3.out · 120 to 200 px |
   | `sai` | layer leaves by the opposite edge | 0.3 · power2.in |
   | `pousa` | falls and bounces once | 0.5 · bounce.out or back.out(1.8), squash 0.92 on impact |
   | `boia` | breathing of a still piece | y ±6 px, 2.8 yoyo inside the scene window (no infinite repeat) |
   | `arco` | travels on a curve | x linear, y up and down, 0.7 · power2.inOut |
   | `desenha` | line or outline traces itself | stroke-dashoffset 1 → 0 with pathLength=1 |
   | `conta` | number runs to the spoken value | 0.8 · power2.out, ends on the anchor word |
   | `carimba` | ✓ or ✕ stamps the piece | scale 1.6 → 1 · 0.25 · back.out(3), −8°, 2 px stage shake |
   | `estilhaça` | piece breaks into chips | 4 to 6 shards, each `arco` down with a fixed seeded rotation |
   | `passa` | scene change | old scene `sai` left, new `entra` right, 0.1 overlap. No crossfade |

4. **Every move anchors on a word** as `(word, occurrence, offset)`. The occurrence matters: "conta" #1 and #3 can be
   20 s apart. Never anchor on a number (whisper writes "12%" for the spoken words).
5. **A reveal has to take its time.** If the voice is still building the idea, the result is not on screen yet (R04: the
   block cracks on one word, the top slice falls on the next, the figure is only free on "tirar"). A hollow block that
   shows the answer in the first second was rejected.
6. **Numbers are drawn, not typed:** counter, bar that grows, line that draws, calendar with a marked day, always with
   the spoken word as a chip.
7. **Right and wrong = ✓/✕ stamp plus chip.** Never colour alone (the owner is colour-blind).
8. **A recurring character for the objection** ("Ah, but..."): the Skeptic bust with a speech balloon, same piece in
   every episode.
9. **One chip at a time** under the stage (y 1275), only words the voice says. Word-by-word caption under it (y 1420).
10. **Palette rules:** violet piece never on violet ground, lime never on lime, lime never as text on paper. No
    gradient, shadow or rounded corners on drawn elements; the marble's shadow comes from the photo.
11. **Real people are never statues.** Named thinkers appear only by name in a chip; statues are generic figures.

## Pipeline

```bash
R=~/Desktop/Cleef/vida/negocios/convexa-conteudo/reels
M=~/Desktop/Cleef/vida/negocio-dentistas/marca-convexa/marmore
# 1. storyboard per Reels: scene table with time (from the whisper JSON), line, layers, motion, chip, sound
#    + one list of every marble piece to generate, grouped in 2x2 grids with the prompt ready ($R/storyboards/)
# 2. generate the grids in Gemini web, Pro model (base prompt below); at most 2 grids per conversation
# 3. cut each quadrant into one PNG per part (+ a JSON with each part's box, to reassemble in place)
python3 $M/recortar_partes.py <quadrant.jpg> <name> [min_area=0.004]   # -> $M/elementos/v2/<name>--pN.png
# 4. write the scenes in $R/cenas_v2/rNN.py (runs inside build_v2.py's namespace) and build
python3 $R/build_v2.py N            # -> rNN-*/anim-v2/index.html
cd $R/rNN-*/anim-v2 && npx hyperframes lint && npx hyperframes render -q draft -o build/draft.mp4
# 5. contact sheet of the DRAFT MP4 (not snapshots), fix, then the final render
npx hyperframes render -o build/rNN-v2.mp4
```

Pilot one episode first and get the owner's ok on it before building the rest. All seven v2 Reels followed the R04 pilot.

## Generating the pieces (Gemini web)

Base prompt, pasted before the 4 items of each grid (in Portuguese for this account):
2x2 grid, thin white borders; hyper-real studio photo of classical pieces in **white marble (neutral grey, no warm
tone)**; every piece is ancient and gets **one modern intervention** only in violet #6A2BF2 and lime #D7F23A; each cell on
**flat cyan #00FFFF**, no shadow, no gradient; for items marked **EXPLODED VIEW**, the parts separated with cyan between
them (no part touching another), same scale and light, ready to assemble; everything inside the cell with margin;
human figures clothed; no text, letters, numbers or logos.

- Check the mode selector says **Pro** before sending. Send the text with `execCommand('insertText')`.
- More than 2 grids in one conversation contaminates the pieces: open a new conversation.
- **Expect fused parts.** Gemini sometimes glues what you asked to be separate (the scale came as one piece, Davi's
  glasses stuck to his face, the temple scaffold fused to two columns). Design the scene so the piece still works if it
  arrives fused, or regenerate only that cell.
- **When the download fails:** hook `fetch` to keep the original image blob, show one quadrant full screen in an
  overlay and take a full-scale screenshot (scale 1, ~1400×851) saved to disk. Scale 0.2 or 0.3 gives pieces too small
  to use.
- A JS `await` longer than ~45 s times out the tool: send the prompt without waiting, poll in separate calls.

## Engine rules (`build_v2.py`)

- Helpers: `init` (initial state), `go` (fromTo from the tracked state), `setp`, `pop`, `out`, `entra`, `sai`,
  `pousa`, `arco`, `treme`, `boia`, `el`, `img(id, piece, cx, cy, w, z, origin, parent)` (copies the PNG, centres it,
  returns its height), `grupo`, `carimbo`, `contador`, `lista`, `chip`. `A(("word", n, offset))` turns an anchor into
  seconds.
- **Exactly one `tl.set` at time 0 per selector** (the `INIT` dict, emitted once). Two sets at the same instant, or a
  missing initial set, make the renderer return the wrong state when it seeks backwards: the calendar showed up early
  and a block stayed hidden. `setp` at t ≤ 0.001 falls back to `init`.
- Every tween is `fromTo` with explicit values from the tracked state, `immediateRender: false`.
- Compute positions inside `img()`; an inline style overrides the CSS translate and throws the piece to the top of
  the frame.
- Element ids are global across scenes: reusing `pe1` in two scenes breaks both. Prefix per scene.
- Benign lint warnings that stay: duplicate_media, gsap_timeline_set_initial_hide, file too large.

## Review

- Contact sheet from the rendered MP4 (`ffmpeg -ss`) at every anchor, not from snapshots.
- Check per scene: does the result appear only after the voice says it? Is anything hiding the piece (the ⏸ covered
  the megaphone until it was moved and shrunk)? Is the ✓/✕ next to every colour cue?
- Then the mute test.

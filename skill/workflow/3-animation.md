# 3. Animation: the picture, with animkit

animkit makes the picture as code. You write one Python function per shot that returns a frame (a numpy image);
animkit takes care of timing from the audio, rendering, the soundtrack and the checks. **You cannot watch video, so
you review by rendering stills and looking at them.** That loop is the whole job.

```bash
export PYTHONPATH="$FILM/kit"      # the film's own snapshot of the kit (see SKILL.md, "A film's folder")
```

## The commands

```bash
python -m animkit.finish "$FILM" --info              # shots, line times, and the film time of EVERY word
python -m animkit.render "$FILM" stills 2:0.5 2:-0.1 3:50%    # frames: shot:sec | shot:-sec-from-end | shot:pct
python -m animkit.render "$FILM" sample --per 4      # 4 frames inside every shot, one labelled sheet
python -m animkit.render "$FILM" sample --per 6 --shots 2     # closer look at one shot
python -m animkit.render "$FILM" all --workers 4     # silent picture -> build/picture.mp4; re-renders what changed
                                                     #   (shots.py, project.json, the kit)
python -m animkit.render "$FILM" all --redo 2,3      # only the segments covering shots 2 and 3
python -m animkit.mix "$FILM"                        # soundtrack -> build/mix.wav at project.json "lufs"
python -m animkit.finish "$FILM"                     # final mp4 + contact sheet + automatic checks
```

- Stills land in `output/stills/` with a labelled sheet (`sheet.jpg` from `stills`, `sample_sheet.jpg` from
  `sample`). **Read the sheet image after every change.** The user sees the images you Read in the desktop app and
  may react mid-turn: that is a review channel, use it.
- `LAYOUT WARNING` lines report logged boxes that overlap or cross the safe margin. Fix them.
- **Run every command in the foreground and wait.** Never end a turn with a render running in the background.
- A full render of a 72 s film takes about 2.5 min with 5 workers; a partial re-render 0.5-1.5 min. Renders are cheap;
  review rounds with the user are expensive.
- Helpers in `kit/tools/` (run as scripts): `sheet.py` (lettered checkpoint sheets), `cel_matte.py` (cut-outs of
  inked cels), `beats.py` (a music file's beat grid, with local-music's interpreter), `words.py` (word timings, with
  local-voice's interpreter).

## project.json

```json
{
 "title": "Ember", "duration": 20.0, "end_fade": 1.5, "grain": 0.02, "lufs": -16,
 "lines": [{"id": "L1", "text": "Before the first fire, night was a wall.",
            "audio": "assets/vo/L1.wav", "words": "assets/vo/L1.words.json"}],
 "shots": [{"id": "1", "lines": ["L1"], "pre": 1.2, "post": 0.3, "fade_in": 1.0},
           {"id": "2", "dur": 3.0, "fade_out": 0.5}],
 "sfx": [{"file": "assets/sfx/ignite.wav", "at": "L1:wall", "gain_db": -12, "fade_out": 0.3}],
 "music": {"file": "assets/music/bed.wav", "gain_db": -14, "start": 0.0, "offset": 0.0, "fade_in": 2.0, "fade_out": 3.0}
}
```

- `lines`: voice lines; a line can also take `"at"` (fixed position in its shot), `"gap_after"` (default 0.35 s) and `"gain_db"`.
- `shots`: padded around the lines they carry (`pre`, default 0.5; `post`, default 0.6), or a fixed `dur`.
  `fade_in`/`fade_out` fade the shot from/to black.
- `duration` (optional) stretches or trims the last shot so the film is exact. `end_fade` fades picture and sound.
- `sfx[].at`: a cue spec or seconds; `offset`, `fade_in`, `fade_out` optional. `music` is never ducked.
- `lufs`: the integrated loudness target of the mix (default -16).
- Changing padding moves every later shot: re-render with `all` (stale segments are cleaned up).
- A regenerated take of a different length also moves every later shot. To keep the rest of the film where it is,
  give the shot a fixed `dur`. Re-run the word timings for the new take, and re-check cue specs against Whisper's
  spelling of the words ("5th" for "fifth").

### From a finished soundtrack

When the audio is already mixed (voice + music), it is **one line** and the shots are cut by duration:

- `"lines": [{"id": "L1", "audio": "assets/vo/final.wav", "words": "assets/vo/final.words.json", "at": 0}]`
- the first shot carries `"lines": ["L1"], "pre": 0`; every shot has a `dur` (sum = the mix length)
- sound effects on word cues of that one line: `"L1:sure#2"`, `"L1:Amen+3.4"`, `"L1:up-0.1"`, or plain seconds
- **no `music` entry** (it's in the mix); set `"lufs"` to the soundtrack's level (e.g. -14)
- cut shots on the bar grid in CUES.md where the music has a pulse

### Timed on the music (no voice)

A wordless film has no lines to cue on, so the music's grid is the timeline (Puff Ahoy):

- `"lines": []`; every shot has a `dur` that ends on a downbeat (cuts at 2.0833 s land within a frame of a 2.07 s
  downbeat); `"duration"` is the music's last hit plus its tail; the music in `"music"` at `gain_db` 0.
- Copy the beats and the named events from `kit/tools/beats.py` into constants at the top of shots.py and work in
  film seconds: `t = s.gf / FPS`. Name every event (`CUE = dict(blow=12.074, clack=12.585, ...)`), so a gag is
  moved in one place. A `bump(t)` that is 1 on each beat and decays over 0.2 s gives the bounce to the music.
- Sound effects take seconds in `"at"`, from the same constants.

## Writing shots.py

```python
import math
import numpy as np
from animkit import *          # W, H, FPS, ramp, ease, lerp, Layer, load_plate, splat, dust, glow, text, ...

def shot_1(s):                 # shot id "1" -> shot_1 ; id "2b" -> shot_2b
    img = load_plate("night", expo=0.5)          # assets/plates/night.png, cover-fitted to 1920x1080
    t_wall = s.c("L1:wall")                      # cue: start of the word "wall" in line L1, in shot seconds
    k = ease(ramp(s.t, t_wall - 0.3, t_wall + 0.8))
    L = Layer()                                  # vector drawing with pycairo
    ctx = L.ctx
    ctx.rectangle(0, 700, W, 380)
    ctx.set_source_rgba(0, 0, 0, 0.8 * k)
    ctx.fill()
    img = L.over(img)                            # composite the layer
    return vignette(img, 0.5)                    # must return float32 (1080, 1920, 3) in [0, 1]
```

- **`s`, the shot context:** `s.t` time in the shot (s), `s.T` the shot length, `s.f`/`s.gf` the frame in the
  shot/film, `s.c(spec)` a cue in shot seconds, `s.box(name, bbox)` logs a layout box for the overlap checks.
- **Cue specs:** `"L2:spark"` start of the word; `"L2:spark+0.2"`, `"L2:end-0.5"` offsets; `"L2:start"` the line's
  start; `"L2:end"` the end of its last word; `"L3:fire#2"` the second occurrence. **Never hard-code beat times.**
- **Determinism:** `np.random.default_rng(seed)` with a fixed seed, or `hash01(...)`. Never unseeded randomness or
  the clock: any frame must render identically on its own, in any order.
- **One shots file per film.** Fold every fix into `shots.py`; don't pile up `patch_*.py` scripts or override modules
  (one film ended with 17 patch scripts; another with six override layers that were hard to read).
- **Style code:** put the film's reusable look (its grade, its glitch pass, its drawing rigs) in functions at the top
  of shots.py or in a `style.py` next to it, so every shot uses the same ones. Start from [cookbook](../cookbook/README.md) recipes.

### Toolbox (`animkit.core`)

| Area | Helpers |
| --- | --- |
| Timing | `ramp(t, t0, t1)` (0→1), `ease(u)`, `ease_in`, `ease_out`, `lerp(a, b, u)`, `clamp`, `vnoise(t, seed, freq)` (smooth wobble in [-1, 1]), `hash01(*ints)` |
| Frames | `blank(col)`, `load_plate(name, desat=0, expo=1)`, `screen(base, light)` (add light), `multiply(base, k)`, `crossfade(a, b, u)`, `gblur(img, sigma)`, `vignette(img, k)`, `grain(img, t)`, `grid()` (pixel coordinate arrays) |
| Light and particles | `glow(img, sigma, strength, thresh)` (bloom), `radial(cx, cy, r, col, k)` (soft light, screen it on), `godrays(src, cx, cy)`, `splat(xs, ys, cols, sizes)` (soft particles, returns light), `dust(t, n, seed, col, k, region, vy, vx)` (drifting motes and embers) |
| Camera | `push(img, scale, cx, cy)` (zoom about a point), `shift(img, dx, dy)` |
| Vector (pycairo) | `Layer()` then `L.ctx`; `L.over(img)` (alpha), `L.add(img)` (additive), `L.alpha()`; `poly_path(ctx, pts)`, `stroke_partial(ctx, pts, u)`, `safe_scale(ctx, sx, sy)` (never 0) |
| Text | `bbox = text(ctx, "EMBER", x, y, size=96, col=(1, .9, .7), a=1, font="Georgia", anchor="center", tracking=8)`, then `s.box("title", bbox)` |
| Colors | `rgb("#ffb347")` → (r, g, b) |
| Cache | `memo(name, fn)`: an expensive static image cached on disk under `build/cache` |

## The loop (in order)

1. **Read BRIEF.md, STYLE.md, REFERENCES.md and DECISIONS.md, and run `finish --info`.** Write down every cue the
   brief requires, with its exact spec and film time.
2. **Plan before coding** (`PLAN.md`), one entry per shot: what is on screen and where (think of a 6×6 grid), what
   moves on which cue, what must never overlap.
3. **Write shots.py one shot at a time.** After each shot, `sample --per 4 --shots N`, read the sheet, compare with the
   plan, fix, repeat. **Check frames inside each motion** (mid-fall, mid-wave): things collide on the way.
4. **C5 animatic stills:** 2-3 stills per shot with every overlay drawn, tiled per act, plus the subtitle list. Send
   them and ask ([4-review](4-review.md#the-checkpoints)) **before the full render**.
5. **Sample the whole film** (`sample --per 4`) and fix continuity: positions at cuts, brightness jumps, leftovers.
6. **Render, mix, finish.** Read `output/checks.txt`, look at `output/contact.jpg`, fix warnings, `--redo` the touched
   shots, mix and finish again.
7. **C6:** send the draft film and the contact sheet, with a short report: every required cue and its time, the
   checks, what you couldn't do.

### Delegating shots

For a long film, shot functions can go to subagents: give each the shot's PLAN entry, its cue specs, the STYLE.md
rules, the shared style functions and a reference still, and have it return when its `sample` sheet matches.
Claude Haiku was a sufficient director for a 20-second piece with a clear brief and recipes; richer models tended to
over-build and needed stripping back. You stay the director: you review every sheet.

## Fitting overlays to the plate

- **Measure, don't guess.** Render a still with a coordinate grid over the plate (or crop it) to read positions; a
  grid crop put paint drips exactly on a character's abs. Anything standing on the ground sits exactly on the plate's
  ground or horizon line: measure the line, check a zoomed crop.
- **Take shapes from the plate itself.** A mask from the plate's own white screen (largest white component, holes
  filled, 1 px dilate) fitted a phone wallpaper exactly, notch included; a drawn rounded rectangle did not.
- **Draw scene overlays onto the plate before the camera move** (`Layer().over(plate)`, then `push`/`shift`), so
  they zoom and pan with it.
- **A glow on top of an object washes out its line art:** screen the halo over everything, then redraw the object
  crisply on top.
- **Depth and occlusion:** to go *behind* something, draw it first and the occluder after (or multiply by
  `1 - occluder_alpha`). To fall *away* from the camera, shrink toward a vanishing point and dim; don't just move down.

## Subtitles

On by default (C0 decides). Burned in, full brightness, readable size, inside the safe area, timed from the word
timings. Group phrases on the speaker tag and its quote, not only on pauses. Show the subtitle list at C5.
(A kit helper is on the BACKLOG; until then draw them in a shared function with `text()` and `s.box`.)

## Pitfalls

- `cairo` raises "invalid matrix" on a zero scale: `safe_scale` or `max(s, 1e-3)`.
- A frame is float32 in [0, 1]: `np.clip(img, 0, 1)` after adding light.
- Full-frame blurs cost seconds per frame; prefer small blurs and `splat` for particles.
- Don't paste a "clean" copy of the image over an effect region ("still pockets"): it reads as a static patch.
  Change the live image instead.
- Bloom, grading and colour splits create forbidden hues by accident: if STYLE.md has palette rules, check after the
  last pass (a "palette guard").
- Never run two renders of one film at once, and never edit code a running render imports (it may pick up the
  change halfway). Wait for one job to finish before the next.
- **A grade that lifts black** (a film base, a fog) fails `finish`'s "ends on black": after the last fade, return
  a true black frame without the grade (Puff Ahoy: last frame 0.030, then 0.012).
- **Gate every effect to its window.** An iris applied all shot long at its "open" radius blacked out the far side
  of the frame, because the radius was smaller than the distance to the farthest corner.
- Windows shell: long heredocs with nested quotes break. Write patches and long text to a file with the editor tool,
  then run it. Pipes hide failures: `cmd || { echo FAILED; exit 1; }`.

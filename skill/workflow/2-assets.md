# 2. Assets: voice, music, plates, sounds

All assets are made locally with the GPU tools. **Each tool's own SKILL.md is the authority on its flags**; this file
holds what worked for films, and the commands as a quick reference.

## The GPU: one server at a time

The 16 GB card holds one model server at a time.

```bash
python ~/.claude/skills/local-gpu/gpu.py status               # what holds the card (read-only)
python ~/.claude/skills/local-gpu/gpu.py switch local-voice   # stops the others (asks first), starts this one
```

- **Order:** voice → word timings → music → plates → sounds. Music goes after the voice because its length and
  shape depend on the finished voice. Plates can move earlier when C1-C3 need drafts first; group GPU work by server.
- Ask once, up front, for the switches the plan needs. Never stop a server you didn't start without a yes.
- Whisper (for checking mixes) fits next to the music server.
- Stop every server before animating; animating needs no GPU.

## Audio-first (two sessions)

When the sound drives the film (a monologue, a song, a sermon), make the soundtrack in one session and animate in a
second. The handoff is three files, and the audio session always delivers them:

1. **The final mix** (`final-*.wav`): voice and music together, the film's only audio besides sound effects.
2. **Word timings on the mix's own timeline** (`*_words.json`, `.srt`): every word and phrase, shifted by the voice's
   offset into the mix.
3. **`CUES.md`**: time | what happens (a voice phrase or a music event) | the bar grid (150 BPM = 1.6 s a bar).

The animation session then needs only a short prompt ("an animation for this file, <inspiration>, ~1 h, 2 review
passes") and works out the scenes from the words, in the [finished-soundtrack mode](3-animation.md#from-a-finished-soundtrack).

## Voice (local-voice)

```bash
SAY=~/.claude/skills/local-voice/scripts/say.py
python $SAY --voices; python $SAY --presets
python $SAY "First line." --voice young-woman --check --wait 240 --out "$FILM/assets/vo/takes"
python $SAY "Second line." --like <first take id> --check --out "$FILM/assets/vo/takes"
```

- **Auditions:** about 4 seeds per instruction, 2-3 contrasting instructions (age, depth). Judge on words heard
  (dry), base pitch, length and how the last word is held, then **send the user 2-3 MP3s and let them pick by ear**.
  The numbers have missed: the user picked a take ranked second, then a younger voice than the brief asked for.
- **One voice for the film:** after the first line, make every other line with `--like <take id of line 1>`.
- **Check every take:** below about 90% of words heard, regenerate. Follow the tool's warnings (bass-heavy take,
  a stray sound after the last word).
- **Deep voices and held endings pull against each other:** the deepest seeds (61-77 Hz) clipped a sung last word
  to under 1 s; seeds at 90-110 Hz held it 3 s. Raise a held word in the mix (`boost`) instead of searching seeds.
- **Long-tail presets** (ai-choir) add about 2 s of echo per line; trim to the last word plus a short tail.
- **Install the takes:** copy each keeper's processed WAV to `assets/vo/L1.wav`, `L2.wav`... and its `_words.json`
  to `L1.words.json`, and list them in project.json `lines`.
- **Word timings must come from the exact file that plays.** If you trimmed, stretched or mixed it, regenerate them:
  ```bash
  ~/.claude/skills/local-voice/.venv/Scripts/python.exe "$REPO/kit/tools/words.py" "$FILM" [L1 L2 ...]
  ```
  Check the printed words against the script; note Whisper spellings ("fifth" heard as "5th") for your cue specs.

## Music (local-music)

```bash
PY=~/.claude/skills/local-music/.venv/Scripts/python.exe; M=~/.claude/skills/local-music/scripts/music.py
$PY $M --show <REQ:SEED> --out "$FILM/assets/music"          # deliver the take the user chose
$PY $M --mix <song ref>,vol=0 voice.wav,at=4,voice,reverb=room,boost=60.9-63.5:+4 --out <dir>
$PY $M --export <final ref> --out "$FILM/source"            # keep the final and everything it's made from
```

- **A bed, not a showpiece.** "Dark suspenseful cinematic underscore, background music that slowly and steadily
  builds tension ... restrained and brooding, holding back, never releasing" sat under a voice at 0 dB. A full
  climax (taiko, brass, choir) fought the voice even at -9 dB and was rejected as "too violent and epic".
- **Length:** the film's length plus a 2-3 s tail; builds placed under the right words.
- **Let the user pick by ear before building on it:** 2-3 candidates as MP3s. A full intro → battle → final-hit chain
  built before the user heard a note was discarded. The scores (CE, PQ, CLAP) didn't predict the take that fit.
- **Deliver the chosen take**, not the top-ranked one (`--show REQ:SEED` or `--pick SEED`).
- **Level:** master the bed around -17 LUFS, constant, **never ducked** under the voice (ducking reads as pumping).
  Offer the music at 0 dB as well as -6/-9/-12; one user wanted 0 dB.
- **Words must survive the mix in the speech band.** A level rule (voice 11 dB over music) can pass while a bright
  music moment masks a word. local-music's `voice` layer flag warns where words may be lost; at 0 dB over a battle
  section words were lost ("Lord" heard as "nor"), at -6 dB 97% were heard. When in doubt, transcribe the final mix.
- **Polish in the mix:** a light room reverb if the dry voice sounds "too dry"; `boost` a held last word (+4 dB).
- **Before any cleanup, `--export` the final**, so a later tweak still has its sources.
- **When the music leads (no voice)**, ask for its ending in the prompt with `--fade-out 0`: "ending on a big band
  button chord" gave a real button (a 0.2 s silence, then one hit) to close the iris on (Puff Ahoy: 2 prompts x 6
  takes, 3 sent, the user picked the recommended one). Then map its grid with `kit/tools/beats.py` (run with
  local-music's interpreter): bars, bar lengths (an accelerando shows as shorter bars), silences, hits, as a CUES.md
  table.

## Plates and references (local-image)

```bash
G=~/.claude/skills/local-image/scripts/generate.py
python $G "<prompt>" --preview --count 4 --size 1664x928 --wait 300 --out "$FILM/assets/plates/drafts/<shot>"
python $G "<change>" --edit ref/hero.png --edit <scene>.png --scale 1328 --out "$FILM/assets/plates/drafts/<shot>"
python $G "" --enhance <keeper.png> --out "$FILM/assets/plates/drafts/<shot>_final"
python $G "<object>" --cutout --size 1024x1024 --preview --count 2 --out <dir>     # a shape to trace or composite
```

**Prompts:**
- Write plates as **backgrounds, not finished shots**: the setting, the light, the palette and the composition, with
  clean space where procedural elements go ("empty, centered", "no people", "no text"). If the animation adds a glow
  or a fire, the plate must not already contain one.
- There is **no negative prompt**: describe what is there, never what to avoid.
- **Big or abstract subjects need a viewpoint:** a horizon, a vantage point, scale cues (tiny figures, a city), and a
  stated light source. "Glitching data" prompts give texture, not an object.
- **Paste the REFERENCES.md attribute string** for every character and prop the shot shows, and **counts** ("only
  one car", "only one priest", "only ONE mouth").
- **Edits say what to keep:** "keep its one open mouth exactly as it is, color its edges red". An edit that only said
  "add lipstick" produced a second mouth.
- **Name each reference in the prompt:** "the priest from the second image".
- Painterly or cinematic matte painting works well; 1664x928 is 16:9 and is cover-fitted to 1080p.

**Acceptance checks before a plate goes to the user** (say which you checked):
- mean luma at least about 0.08, even for dark themes (add darkness in code, not in the plate)
- the subject is nameable at thumbnail size
- spatial logic: the steering wheel's side (mirrored images flip it), which way a vehicle faces at a window, where
  characters look (pupils toward what they react to), the time of day matches the script
- consistency: the same prop design in every shot, every character attribute present
- no anatomy errors (six fingers), no props that read wrong (a seat that seems outside the car)

If a plate fails, **regenerate with a changed prompt** (after two rounds, change the prompt, not just the seed);
don't patch it in code.

**Characters as cut-out cels** (cartoon films; recipe: [cel-animation](../cookbook/cel-animation.md)):
- Make every pose an edit of the C1 pick on its plain cream background; the edits keep the geometry, so full-canvas
  cels swap in place.
- Matte them with `kit/tools/cel_matte.py`, not local-image's `cutout.py`, which cut pale insides (skin, blonde hair,
  a face, white gloves) out of inked cels over cream (Puff Ahoy). Gaps between spokes: `--pocket 150`; a white bird
  with a thin outline: `--tol 12 --fill`.
- Small facial motion (pupils) barely changes in an edit; draw it in code.
- **Matched plates:** make the second plate an edit of the first ("pull the camera far back to a wide view of the
  same scene ... the same rock now small at the lower left"). Wide and close plates generated separately didn't
  match, and the user asked for the wide one again from the close pick.
- Lettered checkpoint sheets: `python kit/tools/sheet.py OUT.jpg "Spoon" drafts/c1_spoon -- "Ship" drafts/c1_ship`.

**A film that moves through scales** (orbit → desert → building → faces → blood; recipe:
[continuous-journey](../cookbook/continuous-journey.md)):
- **Lock the recurring object first, then make every other scale an edit of that locked image** ("show this same
  building from much higher up"). A wider view painted first and cropped into did not match the locked building,
  twice ("not accurate, has to be consistent").
- **For a closer view of the same plate, crop it and upscale it 4x** (`kit/tools/upscale.py`, Real-ESRGAN). The user
  picked the plain crop over repainted crops, which moved coastlines and solar fields; a 4x plate also lets the
  camera push in ~3.7x on real pixels.
- **The model anchors on what is already there.** Four edits asking for smaller solar panels kept their size; edits
  that add something new (oceans, haze, a horizon glow, more fields) worked first time.
- **Show style options at every scale,** not on one key frame: the user may pick a different look per scale, and
  state the film's rule from what they see (Church of Superintelligence; see the recipe).
- Two `--edit` references at `--scale 1328` took about 2 min per image while a CPU upscale ran beside it; batch the
  edits, and upscale on the GPU (seconds) when the image server is idle.

**Limits and operations (16 GB card):**
- At most **3 `--edit` references at `--scale 1328`**; 4 stalled for 20 minutes in `cudaMallocAsync`. Describe a
  4th reference in words. 3 references take about 2.5 min.
- Watch progress in the image server's `logs/server.log` (s/it); cancel a stuck job with `POST /interrupt`.
- **Never edit a running batch script** (bash reads it as it runs): stop it, edit, restart from the first unfinished item.
- Keep every draft in `assets/plates/drafts/<shot>/`; write rejected picks down (`REJECTED.md`) instead of deleting.
- Save each batch's commands as run in `gen/plates_<batch>.sh`.

## Sound effects (local-sounds)

```bash
PY=~/.claude/skills/local-sounds/.venv/Scripts/python.exe; S=~/.claude/skills/local-sounds/scripts/sfx.py
$PY $S "low electrical hum of a vast machine, steady" --mode ambience --duration 12 --wait 240 --out "$FILM/assets/sfx/gen" --name Hum
$PY $S --batch "$FILM/gen/sfx.json" --out "$FILM/assets/sfx/gen" --dry-run     # a whole cue sheet, resumable
```

- One sound per request, with a concrete source and a material.
- **Restraint by default:** few effects, soft (`gain_db` -12 to -22), never competing with the voice; ambiences
  fade in and out. One author removed most effects from a film and disliked cartoon boings and swooshes at
  transitions. A comedy may want exactly those: STYLE.md decides.
- Prefer a cue sheet (`--batch`) for more than a few sounds. Puff Ahoy's 18 cartoon cues ran in about 45 s.
- **Name a concrete source and action.** "Sail filling with wind, deep cloth whump" came back near silent (CLAP
  heard silence); "loud whoomp of a big canvas sail snapping taut in a sudden strong wind" worked.
- A "tail is chopped" warning means a longer `--duration`. Trim and fade the picks to their beat with a small
  `gen/sfx_prep.py` (source take, start, length, fade) into `assets/sfx/`, and keep every take in `assets/sfx/gen/`.
- Levels that worked in a comedy with the music at 0 dB: hits and gags -4 to -9 dB, a gull -13, sea lapping -20.
- **Music-led films want fewer effects than you think.** On a tech-house film the user removed both transition
  whooshes (one "sounds like a closing door") and found a breath on a dying character "a bit kitsch" until it sat
  ~20 LU under the music (gain -19 dB on a -16 LUFS take). Ambience beds and a heartbeat on the kicks stayed.
- **Two copies of one loop crossfading** read as a whoosh where they overlap: extend one copy instead.

## Licences

Record each tool's model licence in the film's README. As of 2026-10: Breeze TTS 2 (voice) research and
non-commercial only; Qwen-Image (plates) research/evaluation; Stable Audio 3 (music, SFX) Stability AI Community
License. Fine for non-monetized posting; check before commercial use.

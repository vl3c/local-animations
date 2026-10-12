# Backlog

What is not built yet, most useful first. The workflow rules these came from are already in `skill/workflow/`;
the evidence is noted per item. Add new items during a film's harvest.

## Kit: next

1. **Checkpoint sheets, the rest.** `kit/tools/sheet.py` now tiles lettered drafts per row (Puff Ahoy). Still
   missing: the subtitle line printed under a tile, and per-act storyboard (C3) and animatic (C5) sheets straight
   from `render stills`, lettered per shot. Unlabelled tiles caused a pick on the wrong image (Lantern Cantor).
2. **Subtitles in the kit.** A helper that draws burned-in subtitles from the word timings, on by default
   (project.json switch), with a style option and safe-area placement. Group phrases on a speaker tag plus its
   quote, not only on pauses ("The ring texted:" + "Maybe don't."). A `--subs` listing for C5.
3. **More checks in `finish`:**
   - darkness: mean luma under about 0.04 for more than a few seconds ("too dark to read"; black wall benchmarks)
   - flash safety: large-area luminance flashes per second, at most 3 (Initial Condition specified it, never measured it)
   - palette rules from project.json, checked at 1-2 fps with CIEDE2000; also runnable on style frames and plates.
     Reference: `Initial Condition/frames/source/palette_check.py` (numpy only)
   - words lost in the speech band (300-3400 Hz margin of the voice over everything else while it speaks), per
     line, as local-music's `music.post.speech_margin` does; calibrated: 0 dB music over a battle section lost
     words, -6 dB kept 97%
4. **`kit/tools/plate_check.py`:** mean luma (at least about 0.08), a thumbnail for "can you name the subject",
   and a side-by-side tile of the drafts, before a plate is accepted.
5. **Overlay helpers in core:** `plate_mask(...)`, a `grid` stills mode for measuring coordinates, and an
   `on_plate(layer_fn)` pattern (draw before the camera). Today they live as code in
   `skill/cookbook/plate-overlays.md`.
6. **Cues on the music grid.** Cue specs that need no voice line: `"M:bar7"`, `"M:beat25"`, `"M:clack"` from
   `assets/music/*.beats.json` (`kit/tools/beats.py`) and named events in project.json, so `s.c()` and `sfx[].at`
   work for wordless films. Puff Ahoy kept the grid as constants in shots.py and film seconds in project.json.
   Read kicks from `<music>.kicks.json` (`kit/tools/kicks.py`), not a computed grid: a grid drifted 20-40 ms and the
   user saw it (Church of Superintelligence); a core `pulse(t)` helper on that list would replace each film's copy.
7. **`animkit.cel`: the cel compositor** from `skill/cookbook/cel-animation.md` (`pose`, `cam_m`, `blit` with mip
   levels, a cairo matrix helper, riders on a parent cel, the waterline mask), so cartoon films stop copying it.
8. **Expected warnings in `finish`.** A project.json list of deliberate checks (`"expect": ["flash@2.17",
   "starts_bright"]`) printed as expected in checks.txt, instead of being explained in the README by hand (an iris
   opening onto a bright scene; a title card at frame 0).
9. **Two checks in `finish`:** `--sync` runs `kit/tools/sync_check.py` when a kicks list exists and prints the
   offset; `--verify` re-renders a few frames from a cold cache and compares them to the encode (a cache-precision
   bug made frames depend on worker timing until Church of Superintelligence's cleanup found it).
10. **A preview encode in `finish`** (`--preview`: CRF 26 copy), and naming the output after the title instead of
   the slug.

## Kit: later

11. **An optional instability (glitch) module**, ported from `Initial Condition/film/post.py`: levels 0-3 per shot
   from project.json, protected windows, an `events.json` that `animkit.mix` turns into glitch sounds, with a palette
   guard after the pass. Lessons in `skill/cookbook/instability-glitch.md`.
12. **A scaffold command** (`kit/tools/new_film.py <Title>`): the folder, the templates and the kit snapshot in one
   step, replacing the shell lines in SKILL.md.
13. **Second picture backends** (from `reports/Animation frameworks for AI agents.md`): HyperFrames (pinned) for
   kinetic type, charts and diagrams, rendered to frames on the same segment grid and through the same post pass;
   then a local-video skill (Wan 2.2 / LTX-2.x via ComfyUI) to animate plates and make transitions, never to carry
   the story; Blender 5.2 LTS later for real depth. Verify alpha output early.

## Local tools (report to their projects)

14. **local-voice: `--bass` vs the "speech low under the bass" metric.** In the black wall Sonnet run the warning
    stayed at -6, -8 and -12 on ai-choir takes. Either the metric measures something the shelf can't reach (layers
    or echo), or the flag isn't applied before the check.
15. **local-voice: echo-tail trimming** for long-tail presets (ai-choir adds about 2 s per line): a `--tail <s>`
    option, or trim to the last word + N s in `animkit.mix`.
16. **local-image: `--cancel`** (wraps `POST /interrupt`) and a progress readout; a warning before 4+ `--edit`
    references at `--scale 1328` on a 16 GB card (it stalls in `cudaMallocAsync`).
17. **local-image: exact-size delivery** (1920x1080 without a cover-fit crop). Edits at `--scale 1328` of a 1664x928
    plate came back 1792x992 (Puff Ahoy), so an edited plate's aspect drifts too.
18. **local-image: `cutout.py` on inked cels.** On drawings over a cream background it keys the colour everywhere and
    cut out the doll's skin and hair, a face and white gloves (Puff Ahoy). A flood-from-the-border mode, as in
    `kit/tools/cel_matte.py`, would fix it in the tool.
19. **local-image: a built-in `--upscale`** (Real-ESRGAN x4plus through spandrel, already in its ComfyUI venv);
    `kit/tools/upscale.py` (added) in the kit until then. Church of Superintelligence: 4x plates (7168x3968 from
    1792x992) let a 1080p frame push in ~3.7x on real pixels, so zooms stop needing dissolves; the user preferred it to
    Lanczos and to generative re-detailing (which moved coastlines and solar fields). It smooths watercolor paper
    grain in flat washes: pair it with a shared paper-grain pass. CPU ~2 min per 1792x992 plate, beside a loaded
    ComfyUI.

## Benchmarks

20. **Finish the agent benchmark** (plan in the frameworks report, "Testing the agents fairly"): three runs per arm,
    blind pairwise judging, the number of human notes to reach "good" as the main metric. Done so far: Ember and
    black wall, Haiku and Sonnet, one run each (`projects/_eval_*`). Still open: Opus; the local model (Qwen 27B)
    alone and as a shot worker under a Claude director (Track C: ten well-specified shot functions); runs with and
    without the skill.
21. **A checkpoint benchmark:** the same brief with and without C1-C5, counting notes after the draft. Lantern
    Cantor's estimate: most of ~17 post-draft notes would move to checkpoints, for 10-15 min of the user's attention
    up front instead of ~2 h of fix rounds. Puff Ahoy (C1 + C3 + C4): 5 notes at the storyboard, none after the
    draft.

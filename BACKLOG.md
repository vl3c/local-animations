# Backlog

What is not built yet, most useful first. The workflow rules these came from are already in `skill/workflow/`;
the evidence is noted per item. Add new items during a film's harvest.

## Kit: next

1. **`kit/tools/sheet.py`: lettered contact sheets.** Drafts tiled with the shot id and a letter in each tile
   (`3-drive A/B/C/D`) and the subtitle line printed on the sheet; per-act storyboard (C3) and animatic (C5) sheets
   from `render stills`. Every checkpoint depends on it; unlabelled tiles caused a pick on the wrong image
   (Lantern Cantor).
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
6. **A preview encode in `finish`** (`--preview`: CRF 26 copy), and naming the output after the title instead of
   the slug.

## Kit: later

7. **An optional instability (glitch) module**, ported from `Initial Condition/film/post.py`: levels 0-3 per shot
   from project.json, protected windows, an `events.json` that `animkit.mix` turns into glitch sounds, with a palette
   guard after the pass. Lessons in `skill/cookbook/instability-glitch.md`.
8. **A scaffold command** (`kit/tools/new_film.py <Title>`): the folder, the templates and the kit snapshot in one
   step, replacing the shell lines in SKILL.md.
9. **Second picture backends** (from `reports/Animation frameworks for AI agents.md`): HyperFrames (pinned) for
   kinetic type, charts and diagrams, rendered to frames on the same segment grid and through the same post pass;
   then a local-video skill (Wan 2.2 / LTX-2.x via ComfyUI) to animate plates and make transitions, never to carry
   the story; Blender 5.2 LTS later for real depth. Verify alpha output early.

## Local tools (report to their projects)

10. **local-voice: `--bass` vs the "speech low under the bass" metric.** In the black wall Sonnet run the warning
    stayed at -6, -8 and -12 on ai-choir takes. Either the metric measures something the shelf can't reach (layers
    or echo), or the flag isn't applied before the check.
11. **local-voice: echo-tail trimming** for long-tail presets (ai-choir adds about 2 s per line): a `--tail <s>`
    option, or trim to the last word + N s in `animkit.mix`.
12. **local-image: `--cancel`** (wraps `POST /interrupt`) and a progress readout; a warning before 4+ `--edit`
    references at `--scale 1328` on a 16 GB card (it stalls in `cudaMallocAsync`).
13. **local-image: exact-size delivery** (1920x1080 without a cover-fit crop).

## Benchmarks

14. **Finish the agent benchmark** (plan in the frameworks report, "Testing the agents fairly"): three runs per arm,
    blind pairwise judging, the number of human notes to reach "good" as the main metric. Done so far: Ember and
    black wall, Haiku and Sonnet, one run each (`projects/_eval_*`). Still open: Opus; the local model (Qwen 27B)
    alone and as a shot worker under a Claude director (Track C: ten well-specified shot functions); runs with and
    without the skill.
15. **A checkpoint benchmark:** the same brief with and without C1-C5, counting notes after the draft. Lantern
    Cantor's estimate: most of ~17 post-draft notes would move to checkpoints, for 10-15 min of the user's attention
    up front instead of ~2 h of fix rounds.

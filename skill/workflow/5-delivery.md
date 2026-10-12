# 5. Delivery and the harvest

## The deliverables

| Path | What |
| --- | --- |
| `output/<Title>.mp4` | Master: 1920x1080, 24 fps, H.264 CRF 16, AAC 256k, at the agreed LUFS. `finish` writes `output/<slug>.mp4`; rename it. |
| `output/<Title> (preview).mp4` | A smaller copy for watching (CRF 24-28). |
| `output/contact.jpg`, `output/checks.txt` | One frame a second; the automatic checks. Explain any deliberate warnings in the README (smash-cuts). |
| `README.md` | Story, files, the rebuild command, licences (template provided). |
| `shots.py`, `project.json`, `kit/` | The film rebuilds on its own. |
| `assets/` with `drafts/`, `takes/`, `gen/` | Every draft, take and prompt kept. |
| `source/` + a rebuild script | What the soundtrack is built from (`local-music --export`), rebuildable without a GPU. |
| `CUES.md`, words JSON, `.srt` | The timeline, for people and for later edits. |

```bash
ffmpeg -i "output/<Title>.mp4" -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 160k "output/<Title> (preview).mp4"
```

- CRF 16 with fine grain runs about 73 Mbit/s (3.5 GB for 6.5 min): fine for YouTube and X Premium (16 GB), close
  to Facebook's 4 GB. Grain 0.03 plus a per-frame flicker ran 110 Mbit/s (288 MB for 21 s, Puff Ahoy): send the
  preview copy for messaging apps.
- **No AI credits or tool logos** unless asked.
- **Before any cleanup, keep everything the final is built from.** A cleanup once removed the music request a later
  tweak needed. When deleting drafts, update the README so its paths stay true.
- **"Clean up the intermediates"** means what is regenerated or superseded: `build/` (600 MB for 21 s), `output/stills/`,
  cut-outs replaced by better ones, and measuring crops. Drafts, takes, checkpoint sheets and `source/` stay
  (Puff Ahoy: 1.2 GB down to 0.6 GB). **"Keep what rendering needs, clean the rest"** goes further: drafts and
  candidates go too, but move each rebuild input out of `drafts/` into `ref/` first and keep `gen/` (Church of
  Superintelligence: 3.1 GB down to 0.77 GB). Delete to a recoverable trash (the Recycle Bin), not `rm`.
- **Prove the rebuild after a cleanup:** clear `build/` and render twice from a cold cache; the two encodes must
  match to the pixel. It found that `memo` returned float32 to the worker that built an entry and float16 to the
  others, so frames differed with worker timing (fixed in the kit).
- Your final message is the report: what you made, where, the checks, deliberate warnings, what you couldn't do.

## The harvest

Every film teaches something. Before closing the film, spend 10 minutes feeding it back into the
`local-animations` repository (`$REPO`), so the next film starts better. This replaces writing a long lessons file.

1. **Kit fixes.** Diff the film's snapshot against the repository's kit and port real fixes:
   ```bash
   diff -r --strip-trailing-cr "$REPO/kit/animkit" "$FILM/kit/animkit"
   ```
   Test each port on `projects/_smoke` (see the repository's CLAUDE.md).
2. **Recipes.** Any effect, rig or pass that another film could use goes to `skill/cookbook/` as one file, with
   style tags, the film it came from, the code, and its lessons (what didn't work). Add it to the cookbook index.
3. **Workflow lessons.** Turn each lesson into an edit of the workflow file it belongs to (a new rule, a corrected
   number, a new checkpoint example). Keep the evidence short: the film's name and what happened.
4. **Tool and kit wishes** go to the repository's BACKLOG.md, prioritized; tool bugs go to that tool's project.
5. **The user's preferences** (how they like to be asked, levels they liked) go to memory.
6. **Stage timings** from DECISIONS.md: if a stage ran far over budget, note why in the workflow.

Commit the repository changes, and show the user a short list of what was harvested.

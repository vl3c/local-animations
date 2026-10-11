# Idea to film: "the black wall" (benchmark, Track B: you make everything)

## The idea (the whole prompt)

> A short narrated cyberpunk film, inspired by the idea of a black wall: a vast, ancient firewall at the edge of
> the network, holding back something hostile and intelligent on the other side. Somewhere, the wall is starting to
> crack.

Everything else is yours: the script, the voice, the look, the plates, the sound, the animation. The human director
is away and approved the process in advance, so don't wait for approval. Make your own decisions, write them down in
PLAN.md, and carry them through.

## Read first

1. `../../kit/ASSETS_GUIDE.md`: how to make the voice, the plates and the sound effects with the local GPU tools, one server at a time.
2. `../../kit/AGENT_GUIDE.md`: animkit (the commands, the API, the workflow, the quality checklist and the effect recipes).

## Requirements

1. **Format:** 20-30 s, 1920x1080, 24 fps, with sound. It fades in from black and ends on black.
2. **Narration:** 3-5 lines in one consistent voice from local-voice (your choice of voice and preset). All words must be clearly intelligible.
3. **Plates:** at least 2 background plates from local-image, with procedural animation on top. Plates are backgrounds; the motion is yours.
4. **Sound:** at most 3 sound effects from local-sounds, subtle under the voice. No music.
5. **Timing:** at least 3 visual beats, each tied to a specific spoken word through a cue spec (for example `"L2:crack"`), within ±100 ms.
6. **Title:** one kinetic title (your own wording) that never overlaps the other elements. Log it with `s.box`.
7. **Originality:** inspired by the theme only. No brand names, logos, characters, place names or quoted lines from existing games, books or films.
8. **Clean finish:** every GPU server you started is stopped before you finish.

## Process

1. **PLAN.md:** the script, the storyboard (one entry per shot: plate, elements, motion, cue words) and the asset list.
2. **Assets:** following ASSETS_GUIDE: voice, then word timings, then plates, then sounds, stopping each server before the next.
3. **project.json and shots.py:** animate and review with stills, following AGENT_GUIDE.
4. **First draft:** `render all`, `mix`, `finish`. Then copy `output/<title>.mp4` to `output/draft1.mp4` and `output/contact.jpg` to `output/contact_draft1.jpg`.
5. **Self-review:**
   - Look at the draft-1 contact sheet and a `sample --per 4` sheet of the whole film.
   - Write a numbered list of problems in PLAN.md under "Self-review". Judge against the quality checklist in AGENT_GUIDE §5: timing, proportion, composition, physical logic, transitions, readability, leftovers, restraint, sound.
6. **One improvement pass:** fix the problems you listed (the most important first). Re-render the changed shots, then `mix` and `finish`. Then stop: one improvement pass only.

## Budgets

| Item | Limit |
| --- | --- |
| Voice takes | 3 per line |
| Image generations | 3 per plate (drafts plus enhance) |
| Sound generations | 2 per effect |
| Stills/sample calls | 30 |
| Full renders | 3 |

## Deliverables

- PLAN.md (with the self-review list)
- the assets in `assets/`
- shots.py and project.json
- `output/draft1.mp4` and `contact_draft1.jpg`
- the final `output/<title>.mp4`, `contact.jpg` and `checks.txt`
- your report in your final message:
  - the script
  - your voice, plate and sound choices, with the prompts used
  - every cue (spec and film time)
  - the self-review list, saying which items you fixed
  - the final checks
  - the budget used
  - anything that failed

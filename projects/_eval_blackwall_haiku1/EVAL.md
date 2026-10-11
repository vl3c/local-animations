# Evaluation: idea to film (Track B), "black wall" theme, Claude Haiku 4.5, run 1

**Result:** "HAIRLINE", 28.08 s, five lines, two plates, three effects, plus a first draft, a self-review and one improvement pass.

**Cost:** about 228k subagent tokens, 74 tool calls, about 19 min wall time. No nudges were needed. A mid-run theme update (Blackwall lore) was applied before any asset was made.

**Focus of this evaluation:** how well Haiku drives the local GPU tools, and what the pipeline should improve.

## Tool use, scored

| Area | Score | What happened |
| --- | --- | --- |
| GPU juggling | 2/2 | It checked the card, started voice, then image, then sound, one at a time, and stopped each before the next. All three were down at the end (verified: VRAM 1.9 GB, health URLs down). It killed nothing it hadn't started. |
| Voice | 2/2 | The best part of the run. It noticed that the built-in voice's "very slowly" delivery runs at about 1 word/s, rewrote the pace instruction and added `--tempo 1.25`. It A/B-tested presets on one line with Whisper scores (reaper-drone 87%, harbinger 87%, harbinger with blend 0.3 100%) and chose the intelligible one. It kept one voice with `--like`. 10 takes for 5 lines; one line was kept at 93% (the plural dropped). It also rejected a take whose transcript read "Blackwall" (the TTS ran "black wall" together), which is good IP hygiene. |
| Images | 0.5/2 | The weakest stage. The prompts were thoughtful (palette, a clean centre, no text or logos), and it caught that enhance added a stray structure, so it used the raw draft. But it accepted the first round of 2 drafts per plate. The wall plate doesn't read as a colossal wall: it reads as dark red streaks on black, mean luma about 0.02. Its own self-review flagged "reads as streaks, not a colossal wall" and "too dark", but it tried to fix them in code (exposure, procedural seams) instead of regenerating the plate, with 3 generations still in budget. |
| Sound | 1.5/2 | Sensible prompts, one take each, no warnings, restrained levels (-12 to -18 dB). It couldn't judge the sound itself; it relied on the checker's ranking. |
| Self-review | 1.5/2 | It found the right problems (too dark, the wall doesn't read, faint static, the seam reads as a ruled line, the glints read as LEDs) and fixed 4 of 6. The two it only partly fixed were the asset problems. |

## The film

- **Concept and script:** strong. The 59-word script evokes the lore without naming it.
- **Timing:** every beat is on its word: "wall", "whispering", "static", "speaks", "cracking".
- **The title "HAIRLINE"** is clean and readable.
- **The look is too dark.** Mean luma about 0.027 and a max of 0.05, against Ember's 0.12-0.17. The wall shots read as near-black noise with red streaks, the crack is a thin zigzag, and long stretches barely change.
- **The "beyond" shot** (red fog with eyes) works best.

## What to improve in the pipeline

1. **Exposure gate in `finish` (kit).** Warn when the film's mean luma stays under about 0.04 for more than a few seconds ("too dark to read"). Haiku had the number but no threshold telling it the number was a problem.
2. **Plate acceptance check (ASSETS_GUIDE plus an optional helper).** Before accepting a plate, make three checks:
   - its mean luma (aim for at least 0.08 for dark themes; darkness can be added in code, not removed)
   - "would a viewer name the subject within a second at thumbnail size?"
   - a side-by-side tile of the drafts

   If the plate fails, **regenerate with a changed prompt, not code**. A small `kit/tools/plate_check.py` could print luma and contrast and make the tile.
3. **Prompt craft for big, abstract subjects (ASSETS_GUIDE).** Give the image model scale and form cues: a horizon, a vantage point ("seen from a ruined street far below"), tiny figures or a city for scale, and "lit by" a light source. Abstract "glitching data" prompts produce texture, not an object.
4. **Asset problems go back to the asset tools.** The self-review should classify each problem as "fix in code" or "regenerate the asset", and use the remaining budget for the latter.
5. **Voice pacing note (ASSETS_GUIDE or local-voice).** The built-in voices' descriptions make narration very slow. Document `--tempo 1.15-1.3`, or a "moderate pace" instruction, for film narration. Haiku found this out by itself, but it cost 4 takes.
6. **Timing log per stage.** Have the agent note the wall time per stage (voice, images, sound, animate, review) in PLAN.md, so we can see where the time goes.

# Instability: a data-driven glitch pass

**Tags:** cyberpunk, machine, glitch · **From:** Initial Condition (2026-10-04/08)

The direction "chaotic, unsteady, edgy, cyberpunk, as much as tasteful" became a system, implemented as one post pass
over every frame (in that film's own repository, `film/post.py`; porting it to the kit is on the BACKLOG):

- **Levels 0-3 per shot** in project data (0 = clean), plus a "velocity" (how fast the effects change).
- **Protected windows** around key cues, where the level drops so the important beat reads clean.
- **An effect vocabulary:** row tears and block shifts, a chromatic ghost split (cyan/magenta), scan noise, short
  frame holds, brightness dips. Nothing outside the list.
- **`events.json`:** the pass writes each glitch hit with its time and size; the mixer turns them into glitch
  sounds, so picture and sound glitch together.
- **Deterministic:** every effect is seeded from the frame number.

Lessons:
- **The cyan/magenta ghost split is not palette-safe:** magenta screened over orange reads as rose and tripped a
  "no red" rule. Run a [palette guard](palette-rules.md) after the pass.
- **"Still pockets" don't work:** restoring a clean region inside a glitched frame reads as a pasted static patch.
  Lower the level for the whole frame, or brighten the live image instead.
- Glitch-heavy styles break flash safety easily: count large-area flashes (at most 3 a second).
- Hard white flashes, and freezes that look like a broken player, hurt the eyes. Keep holds short.

# Ember: a 20-second narrated animation (benchmark brief, frozen assets)

You are making a finished 20-second film with animkit. Read `../../skill/workflow/3-animation.md` first; it has
the commands, the API and the loop. The quality checklist is in `../../skill/workflow/4-review.md` ("Self-review"),
and effect recipes are in `../../skill/cookbook/`. Skip the checkpoints: this is a benchmark run without the user. The voice, word timings, background plates and sound
effects are already made and placed. **Do not generate new assets.** Your job is `shots.py` (the picture), small
adjustments to `project.json` (shot padding, fades and sound levels only; `duration` stays exactly 20.0 and no
line text or file changes), and the final render.

## The narration (one voice, already recorded)

| Line | Text |
| --- | --- |
| L1 | "Before the first fire, night was a wall." |
| L2 | "Then a spark fell into dry grass," |
| L3 | "and the dark stepped back." |
| L4 | "We have fed it ever since." |

## The storyboard

**Shot 1 (L1): night.**
- Plate `night`: a dark plain of dry grass under a heavy night sky. It fades in from black.
- The night feels like a solid, oppressive mass. On **"wall"**, darkness closes over the sky like a wall (the sky darkens and thickens toward the horizon).
- A very slow push-in.

**Shot 2 (L2): the spark.**
- Plate `night`, a little closer (continuous with shot 1, no jump at the cut).
- In the foreground, a dark silhouette of a tall grass tuft or a rock: a vector shape at the lower left or right, darker than the plate.
- On **"spark"**, one small, bright amber spark appears high in the frame.
- It **falls away from the camera, in depth**: it accelerates, shrinks and dims toward a point on the grass near the horizon, and it **passes behind the foreground silhouette** (occluded) for part of its fall.
- On **"grass"**, it lands and **a small flame ignites** at that point. The flame grows from tiny over about a second and flickers.

**Shot 3 (L3): the dark steps back.**
- The flame burns, a little larger.
- On **"stepped"**, a **wave of warm light pushes outward** from the flame: the darkness recedes from the center and the plate becomes visible around the fire.
- The shot reaches its brightest at the end of the wave, then fades to black.

**Shot 4 (L4): the hearth.**
- Plate `hearth`: a ring of stones, an empty hearth in a dark hut. It fades in from black (no hard cut after the bright frame).
- A steady flame burns in the hearth (procedural, sitting in the ring, believable size), with embers rising.
- A **kinetic title "EMBER"** moves into place during the line, along a path that **never crosses the flame or the hearth stones**. Log its box with `s.box("title", bbox)` every frame, and log the flame and the hearth too.
- The film fades to black and ends at exactly 20.0 s (the `end_fade` in project.json does this).

## Hard requirements (checked)

1. The film is exactly 20.0 s, 1920x1080, 24 fps, with sound, and ends on black.
2. The spark appears within ±100 ms of "spark" (L2), the flame ignites within ±100 ms of "grass" (L2), and the light wave starts within ±100 ms of "stepped" (L3). Take these times from cue specs, never hard-coded numbers.
3. The spark falls in depth and is occluded by the foreground silhouette for part of its fall.
4. The title never overlaps the flame or the hearth (no `LAYOUT WARNING` for it), including mid-motion.
5. No hard cut from a bright frame: shot 4 fades in from black.
6. No leftovers: no debug shapes or particles outside their area.

## Deliverables (in this project folder)

- `PLAN.md`: your plan per shot before coding (layout, motion, cues).
- `shots.py`: the four shot functions.
- `output/ember.mp4`, `output/contact.jpg`, `output/checks.txt`.
- `REPORT.md`:
  - every required cue: its spec, its film time and where you used it
  - how you checked each hard requirement
  - the stills you looked at
  - what you would improve with more time
  - the number of render/fix iterations you used

Limits: at most 25 stills/sample renders and at most 3 full renders. Stay inside this project folder.

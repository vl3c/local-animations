# Ember: plan

Frame: 1920x1080. Safe margin: x 77..1843, y 54..1026. Film cues (from `finish --info`, verified with
`timeline.cue_global`): L1:wall 4.66 s, L2:spark 7.14 s, L2:grass 8.98 s, L3:stepped 12.59 s, L4 16.32 to 18.28 s.
Shots: 1 = 0.00-6.54, 2 = 6.54-11.29, 3 = 11.29-15.42, 4 = 15.42-20.00.

Plate geometry: `night` (1664x928) cover-fits with scale 1.164, crop 8 px each side. Horizon near y 690.
Landing point / flame base in plate space: (1150, 690). `hearth` (same fit): ash pile centre near (980, 628),
stone ring about x 340..1630, y 378..931.

Continuity: one global camera push, scale = 1 + 0.005 * film_seconds, about the frame centre, used in shots 1-3.
Shot 2 and 3 pick up the same scale, so there is no jump at the cuts.

## Shot 1 (L1): night, 0-6.54 s
- Plate `night` pushed slowly. Fades in from black (project fade_in).
- On "wall" (film 4.66), a dark mass closes over the sky: an edge rises from the horizon (y 690) to y 230 over
  about 1 s, with a gently wavering lower edge. Above it the sky is multiplied down to about 12 percent.
- Nothing else moves.

## Shot 2 (L2): the spark, 6.54-11.29 s
- Same plate and push. The wall mass stays (no change at the cut).
- On "spark" (7.14): a small amber spark appears high, at about (1560, 200), inside the dark sky.
- It falls toward the landing point (1150, 690): x moves linearly, y accelerates (quadratic), size shrinks 7 to
  1.6 px, brightness drops to about 45 percent. A faint 6-step trail.
- Foreground silhouette: a dark tuft of tall grass (opaque, about 0.01 luminance), lower right, bases x 1230-1920,
  tips at roughly y 280-600, peaking near x 1400. The spark's path crosses the tuft's left flank, so it passes
  behind it for part of its fall. The tuft is drawn after the spark light, so it occludes the spark.
- On "grass" (8.98): the spark is gone and a small flame ignites at (1150, 690). It grows from 6 px to about 115 px
  over 1.1 s, flickers, and has a soft warm glow.

## Shot 3 (L3): the dark steps back, 11.29-15.42 s
- Same plate, push and wall mass. The flame grows gently from 118 px to 150 px over the line.
- On "stepped" (12.59): a wave starts at the flame. Its radius grows to about 1500 px in 1.8 s (ease-out).
  Inside the radius the wall mass is removed (plate visible). A warm ring sits at the front, and warm light fills
  the area near the fire. The flame brightens toward the end of the wave.
- Shot fades to black at the end (project fade_out 0.5).
- Whoosh sound effect at stepped-0.15 (project sfx).

## Shot 4 (L4): the hearth, 15.42-20.00 s
- Plate `hearth`, fades in from black (fade_in 0.8). Fire base at (980, 628), flame about 215 px tall. Warm glow on
  the stones. Steady flicker.
- Embers: about 36 seeded particles rising about 260 px and fading at both ends, inside x 920..1040, y 370..640.
- Title "EMBER": size 150, Georgia, warm off-white. Moves from (560, 250) to (960, 215) with ease-out during L4
  (cue L4:start to L4:end) and tracking tightens 70 to 26. The path stays above y 300, so it never crosses the
  flame (box y 412..628) or the hearth (box y 628..935). Boxes logged every frame: title, flame, hearth.
- Film ends with project end_fade 1.5 s.

## Must never overlap
- Title box (about y 147..305) and flame box (about y 412..628), hearth box (y 628..935).
- Silhouette tuft and the landing point / flame (tuft bases start at x 1230; flame half width under 40 px).
- No debug shapes; particles inside their regions.

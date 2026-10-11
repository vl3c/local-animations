# Ember: plan (frame = 6x6 grid, 320 x 180 px cells; horizon of the night plate is y~700 on screen)

Cue times (film time = shot start + shot seconds; shots start at 0, 6.54, 11.29, 15.42):
- L1:wall   shot 1, ~4.66 s film  -> darkness closes over the sky
- L2:spark  shot 2, 7.14 s film   -> spark appears
- L2:grass  shot 2, 8.98 s film   -> spark lands, flame ignites
- L3:stepped shot 3, 12.59 s film -> light wave starts (whoosh sfx is already mixed at stepped-0.15)
- L4:start / L4:since (shot 4)    -> title EMBER travels and settles

Camera (screen space, pushes about the horizon point (960, 700), so the horizon stays put):
shot 1 scale 1.00 -> 1.07 (very slow), shot 2 1.07 -> 1.12, shot 3 1.12 -> 1.17. No jumps at the cuts.
The fire is anchored in plate coordinates (760, 742) and mapped through the same camera so it never slides.

## Shot 1: night (L1)
- On screen: plate `night` brightened so the dim blue sky and the grass read (cells rows 1-4 sky, 5-6 grass).
- Motion: slow push. On "wall" a veil rises from the horizon over the sky (soft edge, no band), densest at
  the horizon, so the whole sky ends as one dark mass. Final state = the start state of shots 2 and 3.
- Never: a hard-edged band or ring; a bright element.

## Shot 2: the spark (L2)
- Same plate and dark state, closer. Foreground silhouette: a leaning tuft of tall grass, lower right (cells
  4-6 x 4-6, tips reaching up to y~380). It is a vector shape much darker than the plate; it fades in and
  rises ~25 px during the first 0.7 s (so it does not pop), then stays.
- On "spark": small amber spark appears high (about x 1290, y 120), then falls toward the fire point at
  (760, 742)-ish with y accelerating (v = u^1.8), x curving left, size 7 -> 1.6, brightness 1 -> 0.45.
  Draw order: plate, light (spark, flame), then the silhouette on top. The path is chosen so the tuft's
  upper left part covers the spark for ~0.3 s mid-fall; it emerges left of the tuft and lands.
- On "grass": a small flash and the flame ignites at the landing point, grows from ~3 px to ~36 px over
  ~1 s (ease-out), then flickers. A soft warm light grows on the grass around it.
- Never: the flame under/behind the tuft, a spark that jumps, silhouette lighter than the plate.

## Shot 3: the dark steps back (L3)
- Same camera, silhouette stays (dark, nearer than the fire). Flame grows from 44 px to 70 px.
- On "stepped": a soft warm reveal veil (radius 0 -> ~1800 px, 450 px soft edge) opens from the flame;
  inside it the plate shows lit and warm, with light falling off with distance. Brightest at the end of the
  wave (~stepped + 2 s), then the shot fades to black (fade_out in project.json).
- Never: a drawn ring or band; a blown-out white core.

## Shot 4: the hearth (L4)
- Plate `hearth` with a very slow push (1.00 -> 1.04). Fades in from black (0.8 s, project.json).
- Flame: particle flame, ~175 px tall, standing on the ash heap at about (985, 655); warm light on the
  stones that flickers; embers rise from the flame in a narrow column (x 900-1070), fading with height.
- Title "EMBER" (Georgia, 104 px): fades in and glides from y 250 up to y 165 at the top centre while the
  letter-spacing tightens, travelling from L4:start to L4:since. The ring of stones starts at y~378, the
  flame top is at ~480: the title lives in the empty dark band at the top and never enters those boxes.
- Logged boxes every frame: "title", "flame", and the hearth as four boxes around the ring
  (hearth_back/left/right/front), all transformed with the camera push.
- Film end fade (1.5 s) takes everything to black at exactly 20.0 s.

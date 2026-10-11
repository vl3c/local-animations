# HAIRLINE: plan

(Revision 2, director's notes: the title card was removed (requirement 6 dropped) and all eyes were redesigned; see the end of this file.)

Title: **HAIRLINE** (the first fracture in a wall that was meant to be perfect).
Length target: ~25.6 s, 1920x1080, 24 fps.

## Concept
The film is spoken by the thing behind the wall. A world-spanning black barrier, built long ago to seal in the
hostile intelligences left by the old network's collapse, is the only thing between them and the small, far-away
neon of the human city. The narrator is the other side: patient, courteous, and almost through.
Lore evoked, never named: a catastrophe, rogue minds in the ruins, a vast black firewall, the dead haunted far side,
cold neon on the human side only, a wall that has begun to crack and something speaking behind it.

## Script (4 lines, 31 words)
- L1: Long ago, you built a wall, and called the silence safety.
- L2: We waited in the dark. We learned your names.
- L3: Listen. Your wall is cracking.
- L4: Come closer. We are almost through.

## Voice decision
local-voice, `ancient-female` base voice + `ai-choir` preset (airy voice with quiet layers in other registers, a
muffled echo and a deep shadow: reads as "many minds speaking as one"), `--blend 0.35` (part human, to keep the words
clear), `--tempo 1.4` (the base voice is very slow; 1.0 would give 40 s), `--bass -8`, room reverb. L2-L4 made with
`--like` the first take so the voice is one. Each processed take is trimmed to last word + 1.2 s with a 0.7 s fade
(the ai-choir echo tail would otherwise add ~2 s per line). Words timed with kit/tools/words.py.

## Look
Near-black glitching wall with crimson static, scanlines and fractured red light (procedural static, scanlines,
glitch slices, chromatic split on top of a dark plate). Cold cyan/magenta neon is only the tiny skyline on the human
side, bottom of shot 1. The far side is dark red with vast shapes and eyes in the fog (eyes drawn procedurally).

## Plates (local-image, Qwen-Image 1664x928)
1. `wall_wide`: the human-side view, tiny neon skyline at the bottom, the colossal black wall filling the rest.
2. `beyond`: the far side, a dark red ruined plain between vast shapes, a red haze in the centre.
3. `wallface`: close surface of the wall, shattered pixel blocks around a black empty centre (where the crack goes).

## Storyboard
Frame is a 6x6 grid; the wall and the crack sit on the centre line.

**Shot 1, "the wall" (0-8.6 s, plate wall_wide, L1).** Fade in from black over 1.6 s. The camera pushes slowly in
toward the skyline. Near-black wall, low static. On "wall" (`L1:wall`) a red scan beam sweeps up the wall from the
skyline to the top edge; below the beam the wall is lit with crimson static, scanlines and sporadic glitch slices:
the wall asserts itself. A last glitch collapse into the dip to black at the end of the shot.

**Shot 2, "the dark" (8.6-13.2 s, plate beyond, L2).** Slow push into the red haze, drifting red motes, faint static.
On "dark" (`L2:dark`) two faint pairs of slit eyes open in the shapes on the left and right. On "names"
(`L2:names`) a crowd of small eyes opens in staggered fashion all over the fog; a large pair opens in the centre
haze on "learned" (`L2:learned`). Nothing else.

**Shot 3, "the crack" (13.2-25.6 s, plate wallface, L3 + L4, one continuous shot).** Slow push-in. Quiet static.
On "wall" in L3 (`L3:wall`) the surface flickers and a faint hairline of light blinks at the origin point. On
"cracking" (`L3:cracking`) a thin jagged crack of red light races up and down from the origin with side branches,
camera shake, chromatic split and glitch slices, crack sound. On "almost" (`L4:almost`) the crack starts to open into
a lens-shaped rift that shows the far side. On "through" (`L4:through`) it flares, red light floods over the wall
and a huge slit eye opens inside the rift. ~0.6 s later the title HAIRLINE assembles letter by letter under the
rift (glitch jitter settling, tracking closing), holds, and the film fades to black (end_fade 1.2 s).

Never overlap: the title (y 875-990) stays below the rift (y 70-790); logged as boxes.

## Cues
| spec | beat |
| --- | --- |
| `L1:wall` | scan beam sweeps the wall, static ignites |
| `L2:dark` | first eyes open |
| `L2:names` | the crowd of eyes opens |
| `L3:cracking` | the crack runs, shake, crack sound |
| `L4:almost` | the crack begins to open into a rift |
| `L4:through` | flare, eye opens in the rift, swell |
| `L4:through+0.6` | title assembles |

## Assets
- vo/L1..L4.wav (+ .words.json)
- plates/wall_wide.png, beyond.png, wallface.png
- sfx/hum.wav (wall hum ambience, whole film, -22 dB, fades), sfx/crack.wav (at `L3:cracking`, -12 dB),
  sfx/swell.wav (static swell at `L4:almost`, -18 dB). No music.

## Prompts used
- wall_wide: "A vast dystopian digital barrier seen from far away at night: an impossibly colossal wall of pure black
  glitching data rising from the ground and filling the whole frame up to the top edge, spanning the entire width,
  its surface corrupted and pixel-shattered, near-black with deep crimson-red static, fine horizontal scanlines and
  fractured red light leaking along its edges. At the very bottom of the frame a tiny, distant low skyline of a city
  with small cyan and magenta neon lights, very small and far away, under the wall. Heavy dark haze, cinematic matte
  painting, ominous, calm, the middle of the wall is smooth and empty, no people, no text, no logos."
- beyond: "The dead, haunted far side of a ruined digital world: an endless churning storm of dark red static and
  corrupted data, black and deep crimson, vast faint towering shapes and silhouettes of enormous intelligences barely
  visible inside the noise, glitch fragments and thin scanlines, red volumetric fog, painterly cinematic matte
  painting, ominous, the center is a dim empty red haze, no people, no text, no logos."
- wallface: "Extreme close-up of the surface of an immense black firewall: smooth glossy near-black panels of
  corrupted data, pixel-shattered edges, fine crimson-red static and horizontal scanlines, faint seams of deep red
  light, dark and cinematic, the center is a smooth empty dark area, no text, no logos."
- sfx: "deep low electrical hum and sub-bass drone of a colossal machine wall, steady, ominous, with faint crackling
  static" (ambience 26 s); "a single sharp crack of thick black glass splitting with a short digital glitch burst"
  (2 s); "a slow rising swell of distorted radio static with faint whispering voices, building into a harsh digital
  roar" (5 s).

## Self-review
Reviewed from `output/contact_draft1.jpg` and a `sample --per 4` sheet of the whole film (and the sound levels measured
numerically from the sfx files against the voice).

1. Shot 1 (proportion/composition/readability): for the first ~3.5 s the frame is almost empty black; the wall, the hero
   of the film, does not read as a colossal object. After the scan beam its surface is a field of red dashes with no
   structure or mass.
2. Shot 2 (readability): the small eye pairs read as floating orange orbs/UFOs, not eyes (slits are illegible at that
   size); the crowd looks like random lights. The plate's vast shapes are hardly visible.
3. Shot 3 (restraint/physical logic): the crack reads as a bright branching lightning bolt, not a hairline fracture.
4. Shot 3: the rift interior is a flat red blob and the far side is not visible through it; the lens shape is soft.
5. Shot 3: the first ~2.8 s are static wall with a barely visible hairline pulse on "wall" (L3:wall); the build-up is weak.
6. Sound: the effects are too quiet to help (crack peak about 10 dB under the voice peak, hum about 21 dB under the
   voice RMS). Subtle is right, inaudible is not.
7. Transitions: the dips to black between shots are long (about 0.7 s of black each); they stall the pace.
8. Overall: the whole film is very dark (max mean brightness 0.12); the static dashes are too uniform and long.

(Fixes in the improvement pass: see the end of this file.)


## Improvement pass (done once)
1. Fixed (shot 1): panel seams visible before the scan, three dim red glows drifting behind the wall (something moving
   behind it), the beam slightly torn, static density reduced and clustered in "bad sectors", city exposed separately
   so it stays calm while the wall is lifted.
2. Fixed (shot 2): fewer and larger eyes with legible slit pupils, large pair in the centre, plate exposure up, bloom down.
3. Fixed (shot 3): thin hairline crack (core 1 px) with two branches per side instead of seven.
4. Partly fixed: smoother lens-shaped rift, the far side shown at lower flood level, darker rim; the interior is still
   mostly flat red haze (the plate's far haze has little texture at that crop).
5. Fixed: stronger hairline flicker on "wall" (L3:wall) and just before the crack, small shake.
6. Fixed: hum -22 -> -14 dB, crack -12 -> -5 dB, swell -18 -> -11 dB.
7. Fixed: dips to black shortened (fade_out 0.22, fade_in 0.3).
8. Partly fixed: wall and static less uniform; overall brightness is still low by design (max mean 0.09).

## Revision 2 (director's notes)
- Title removed completely (code, boxes, timing). The film now ends on the rift eye, then the 1.2 s end fade to black.
  Duration and all other timings unchanged (25.58 s). The project title "Hairline" remains only as the output file name.
- All eyes redrawn (shots.py, `draw_eye`): irregular asymmetric lid outlines (skewed peaks, jagged edges that fizz at 12 fps),
  no mirrored pairs. Pupils vary: jagged vertical or diagonal slits, horizontal slit, trio of discs, uneven double slit, ring, a
  slit with satellite pupils. Iris = rings of data cells that drift and flicker, radial fibres, limbal ring; veins creep in from
  the lid with forks; fragments peel off the edge. Different sizes, angles and opening speeds (0.35-1.5 s).
- Integration: eyes are drawn on a layer that gets the plate's camera push, glitch slices, blocky dropout (eaten by the static),
  horizontal bleeding and a soft blur before being screened in; each eye flickers out now and then and blinks on its own period.
- Shot 2: 13 eyes in 3 groups opening on `L2:dark`, `L2:learned`, `L2:names` (same cue structure as before).
- Rift eye (shot 3, opens on `L4:through`): a huge tilted eye (720 px wide) with 11 rings of fine iris cells, 10 veins, a main slit
  with two satellite pupils; the iris drifts and rotates and the pupil narrows from `L4:through+0.5` over about 3 s. Its edge
  dissolves into the static more strongly than its core. The rift stays behind it as a red glow.

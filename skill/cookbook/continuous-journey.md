# Continuous journey: one zoom through generated paintings

Style tags: `painterly`, `atmospheric`, `any`. From: Church of Superintelligence (68 s, wordless, watercolor, orbit
→ desert → crowd → faces → bloodstream → eye).

A film that is one unbroken move through scales, built from separately generated plates, without ever showing an
enlarged pixel or a plain crossfade.

## The plates

- **Upscale every plate 4x with Real-ESRGAN** (x4plus, through spandrel; local-image's ComfyUI venv has torch and
  spandrel): 1792x992 → 7168x3968, so a 1080p camera can push in ~3.7x on real pixels. GPU: seconds per plate;
  CPU: ~2 min. It keeps edges crisp and smooths paper grain in flat washes, so add one shared paper texture in the
  render. The user preferred it to Lanczos and to generative re-detailing (which moved coastlines and solar fields).
- **Build each scale so it matches its neighbours.** Two ways that worked:
  - *Crop, then upscale*: the closer plate is a crop of the wider one, Real-ESRGAN'd. Better still, upscale the
    whole wide plate once and push into it: the opening became one push from the whole globe into North Africa on
    one 7056x3968 plate (a 1764x992 crop of the globe, 4x), with no dissolve and no change of direction (the first version dissolved between two plates
    and the push turned from the Middle East to Spain: "both should zoom toward North Africa").
  - *Edit with the locked reference*: the desert's drone and high views were edits of the locked church image
    ("show this same building from much higher up"), so the building is the same at every scale.
  - What failed: repainting an upscaled crop as "crisp detail" (the model moved things), and painting a wider view
    and cropping into it (the monument didn't match the locked design).
- **A collage plate for a row of people**: crops of the locked faces edge to edge, joined by a narrow ragged seam
  (~36 px soft, a 90 px overlap); wide fades between faces blurred their bodies. Faces with raised hands crossing
  the seams were regenerated with the hands lowered.

## The camera

```python
def cam(name, cx, cy, zoom=1.0, rot=0.0):
    """Frame from a 4x plate: centre in plate fractions, zoom 1 = the 16:9 cover-fit. Pre-shrink big windows with
    INTER_AREA (keeping the sub-pixel centre), then one warpAffine with INTER_CUBIC: slow moves never step."""
```

Write the film as one compositor `frame(t)` in film seconds, with the music's beats as named constants, and make
the project's shots thin windows on it (`def shot_3(s): return render_t(s)`), cut on downbeats.

## Transitions that are things in the world

| Transition | How |
| --- | --- |
| aligned fade (two views of one object) | rigid only: one uniform scale + shift, least-squares fitted to 6-8 hand-marked landmarks (feature matching failed on two separately generated paintings: 6 inliers), the views zooming about the landmarks' centroid on one shared zoom curve, then a plain 1.8 s fade. A landmark homography with a morph aligned better and was rejected: "it changes geometry by melting it". |
| clouds / haze / vapour | billowy fractal noise (6 octaves, contrast in the mid-tones) on a 2W x 2H field, seen through a window that zooms in as you pass (flying through it); cover `sin(pi u)^sharp * 1.3`, so it is opaque only near the peak; **after the peak it parts from a point** (raise the threshold near that point), so the subject is revealed first. A plain noise mask looked like flat camouflage. |
| a mist rising | the same, with the threshold biased by height while it builds |
| wash dissolve | `b` spreads over `a` through a noise-edged front with a slightly darker wet line: reads as wet paint |
| a light bloom | a radial light from the subject's on-screen position swelling to white over ~0.7 s, then receding on the next scene (count it as the film's one flash) |
| a glow opening | a noise-edged disc growing from the centre, with an iridescent rim on its edge |

## Making painted stills feel alive (without puppeting faces)

- **A kick pulse** (`bump(t)`: 1 on each detected kick, decaying over 0.2 s) that brightens only the saturated
  colour.
- **Billow only the substance**: a slow flow distortion (`cv2.remap` by two scrolling noise fields) masked to the
  substance's hues (HSV hue cyan..magenta, saturated, not dark), feathered ~3 px. Masking by saturation alone also
  caught sand and skin, and the building's edges wobbled; on the faces it warped the painted eyes, so it is off there.
- **A pan over a row of faces**: the user wanted one constant speed from the first face to the last (holds and
  glides were rejected), starting only once the transition into it has cleared (the first face was lost in a bloom).
  A quarter-frame horizontal blur keeps it readable; averaging 4 sub-frame positions made a comb.
- **Pulses on the music**: drive them from the kicks detected in the waveform (`kit/tools/kicks.py`), never from a
  BPM grid, and check them on the encode (`kit/tools/sync_check.py`).

## Style per scale

A grid of five watercolor looks x six scales let the user mix looks (one for the building, another for the planet,
a third for the faces) and state the film's colour rule: "inner ecstasy vs outer desolation", saturated colour only
on the people and the substance, a muted world.

## Measure motion you can't watch

Read the encode back, frame-difference it at 480x270, and list the biggest diffs and any 3-frame luma jumps: it
found the too-fast pan and the one deliberate flash.

# Cel animation from generated drawings

**Tags:** cartoon, comedy, rubber-hose, any character animation · **From:** Puff Ahoy (2026-10-11)

Characters as cut-out cels placed with affine matrices over painted plates, swapped like 1930s replacement
drawings (talk, point, puff, inhale, blow, flop), with squash, stretch and camera moves in code. 21 seconds, six
shots, 14 cels, accepted at the first draft.

## Making the cels

1. **C1 picks the base drawing** of each character, on a plain cream background ("character model sheet ... full
   body, centered, on a plain cream background").
2. **Every pose is an edit of the pick** (`--edit ref/<name>.png --scale 1024`), with the design pasted as a "Keep
   the same character design exactly: ..." sentence. The edits keep the geometry, so the variants line up.
3. **Matte with `kit/tools/cel_matte.py`, keeping the full canvas.** Variants then swap in place: the spoon's feet
   stay on the rock through talk, puff, inhale and flop with one anchor. Don't use local-image's `cutout.py` on
   cream-background cels: it cut the doll's skin and hair, the hero's face and the white gloves out.
4. **Measure anchors on a grid crop** of the cel (feet, the wheel's centre, the chest), and write them as constants.

Prompt lessons:
- "a long trumpet-shaped pucker" drew a wooden stick that read as a second handle; "ONE mouth pursed into a small
  round O ... a gust of air shooting out of it to the right" worked (4 of 4).
- "glance hard to the LEFT: pupils in the left corners" barely moved the pupils (2 seeds, 2 directions). Small
  facial motion is better drawn in code (below).
- A trademark-looking emblem from the prompt can be erased with an edit ("erase the emblem ... plain dark grey like
  the rest of the bodysuit"); the C1 pick kept everything else.

## The compositor

```python
def pose(x, y, k, anchor, rot=0.0, sx=1.0, sy=1.0):
    """Cel anchor -> (x, y), scaled k (squash sx, sy), rotated about the anchor."""
    return Tm(x, y) @ Rm(rot) @ Sm(max(k * sx, 1e-3), max(k * sy, 1e-3)) @ Tm(-anchor[0], -anchor[1])

def cam_m(cam):
    """World -> screen: zoom z about (cx, cy), clamped so the plate always fills the frame."""
    z, cx, cy = cam
    cx = min(max(cx, W / (2 * z)), W - W / (2 * z))
    cy = min(max(cy, H / (2 * z)), H - H / (2 * z))
    return np.array([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy], [0, 0, 1]], float)

def blit(img, name, M):
    """Composite a premultiplied RGBA cel through the 3x3 matrix M (cel px -> screen px)."""
    scale = math.sqrt(abs(np.linalg.det(M[:2, :2])))
    level = int(min(3, max(0, math.floor(math.log2(1 / max(scale, 1e-6)) - 0.5))))
    spr = cel(name, level)                  # mip levels by cv2.pyrDown: 1024 px cels at 0.23 alias otherwise
    M = M @ Sm(2 ** level)
    h, w = spr.shape[:2]
    c = M @ np.array([[0, w, w, 0], [0, 0, h, h], [1, 1, 1, 1]], float)
    x0, x1 = max(0, int(c[0].min())), min(W, int(math.ceil(c[0].max())))
    y0, y1 = max(0, int(c[1].min())), min(H, int(math.ceil(c[1].max())))
    if x1 <= x0 or y1 <= y0:
        return img
    out = cv2.warpAffine(spr, (Tm(-x0, -y0) @ M)[:2], (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
    img[y0:y1, x0:x1] = out[..., :3] + img[y0:y1, x0:x1] * (1 - out[..., 3:4])
    return img
```

- **Warp only the cel's bounding box**, not the frame: 6-8 cels a frame rendered 21 s in 70 s on 4 workers.
- **Cairo drawing shares the matrices:** `ctx.set_matrix(cairo.Matrix(M[0,0], M[1,0], M[0,1], M[1,1], M[0,2],
  M[1,2]))`, then draw in the cel's own pixels. The sail was drawn in ship pixels and rode every bob, lurch and
  rocket for free.
- **Characters riding a vehicle** are placed in the vehicle's cel pixels (`Ms @ Tm(x, y) @ Sm(kr) @ Tm(-anchor)`),
  so they follow it. Draw them **before** the hull (it hides their feet), and the sail before the passengers.
- **Sit the hull in the water:** after drawing the ship, put the plate's own sea back below a wavy waterline
  (a cairo mask of the wave shape, `img = img * (1 - m) + plate * m`), then draw foam curls on the line. A flat
  "sea colour" strip read as a rectangle.
- **Camera snaps** are a zoom about a moving world point (the doll's chest, from her matrix): 1.0 → 2.5 in 0.18 s,
  hold, back out for the next beat. The plate is warped with the same matrix.

## Replacement timing

- **Mouth flaps on twos:** `"talk" if int(t * 12) % 2 == 0 else "closed"`, only inside the babble's windows.
- **Bounce to the music:** squash `sy = 1 - 0.05 * bump(t)`, where `bump` is 1 on each beat decaying over 0.22 s.
- **Eye darts in code:** paint the eye whites over the old pupils (the convex hull of each white blob, eroded 1 px),
  then bake N gaze cels with round pupils clipped to the eye (Puff Ahoy `gen/eyes.py`); pick one per beat.
- **A swap that must never show the in-between** (a top flying off as shells cover her): the cel swap, the flying
  prop's start and the impact stars happen on the same frame, and the props fly in *before* that frame. Check it
  frame by frame on a crop of 6 stills around the cue.
- **A released-balloon flight reads only if the nozzle trails:** orient the cel so its mouth points against the
  velocity (`rot = atan2(-vy, -vx)` for a mouth on the cel's +x), trail puffs where the mouth was 35 ms ago, and
  shrink it as it flies. Flying the round "inhale" cel on a loop read as "why is the spoon in the air" (user note).
  Fly along a Catmull-Rom spline through hand-placed points, and keep the loop inside the frame.

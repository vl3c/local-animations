# Vintage film: two-strip colour, film wear, iris

**Tags:** cartoon, vintage, 1930s · **From:** Puff Ahoy (2026-10-11)

The last pass of every shot, so generated plates and cels with modern colours sit together as one old print.

```python
def two_strip(img):
    """Red-orange and blue-green records: yellow turns salmon-orange, blue turns teal; warm paper whites."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    two = np.stack([r, 0.55 * g + 0.45 * b, 0.42 * g + 0.58 * b], -1) * np.array([1.0, 0.97, 0.87], np.float32)
    out = img * 0.35 + two * 0.65
    return 0.03 + 0.95 * (out + 0.10 * out * (1 - out) * (out - 0.5) * 4)   # gentle S, lifted film base

def finish_frame(img, s):
    t = s.gf / FPS
    img = two_strip(np.clip(img, 0, 1))
    dx, dy = 1.2 * vnoise(t, 11, 2.0), 1.6 * vnoise(t, 12, 1.7)                  # gate weave
    img = cv2.warpAffine(img, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    img = img * (1 + 0.035 * (hash01(s.gf, 7) - 0.5))                           # per-frame flicker
    return np.clip(vignette(img, 0.35), 0, 1)                                   # + project.json "grain": 0.03
```

- Mixing 65% of the two-strip version kept the cels' coral and teal and turned a lemon-yellow belt and blonde hair
  orange-gold. Prompting the drawings in "faded two-strip Technicolor (coral red, burnt orange, teal green, cream,
  black)" made the grade's job small.
- **The lifted film base breaks "ends on black":** `finish` warned "does not end on black" (last frame 0.030). After
  the final iris, return `np.zeros((H, W, 3))` without the grade (last frame 0.012, from the kit's grain).

## Iris

```python
def iris(img, cx, cy, r):           # a hard-edged circle, 3 px soft, centred on the subject's screen position
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return img * np.clip((r - d) / 3 + 0.5, 0, 1)[..., None]
```

- Close it on the music's final hit (`ease`, 0.75 s), centred on the subject's *screen* position after the camera.
- **Apply it only inside its window.** An iris "open" at a radius smaller than the distance to the farthest corner
  blacks out part of the frame: one centred on the spoon at the left edge cut the whole right of shot 6.
- `finish` reports an iris opening from black onto a bright scene as a FLASH/CUT warning; it is the period's
  grammar. Say so in the README.

# Overlays that fit a generated plate

**Tags:** cartoon, comedy, any plate-based · **From:** Lantern Cantor (2026-10-10)

Drawn details (a phone wallpaper, paint drips, a halo, a ruler, an HP bar) must sit on the plate exactly and move
with the camera.

## Measure positions on a grid, don't guess

Render a still with a labelled grid over the plate, or crop and zoom the region, and read coordinates off it. A grid
crop put paint drips exactly on a character's abs.

```python
def grid_overlay(img, step=60):
    """Debug only: a labelled coordinate grid. Never leave it in a shot."""
    L = Layer(); ctx = L.ctx
    ctx.set_source_rgba(1, 0, 1, 0.5); ctx.set_line_width(1)
    for x in range(0, W, step):
        ctx.move_to(x, 0); ctx.line_to(x, H)
    for y in range(0, H, step):
        ctx.move_to(0, y); ctx.line_to(W, y)
    ctx.stroke()
    for x in range(0, W, step * 2):
        for y in range(0, H, step * 2):
            text(ctx, f"{x},{y}", x + 2, y + 10, size=10, col=(1, 0, 1), anchor="left")
    return L.over(img)
```

## Take shapes from the plate itself

A mask from the plate's own white screen (largest white component, holes filled, 1 px dilate) fitted a phone
wallpaper exactly, notch included. A drawn rounded rectangle did not.

```python
import cv2

def plate_mask(img, test=lambda im: im.min(axis=2) > 0.85, dilate=1):
    """Largest connected region where test() holds, holes filled, as a float mask in [0, 1]."""
    m = test(img).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n < 2:
        return np.zeros(img.shape[:2], np.float32)
    m = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(m, cnts, -1, 1, thickness=cv2.FILLED)      # fill holes
    if dilate:
        m = cv2.dilate(m, np.ones((2 * dilate + 1, 2 * dilate + 1), np.uint8))
    return m.astype(np.float32)
```

Compute it once per plate with `memo`, then composite: `img = img * (1 - m[..., None]) + wallpaper * m[..., None]`.

## Draw onto the plate before the camera move

So drawn details zoom and pan with the plate:

```python
base = load_plate("gym")
base = drips_layer(s).over(base)              # drawn in plate coordinates
img = push(base, lerp(1.0, 1.15, u), cx, cy)  # then the camera
```

## Halos over line art

A glow on top of an object washes out its line art. Screen the halo over everything, then redraw the object crisply
on top (or composite its cut-out again).

## Text that doesn't change

local-image renders text well: a sign or a fixed screen text can be generated in the plate instead of drawn.

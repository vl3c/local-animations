# Palette rules: check and guard

**Tags:** any with colour rules · **From:** Initial Condition (2026-10-04/08)

A STYLE.md palette rule ("no gold before 4:20", "red only on weapon edges", "at most 0.02% of #D7263D") needs a
**check** that measures it and, sometimes, a **guard** that enforces it after effects that create hues by accident
(bloom, grading, colour splits).

## Check

Measure the share of pixels within a colour distance of a forbidden colour, at 1-2 fps on the final encode, and on
style frames and plate picks before animating. A check run over one film's own style frames found two breaking the
rules they illustrated. That film used CIEDE2000 (numpy only, in its `frames/source/palette_check.py`); a kit version
is on the BACKLOG. A cheap first version, enough for a "how much of this colour" rule:

```python
import cv2

def colour_share(img, hex_col, de=12.0):
    """Fraction of pixels within ~de (CIE76 in Lab, a rough stand-in for CIEDE2000) of hex_col."""
    def lab(a):
        x = cv2.cvtColor((np.clip(a, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        x[..., 0] *= 100 / 255
        x[..., 1:] -= 128
        return x
    ref = lab(np.array([[rgb(hex_col)]], np.float32))[0, 0]
    return float((np.linalg.norm(lab(img) - ref, axis=2) < de).mean())
```

## Guard

Clamp warm saturated pixels into an allowed hue band, as the last step of a shot:

```python
def palette_guard(img, lo=0.32, hi=0.56, sat=0.12):
    """Keep warm saturated pixels in the orange band: no red, no gold. Hue as (g-b)/(r-b) where red is largest."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    m = (r >= g) & (r >= b) & (r - np.minimum(g, b) > sat)
    lo_ch = np.minimum(g, b)
    h = (g - lo_ch) / (r - lo_ch + 1e-6)
    out = img.copy()
    out[..., 1] = np.where(m, lo_ch + np.clip(h, lo, hi) * (r - lo_ch), g)
    out[..., 2] = np.where(m, lo_ch, b)
    bright = m & (out.mean(axis=2) > 0.62)          # bright warm pixels go peach, never pale gold
    out[..., 2] = np.where(bright, np.maximum(out[..., 2], out[..., 1] - 0.04), out[..., 2])
    return out
```

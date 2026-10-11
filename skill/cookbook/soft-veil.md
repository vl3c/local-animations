# Soft veil: darkness that closes in or steps back

**Tags:** painterly, atmospheric, any · **From:** Ember (2026-10-09)

Use a soft veil, not a shape. Never draw a band or a ring: in the Ember benchmark a drawn dark band read as "a crude
band with a wavy edge", and a drawn wave read as a lens flare, not as darkness receding.

```python
yy, xx = grid()
d = np.hypot(xx - fx, yy - fy)                    # distance from the light source (fx, fy)
r = lerp(0, 1400, ease_out(ramp(s.t, s.c("L3:stepped"), s.c("L3:stepped") + 1.8)))
veil = np.clip((d - r) / 450, 0, 1)               # 0 inside the reveal, 1 outside, a 450 px soft edge
img = img * (1 - 0.85 * veil[..., None])          # darken outside the reveal
img = screen(img, radial(fx, fy, 260 + r * 0.4, (1.0, 0.55, 0.2), k=0.5))   # warm light near the source
```

For darkness closing in, run `r` the other way. For a sky "becoming a wall", darken and thicken toward the horizon
with a soft vertical gradient of the same kind, not a shape.

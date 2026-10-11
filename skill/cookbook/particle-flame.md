# Particle flame

**Tags:** painterly, atmospheric · **From:** Ember (2026-10-09)

Hundreds of soft `splat` particles fill a teardrop: hot pale yellow near the base, deep orange at the tip, wobbling,
plus two radial glows. The director preferred this over layered vector flame tongues. Keep `k` and the size
believable so the core never blows out to white ("an overexposed blob" was a note).

```python
_r = np.random.default_rng(5); FL_N = 900                     # module level: fixed particles, deterministic
FL_U = _r.uniform(-1, 1, FL_N); FL_V = _r.uniform(0, 1, FL_N) ** 0.9   # FL_V: 0 = base ... 1 = tip
FL_PH = _r.uniform(0, 50, FL_N); FL_SZ = _r.uniform(0.7, 1.5, FL_N)

def flame(bx, by, S, t, k=1.0):
    """Light image of a flame S px tall standing on (bx, by). Add it with screen(img, flame(...))."""
    v = FL_V
    wob = np.sin(t * (2.7 + 0.11 * FL_PH) + FL_PH) * 0.6 + np.sin(t * 6.1 + FL_PH * 1.7) * 0.4
    xs = bx + FL_U * (S * 0.20 * (1 - v) ** 0.85 + 1.5) + S * 0.07 * v * wob
    ys = by - v * S * (0.95 + 0.07 * wob)
    col = np.array([1.0, 0.82, 0.45]) * (1 - v[:, None]) + np.array([1.0, 0.30, 0.06]) * v[:, None]
    cols = col * (k * (1 - v) ** 0.6 * (0.8 + 0.2 * wob))[:, None] * 1.7
    light = splat(xs, ys, cols, (1.0 + S * 0.018 * (1 - v)) * FL_SZ)
    light += radial(bx, by - S * 0.35, S * 1.1, (1.0, 0.42, 0.12), 0.35 * k)   # warm halo
    light += radial(bx, by - S * 0.22, S * 0.35, (1.0, 0.78, 0.45), 0.55 * k)  # hot core
    return light
```

- An ignition grows `S` from tiny over about a second (`ease_out(ramp(...))` from the cue).
- The flame stands on the plate's ground line: measure the line in the plate, check a zoomed crop.
- Don't use a plate that already has a fire or a glow where this one goes.

# Embers, motes and secondary motion

**Tags:** painterly, atmospheric · **From:** Ember (2026-10-09); Initial Condition's fresh-eyes polish pass

```python
img = screen(img, dust(s.t, n=40, seed=7, col=(1, .55, .2), k=0.9, region=(x0, y0, x1, y1), vy=-60, vx=4))
```

- **Rising embers:** keep `region` a column above the fire. Make them big enough to see on the contact sheet (`k`
  about 0.8-1.2); "barely visible embers" was a note.
- **Drifting dust in a light:** low `vy`, small `k`, a region inside the light.
- **Long holds need secondary motion.** A late fresh-eyes reviewer ranked the weakest long holds and asked for motes,
  embers, reflections, a slow light pulse (`vnoise`) or a slow push (`push`). One of these per hold, not all of them.

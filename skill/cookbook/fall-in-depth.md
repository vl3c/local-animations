# Falling in depth, behind a foreground object

**Tags:** any · **From:** Ember (2026-10-09); the rule from Initial Condition ("a falling knife should fall in
depth, behind the hand")

Fall toward a point on the horizon: accelerate, shrink and dim. Draw the falling thing before the occluder, so the
occluder covers it. Check stills mid-fall where it must be hidden.

```python
u = ease_in(ramp(s.t, t0, t1))                    # accelerating
x, y = lerp(x0, xland, u) + 15 * math.sin(u * 3), lerp(y0, yland, u)
size, k = lerp(7, 1.5, u), lerp(1.0, 0.45, u)
img = img + splat([x], [y], [(1.0, .6, .2)], [size]) * k   # the spark, drawn first
img = occluder.over(img)                           # the foreground Layer, drawn after: it hides the spark
```

What went wrong in the benchmarks:
- a long diagonal from the upper right read as a meteor, not a falling spark
- an occlusion lasting a few frames went unnoticed: make it last
- the foreground silhouette vanished at the next cut while the flame stayed: keep the occluder across the cut, or fade it

"""Ember: four shots. The night closes in, the spark falls to the horizon, the dark recedes, the hearth.

Plate space is the 1920x1080 frame before the camera push. Every beat comes from a cue spec (F(s, "L2:spark")),
never from a hard-coded time."""
import math

import numpy as np

from animkit import *  # noqa: F401,F403  (W, H, FPS, ramp, ease, lerp, Layer, load_plate, splat, radial, text, ...)

SC = (960.0, 540.0)            # camera push centre
LAND = (1080.0, 705.0)         # landing point and flame base: on the far ground, just below the measured horizon (plate row ~703)
HEARTH_FIRE = (980.0, 628.0)   # flame base in the hearth plate (centre of the ash pile)
WARM = np.array([1.0, 0.56, 0.22], np.float32)
LUMA = np.array([0.3, 0.59, 0.11], np.float32)

def T_of(s):
    """Film time (s) of this frame."""
    return s.gf / FPS


def F(s, spec):
    """Film time (s) of a cue spec, usable from any shot."""
    return s.c(spec) + (s.gf - s.f) / FPS


def cam(T):
    """One camera push for shots 1 to 3, a function of film time so the cuts do not jump."""
    return 1.0 + 0.005 * T


def P(x, y, sc):
    """Plate point -> frame point under the camera push."""
    return SC[0] + (x - SC[0]) * sc, SC[1] + (y - SC[1]) * sc


def night_plate(T):
    return push(load_plate("night"), cam(T))


def wall_k(T, tw):
    """0 before the wall cue, 1 once the wall has closed."""
    return ease(ramp(T, tw - 0.1, tw + 0.9))


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def heavy(img, k, reveal=None):
    """The night closing in: the top and the sides darken and lose colour, smoothly, with no edge.
    k in [0, 1] is the strength. reveal = (cx, cy, R, soft) lifts the darkness inside a soft disc (the wave)."""
    if k <= 0:
        return img
    yy, xx = grid()
    vy = np.clip((760.0 - yy) / 760.0, 0, 1) ** 1.3          # heavier toward the top
    vx = np.clip(np.abs(xx - SC[0]) / SC[0], 0, 1) ** 2      # heavier toward the sides
    kw = k * np.clip(0.25 + 0.6 * vy + 0.35 * vx, 0, 1)
    if reveal is not None:
        cx, cy, R, soft = reveal
        d = np.hypot(xx - cx, yy - cy)
        kw = kw * smooth((d - (R - soft)) / soft)
    kw = kw.astype(np.float32)[..., None]
    lum = (img @ LUMA)[..., None]
    out = lum + (img - lum) * (1 - 0.6 * kw)                 # desaturate
    return out * (1 - 0.8 * kw)                              # darken


def spark_at(u):
    """Plate position of the falling spark at fall progress u in [0, 1]: it falls mostly straight down
    (slight drift, late), accelerating (quadratic)."""
    return 1250.0 - 170.0 * u ** 3, 150.0 + (LAND[1] - 150.0) * u * u


def spark_light(T, ts, tg, sc):
    """Amber spark from the 'spark' cue to the 'grass' cue, with a short faint trail. None outside."""
    if T < ts or T > tg + 0.05:
        return None
    u = clamp((T - ts) / (tg - ts))
    app = ramp(T, ts, ts + 0.05) * (1 - ramp(T, tg - 0.02, tg + 0.05))
    xs, ys, cs, zs = [], [], [], []
    for j in range(9):
        x, y = P(*spark_at(clamp(u - 0.012 * j)), sc)
        b = app * (1.0 if j == 0 else 0.55 ** j) * lerp(1.0, 0.45, u)
        xs.append(x)
        ys.append(y)
        zs.append(max(lerp(7.0, 1.6, u) * (1 - 0.06 * j), 0.8))
        cs.append((1.0 * b, 0.62 * b, 0.22 * b))
    return splat(np.array(xs), np.array(ys), np.array(cs, np.float32) * 3.4, np.array(zs))


_FR = np.random.default_rng(3)
FL_N = 240
FL_U = _FR.uniform(-1, 1, FL_N)
FL_V = _FR.uniform(0, 1, FL_N) ** 0.9
FL_PH = _FR.uniform(0, 50, FL_N)
FL_SZ = _FR.uniform(0.7, 1.5, FL_N)


def flame(bx, by, S, t, k):
    """Warm flame of height S px standing on (bx, by), flickering at time t. Returns a light image.
    The core is clamped at 0.7 so a larger flame never blows out to white."""
    v = FL_V
    wob = np.sin(t * (2.7 + 0.11 * FL_PH) + FL_PH) * 0.6 + np.sin(t * 6.1 + FL_PH * 1.7) * 0.4
    w = S * 0.20 * (1 - v) ** 0.85 + 1.5
    xs = bx + FL_U * w + S * 0.07 * v * wob
    ys = by - v * S * (0.95 + 0.07 * wob)
    fall = (1 - v) ** 0.6
    base_col = np.array([1.0, 0.82, 0.45])
    tip_col = np.array([1.0, 0.30, 0.06])
    mix = v[:, None]
    cols = (base_col * (1 - mix) + tip_col * mix) * (k * fall * (0.8 + 0.2 * wob))[:, None] * 1.7
    sizes = (1.0 + S * 0.018 * (1 - v)) * FL_SZ
    light = splat(xs, ys, cols, sizes)
    light += radial(bx, by - S * 0.35, S * 1.1, (1.0, 0.42, 0.12), 0.35 * k)
    light += radial(bx, by - S * 0.22, S * 0.35, (1.0, 0.78, 0.45), 0.55 * k)
    return np.minimum(light, 0.7).astype(np.float32)


def embers(bx, by, t, k, n=40, rise=270.0, seed=21):
    """A few dozen small warm embers rising from (bx, by) in a narrow column. Each flickers, drifts up,
    and fades out at the top. Stays inside the column (top at about y 335 on the hearth plate)."""
    r = np.random.default_rng(seed)
    p0 = r.random(n)
    dx = (r.random(n) - 0.5) * 60
    sp = 0.6 + 0.4 * r.random(n)
    sz = 1.6 + 1.8 * r.random(n)
    ph = (p0 + t * 0.085 * sp) % 1.0
    xs = bx + dx + (10 + 14 * ph) * np.sin(t * 1.9 * sp + p0 * 6.3) * ph
    ys = by - 25 - ph * rise * (0.7 + 0.3 * sp)
    fade = np.sin(np.pi * ph) ** 1.4
    flick = 0.7 + 0.3 * np.sin(t * 11 * sp + p0 * 40)
    b = fade * flick * k
    cols = np.stack([b, 0.5 * b, 0.16 * b], axis=1) * 4.2
    return splat(xs, ys, cols, sz)


def shot_1(s):
    """Night. On 'wall' the sky and the edges darken and lose colour: the night closes in. Slow push-in."""
    T = T_of(s)
    img = night_plate(T)
    img = heavy(img, wall_k(T, F(s, "L1:wall")))
    return vignette(img, 0.5)


def shot_2(s):
    """The spark falls to the far ground; on 'grass' a small flame ignites at the landing point."""
    T = T_of(s)
    sc = cam(T)
    img = night_plate(T)
    img = heavy(img, wall_k(T, F(s, "L1:wall")))
    ts, tg = F(s, "L2:spark"), F(s, "L2:grass")
    fx, fy = P(LAND[0], LAND[1], sc)
    gro = ramp(T, tg, tg + 1.1)
    if T >= tg - 0.02:
        img = screen(img, flame(fx, fy, lerp(6.0, 92.0, ease(gro)), T, ramp(T, tg - 0.02, tg + 0.15)))
    sl = spark_light(T, ts, tg, sc)
    if sl is not None:
        img = screen(img, sl)
    img = glow(img, 10, 0.5, 0.3)
    return vignette(img, 0.5)


def shot_3(s):
    """The dark recedes. It starts under the same veil as shot 2. On 'stepped' a soft hole opens in the veil
    around the flame and expands outward (eased), revealing the plate warmly lit near the fire."""
    T = T_of(s)
    sc = cam(T)
    tb = F(s, "L3:stepped")
    w = ramp(T, tb, tb + 1.8)
    R = 1300.0 * ease_out(w)
    soft = 420.0
    fx, fy = P(LAND[0], LAND[1], sc)
    yy, xx = grid()
    d = np.hypot(xx - fx, yy - fy)
    img = night_plate(T)
    img = heavy(img, wall_k(T, F(s, "L1:wall")), reveal=(fx, fy, R, soft))
    inside = 1 - smooth((d - (R - soft)) / soft)
    aw = ramp(T, tb, tb + 0.4)
    warm = inside * aw * (0.30 * np.exp(-(d / 230.0) ** 2) + 0.08 * np.exp(-(d / 650.0) ** 2))
    front = ramp(T, tb, tb + 0.2) * (1 - ramp(T, tb + 1.6, tb + 1.8))
    rim = np.exp(-((d - R) / 200.0) ** 2) * 0.03 * front            # very faint warm edge of the reveal
    img = screen(img, (warm + rim)[..., None] * WARM)
    S = lerp(92.0, 122.0, ease(ramp(T, F(s, "L3:start"), F(s, "L3:end"))))
    img = screen(img, flame(fx, fy, S, T, 0.9 + 0.2 * ease(w)))
    img = glow(img, 10, 0.45, 0.3)
    return vignette(img, 0.5)


def shot_4(s):
    """The hearth: a steady flame with a few dozen rising embers, and the title EMBER moving into place."""
    T = T_of(s)
    fx, fy = HEARTH_FIRE
    img = load_plate("hearth")
    img = screen(img, radial(fx, fy - 40, 420, (1.0, 0.45, 0.14), 0.16))
    img = screen(img, flame(fx, fy, 200.0, T, 1.0))
    img = screen(img, embers(fx, fy, T, 1.0))
    img = glow(img, 10, 0.5, 0.3)
    a0, a1 = F(s, "L4:start"), F(s, "L4:end")
    u = ease_out(ramp(T, a0, a1))
    alpha = ease(ramp(T, a0 - 0.2, a0 + 0.5))
    L = Layer()
    bbox = text(L.ctx, "EMBER", lerp(560.0, 960.0, u), lerp(250.0, 215.0, u), size=150,
                col=(1.0, 0.88, 0.66), a=alpha, font="Georgia", tracking=lerp(70.0, 26.0, u))
    img = L.over(img)
    s.box("title", bbox)
    s.box("flame", (fx - 110, fy - 240, fx + 110, fy))
    s.box("hearth", (330, fy, 1640, 935))
    return vignette(img, 0.5)

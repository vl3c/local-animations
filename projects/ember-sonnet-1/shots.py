"""Ember: four shots. Every beat comes from a cue (s.c(...)); nothing is timed with a hard-coded number."""
import math

import cairo
import cv2
import numpy as np
from animkit import *  # noqa: F401,F403

CAM_C = (960.0, 700.0)          # camera pushes about the horizon point, so the horizon stays put
FIRE_P = (760.0, 704.5)         # landing point and flame base, plate coordinates: x 760, y = measured horizon line
                                # (sky/land edge of the night plate at x~700-820 is y=703.5-704.5; checked after the push)
HORIZON = 700.0
SPARK_X0, SPARK_Y0, SPARK_PW = 1300.0, 120.0, 1.5


# ------------------------------------------------------------------ common helpers

def to_screen(p, sc):
    return CAM_C[0] + (p[0] - CAM_C[0]) * sc, CAM_C[1] + (p[1] - CAM_C[1]) * sc


def cam1(s):
    return lerp(1.00, 1.07, s.t / s.T)


def cam2(s):
    return lerp(1.07, 1.12, s.t / s.T)


def cam3(s):
    return lerp(1.12, 1.17, s.t / s.T)


def night_plate(sc):
    return push(load_plate("night", expo=2.4), sc, CAM_C[0], CAM_C[1])


_Y = np.arange(H, dtype=np.float32)[:, None]


def wall_veil(u):
    """(H, 1) multiplier: darkness that rises from the horizon over the sky, densest at the horizon."""
    front = lerp(780.0, -380.0, ease(u))
    w = np.clip((_Y - front) / 380.0, 0, 1)
    sky = 0.50 + 0.46 * np.clip(_Y / HORIZON, 0, 1) ** 1.4
    dens = np.where(_Y < HORIZON, sky, 0.30)
    return (1 - w * dens).astype(np.float32)


def dark_night(sc, u=1.0):
    return night_plate(sc) * wall_veil(u)[..., None]


# ------------------------------------------------------------------ flame (soft particles, guide recipe)

_r = np.random.default_rng(5)
FL_N = 900
FL_U = _r.uniform(-1, 1, FL_N)
FL_V = _r.uniform(0, 1, FL_N) ** 0.9
FL_PH = _r.uniform(0, 50, FL_N)
FL_SZ = _r.uniform(0.7, 1.5, FL_N)


def flame(bx, by, S, t, k=1.0, halo=1.0):
    """Light image of a flame S px tall standing on (bx, by). Add it with screen(img, flame(...))."""
    n = int(clamp(150 + S * 4.0, 150, FL_N))
    sel = slice(0, n)
    v, u_, ph, sz = FL_V[sel], FL_U[sel], FL_PH[sel], FL_SZ[sel]
    fl = 1.0 + 0.10 * vnoise(t, 11, 7.0) + 0.05 * vnoise(t, 12, 17.0)
    wob = np.sin(t * (2.7 + 0.11 * ph) + ph) * 0.6 + np.sin(t * 6.1 + ph * 1.7) * 0.4
    lean = 0.10 * S * vnoise(t, 3, 1.3) * v ** 1.5
    xs = bx + u_ * (S * 0.20 * (1 - v) ** 0.85 + 1.2) + S * 0.07 * v * wob + lean
    ys = by - v * S * (0.95 + 0.07 * wob) * (0.94 + 0.06 * fl)
    col = np.array([1.0, 0.80, 0.42]) * (1 - v[:, None]) + np.array([1.0, 0.28, 0.05]) * v[:, None]
    dens = 1.0 / (1.0 + (S / 90.0) ** 1.0)             # many particles fill a small area: tone the sum down
    cols = col * (k * dens * (1 - v) ** 0.42 * (0.8 + 0.2 * wob))[:, None] * 1.9
    light = splat(xs, ys, cols, (0.9 + S * 0.016 * (1 - v)) * sz)
    light += radial(bx, by - S * 0.35, S * 1.1 + 6, (1.0, 0.42, 0.12), 0.30 * k * fl * halo)
    light += radial(bx, by - S * 0.22, S * 0.33 + 3, (1.0, 0.76, 0.42), 0.50 * k * fl * halo)
    return light


# ------------------------------------------------------------------ the spark

def spark_pos(s, sc):
    ts, tg = s.c("L2:spark"), s.c("L2:grass")
    u = ramp(s.t, ts, tg)
    tx, ty = to_screen(FIRE_P, sc)
    x0, y0 = SPARK_X0, SPARK_Y0
    v = u ** 1.8
    w = u ** SPARK_PW
    x = lerp(x0, tx, w) + 22 * math.sin(u * 3.4) * (1 - u)
    y = lerp(y0, ty, v)
    size = lerp(7.0, 1.7, v)
    k = lerp(1.0, 0.45, v)
    return x, y, size, k, u


def spark_light(s, sc):
    x, y, size, k, u = spark_pos(s, sc)
    on = ramp(s.t, s.c("L2:spark"), s.c("L2:spark") + 0.08) * (1 - ramp(s.t, s.c("L2:grass") - 0.06, s.c("L2:grass")))
    if on <= 0:
        return None
    fl = 0.85 + 0.15 * vnoise(s.t, 5, 14.0)
    kk = k * on * fl
    light = splat([x], [y], [(1.0, 0.88, 0.6)], [size * 0.7]) * 2.8 * kk
    light += splat([x], [y], [(1.0, 0.5, 0.14)], [size * 2.0]) * 1.3 * kk
    return light


# ------------------------------------------------------------------ SHOT 1: night

def shot_1(s):
    sc = cam1(s)
    t_wall = s.c("L1:wall")
    u = ramp(s.t, t_wall - 0.15, t_wall + 1.5)
    img = dark_night(sc, u)
    return vignette(np.clip(img, 0, 1), 0.55)


# ------------------------------------------------------------------ SHOT 2: the spark

def fire_S2(s):
    tg = s.c("L2:grass")
    grow = ease_out(ramp(s.t, tg, tg + 1.0))
    S = lerp(3.0, 38.0, grow)
    S += 7.0 * ramp(s.t, tg + 1.0, s.T)
    return S


def shot_2(s):
    sc = cam2(s)
    ts, tg = s.c("L2:spark"), s.c("L2:grass")
    img = dark_night(sc, 1.0)
    fx, fy = to_screen(FIRE_P, sc)
    # the light: spark in flight, ignition flash, flame, soft warm glow on the grass
    light = np.zeros_like(img)
    sp = spark_light(s, sc)
    if sp is not None:
        light = light + sp
    lit = ramp(s.t, tg, tg + 0.4)
    if lit > 0:
        S = fire_S2(s)
        flash = math.exp(-max(0.0, s.t - tg) / 0.2) * 1.0 * lit
        light = light + flame(fx, fy, S, s.t, 0.9 * lit)
        light = light + radial(fx, fy - 4, 50 + S * 1.6, (1.0, 0.7, 0.35), flash)
        # warm light on the grass around the fire, growing with the flame
        glow_r = 60 + S * 6.5
        img = img * (1 + 2.2 * radial(fx, fy, glow_r, (1.0, 0.8, 0.55), 0.9 * lit)[..., :1]
                     * np.array([1.0, 0.7, 0.4], np.float32))
        light = light + radial(fx, fy - 6, glow_r * 0.7, (1.0, 0.5, 0.18), 0.10 * lit)
    img = screen(img, light)
    return vignette(np.clip(img, 0, 1), 0.55)


# ------------------------------------------------------------------ SHOT 3: the dark steps back

def shot_3(s):
    sc = cam3(s)
    ts = s.c("L3:stepped")
    fx, fy = to_screen(FIRE_P, sc)
    S = lerp(45.0, 62.0, ease(ramp(s.t, 0.0, ts))) + 14.0 * ease(ramp(s.t, ts, ts + 2.0))
    base = dark_night(sc, 1.0)
    yy, xx = grid()
    d = np.hypot(xx - fx, yy - fy)
    r = lerp(0.0, 2000.0, ease_out(ramp(s.t, ts, ts + 2.1) ** 0.9))
    m = np.clip((r - d) / 480.0, 0, 1)
    m = m * m * (3 - 2 * m)
    # the plate as the fire sees it: warm, bright near the fire, falling off with distance
    lit_plate = push(load_plate("night", expo=6.0), sc, CAM_C[0], CAM_C[1])
    fall = 0.35 + 0.65 * np.exp(-(d / 1100.0) ** 1.6)
    tint = np.array([1.0, 0.70, 0.44], np.float32)
    skyk = np.where(_Y < HORIZON, 0.5 + 0.5 * np.clip(_Y / HORIZON, 0, 1) ** 2, 1.0).astype(np.float32)
    lit = lit_plate * fall[..., None] * tint * 1.15 * skyk[..., None]
    # lift the sky a touch: the dark wall thins as the light arrives
    img = base * (1 - m[..., None]) + np.maximum(lit, base) * m[..., None]
    fl = 1.0 + 0.08 * vnoise(s.t, 7, 6.0)
    img = screen(img, radial(fx, fy - 18, 90 + 600 * ease(ramp(s.t, ts, ts + 2.0)), (1.0, 0.55, 0.22),
                             (0.10 + 0.22 * ease(ramp(s.t, ts, ts + 2.0))) * fl))
    img = screen(img, flame(fx, fy, S, s.t, 0.95))
    return vignette(np.clip(img, 0, 1), 0.5)


# ------------------------------------------------------------------ SHOT 4: the hearth

H_BASE = (985.0, 655.0)
H_FLAME_S = 175.0
# hearth stones as boxes around the ring (screen coordinates at scale 1)
H_BOXES = {
    "hearth_back": (500, 378, 1470, 470),
    "hearth_left": (350, 470, 600, 800),
    "hearth_right": (1340, 470, 1645, 800),
    "hearth_front": (540, 790, 1500, 935),
}
H_CAM_C = (960.0, 650.0)


def h_cam(s):
    return lerp(1.0, 1.04, s.t / s.T)


def h_map(p, sc):
    return H_CAM_C[0] + (p[0] - H_CAM_C[0]) * sc, H_CAM_C[1] + (p[1] - H_CAM_C[1]) * sc


def title_state(s):
    """Return (size, x, y, tracking, alpha) of the title for this shot time."""
    t0, t1 = s.c("L4:start") - 0.25, s.c("L4:since") + 0.15
    u = ease(ramp(s.t, t0, t1))
    a = ease(ramp(s.t, t0, t0 + 0.7))
    return 104, 960.0, lerp(255.0, 168.0, u), lerp(52.0, 16.0, u), a


def embers(t, fx, fy, k=1.0):
    n = 46
    rng = np.random.default_rng(9)
    ph = rng.random(n)
    life = rng.uniform(2.6, 4.2, n)
    x0 = rng.normal(0, 14, n)
    age = ((t / life + ph) % 1.0)
    rise = age * rng.uniform(190, 320, n)
    xs = fx + x0 + 26 * np.sin(age * rng.uniform(3, 7, n) + ph * 6) * age + 8 * age * rng.uniform(-1, 1, n) * 40 * 0.1
    ys = fy - H_FLAME_S * 0.55 - rise
    fade = np.clip(age / 0.1, 0, 1) * (1 - age) ** 1.4
    tw = 0.6 + 0.4 * np.sin(t * rng.uniform(4, 11, n) + ph * 9)
    cols = np.array([1.0, 0.55, 0.2], np.float32)[None, :] * (fade * tw * k * 4.5)[:, None]
    return splat(xs, ys, cols, 1.6 + 2.0 * rng.random(n))


def shot_4(s):
    sc = h_cam(s)
    plate = push(load_plate("hearth", expo=0.8), sc, *H_CAM_C)
    fx, fy = h_map(H_BASE, sc)
    fl = 1.0 + 0.10 * vnoise(s.t, 31, 6.0) + 0.05 * vnoise(s.t, 32, 15.0)
    yy, xx = grid()
    d = np.hypot(xx - fx, (yy - (fy - 60)) * 1.35)
    wl = np.exp(-(d / 560.0) ** 1.7) * fl                       # warm light thrown on stones and floor
    tint = np.array([1.0, 0.62, 0.34], np.float32)
    img = plate * (0.62 + 2.1 * wl[..., None] * tint)
    S = H_FLAME_S * sc
    img = screen(img, flame(fx, fy, S, s.t, 0.95, 0.9))
    img = screen(img, embers(s.t, fx, fy, 1.0))
    # the title travels in the dark band above the ring
    size, x, y, tr, a = title_state(s)
    L = Layer()
    bb = text(L.ctx, "EMBER", x, y, size=size, col=(1.0, 0.86, 0.62), a=a, tracking=tr)
    img = L.over(img)
    img = screen(img, radial(x, y, 340, (1.0, 0.55, 0.2), 0.05 * a))   # faint warm bloom behind the letters
    s.box("title", bb)
    fb = (fx - S * 0.22, fy - S, fx + S * 0.22, fy)
    s.box("flame", fb)
    for name, (x0, y0, x1, y1) in H_BOXES.items():
        p0, p1 = h_map((x0, y0), sc), h_map((x1, y1), sc)
        s.box(name, (p0[0], p0[1], p1[0], p1[1]))
    return vignette(np.clip(img, 0, 1), 0.45)

"""HAIRLINE: three shots. All motion is procedural on top of three generated plates."""
import math

import cv2
import numpy as np
import cairo
from animkit import *

RED = np.array([1.0, 0.10, 0.14], np.float32)
EMBER = (1.0, 0.16, 0.10)
OX, OY = 960.0, 430.0            # origin of the crack on the wall face (plate space)


# ------------------------------------------------------------------ shared procedural looks

def static_light(t, seed, dens=0.018, streak=0.0016, rate=12):
    """Crimson digital static: blocky sparks and short horizontal streaks, re-rolled `rate` times a second.
    Density follows a fixed coarse map of 'bad sectors' so the corruption clusters instead of sprinkling evenly."""
    f = int(t * rate)
    rng = np.random.default_rng(seed * 9973 + f)
    coarse = np.random.default_rng(seed + 500).random((6, 10)).astype(np.float32)
    m = np.clip(coarse * 1.7 - 0.25, 0, 1) ** 1.6
    m1 = cv2.resize(m, (W // 6, H // 3), interpolation=cv2.INTER_CUBIC)
    a = (rng.random((H // 3, W // 6)) > 1 - dens * (0.12 + 3.2 * m1)) * rng.random((H // 3, W // 6))
    a = cv2.resize(a.astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST)
    m2 = cv2.resize(m, (W // 20, H // 2), interpolation=cv2.INTER_CUBIC)
    b = (rng.random((H // 2, W // 20)) > 1 - streak * (0.1 + 3.4 * m2)).astype(np.float32)
    b = cv2.dilate(b, np.ones((1, int(2 + 6 * hash01(seed, f // 3)),), np.uint8))
    b = cv2.resize(b, (W, H), interpolation=cv2.INTER_NEAREST) * 0.38
    return (np.maximum(a, b))[..., None] * RED


def scanlines(img, k=0.16, t=0.0):
    y = np.arange(H, dtype=np.float32)
    lines = 1 - k * (0.5 + 0.5 * np.sin(y * (math.pi / 2)))        # 4 px period
    roll = 1 + 0.10 * np.exp(-(((y - (t * 70) % (H + 400) + 200) / 90.0) ** 2))   # slow bright band rolling down
    return img * (lines * roll)[:, None, None]


def slices(img, t, seed, rate=8, thresh=0.9, amount=40, n=7):
    """Horizontal glitch slices: bands of rows displaced sideways. Deterministic per time step."""
    f = int(t * rate)
    if hash01(seed, f) < thresh:
        return img
    rng = np.random.default_rng(seed * 31 + f)
    out = img.copy()
    for _ in range(n):
        y0 = int(rng.integers(0, H - 70))
        h = int(rng.integers(4, 60))
        dx = int(rng.normal(0, amount))
        out[y0:y0 + h] = np.roll(out[y0:y0 + h], dx, axis=1)
    return out


def split(img, d):
    """Chromatic split: red one way, blue the other."""
    if abs(d) < 0.5:
        return img
    d = int(round(d))
    out = img.copy()
    out[..., 0] = np.roll(img[..., 0], d, axis=1)
    out[..., 2] = np.roll(img[..., 2], -d, axis=1)
    return out


def bloom(light, a=1.0):
    """Soft halo of a light image (cheap two-scale bloom)."""
    return light + (gblur(light, 12) * 0.9 + gblur(light, 40) * 0.8) * a


# ------------------------------------------------------------------ eyes: organic, asymmetric, half-dissolved in static

_LID = {}


def lid_shape(seed):
    """Irregular lid outline for one eye: asymmetric top and bottom curves with a skewed peak and jagged edges."""
    if seed in _LID:
        return _LID[seed]
    r = np.random.default_rng(seed)
    n = 44
    u = np.cos(np.linspace(0, math.pi, n))                       # +1 (right corner) ... -1 (left corner)
    skew = r.uniform(-0.65, 0.65)
    ph = r.uniform(0, 6.28, 4)
    bt = np.clip(1 - u ** 2, 0, 1) ** r.uniform(0.55, 1.0)
    bb = np.clip(1 - u ** 2, 0, 1) ** r.uniform(0.9, 1.5) * r.uniform(0.40, 0.85)
    top = bt * (1 + skew * u) * (1 + 0.20 * np.sin(u * 3 + ph[0]) + 0.09 * np.sin(u * 11 + ph[1]))
    bot = bb * (1 - 0.5 * skew * u) * (1 + 0.22 * np.sin(u * 4 + ph[2]) + 0.10 * np.sin(u * 13 + ph[3]))
    top = np.clip(top * (1 + r.normal(0, 0.05, n)), 0, None)
    bot = np.clip(bot * (1 + r.normal(0, 0.07, n)), 0, None)
    _LID[seed] = (u, top, bot)
    return _LID[seed]


def lid_points(seed, w, h, t):
    u, top, bot = lid_shape(seed)
    n = len(u)
    f = int(t * 12)
    jt = np.array([hash01(seed, i, f) for i in range(n)]) - 0.5                # fractal fizz on the edge
    jb = np.array([hash01(seed + 1, i, f) for i in range(n)]) - 0.5
    amp = 0.07 * h
    pts_t = [(u[i] * w / 2, -(top[i] * h) - jt[i] * amp * (0.3 if top[i] < 1e-3 else 1)) for i in range(n)]
    pts_b = [(u[i] * w / 2, bot[i] * h + jb[i] * amp * (0.3 if bot[i] < 1e-3 else 1)) for i in range(n - 1, -1, -1)]
    return pts_t + pts_b[1:-1]


def _pupil(ctx, kind, ix, iy, rx, ry, pn, seed, a):
    """Pupil shapes: vertical or diagonal jagged slits, trios, uneven pairs, a ring, a horizontal slit, a slit with satellites."""
    ctx.save()
    ctx.translate(ix, iy)
    r = np.random.default_rng(seed + 7)

    def slit(cx, cy, hh, ww, rot):
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(rot)
        pts = []
        for i in range(13):
            y = -hh + 2 * hh * i / 12
            pts.append((ww * max(0.0, 1 - (y / hh) ** 2) ** 0.8 * (0.85 + 0.3 * r.random()) + 0.3, y))
        for i in range(12, -1, -1):
            y = -hh + 2 * hh * i / 12
            pts.append((-ww * max(0.0, 1 - (y / hh) ** 2) ** 0.8 * (0.85 + 0.3 * r.random()) - 0.3, y))
        poly_path(ctx, pts)
        ctx.restore()

    def disc(cx, cy, rr):
        ctx.save()
        ctx.translate(cx, cy)
        ctx.arc(0, 0, max(rr, 0.6), 0, 2 * math.pi)
        ctx.restore()

    pw = ry * 0.17 * pn
    if kind == "softsat":  # (polish pass) the rift eye: a smooth, deep slit with soft satellites and a catchlight
        hh, ww = ry * 0.92, max(1.5, pw * 1.15)
        ctx.move_to(0, -hh)
        ctx.curve_to(ww * 1.15, -hh * 0.45, ww * 1.15, hh * 0.45, 0, hh)
        ctx.curve_to(-ww * 1.15, hh * 0.45, -ww * 1.15, -hh * 0.45, 0, -hh)
        ctx.close_path()
        g = cairo.RadialGradient(0, 0, 0, 0, 0, hh)
        g.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, a)
        g.add_color_stop_rgba(0.7, 0.03, 0.0, 0.01, a)
        g.add_color_stop_rgba(1.0, 0.16, 0.01, 0.03, a)
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 0.50, 0.30, a * 0.45)
        ctx.set_line_width(2.2)
        ctx.stroke()
        for (dx, dy, rr) in ((-rx * 0.45, ry * 0.25, ry * 0.13), (rx * 0.40, -ry * 0.35, ry * 0.09)):
            g2 = cairo.RadialGradient(dx, dy, 0, dx, dy, rr)
            g2.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, a * 0.95)
            g2.add_color_stop_rgba(1.0, 0.10, 0.0, 0.02, 0.0)
            ctx.arc(dx, dy, rr, 0, 2 * math.pi)
            ctx.set_source(g2)
            ctx.fill()
        ctx.save()  # a wet catchlight: the thing is alive
        ctx.translate(-ww * 0.9, -hh * 0.38)
        safe_scale(ctx, 1.0, 1.6)
        ctx.arc(0, 0, max(2.0, ry * 0.045), 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(1.0, 0.85, 0.75, a * 0.55)
        ctx.fill()
        ctx.restore()
        return
    if kind == "slit":
        slit(0, 0, ry * 0.95, pw, 0.0)
    elif kind == "diag":
        slit(0, 0, ry * 1.0, pw, 0.75)
    elif kind == "hslit":
        slit(0, 0, rx * 0.8, pw * 0.7, math.pi / 2)
    elif kind == "tri":
        for dx, dy, rr in ((-rx * 0.28, ry * 0.15, ry * 0.26), (rx * 0.22, -ry * 0.3, ry * 0.18), (rx * 0.30, ry * 0.35, ry * 0.12)):
            disc(dx, dy, rr * (0.5 + 0.5 * pn))
    elif kind == "duo":
        slit(-rx * 0.30, 0, ry * 0.9, pw * 0.9, 0.1)
        slit(rx * 0.25, ry * 0.1, ry * 0.5, pw * 0.7, -0.15)
    elif kind == "ring":
        disc(0, 0, ry * 0.5 * (0.6 + 0.4 * pn))
    elif kind == "sat":
        slit(0, 0, ry * 0.95, pw, 0.05)
        disc(-rx * 0.45, ry * 0.25, ry * 0.15)
        disc(rx * 0.40, -ry * 0.35, ry * 0.10)
    ctx.set_source_rgba(0.02, 0, 0.01, a)
    ctx.fill_preserve()
    ctx.set_source_rgba(1.0, 0.55, 0.30, a * 0.8)
    ctx.set_line_width(1.3)
    ctx.stroke()
    ctx.restore()


def draw_eye(ctx, sp, open_, a, t, pn=1.0):
    """One alien eye. sp = (cx, cy, width, angle, seed, pupil kind). open_ in 0..1, a = alpha, pn = pupil size factor.
    Irregular lid, iris built from rings of drifting data cells, radial fibres, veins creeping in from the lid edge."""
    cx, cy, w, ang, seed, kind = sp[:6]
    if open_ < 0.03 or a < 0.01:
        return
    h = w * 0.27 * open_
    pts = lid_points(seed, w, h, t)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(ang)
    ctx.save()
    poly_path(ctx, pts)
    ctx.clip()
    g = cairo.RadialGradient(0, 0, 1, 0, 0, w * 0.55)
    g.add_color_stop_rgba(0.0, 0.40, 0.03, 0.05, a)
    g.add_color_stop_rgba(1.0, 0.06, 0.0, 0.015, a)
    ctx.set_source(g)
    ctx.paint()
    drift = vnoise(t, seed, 0.5)
    ix, iy = w * 0.07 * drift + w * 0.05 * hash01(seed, 3), h * 0.12 * vnoise(t, seed + 1, 0.7)
    rx, ry = w * 0.27, h * 0.95
    big = w >= 140
    huge = w >= 400
    nr = 11 if huge else (7 if big else (4 if w >= 70 else 3))
    for k in range(nr):
        rk = ry * (0.30 + 0.70 * (k + 0.5) / nr)
        cw = max(2.2, w * (0.008 if huge else (0.018 if big else 0.03)))
        nc = max(7, int(2 * math.pi * rk * (rx / ry) / (cw * 1.3)))
        rot = t * 0.18 * (1 if k % 2 else -1) * (1 + 0.3 * k) + hash01(seed, k) * 6.28
        dr = ry * 0.65 / nr
        for m in range(nc):
            hv = hash01(seed, k, m, int(t * 5 + hash01(seed, k, m) * 3))
            if hv < 0.38:
                continue
            b = (hv ** 1.6) * (1.0 - 0.45 * k / nr)
            ctx.save()
            ctx.translate(ix, iy)
            safe_scale(ctx, rx / ry, 1.0)
            ctx.rotate(rot + 2 * math.pi * m / nc)
            ctx.rectangle(rk - dr / 2, -cw / 2 * (0.6 + 0.8 * hash01(seed, m)), dr * (0.5 + hash01(seed, k + 9, m)), cw)
            ctx.restore()
            ctx.set_source_rgba(0.95, 0.10 + 0.50 * b ** 3, 0.05 + 0.15 * b ** 3, a * (0.14 + 0.78 * b))
            ctx.fill()
    ctx.save()                                                          # limbal ring around the iris
    ctx.translate(ix, iy)
    safe_scale(ctx, rx / ry, 1.0)
    ctx.arc(0, 0, ry * 1.02, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(1.0, 0.45, 0.2, a * (0.55 if huge else 0.3))
    ctx.set_line_width(2.0 if huge else 1.0)
    ctx.stroke()
    for i in range(30 if huge else (16 if big else 8)):                 # radial fibres
        an = 2 * math.pi * hash01(seed, 40 + i)
        ctx.move_to(ix + math.cos(an) * rx * 0.2, iy + math.sin(an) * ry * 0.2)
        ctx.line_to(ix + math.cos(an) * rx * 1.05, iy + math.sin(an) * ry * 1.05)
        ctx.set_source_rgba(1.0, 0.45, 0.25, a * 0.28)
        ctx.set_line_width(0.9)
        ctx.stroke()
    _pupil(ctx, kind, ix, iy, rx, ry, pn, seed, a)
    if w >= 60:                                                         # veins creeping in from the lid edge
        rr = np.random.default_rng(seed + 33)
        for i in range(10 if huge else (5 if big else 3)):
            p = pts[int(rr.integers(2, len(pts) - 2))]
            x, y = p
            an = math.atan2(-y, -x) + rr.normal(0, 0.4)
            ctx.move_to(x, y)
            for _ in range(int(7 + 6 * big + 6 * huge)):
                an += rr.normal(0, 0.45)
                x += math.cos(an) * w * 0.035
                y += math.sin(an) * w * 0.035
                ctx.line_to(x, y)
                if rr.random() < 0.25:                                  # a fork
                    ctx.move_to(x, y)
                    an += rr.normal(0, 0.9)
            ctx.set_source_rgba(0.95, 0.12, 0.12, a * 0.5)
            ctx.set_line_width(0.8 if not big else 1.2)
            ctx.stroke()
    ctx.restore()
    poly_path(ctx, pts)                                                 # the lid's own thin glitchy outline
    ctx.set_source_rgba(1.0, 0.25, 0.2, a * (0.85 if huge else 0.45))
    ctx.set_line_width(max(1.0, w * 0.007))
    ctx.stroke()
    rr = np.random.default_rng(seed + 55 + int(t * 8))
    for _ in range(12 if huge else (3 if w > 60 else 1)):                                 # fragments of eye peeling off into the noise
        p = pts[int(rr.integers(0, len(pts)))]
        ctx.rectangle(p[0] + rr.normal(0, w * 0.05), p[1] + rr.normal(0, h * 0.2), rr.uniform(3, w * 0.12), rr.uniform(1.5, 4))
        ctx.set_source_rgba(1.0, 0.3, 0.2, a * 0.5)
        ctx.fill()
    ctx.restore()


def dissolve_mask(t, seed, strength=0.35):
    """(H, W) mask 1 = visible: blocky dropout and torn rows, so what is drawn looks half-eaten by the static."""
    f = int(t * 12)
    rng = np.random.default_rng(seed * 131 + f)
    coarse = cv2.resize(np.random.default_rng(seed + 9).random((5, 9)).astype(np.float32), (W // 12, H // 6),
                        interpolation=cv2.INTER_CUBIC)
    lo = rng.random((H // 6, W // 12)).astype(np.float32)
    m = (lo > strength * (0.4 + coarse)).astype(np.float32)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_NEAREST)
    rows = cv2.resize((rng.random((H // 4, 1)) > 0.94).astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST)
    return gblur(m * (1 - 0.75 * rows), 1.0)


def flick(t, seed, p=0.07):
    """Per-eye flicker: now and then an eye drops out for a moment (about a tenth of a second)."""
    return 0.12 if hash01(seed, int(t * 9)) < p else 1.0


def blink(t, seed, period=4.5):
    """1 = open, dips for ~0.25 s once per period at a per-eye phase."""
    ph = (t + hash01(seed) * period) % period
    return 1 - 0.85 * math.exp(-((ph - 1.0) / 0.10) ** 2)


# ------------------------------------------------------------------ shot 1: the wall

SEAMS_X = np.cumsum(np.random.default_rng(2).uniform(230, 360, 9)) - 160      # vertical panel seams of the wall
SEAMS_Y = [190, 400, 610, 820]
BLOBS = [(420, 430, 560), (1480, 300, 620), (1000, 700, 480)]     # dim shapes moving behind the wall


def shot_1(s):
    t = s.t
    lo = load_plate("wall_wide", expo=1.9)
    hi = load_plate("wall_wide", expo=3.4)
    ys = np.arange(H, dtype=np.float32)
    xs = np.arange(W, dtype=np.float32)
    wall = np.clip((1004 - ys) / 24, 0, 1)                         # only the wall, not the city below it
    img = lo + (hi - lo) * wall[:, None, None]                    # the city keeps its calm light; the wall is lifted
    img = push(img, 1.0 + 0.075 * ease(ramp(t, 0, s.T)), 960, 880)
    tw = s.c("L1:wall")
    u = ramp(t, tw - 0.05, tw + 2.0)
    live = 1.0 if 0 < u < 1 else 0.0
    by = lerp(1012, -60, ease(u))                                  # beam travels from the skyline to the top edge
    byx = by + 4 * np.sin(xs / 150.0 + t * 6) + 3 * np.sin(xs / 41.0 - t * 11)          # a slightly torn beam
    d = (ys[:, None] - byx[None, :])
    beam = (np.exp(-(d / 22.0) ** 2) + 0.28 * np.exp(-(d / 120.0) ** 2)) * wall[:, None] * live
    scanned = np.clip((ys - by) / 90, 0, 1) * (1 if u > 0 else 0) * wall    # rows the beam has already passed
    afterglow = scanned * (0.55 + 0.45 * np.clip((ys - 120) / 700, 0, 1))   # a little stronger toward the city
    img = screen(img, beam[..., None] * RED * 0.55)
    # the wall's panel seams and bad sectors light up behind the beam
    Lw = Layer()
    c = Lw.ctx
    c.set_line_width(2.0)
    for i, x in enumerate(SEAMS_X):
        fl = 0.5 + 0.5 * vnoise(t, 100 + i, 2.0)
        c.set_source_rgba(1.0, 0.10, 0.12, 0.55 * fl)
        c.move_to(x, 0)
        c.line_to(x + 14 * math.sin(i), 1004)
        c.stroke()
    for j, y in enumerate(SEAMS_Y):
        c.set_source_rgba(1.0, 0.10, 0.12, 0.30)
        c.move_to(0, y)
        c.line_to(W, y)
        c.stroke()
    sl, _ = Lw.rgba()
    seamk = np.maximum(afterglow, 0.35 * wall)
    img = screen(img, sl * seamk[:, None, None] * 1.0)
    img = screen(img, (afterglow * 0.04)[:, None, None] * np.array([1.0, 0.05, 0.1], np.float32))
    for i, (bx, byy, r) in enumerate(BLOBS):
        k = (0.07 + 0.09 * float(scanned.mean() > 0.2 and u > 0.3)) * (0.65 + 0.35 * vnoise(t, 200 + i, 0.4))
        img = screen(img, radial(bx + 110 * math.sin(t * 0.13 + i * 2.1), byy + 50 * math.sin(t * 0.09 + i), r,
                                 (0.9, 0.05, 0.10), k))
    # tear blocks: wide short rectangles that flicker like corrupted memory
    f = int(t * 12)
    rng = np.random.default_rng(900 + f)
    for _ in range(7):
        x0, y0 = int(rng.uniform(0, W - 500)), int(rng.uniform(40, 990))
        w, h = int(rng.uniform(90, 520)), int(rng.uniform(3, 24))
        k = 0.05 + 0.13 * rng.random()
        kk = afterglow[min(y0, H - 1)]
        img[y0:y0 + h, x0:x0 + w] = screen(img[y0:y0 + h, x0:x0 + w], RED * k * kk)
    # static: faint before the scan, rich after it
    rowk = 0.08 + 0.92 * scanned
    st = static_light(t, 1, dens=0.012) * rowk[:, None, None]
    st2 = static_light(t, 2, dens=0.004, streak=0.0006, rate=24) * (rowk * 1.4)[:, None, None]
    img = screen(img, bloom((st * 0.65 + st2) * wall[:, None, None], 0.45))
    # glitch slices become more frequent after the scan; a collapse in the last half second
    img = slices(img, t, 11, rate=8, thresh=0.985 if u < 0.05 else 0.92, amount=34)
    if t > s.T - 0.7:
        k = ramp(t, s.T - 0.7, s.T - 0.1)
        img = slices(img, t, 12, rate=24, thresh=1 - 0.9 * k, amount=60 + 80 * k, n=9)
        img = split(img, 10 * k)
    img = img * (1 + 0.04 * vnoise(t, 3, 6.0))                     # the small human city flickers very slightly
    img = scanlines(img, 0.14 + 0.08 * scanned.mean(), t)
    return np.clip(vignette(img, 0.5), 0, 1)


# ------------------------------------------------------------------ shot 2: the dark

# (cx, cy, width, angle, seed, pupil, group, delay, opening seconds, alpha)   group 0 = "dark", 1 = "learned", 2 = "names"
EYES2 = [
    (330, 215, 96, -0.22, 101, "slit", 0, 0.00, 0.95, 0.85),
    (452, 266, 58, 0.40, 102, "duo", 0, 0.35, 0.60, 0.70),
    (402, 160, 34, -0.70, 103, "tri", 0, 0.62, 0.45, 0.60),
    (1498, 256, 88, 0.14, 104, "diag", 0, 0.12, 1.25, 0.85),
    (1620, 308, 46, -0.45, 105, "ring", 0, 0.52, 0.55, 0.60),
    (716, 352, 310, -0.08, 111, "slit", 1, 0.00, 1.50, 0.62),
    (1222, 330, 205, 0.13, 112, "tri", 1, 0.28, 1.05, 0.55),
    (250, 520, 70, 0.55, 121, "hslit", 2, 0.05, 0.50, 0.65),
    (1700, 560, 118, -0.30, 122, "sat", 2, 0.30, 0.80, 0.70),
    (1010, 150, 52, 0.20, 123, "diag", 2, 0.55, 0.40, 0.55),
    (600, 600, 40, -0.60, 124, "duo", 2, 0.20, 0.35, 0.55),
    (1380, 430, 62, 0.75, 125, "tri", 2, 0.75, 0.60, 0.60),
    (150, 330, 44, 0.10, 126, "slit", 2, 0.48, 0.45, 0.55),
]


def shot_2(s):
    t = s.t
    img = load_plate("beyond", expo=1.3)
    k = ease(ramp(t, 0, s.T))
    sc = 1.0 + 0.07 * k
    img = push(img, sc, 960, 600)
    img = img * (1 + 0.05 * math.sin(t * 1.3))                      # the haze breathes
    L = Layer()
    c = L.ctx
    t0 = {0: s.c("L2:dark") - 0.1, 1: s.c("L2:learned") - 0.1, 2: s.c("L2:names") - 0.1}
    for sp in EYES2:
        g, dl, du, al = sp[6], sp[7], sp[8], sp[9]
        u = ease(ramp(t, t0[g] + dl, t0[g] + dl + du))
        o = u * (1 + 0.06 * math.sin(t * 6 + sp[4])) * (0.3 + 0.7 * blink(t, sp[4], 3.5 + (sp[4] % 5)))
        draw_eye(c, sp, clamp(o), al * flick(t, sp[4]), t, pn=1.0 - 0.25 * math.sin(t * 0.9 + sp[4]))
    lr, _ = L.rgba()
    lr = push(lr, sc, 960, 600)                                    # the eyes belong to the plate: same camera
    lr = slices(lr, t, 41, rate=10, thresh=0.8, amount=22, n=5)
    lr = lr * dissolve_mask(t, 3, 0.30)[..., None]                 # eaten by static
    lr = gblur(lr * 0.8 + cv2.blur(lr, (41, 1)) * 0.6, 1.1)
    img = screen(img, np.clip(bloom(lr, 0.5), 0, 1))
    img = screen(img, dust(t, n=110, seed=5, col=EMBER, k=0.7, region=(0, 0, W, H), vy=-22, vx=9))
    img = screen(img, static_light(t, 4, dens=0.006, streak=0.0006) * 0.7)
    img = slices(img, t, 13, rate=8, thresh=0.985, amount=26, n=4)
    ev = ramp(t, t0[2] + 0.05, t0[2] + 0.18) * (1 - ramp(t, t0[2] + 0.18, t0[2] + 0.4))
    img = split(img, 8 * ev)
    img = scanlines(img, 0.12, t)
    return np.clip(vignette(img, 0.55), 0, 1)


# ------------------------------------------------------------------ shot 3: the crack

def _walk(y0, y1, seed, step=16, amp=11):
    rng = np.random.default_rng(seed)
    n = int(abs(y1 - y0) / step)
    sgn = 1 if y1 > y0 else -1
    xs, ys, v, x = [OX], [OY], 0.0, OX
    for i in range(n):
        v = v * 0.2 + rng.normal(0, amp)
        x = float(np.clip(x + v, OX - 90, OX + 90))
        xs.append(x)
        ys.append(OY + sgn * step * (i + 1) + rng.normal(0, 3))
    return np.array(list(zip(xs, ys)), np.float64)


def _branch(p, ang, n, seed, step=20):
    rng = np.random.default_rng(seed)
    pts, a = [p], ang
    for _ in range(n):
        a += rng.normal(0, 0.28)
        pts.append((pts[-1][0] + step * math.cos(a), pts[-1][1] + step * math.sin(a)))
    return np.array(pts, np.float64)


MAIN_DN = _walk(OY, 740, 3)
MAIN_UP = _walk(OY, -40, 8)
PATHS = [(MAIN_DN, 0.0, 1.0), (MAIN_UP, 0.0, 1.0)]       # (points, start distance offset, width factor)
_br = [(MAIN_DN, 8, 0.25, 8, 13, 0.55), (MAIN_DN, 20, math.pi - 0.3, 5, 14, 0.5),
       (MAIN_UP, 8, math.pi + 0.2, 12, 16, 0.5), (MAIN_UP, 22, -0.3, 8, 17, 0.45)]
for par, idx, ang, n, seed, wf in _br:
    pt = par[min(idx, len(par) - 1)]
    cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(par, axis=0).T))])
    PATHS.append((_branch(pt, ang, n, seed), float(cum[min(idx, len(par) - 1)]), wf))


def _cum(p):
    return np.concatenate([[0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])


def partial(p, d):
    """The first d px (arc length) of polyline p."""
    if d <= 0:
        return None
    cu = _cum(p)
    if d >= cu[-1]:
        return p
    i = int(np.searchsorted(cu, d)) - 1
    f = (d - cu[i]) / max(cu[i + 1] - cu[i], 1e-6)
    return np.vstack([p[:i + 1], p[i] + (p[i + 1] - p[i]) * f])


# centre line of the main crack as x(y), for the rift
_MAIN = np.vstack([MAIN_UP[::-1], MAIN_DN[1:]])
_MAIN = _MAIN[np.argsort(_MAIN[:, 1])]
RY0, RY1 = 90.0, 780.0                    # rift extent
RYC = (RY0 + RY1) / 2


def rift_alpha(width):
    """(H, W) alpha of the lens-shaped opening; `width` is the half width at the middle in px."""
    ys = np.arange(RY0, RY1 + 1, 6.0)
    cx = np.interp(ys, _MAIN[:, 1], _MAIN[:, 0])
    cx = OX + np.convolve(np.pad(cx - OX, 12, mode='edge'), np.ones(25) / 25, mode='valid')   # a graceful lens
    sn = (ys - RYC) / (RY1 - RY0) * 2
    prof = np.clip(1 - sn ** 2, 0, 1) ** 1.25
    jag = np.array([hash01(5, int(y)) for y in ys]) * 2 - 1
    hw = width * prof * (1 + 0.07 * jag)
    left = np.stack([cx - hw, ys], 1)
    right = np.stack([cx + hw, ys], 1)[::-1]
    L = Layer()
    poly_path(L.ctx, np.vstack([left, right]))
    L.ctx.set_source_rgba(1, 1, 1, 1)
    L.ctx.fill()
    return L.alpha(), float(cx.mean())


def draw_crack(ctx, d, width_boost, glow_k):
    for p, off, wf in PATHS:
        q = partial(p, d - off)
        if q is None or len(q) < 2:
            continue
        main = wf >= 1.0
        fade = 1 - 0.8 * width_boost * (1 if main else 0)     # the main seam dims as the rift opens around it
        for lw, col, al in ((5.0 * wf * glow_k, (0.9, 0.05, 0.10), 0.10),
                            (2.2 * wf * glow_k, (1.0, 0.16, 0.14), 0.26),
                            ((1.0) * max(wf, 0.6), (1.0, 0.45, 0.36), 0.85 * fade)):
            ctx.set_source_rgba(*col, al)
            ctx.set_line_width(lw)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            poly_path(ctx, q, close=False)
            ctx.stroke()


def shot_3(s):
    t = s.t
    t_wall, t_crack = s.c("L3:wall"), s.c("L3:cracking")
    t_alm, t_thr = s.c("L4:almost"), s.c("L4:through")
    base = load_plate("wallface", expo=3.0)
    beyond = load_plate("beyond", expo=0.9)

    # --- crack growth (plate space)
    d = ease_out(ramp(t, t_crack, t_crack + 0.95)) * 1000
    open_ = ease(ramp(t, t_alm, t_thr + 0.5))
    open2 = ease_in(ramp(t, t_alm, t_thr + 0.35))
    width = 3 + 140 * (0.25 * open_ + 0.75 * open2) * (1 if t > t_alm else 0.0)
    img = base.copy()
    # the wall face crackles with red static; harder after the crack
    pre = ramp(t, t_wall - 0.1, t_wall + 0.2)
    post = ramp(t, t_crack, t_crack + 0.4)
    img = screen(img, static_light(t, 7, dens=0.007 + 0.008 * post, streak=0.0012 + 0.0018 * post) * (0.55 + 0.45 * post))
    # a premonition on "wall": a hairline blinks at the origin
    pulse = math.exp(-((t - (t_wall + 0.15)) / 0.14) ** 2) + 0.8 * math.exp(-((t - (t_wall + 0.55)) / 0.10) ** 2) + 0.9 * math.exp(-((t - (t_crack - 0.25)) / 0.08) ** 2)
    L = Layer()
    c = L.ctx
    if pulse > 0.02 and t < t_crack:
        ctx_pts = np.array([[OX, OY - 52], [OX + 6, OY - 22], [OX - 4, OY + 8], [OX + 5, OY + 34], [OX, OY + 58]])
        c.set_source_rgba(1.0, 0.45, 0.4, min(1.0, 0.9 * pulse))
        c.set_line_width(1.8)
        poly_path(c, ctx_pts, close=False)
        c.stroke()
    flicker = 1.0 + 0.2 * vnoise(t, 9, 14.0)
    if t >= t_crack:
        draw_crack(c, d, open_, flicker)
    lr, _ = L.rgba()
    # rift: far side seen through the opening
    if t > t_alm:
        a, cxm = rift_alpha(width)
        a = cv2.GaussianBlur(a, (0, 0), 1.2)
        a3 = a[..., None]
        par = ease(ramp(t, t_alm, s.T))
        far = push(beyond, 1.25 + 0.12 * par, 960, 560)
        far = far * (1 + 0.1 * vnoise(t, 4, 5.0))
        far = far * (0.45 + 0.55 * np.clip(gblur(a, 22) * 1.3, 0, 1)[..., None])
        img = img * (1 - a3) + far * a3
        rim = gblur(a, 9)[..., None] * (1 - a3) * np.array([1.0, 0.12, 0.16], np.float32) * 0.9
        img = screen(img, rim)
    if t > t_thr:
        # the eye looking through the breach: large, tilted, alive; its edges are eaten by the static
        Le = Layer()
        eo = ease(ramp(t, t_thr, t_thr + 1.1)) * (0.3 + 0.7 * blink(t, 70, 7.0))
        pn = lerp(1.35, 0.38, ease(ramp(t, t_thr + 0.5, t_thr + 3.6))) + 0.05 * math.sin(t * 2.2)
        sp = (OX + 6 * vnoise(t, 8, 0.7), 432, 720, -0.13 + 0.03 * vnoise(t, 9, 0.5), 200, "softsat")
        draw_eye(Le.ctx, sp, clamp(eo), (0.88 + 0.12 * math.sin(t * 3.1)) * flick(t, 200, 0.04), t, pn=pn)
        er, ea = Le.rgba()
        er = slices(er, t, 51, rate=10, thresh=0.8, amount=22, n=5)
        ea = slices(ea, t, 51, rate=10, thresh=0.8, amount=22, n=5)
        soft = gblur(ea[..., 0], 16)
        core = np.clip((soft - 0.45) / 0.45, 0, 1)[..., None]
        dm = dissolve_mask(t, 5, 0.10)[..., None] * core + dissolve_mask(t, 6, 1.0)[..., None] * (1 - core)
        er, ea = er * dm, ea * dm
        er = er * 0.75 + cv2.blur(er, (71, 1)) * 0.55                  # the eye bleeds sideways into the noise
        er, ea = gblur(er, 0.9), gblur(ea, 0.9)[..., None]
        img = er + img * (1 - ea)
        img = screen(img, np.clip(bloom(er, 0.35), 0, 1) * 0.5)
    img = screen(img, np.clip(bloom(lr, 1.0), 0, 1))
    img = screen(img, lr)
    # camera: slow push-in about the origin, shake on the crack and on the breach
    cam = 1.0 + 0.12 * ease(ramp(t, 0, s.T))
    shk = lambda t0, amp, dur: amp * math.exp(-(t - t0) / dur) * (1 if t >= t0 else 0)
    amp = shk(t_crack, 16, 0.22) + shk(t_thr, 22, 0.35) + shk(t_alm, 5, 0.3) + shk(t_wall + 0.15, 4, 0.12)
    dx, dy = amp * vnoise(t, 31, 26.0), amp * vnoise(t, 32, 26.0)
    img = push(img, cam, 960, 450)
    img = shift(img, dx, dy)
    # impact looks: split + slices
    ev = math.exp(-(t - t_crack) / 0.18) * (t >= t_crack) + 1.3 * math.exp(-(t - t_thr) / 0.30) * (t >= t_thr)
    img = split(img, 9 * ev)
    if ev > 0.15:
        img = slices(img, t, 21, rate=24, thresh=0.0, amount=50 * ev, n=7)
    elif t > t_crack:
        img = slices(img, t, 22, rate=8, thresh=0.96, amount=30)
    # the flood of red light from the breach
    u = ease_out(ramp(t, t_thr, t_thr + 1.6))
    fl = (1 - 0.55 * ramp(t, t_thr + 1.2, t_thr + 3.0)) * u
    if fl > 0.01:
        yy_c = (OY - 450) * cam + 450
        img = screen(img, radial(960, yy_c, lerp(300, 1250, u), (0.80, 0.07, 0.10), 0.30 * fl))
    if t > t_alm:
        s.box("rift", (OX - 190, RY0, OX + 190, RY1))
    img = scanlines(img, 0.13, t)
    return np.clip(vignette(img, 0.5), 0, 1)


# ------------------------------------------------------------------ polish pass: a gentle midtone lift
# Blacks stay black; the dark midtones open up so the film survives a bright phone feed. Strongest in shot 1, whose
# first seconds were near-black.
_shot_1, _shot_2, _shot_3 = shot_1, shot_2, shot_3


def _lift(img, gamma):
    return np.clip(img, 0, 1) ** gamma


def shot_1(s):
    return _lift(_shot_1(s), 0.80)


def shot_2(s):
    return _lift(_shot_2(s), 0.90)


def shot_3(s):
    return _lift(_shot_3(s), 0.88)

"""HAIRLINE: the picture. One function per shot. Every beat is a voice cue (cue_t), never a hard-coded time.

Shots: 1 wall (L1), 2 wall (L2), 3 beyond (L3), 4 wall with the seam (L4), 5 wall with the crack flare (L5),
6 the title alone on black. The wall's glitching and the seam use absolute film time, so they continue across cuts."""
import math

import cairo
import numpy as np
from animkit import *

TITLE = "HAIRLINE"
TITLE_SIZE = 150
TRACK = 26
# Eye-like glints in the beyond plate, in plate pixels (1664x928), mapped to the 1920x1080 cover frame below.
PLATE_EYES = [(750, 665), (900, 665), (1025, 420), (875, 595)]


def now_of(s):
    return s.gf / FPS


def cue_t(s, spec):
    """Absolute film time (s) of a voice cue such as 'L4:speaks'."""
    return (s.gf - s.f) / FPS + s.c(spec)


def plate_to_frame(x, y):
    """Map a point of the 1664x928 plate to the cover-fitted 1920x1080 frame (before the camera push)."""
    f = H / 928.0
    return x * f - (round(1664 * f) - W) / 2.0, y * f


def scanlines(img, gf, k=0.10):
    rows = ((np.arange(H) + gf // 2) % 3 == 0).astype(np.float32)
    return img * (1 - k * rows)[:, None, None]


def glitch(img, now, density, amount, seed=3, n=10):
    """Horizontal slices shifted sideways, re-chosen 12 times a second (deterministic)."""
    if density <= 0.001 or amount < 1:
        return img
    out = None
    q = int(now * 12)
    for k in range(n):
        if hash01(seed, k, q, 9) > density:
            continue
        if out is None:
            out = np.array(img, dtype=np.float32, copy=True)
        y0 = int(hash01(seed, k, q, 1) * (H - 60))
        hh = int(4 + hash01(seed, k, q, 2) * 46)
        dx = int((hash01(seed, k, q, 3) * 2 - 1) * amount)
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], dx, axis=1)
    return img if out is None else out


def static(img, now, k):
    """Crimson static: a scatter of bright rows, re-drawn 24 times a second."""
    if k <= 0.001:
        return img
    r = np.random.default_rng(int(now * 24) * 7 + 1)
    rows = r.random(H) > 0.84
    lvl = 0.4 + 0.6 * r.random(H)
    add = np.zeros((H, W, 3), np.float32)
    add[rows, :, 0] = (0.16 * k * lvl[rows])[:, None]
    add[rows, :, 1] = (0.02 * k * lvl[rows])[:, None]
    return screen(img, add)


def wall_plate(now):
    sc = 1.0 + 0.003 * now                       # a slow camera push, continuous across the wall shots
    return push(load_plate("wall", expo=2.3), sc), sc


def wall_blocks(img):
    """Faint block seams of a colossal wall: dark mortar lines with a faint red edge light (procedural)."""
    L = Layer()
    ctx = L.ctx
    for r in range(6):
        y = 60 + r * 210
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.45)
        ctx.set_line_width(5)
        ctx.move_to(0, y)
        ctx.line_to(W, y)
        ctx.stroke()
        ctx.set_source_rgba(0.9, 0.08, 0.06, 0.12)
        ctx.set_line_width(1.5)
        ctx.move_to(0, y + 4)
        ctx.line_to(W, y + 4)
        ctx.stroke()
        off = 0 if r % 2 == 0 else 180
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.45)
        ctx.set_line_width(5)
        for x in range(off, W + 1, 360):
            ctx.move_to(x, y)
            ctx.line_to(x, y + 210)
            ctx.stroke()
    return L.over(img)


# ---------------------------------------------------------------- the seam (the crack)

_cr = np.random.default_rng(11)
_N = 90
CR_Y = np.linspace(0, H, _N)
_j = _cr.normal(0, 20, _N)
_j = _j - np.linspace(_j[0], _j[-1], _N)          # keep both ends where they are
CR_X = 1090 - 120 * CR_Y / H + _j
MAIN = list(zip(CR_X, CR_Y))


def _branch(i, ang, length, seed):
    r = np.random.default_rng(seed)
    x, y = MAIN[i]
    pts = [(x, y)]
    a, step = ang, length / 14.0
    for _ in range(14):
        a += r.normal(0, 0.35)
        x += math.cos(a) * step
        y += math.sin(a) * step
        pts.append((x, y))
    return pts


BRANCHES = [_branch(26, 0.55, 280, 21), _branch(52, math.pi - 0.7, 220, 22), _branch(74, 0.25, 160, 23)]


def draw_crack(img, u_main, u_br, flare):
    L = Layer()
    ctx = L.ctx
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    k = 0.75 + 0.25 * flare
    for width, col, a in ((22, (0.8, 0.02, 0.02), 0.22), (6, (1.0, 0.10, 0.08), 0.55), (1.6, (1.0, 0.70, 0.62), 0.85)):
        ctx.set_line_width(width)
        ctx.set_source_rgba(*col, a * k)
        stroke_partial(ctx, MAIN, u_main)
        for pts in BRANCHES:
            stroke_partial(ctx, pts, u_br)
    img = L.add(img)
    if flare > 0.01:
        x, y = MAIN[len(MAIN) // 2]
        img = screen(img, radial(x, y, 340, (0.8, 0.03, 0.03), k=0.35 * flare))
    return img


def wall_scene(s, now):
    """The wall with its glitching, static and seam. Used by every wall shot, so it reads continuously."""
    T2, T4, T5 = cue_t(s, "L2:wall"), cue_t(s, "L4:static"), cue_t(s, "L5:cracking")
    T4sp = cue_t(s, "L4:speaks")
    img, _ = wall_plate(now)
    img = wall_blocks(img)
    img = scanlines(img, s.gf)
    dens = 0.05 + 0.10 * ramp(now, T2, T4) + 0.20 * ramp(now, T4, T5) + 0.25 * ramp(now, T5, T5 + 1.0)
    img = glitch(img, now, dens, 6 + 26 * ramp(now, T2, T4) + 40 * ramp(now, T5, T5 + 1.0))
    img = static(img, now, 1.0 * ramp(now, T4, T4 + 0.8))
    u_main = ease(ramp(now, T4sp, T4sp + 1.6))
    u_br = ease(ramp(now, T5, T5 + 0.8))
    flare = ramp(now, T5, T5 + 0.12) * (1 - 0.45 * ramp(now, T5 + 0.12, T5 + 1.6))
    if u_main > 0:
        img = draw_crack(img, u_main, u_br, flare)
    return img


def shot_1(s):
    now = now_of(s)
    img = wall_scene(s, now)
    return vignette(img, 0.5)


def shot_2(s):
    now = now_of(s)
    T = cue_t(s, "L2:wall")
    img = wall_scene(s, now)
    u = ramp(now, T, T + 1.2)                     # a red band sweeps down the wall on the word "wall"
    if 0 < u < 1:
        yy, _ = grid()
        band = np.exp(-(((yy - (u * (H + 120) - 60)) / 26.0) ** 2)) * (1 - 0.5 * u) * 0.8
        img = screen(img, band[..., None] * np.array([0.6, 0.05, 0.05], np.float32))
    return vignette(img, 0.5)


def shot_3(s):
    """The far side: dark red static with a few pale glints that open on the word 'whispering'."""
    now = now_of(s)
    T = cue_t(s, "L3:whispering")
    sc = 1.0 + 0.003 * now
    img = push(load_plate("beyond", expo=1.0), sc)
    img = scanlines(img, s.gf, 0.12)
    img = glitch(img, now, 0.12 + 0.10 * ramp(now, T, T + 1.5), 16)
    p = ease(ramp(now, T, T + 0.5))
    for i, (x, y) in enumerate(PLATE_EYES):
        X, Y = plate_to_frame(x, y)
        X, Y = W / 2 + (X - W / 2) * sc, H / 2 + (Y - H / 2) * sc
        flick = 0.75 + 0.25 * math.sin(now * (7 + 1.3 * i) + i)
        k = p * flick * (0.8 if i != 2 else 0.6)
        img = screen(img, radial(X, Y, 42, (1.0, 0.12, 0.10), k=0.40 * k))
        img = screen(img, radial(X, Y, 10, (1.0, 0.75, 0.70), k=0.35 * k))
    return vignette(img, 0.5)


def shot_4(s):
    return vignette(wall_scene(s, now_of(s)), 0.5)


def shot_5(s):
    return vignette(wall_scene(s, now_of(s)), 0.5)


# ---------------------------------------------------------------- the title

_m = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))
_m.select_font_face("Bahnschrift", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
_m.set_font_size(TITLE_SIZE)
_adv = [_m.text_extents(ch).x_advance for ch in TITLE]
_total = sum(_adv) + TRACK * (len(TITLE) - 1)
TITLE_XS, _x = [], W / 2 - _total / 2
for _a in _adv:
    TITLE_XS.append(_x)
    _x += _a + TRACK


def shot_6(s):
    now = now_of(s)
    T0 = (s.gf - s.f) / FPS
    base = H / 2 + TITLE_SIZE * 0.35
    L = Layer()
    ctx = L.ctx
    boxes = []
    for i, (ch, x) in enumerate(zip(TITLE, TITLE_XS)):
        a0 = T0 + 0.30 + 0.09 * i
        u = ease(ramp(now, a0, a0 + 0.40))
        dx = (1 - u) * (-26 if i % 2 == 0 else 26)
        text(ctx, ch, x + dx - 5, base, size=TITLE_SIZE, col=(0.9, 0.05, 0.05), a=0.65 * u,
             font="Bahnschrift", weight="bold", anchor="left")
        b = text(ctx, ch, x + dx, base, size=TITLE_SIZE, col=(0.95, 0.93, 0.92), a=u,
                 font="Bahnschrift", weight="bold", anchor="left")
        boxes.append(b)
    s.box("title", (min(b[0] for b in boxes), min(b[1] for b in boxes),
                    max(b[2] for b in boxes), max(b[3] for b in boxes)))
    w = 620 * ease(ramp(now, T0 + 0.8, T0 + 1.5))  # a hairline draws out under the title
    ctx.set_source_rgba(0.9, 0.1, 0.08, 0.9)
    ctx.set_line_width(2.0)
    y = base + TITLE_SIZE * 0.42
    ctx.move_to(W / 2 - w / 2, y)
    ctx.line_to(W / 2 + w / 2, y)
    ctx.stroke()
    return L.over(blank((0.012, 0.0, 0.0)))

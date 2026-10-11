"""animkit.core: drawing and compositing helpers for procedural 2D animation frames.

Frames are float32 RGB numpy arrays, shape (H, W, 3), values in [0, 1]. Draw vector shapes with pycairo on a
Layer, then composite onto the frame. Everything is deterministic: use seeded numpy RNGs, never time or random()."""
import math
import os
from functools import lru_cache

import cairo
import cv2
import numpy as np

W, H, FPS = 1920, 1080, 24
BLACK = np.zeros(3, np.float32)
PROJECT_DIR = os.environ.get("ANIMKIT_PROJECT", os.getcwd())  # set by the CLI; asset paths are relative to it


def set_project(path):
    global PROJECT_DIR
    PROJECT_DIR = os.path.abspath(path)
    os.environ["ANIMKIT_PROJECT"] = PROJECT_DIR


# ---------------------------------------------------------------- math and timing

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ramp(t, t0, t1):
    """0 before t0, 1 after t1, linear in between."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def ease(u):
    """Smoothstep: slow start and end. Use for most motion."""
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def lerp(a, b, u):
    return a + (b - a) * u


def hash01(*k):
    """Deterministic pseudo-random number in [0, 1) from integers."""
    x = 0
    for v in k:
        x = (x * 1000003 + int(v) * 2654435761 + 12345) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0xFFFFFFFF
    x ^= x >> 16
    return x / 4294967296.0


def vnoise(t, seed, freq=1.0):
    """Smooth 1-D value noise in [-1, 1] (flicker, sway)."""
    x = t * freq
    i = math.floor(x)
    f = x - i
    a, b = hash01(seed, i) * 2 - 1, hash01(seed, i + 1) * 2 - 1
    return lerp(a, b, f * f * (3 - 2 * f))


def rgb(hexstr):
    """'#ff8a3d' -> (r, g, b) floats in [0, 1]."""
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ---------------------------------------------------------------- frames

def blank(col=(0.02, 0.02, 0.03)):
    return np.zeros((H, W, 3), np.float32) + np.asarray(col, np.float32)


def gblur(img, sigma):
    if sigma <= 0.3:
        return img
    if sigma > 6:
        f = max(2, int(sigma // 3))
        h, w = img.shape[:2]
        small = cv2.resize(img, (w // f, h // f), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), sigma / f)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(img, (0, 0), sigma)


def screen(base, add):
    """Light-adding blend that never clips harshly. Use to add glows, light, particles."""
    return 1 - (1 - base) * (1 - np.clip(add, 0, 1))


def multiply(base, k):
    """Darken: k is a scalar, an (H, W) mask or an (H, W, 3) image."""
    k = np.asarray(k, np.float32)
    if k.ndim == 2:
        k = k[..., None]
    return base * k


def glow(img, sigma=12, strength=0.9, thresh=0.25):
    """Bloom: bright parts get soft halos (4 octaves). thresh = luminance where bloom starts."""
    lum = img.max(axis=2)
    x = np.clip((lum - thresh + 0.15) / (1 - thresh + 0.15), 0, 1)
    src = img * (x * x * (3 - 2 * x))[..., None]
    g = (gblur(src, sigma * 0.3) + gblur(src, sigma) * 0.6 + gblur(src, sigma * 3) * 0.35 +
         gblur(src, sigma * 8) * 0.2) * strength
    return screen(img, g)


def vignette(img, strength=0.45):
    return img * _vig(round(strength, 2))[..., None]


@lru_cache(maxsize=8)
def _vig(strength):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return (1 - strength * np.clip(d - 0.35, 0, 1) ** 1.6).astype(np.float32)


@lru_cache(maxsize=2)
def grid():
    """(yy, xx) pixel coordinate arrays, for radial masks: d = np.hypot(xx - cx, yy - cy)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    return yy, xx


def radial(cx, cy, r, col, k=1.0, falloff=2.0):
    """A soft radial light at (cx, cy), radius r (px), as an RGB image to screen() onto a frame."""
    yy, xx = grid()
    d = np.hypot(xx - cx, yy - cy) / max(r, 1e-3)
    return (np.exp(-d ** falloff) * k)[..., None] * np.asarray(col, np.float32)


def push(img, scale, cx=W / 2, cy=H / 2):
    """Camera zoom that keeps the point (cx, cy) fixed on screen (scale 1.05 = 5% closer)."""
    if abs(scale - 1) < 1e-5:
        return img
    M = np.array([[scale, 0, cx * (1 - scale)], [0, scale, cy * (1 - scale)]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def shift(img, dx, dy):
    """Camera pan by (dx, dy) px (edges reflect)."""
    if abs(dx) < 1e-3 and abs(dy) < 1e-3:
        return img
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def crossfade(a, b, u):
    u = clamp(u)
    return a * (1 - u) + b * u


# ---------------------------------------------------------------- particles and light

def splat(xs, ys, cols, sizes):
    """Additive soft particles (thousands per frame are fine). xs, ys: arrays; cols: (n, 3); sizes: radius px.
    Returns an RGB light image: frame = screen(frame, splat(...)) or frame + splat(...)."""
    out = np.zeros((H, W, 3), np.float32)
    xs, ys = np.asarray(xs, np.float64), np.asarray(ys, np.float64)
    cols = np.asarray(cols, np.float32).reshape(-1, 3) if np.ndim(cols) > 1 else np.tile(np.asarray(cols, np.float32), (len(xs), 1))
    sizes = np.broadcast_to(np.asarray(sizes, np.float32), xs.shape)
    ok = (xs >= 0) & (xs < W - 1) & (ys >= 0) & (ys < H - 1)
    xs, ys, cols, sizes = xs[ok], ys[ok], cols[ok], sizes[ok]
    for lo, hi, sg in ((0, 0.9, 0.6), (0.9, 1.8, 1.2), (1.8, 3.5, 2.5), (3.5, 7, 5.0), (7, 1e9, 11.0)):
        m = (sizes >= lo) & (sizes < hi)
        if not m.any():
            continue
        buf = np.zeros((H, W, 3), np.float32)
        xi, yi = xs[m], ys[m]
        x0, y0 = np.floor(xi).astype(int), np.floor(yi).astype(int)
        fx, fy = (xi - x0)[:, None], (yi - y0)[:, None]
        cc = cols[m] * (sg * sg * 2.5)
        for dx, dy, wgt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            np.add.at(buf, (y0 + dy, x0 + dx), cc * wgt)
        out += cv2.GaussianBlur(buf, (0, 0), sg)
    return out


def dust(t, n=260, seed=1, col=(1.0, 0.8, 0.6), k=0.35, region=(0, 0, W, H), vy=-8.0, vx=4.0):
    """Drifting motes/embers in depth (near = bigger, faster). vy < 0 rises. Returns an RGB light image."""
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = region
    d = rng.random(n)
    sp = 0.4 + 1.6 * d
    xs = x0 + (rng.random(n) * (x1 - x0) + t * vx * sp + 6 * np.sin(t * 0.7 + rng.random(n) * 6)) % (x1 - x0)
    ys = y0 + (rng.random(n) * (y1 - y0) + t * vy * sp) % (y1 - y0)
    sizes = 0.6 + 5.5 * d ** 3
    tw = 0.5 + 0.5 * np.sin(t * (1 + 3 * rng.random(n)) + rng.random(n) * 6)
    cols = np.outer(tw * (0.25 + 0.75 * rng.random(n)), np.array(col, np.float32)) * k
    return splat(xs, ys, cols, sizes)


def godrays(src, cx, cy, steps=14, span=0.35, decay=0.9):
    """Radial light streaks from (cx, cy): the bright parts of src smear outward. screen() the result on."""
    acc = np.zeros_like(src)
    wsum = 0.0
    for i in range(steps):
        s = 1 + span * i / steps
        M = np.float32([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]])
        w = decay ** i
        acc += cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR) * w
        wsum += w
    return acc / wsum


def grain(img, t, k=0.025, seed=0):
    """Fine film grain (deterministic per frame)."""
    rng = np.random.default_rng(seed * 100003 + int(round(t * 1000)))
    return np.clip(img + rng.normal(0, k, (H, W, 1)).astype(np.float32), 0, 1)


# ---------------------------------------------------------------- vector drawing (pycairo)

class Layer:
    """A transparent cairo canvas the size of the frame. Draw with layer.ctx (cairo.Context), then
    frame = layer.over(frame) (normal alpha), or frame = layer.add(frame) (additive light)."""

    def __init__(self):
        self.s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.ctx = cairo.Context(self.s)
        self.ctx.set_antialias(cairo.ANTIALIAS_GOOD)

    def rgba(self):
        self.s.flush()
        a = np.ndarray((H, W, 4), np.uint8, self.s.get_data()).astype(np.float32) * (1 / 255)
        return a[:, :, [2, 1, 0]], a[:, :, 3:4]   # premultiplied rgb, alpha

    def over(self, img):
        rgb_, a = self.rgba()
        return rgb_ + img * (1 - a)

    def add(self, img, k=1.0):
        rgb_, _ = self.rgba()
        return screen(img, rgb_ * k)

    def alpha(self):
        return self.rgba()[1][..., 0]


def poly_path(ctx, pts, close=True):
    pts = list(pts)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def stroke_partial(ctx, pts, u):
    """Stroke the first fraction u of a polyline (a line drawing itself on)."""
    if u <= 0 or len(pts) < 2:
        return
    n = max(2, int(len(pts) * clamp(u)))
    poly_path(ctx, pts[:n], close=False)
    ctx.stroke()


def safe_scale(ctx, sx, sy=None):
    """ctx.scale that never passes 0 (cairo raises 'invalid matrix' on a zero scale)."""
    sy = sx if sy is None else sy
    ctx.scale(sx if abs(sx) > 1e-4 else 1e-4, sy if abs(sy) > 1e-4 else 1e-4)


def text(ctx, s, x, y, size=64, col=(1, 1, 1), a=1.0, font="Georgia", weight="normal", anchor="center", tracking=0.0):
    """Draw text and return its bounding box (x0, y0, x1, y1) so it can be logged with s.box(...).
    anchor: 'center' (x, y is the center), 'left' or 'right' (y is the baseline)."""
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if weight == "bold" else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    width = ext.x_advance + tracking * max(0, len(s) - 1)
    if anchor == "center":
        x0, base = x - width / 2, y + size * 0.35
    elif anchor == "right":
        x0, base = x - width, y
    else:
        x0, base = x, y
    ctx.set_source_rgba(*col, a)
    if tracking:
        cx = x0
        for ch in s:
            ctx.move_to(cx, base)
            ctx.show_text(ch)
            cx += ctx.text_extents(ch).x_advance + tracking
    else:
        ctx.move_to(x0 - ext.x_bearing * 0, base)
        ctx.show_text(s)
    return (x0, base - size * 0.8, x0 + width, base + size * 0.25)


# ---------------------------------------------------------------- plates (generated background images)

_MEMO = {}


def memo(name, fn):
    """Process + disk cache for expensive static images (build/cache/<name>.npy)."""
    if name in _MEMO:
        return _MEMO[name]
    d = os.path.join(PROJECT_DIR, "build", "cache")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ".npy")
    if os.path.exists(p):
        v = np.load(p).astype(np.float32)
    else:
        v = np.asarray(fn(), np.float32)
        np.save(p + ".tmp.npy", v.astype(np.float16))
        os.replace(p + ".tmp.npy", p)
    _MEMO[name] = v
    return v


def load_plate(name, desat=0.0, expo=1.0, w=W, h=H):
    """assets/plates/<name>.png cover-fitted to the frame (cropped, never stretched), optionally desaturated
    and exposure-scaled. Returns an RGB float frame. Cached."""
    def mk():
        from PIL import Image
        im = Image.open(os.path.join(PROJECT_DIR, "assets", "plates", name + ".png")).convert("RGB")
        sc = max(w / im.width, h / im.height)
        im = im.resize((int(round(im.width * sc)), int(round(im.height * sc))), Image.LANCZOS)
        x0, y0 = (im.width - w) // 2, (im.height - h) // 2
        a = np.asarray(im.crop((x0, y0, x0 + w, y0 + h)), np.float32) / 255
        lum = a.mean(axis=2, keepdims=True)
        return np.clip((lum + (a - lum) * (1 - desat)) * expo, 0, 1)
    src = os.path.join(PROJECT_DIR, "assets", "plates", name + ".png")
    stamp = int(os.path.getmtime(src)) if os.path.exists(src) else 0  # a replaced plate never hits a stale cache
    return memo(f"plate_{name}_{w}x{h}_{desat}_{expo}_{stamp}", mk)

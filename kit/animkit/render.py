"""animkit.render: render stills for review, or the whole film in parallel segments.

    python -m animkit.render PROJECT stills 1:0.5 2:-0.2 3:50%     # shot:seconds | shot:-seconds-from-end | shot:percent
    python -m animkit.render PROJECT sample [--per 4] [--shots 2,3] # N frames inside every shot + one labelled sheet
    python -m animkit.render PROJECT all [--workers 4] [--redo 2,3] # build/picture.mp4 (silent), resumable

The project's shots.py defines one function per shot, named shot_<id> (dots and dashes become '_'), e.g.
`def shot_2(s): ... return frame`. `s` gives: s.t (seconds into the shot), s.T (shot length), s.f / s.gf
(frame in shot / in film), s.c("L2:spark") (cue time in shot seconds), s.box(name, bbox) (log a layout box)."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

from . import core, timeline

SEG = 120  # frames per segment (5 s at 24 fps): delete one to re-render just that part
MARGIN = (0.04 * core.W, 0.05 * core.H)  # title-safe margin for logged boxes


class Shot:
    def __init__(self, tl, sh, f):
        self.tl, self.sh, self.id = tl, sh, sh["id"]
        self.f, self.gf = f, sh["start"] + f
        self.t, self.T = f / core.FPS, sh["frames"] / core.FPS
        self.lines = sh["lines"]
        self.boxes = []

    def c(self, spec):
        """Cue time in seconds from this shot's start, e.g. s.c("L2:spark+0.1")."""
        return timeline.cue(self.tl, self.sh, spec)

    def box(self, name, bbox):
        """Log a layout box (x0, y0, x1, y1) for an important element (titles, subjects) so stills can check
        overlaps and the safe margin. core.text() returns such a box."""
        self.boxes.append((name, tuple(float(v) for v in bbox)))


def load_shots(pdir):
    spec = importlib.util.spec_from_file_location("project_shots", os.path.join(pdir, "shots.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, pdir)
    spec.loader.exec_module(mod)
    return mod


def _fn(mod, sid):
    name = "shot_" + "".join(ch if ch.isalnum() else "_" for ch in sid)
    fn = getattr(mod, name, None)
    if fn is None:
        raise AttributeError(f"shots.py has no function {name}() for shot {sid!r}")
    return fn


def frame_at(tl, mod, gf):
    """Render global frame gf -> (uint8 RGB image, Shot context)."""
    for sh in tl["shots"]:
        if sh["start"] <= gf < sh["start"] + sh["frames"]:
            break
    s = Shot(tl, sh, gf - sh["start"])
    img = np.asarray(_fn(mod, sh["id"])(s), np.float32)
    if img.shape != (core.H, core.W, 3):
        raise ValueError(f"shot {sh['id']} returned shape {img.shape}, expected {(core.H, core.W, 3)}")
    k = 1.0
    if sh["fade_in"] > 0:
        k *= core.ease(s.t / sh["fade_in"])
    if sh["fade_out"] > 0:
        k *= core.ease((s.T - s.t - 1 / core.FPS) / sh["fade_out"])
    if tl["end_fade"] > 0:
        k *= core.ease((tl["frames"] - 1 - gf) / core.FPS / tl["end_fade"])
    img = np.clip(img, 0, 1) * k
    if tl["grain"] > 0:
        img = core.grain(img, gf / core.FPS, tl["grain"])
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), s


def check_boxes(s):
    out = []
    bx = s.boxes
    for name, (x0, y0, x1, y1) in bx:
        if x0 < MARGIN[0] or y0 < MARGIN[1] or x1 > core.W - MARGIN[0] or y1 > core.H - MARGIN[1]:
            if x1 > 0 and y1 > 0 and x0 < core.W and y0 < core.H:
                out.append(f"'{name}' crosses the safe margin {tuple(round(v) for v in (x0, y0, x1, y1))}")
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i][1], bx[j][1]
            ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
            iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
            if ix * iy > 0.02 * min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])):
                out.append(f"'{bx[i][0]}' overlaps '{bx[j][0]}'")
    return out


def _resolve_still(tl, spec):
    sid, _, when = spec.partition(":")
    sh = timeline.shot_by_id(tl, sid)
    n = sh["frames"]
    if when.endswith("%"):
        f = int(round(float(when[:-1]) / 100 * (n - 1)))
    else:
        v = float(when or 0)
        f = int(round(v * core.FPS)) if v >= 0 else n - 1 + int(round(v * core.FPS))
    return sh["start"] + max(0, min(n - 1, f))


def _sheet(paths, labels, out):
    from PIL import Image, ImageDraw
    cols = 3 if len(paths) > 4 else 2 if len(paths) > 1 else 1
    tw, th = 640, 360
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for i, (p, lab) in enumerate(zip(paths, labels)):
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(Image.open(p).resize((tw, th)), (x, y + 22))
        d.text((x + 6, y + 4), lab, fill=(220, 220, 220))
    sheet.save(out, quality=88)


def stills(pdir, gfs, sheet_name="sheet.jpg"):
    from PIL import Image
    tl = timeline.build(pdir)
    mod = load_shots(pdir)
    od = os.path.join(pdir, "output", "stills")
    os.makedirs(od, exist_ok=True)
    paths, labels, warns = [], [], []
    for gf in gfs:
        img, s = frame_at(tl, mod, gf)
        p = os.path.join(od, f"{s.id}_{s.f:04d}.png")
        Image.fromarray(img).save(p)
        paths.append(p)
        labels.append(f"shot {s.id}  t={s.t:.2f}s  film {gf / core.FPS:.2f}s")
        for w in check_boxes(s):
            warns.append(f"shot {s.id} t={s.t:.2f}: {w}")
        print(p)
    sp = os.path.join(od, sheet_name)
    _sheet(paths, labels, sp)
    print("sheet:", sp)
    for w in warns:
        print("LAYOUT WARNING:", w)
    return sp


def _render_seg(args):
    pdir, a, b, path, key = args
    core.set_project(pdir)
    tl = timeline.build(pdir, write=False)
    mod = load_shots(pdir)
    tmp = path + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{core.W}x{core.H}",
           "-r", str(core.FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt",
           "yuv420p", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    luma = []
    for gf in range(a, b):
        img, _ = frame_at(tl, mod, gf)
        luma.append(round(float(img.mean()) / 255, 4))
        p.stdin.write(img.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f"ffmpeg failed on {path}")
    os.replace(tmp, path)
    with open(path + ".luma.json", "w") as f:
        json.dump(dict(start=a, luma=luma, key=key), f)
    return path


def code_key(pdir):
    """A hash of everything that decides the pixels: shots.py, project.json and the kit itself."""
    h = hashlib.sha1()
    files = [os.path.join(pdir, "shots.py"), os.path.join(pdir, "project.json")]
    kd = os.path.dirname(os.path.abspath(__file__))
    files += sorted(os.path.join(kd, f) for f in os.listdir(kd) if f.endswith(".py"))
    for f in files:
        with open(f, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def _seg_key(path):
    try:
        with open(path + ".luma.json") as f:
            return json.load(f).get("key")
    except (OSError, ValueError):
        return None


def render_all(pdir, workers=4, redo=()):
    """Render missing or stale segments. A segment is stale when shots.py, project.json or the kit changed since
    it was rendered. With --redo, only the segments covering those shots are re-rendered, and the others are
    trusted as current."""
    tl = timeline.build(pdir)
    sd = os.path.join(pdir, "build", "seg")
    os.makedirs(sd, exist_ok=True)
    key = code_key(pdir)
    jobs = []
    for a in range(0, tl["frames"], SEG):
        b = min(tl["frames"], a + SEG)
        path = os.path.join(sd, f"seg_{a:06d}_{b:06d}.mp4")
        hit = any(sh["start"] < b and a < sh["start"] + sh["frames"] for sh in tl["shots"] if sh["id"] in redo)
        stale = os.path.exists(path) and _seg_key(path) != key
        if redo and stale and not hit:  # the caller says the rest is current: adopt it
            with open(path + ".luma.json") as f:
                d = json.load(f)
            d["key"] = key
            with open(path + ".luma.json", "w") as f:
                json.dump(d, f)
            stale = False
        if (hit or stale) and os.path.exists(path):
            os.remove(path)
        if not os.path.exists(path):
            jobs.append((pdir, a, b, path, key))
    # drop stale segments from an older timeline
    keep = {os.path.basename(j[3]) for j in jobs} | {f"seg_{a:06d}_{min(tl['frames'], a + SEG):06d}.mp4"
                                                      for a in range(0, tl["frames"], SEG)}
    for fn in os.listdir(sd):
        if fn.endswith(".mp4") and fn not in keep:
            os.remove(os.path.join(sd, fn))
    t0 = time.time()
    print(f"{tl['frames']} frames, {len(jobs)} segment(s) to render with {workers} worker(s)")
    if jobs:
        with Pool(min(workers, len(jobs))) as pool:
            for done in pool.imap_unordered(_render_seg, jobs):
                print("  done", os.path.basename(done), f"{time.time() - t0:.0f}s")
    segs = sorted(fn for fn in os.listdir(sd) if fn.endswith(".mp4"))
    lst = os.path.join(sd, "list.txt")
    with open(lst, "w") as f:
        for fn in segs:
            f.write(f"file '{fn}'\n")
    out = os.path.join(pdir, "build", "picture.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out],
                   check=True)
    print("wrote", out, f"({tl['seconds']}s) in {time.time() - t0:.0f}s")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="animkit.render")
    ap.add_argument("project")
    ap.add_argument("mode", choices=["stills", "sample", "all"])
    ap.add_argument("specs", nargs="*")
    ap.add_argument("--per", type=int, default=4)
    ap.add_argument("--shots", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--redo", default="")
    a = ap.parse_args(argv)
    pdir = os.path.abspath(a.project)
    core.set_project(pdir)
    if a.mode == "stills":
        tl = timeline.build(pdir)
        stills(pdir, [_resolve_still(tl, sp) for sp in a.specs])
    elif a.mode == "sample":
        tl = timeline.build(pdir)
        want = [x for x in a.shots.split(",") if x]
        gfs = []
        for sh in tl["shots"]:
            if want and sh["id"] not in want:
                continue
            n = sh["frames"]
            for k in range(a.per):
                gfs.append(sh["start"] + int(round((k + 0.5) / a.per * (n - 1))))
        stills(pdir, gfs, "sample_sheet.jpg")
    else:
        render_all(pdir, a.workers, [x for x in a.redo.split(",") if x])


if __name__ == "__main__":
    main()

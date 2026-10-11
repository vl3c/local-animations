"""animkit.mix: the soundtrack, built outside the renderer from the same timeline.

    python -m animkit.mix PROJECT        -> build/mix.wav (48 kHz stereo, peaks under -1 dBFS) at the project.json "lufs"
                                            target (integrated, default -16)

Voice lines play where the timeline puts them. Sound effects come from project.json "sfx": a list of
{"file": "assets/sfx/x.wav", "at": "L2:spark" | 3.5, "gain_db": -12, "fade_out": 0.3}. Optional music:
{"file": ..., "gain_db": -14, "start": 0.0, "offset": 0.0, "fade_in": 2.0, "fade_out": 3.0}. The music is not
ducked under the voice (it reads as pumping); set its level so the voice sits clearly above it."""
import argparse
import os

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy.signal import resample_poly

from . import core, timeline

SR = 48000


def db(x):
    return 10 ** (x / 20)


def load(path):
    a, sr = sf.read(path, dtype="float32", always_2d=True)
    if a.shape[1] == 1:
        a = np.repeat(a, 2, axis=1)
    a = a[:, :2]
    if sr != SR:
        a = resample_poly(a, SR, sr, axis=0).astype(np.float32)
    return a


def place(bus, a, t, gain_db=0.0, fade_in=0.0, fade_out=0.0):
    a = a * db(gain_db)
    n = len(a)
    if fade_in > 0:
        k = min(n, int(fade_in * SR))
        a[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out > 0:
        k = min(n, int(fade_out * SR))
        a[n - k:] *= np.linspace(1, 0, k)[:, None]
    i = int(round(t * SR))
    if i < 0:
        a, i = a[-i:], 0
    j = min(len(bus), i + len(a))
    if j > i:
        bus[i:j] += a[:j - i]


def build(pdir):
    tl = timeline.build(pdir)
    P = timeline.load_project(pdir)
    n = int(round(tl["seconds"] * SR))
    vo, fx, mu = (np.zeros((n, 2), np.float32) for _ in range(3))
    lines = {ln["id"]: ln for ln in P.get("lines", [])}
    for sh in tl["shots"]:
        for ln in sh["lines"]:
            src = lines[ln["id"]]
            place(vo, load(os.path.join(pdir, src["audio"])), sh["start"] / core.FPS + ln["start"],
                  float(src.get("gain_db", 0.0)))
    for e in P.get("sfx", []):
        at = e["at"]
        t = float(at) if isinstance(at, (int, float)) or str(at).replace(".", "", 1).isdigit() else timeline.cue_global(tl, at)
        place(fx, load(os.path.join(pdir, e["file"])), t + float(e.get("offset", 0.0)), float(e.get("gain_db", -12)),
              float(e.get("fade_in", 0.0)), float(e.get("fade_out", 0.0)))
    m = P.get("music")
    if m:
        a = load(os.path.join(pdir, m["file"]))
        a = a[int(float(m.get("offset", 0)) * SR):]
        a = a[:max(0, n - int(float(m.get("start", 0)) * SR))]
        place(mu, a, float(m.get("start", 0)), float(m.get("gain_db", -14)), float(m.get("fade_in", 2.0)),
              float(m.get("fade_out", 3.0)))
    mix = vo + fx + mu
    if tl["end_fade"] > 0:  # the soundtrack fades with the picture
        k = int(tl["end_fade"] * SR)
        mix[n - k:] *= np.linspace(1, 0, k)[:, None] ** 1.5
    meter = pyln.Meter(SR)
    lufs = meter.integrated_loudness(mix)
    target = float(P.get("lufs", -16))  # integrated loudness target (project.json "lufs")
    mix *= db(target - lufs)
    pk = np.abs(mix).max()
    if pk > db(-1):
        mix = np.tanh(mix / db(-1)) * db(-1)  # soft limit the few peaks
    out = os.path.join(pdir, "build", "mix.wav")
    sf.write(out, mix, SR, subtype="PCM_24")
    final = meter.integrated_loudness(mix)
    print(f"wrote {out}: {n / SR:.2f}s, {final:.1f} LUFS, peak {20 * np.log10(np.abs(mix).max() + 1e-9):.1f} dBFS")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="animkit.mix")
    ap.add_argument("project")
    a = ap.parse_args(argv)
    pdir = os.path.abspath(a.project)
    core.set_project(pdir)
    build(pdir)


if __name__ == "__main__":
    main()

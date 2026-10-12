"""Check that a film's light pulses land on the music's kicks, measured on the encoded file (picture and sound as
the viewer gets them).

    python kit/tools/sync_check.py "$FILM/output/<slug>.mp4" "$FILM/assets/music/bed.kicks.json" [--from 15 --to 58]
        [--shift S]

Kick times are music-file times; --shift S maps them to film time (film t = kick t + S: S = the project's
music "start" minus its "offset"; 0 when the music starts the film). Per frame, the brightness of the saturated
pixels (where a pulse shows), minus its 1 s running mean; per kick, the frame of the highest value within +-4
frames. Prints the offset pulse - kick (median and 10-90%; a frame is 42 ms at 24 fps; within half a frame reads
as on the beat) and writes <video>.sync.png: the kick band of the encoded audio
against the pulse, three windows. Church of Superintelligence: 1 ms median, -16..18 ms.
"""
import argparse
import json
import os
import subprocess
import tempfile

import cv2
import numpy as np
import soundfile as sf
from scipy.signal import stft


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("kicks")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=1e9)
    ap.add_argument("--shift", type=float, default=0.0, help="film t = kick t + SHIFT (music start - offset)")
    o = ap.parse_args()
    wav = os.path.join(tempfile.mkdtemp(), "a.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", o.video, "-vn", "-ac", "1", "-ar", "48000", wav],
                   check=True)
    y, sr = sf.read(wav)
    fr, ta, Z = stft(y, fs=sr, nperseg=2048, noverlap=2048 - 128)
    low = np.abs(Z)[(fr > 30) & (fr < 120)].sum(0)
    low /= max(low.max(), 1e-9)
    cap = cv2.VideoCapture(o.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    P = []
    while True:
        ok, im = cap.read()
        if not ok:
            break
        hsv = cv2.cvtColor(cv2.resize(im, (320, 180)), cv2.COLOR_BGR2HSV).astype(np.float32)
        m = hsv[..., 1] > 90
        P.append((hsv[..., 2] * m).sum() / max(m.sum(), 1))
    P = np.array(P)
    if len(P) < 3 * fps:
        raise SystemExit("video too short to check (under 3 s)")
    tv = np.arange(len(P)) / fps
    res = P - np.convolve(P, np.ones(int(fps) + 1) / (int(fps) + 1), mode="same")
    ks = json.load(open(o.kicks)).get("kicks", [])
    K = np.array([k[0] for k in ks], np.float64) + o.shift
    K = K[(K >= max(o.t0, 1)) & (K <= min(o.t1, tv[-1] - 1))]
    if len(K) < 3:
        raise SystemExit(f"only {len(K)} kicks in the checked span: nothing to measure")
    offs = []
    for k in K:
        i0 = int(round(k * fps))
        w = res[i0 - 4:i0 + 5]
        offs.append(((i0 + np.argmax(w) - 4) / fps - k) * 1000)
    offs = np.array(offs)
    print(f"pulse peak - kick attack: median {np.median(offs):.0f} ms, 10-90% {np.percentile(offs, 10):.0f}.."
          f"{np.percentile(offs, 90):.0f} ms over {len(offs)} kicks (1 frame = {1000 / fps:.0f} ms)")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 1, figsize=(16, 8))
    for ax, c in zip(axs, np.linspace(K[0] + 2, K[-1] - 2, 3)):
        a, b = c - 2, c + 2
        m = (ta >= a) & (ta < b)
        ax.plot(ta[m], low[m], color="tab:blue", label="kick band, encoded audio")
        v = (tv >= a) & (tv < b)
        r = res[v]
        ax.plot(tv[v], (r - r.min()) / (np.ptp(r) + 1e-9), "o-", color="tab:pink", ms=3, label="light pulse, picture")
        for k in K:
            if a <= k < b:
                ax.axvline(k, color="tab:red", lw=0.8)
        ax.set_xlim(a, b)
        ax.legend(loc="upper right")
    fig.tight_layout()
    out = os.path.splitext(o.video)[0] + ".sync.png"
    fig.savefig(out, dpi=85)
    print(out)


if __name__ == "__main__":
    main()

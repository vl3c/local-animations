"""The kicks of a music file, detected in the waveform, for films whose pulses must land on the beat.

    ~/.claude/skills/local-music/.venv/Scripts/python.exe kit/tools/kicks.py "$FILM/assets/music/bed.wav" \
        [--end-after 15] [--slow-to 66.2] [--band 30,120]

Writes <music>.kicks.json ({"kicks": [[t, strength], ...], "slowing": [...], "beat_median": s}) and
<music>.kicks.png (the waveform in four windows with every kick marked): Read the PNG before using the list.

A kick is the attack of the low band: the onset envelope (hop 2.7 ms) peak-picked with a 0.3 s minimum gap and a
threshold relative to the local level, each peak moved back to where the band has risen half-way to its peak (the
moment the ear hears the hit). Every kick is kept and gaps over 1 s (breakdowns) are printed; with --end-after T the
list stops at the first such gap after T s (the drums have ended; later low hits are not kicks). With --slow-to,
synthetic pulses follow the last kick, each interval x1.28 longer and 10% weaker, until that time (a beat that
"runs down" after the music's drums stop).

Why not a beat grid: in Church of Superintelligence a fitted grid read 127.84 BPM, a "refit" read 127.96, and the
pulses still drifted 20-40 ms off the kicks by the middle of the film, which the user saw ("the pulsing gets
desynced"). Pulses driven by these detected attacks measured 1 ms median, -16..18 ms (10-90%) on the encode
(kit/tools/sync_check.py).
"""
import argparse
import json
import os

import numpy as np


def detect(path, band=(30, 120), gap_s=0.3, hop=128, end_after=None):
    import librosa
    y, sr = librosa.load(path, sr=None, mono=True)
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    low = S[(f > band[0]) & (f < band[1])].sum(0)
    low = low / max(low.max(), 1e-9)
    env = np.maximum(0, np.diff(low, prepend=low[0]))
    t = librosa.frames_to_time(np.arange(len(env)), sr=sr, hop_length=hop)
    gap = int(gap_s * sr / hop)
    w = int(2.0 * sr / hop)
    loc = np.array([env[max(0, i - w):i + w].max() for i in range(len(env))])
    kicks, i = [], 0
    while i < len(env):
        if env[i] > 0.35 * loc[i] and env[i] > 0.02 and env[i] == env[max(0, i - gap):i + gap].max():
            j0 = max(0, i - int(0.06 * sr / hop))
            base = low[j0:i + 1].min()
            pk = low[i:i + int(0.05 * sr / hop)].max()
            j = i
            while j > j0 and low[j] > base + 0.5 * (pk - base):
                j -= 1
            kicks.append((float(t[j]), float(env[i] / loc[i])))
            i += gap
        else:
            i += 1
    real = kicks[:1]
    for k in kicks[1:]:
        if end_after is not None and k[0] > end_after and k[0] - real[-1][0] > 1.0:
            break
        real.append(k)
    return y, sr, t, low, real


def main():
    ap = argparse.ArgumentParser(description="kicks of a music file")
    ap.add_argument("music")
    ap.add_argument("--band", default="30,120", help="low band in Hz (default 30,120)")
    ap.add_argument("--end-after", type=float, default=None,
                    help="stop at the first gap over 1 s after T s (the drums end there)")
    ap.add_argument("--slow-to", type=float, default=0.0, help="add slowing pulses after the last kick until T s")
    o = ap.parse_args()
    y, sr, t, low, real = detect(o.music, tuple(float(x) for x in o.band.split(",")), end_after=o.end_after)
    if not real:
        raise SystemExit("no kicks found (is there a kick drum in this band?)")
    beat = float(np.median(np.diff([k[0] for k in real]))) if len(real) > 2 else 0.0
    gaps = [(a, b - a) for (a, _), (b, _) in zip(real[:-1], real[1:]) if b - a > 1.0]
    if gaps:
        print("gaps over 1 s (breakdowns?): " + ", ".join(f"{a:.2f} s +{g:.2f}" for a, g in gaps))
    synth = []
    if o.slow_to and beat > 0:
        tl, d, s = real[-1][0], beat, 1.0
        while True:
            d *= 1.28
            tl += d
            s *= 0.9
            if tl > o.slow_to:
                break
            synth.append((tl, s))
    base = os.path.splitext(o.music)[0]
    json.dump({"source": os.path.basename(o.music), "beat_median": beat,
               "kicks": [[round(a, 4), round(b, 3)] for a, b in real],
               "slowing": [[round(a, 4), round(b, 3)] for a, b in synth]}, open(base + ".kicks.json", "w"), indent=0)
    print(f"{len(real)} kicks, {real[0][0]:.3f}-{real[-1][0]:.3f} s, median beat {beat:.4f} s "
          f"({60 / beat if beat else 0:.2f} BPM); {len(synth)} slowing pulses")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dur = len(y) / sr
    if dur < 4.5:
        return
    wins = [(a, a + 4) for a in np.linspace(0, dur - 4, 4)]
    fig, axs = plt.subplots(4, 1, figsize=(16, 11))
    ts = np.arange(len(y)) / sr
    for ax, (a, b) in zip(axs, wins):
        m = (ts >= a) & (ts < b)
        ax.plot(ts[m], y[m], lw=0.4, color="0.3")
        lm = (t >= a) & (t < b)
        ax.plot(t[lm], low[lm] * max(np.abs(y[m]).max(), 1e-6), lw=1, color="tab:blue")
        for k, _ in real:
            if a <= k < b:
                ax.axvline(k, color="tab:red", lw=1.2)
        for k, _ in synth:
            if a <= k < b:
                ax.axvline(k, color="tab:purple", lw=1.2, ls="--")
        ax.set_xlim(a, b)
        ax.set_title(f"{a:.1f}-{b:.1f} s: red = kicks, purple dashed = slowing pulses, blue = low band")
    fig.tight_layout()
    fig.savefig(base + ".kicks.png", dpi=90)
    print(base + ".kicks.png")


if __name__ == "__main__":
    main()

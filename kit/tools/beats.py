"""The beat grid of a music file, for films timed on the music (no voice to cue on).

    ~/.claude/skills/local-music/.venv/Scripts/python.exe kit/tools/beats.py "$FILM/assets/music/bed.wav" [--bar 4]

Prints the tempo, every beat, the bar lengths (an accelerando shows as shorter bars), the silences, and a CUES.md
table to edit (downbeats, every --bar beats from the strongest phase, and the strongest onsets off the downbeats);
writes <music>.beats.json next to the file. Run it with local-music's interpreter (it has librosa).
In Puff Ahoy it found the band's accelerando (bars 2.00 s -> 1.83 s from 16 s), the silence before the button chord
and the chord itself (20.29 s); every cut and gag was put on that grid.
"""
import argparse
import json
import os
import sys

import numpy as np


def main(argv=None):
    ap = argparse.ArgumentParser(description="Beat grid of a music file")
    ap.add_argument("music")
    ap.add_argument("--bar", type=int, default=4, help="beats per bar (default 4)")
    o = ap.parse_args(argv)
    import librosa

    y, sr = librosa.load(o.music, sr=22050, mono=True)
    dur = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", tightness=200)
    tempo = float(np.atleast_1d(tempo)[0])
    env = librosa.onset.onset_strength(y=y, sr=sr)
    et = librosa.times_like(env, sr=sr)
    strength = np.interp(beats, et, env)
    phase = int(np.argmax([strength[p::o.bar].mean() for p in range(o.bar)]))
    downs = beats[phase::o.bar]
    hits = np.sort(et[np.argsort(env)[-12:]])
    rms = librosa.feature.rms(y=y)[0]
    rt = librosa.times_like(rms, sr=sr)
    db = 20 * np.log10(rms + 1e-9)
    loud = db.max()
    quiet = rt[(db < loud - 30) & (rt < dur - 0.5)]
    gaps = []
    for t in quiet:
        if not gaps or t - gaps[-1][1] > 0.1:
            gaps.append([t, t])
        else:
            gaps[-1][1] = t
    gaps = [(round(float(a), 2), round(float(b), 2)) for a, b in gaps if b - a >= 0.1]
    ibi = np.diff(beats)
    bars = np.diff(downs)

    print(f"{os.path.basename(o.music)}: {dur:.2f} s, about {tempo:.1f} BPM, beat {np.median(ibi):.3f} s, "
          f"bar {np.median(ibi) * o.bar:.2f} s")
    print("beats:", [round(float(b), 3) for b in beats])
    print("bar lengths (s), a tempo change shows here:",
          [f"{float(t):.2f}:{float(b):.2f}" for t, b in zip(downs[:-1], bars)])
    if gaps:
        print("silences:", gaps)
    print("\n| Time (s) | Music event | Bar | Shot / beat |\n| --- | --- | --- | --- |")
    rows = [(float(t), "downbeat", i + 1) for i, t in enumerate(downs)]
    rows += [(float(t), "strong onset", None) for t in hits if np.min(np.abs(downs - t)) > 0.12]
    rows += [(a, "silence starts", None) for a, _ in gaps]
    for t, what, bar in sorted(rows):
        print(f"| {t:.2f} | {what} | {bar or ''} | |")
    out = os.path.splitext(o.music)[0] + ".beats.json"
    json.dump(dict(tempo=tempo, beats=[round(float(b), 4) for b in beats], downbeats=[round(float(b), 4) for b in downs],
                   hits=[round(float(h), 4) for h in hits], silences=gaps, duration=round(dur, 3)), open(out, "w"),
              indent=1)
    print("\nwrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

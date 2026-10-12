"""animkit.finish: mux picture + soundtrack, make a contact sheet, run the automatic checks.

    python -m animkit.finish PROJECT [--every 1.0] [--strict]
        -> output/<title>.mp4, output/contact.jpg, and a check report printed (and saved to output/checks.txt);
           --strict exits 1 when the report has a WARNING (for CI)
    python -m animkit.finish PROJECT --info
        -> prints the timeline: shots, their times, every line and the film time of every word (for cue specs)"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

from . import core, timeline


def info(pdir):
    tl = timeline.build(pdir)
    print(f"{tl['title']}: {tl['seconds']}s, {tl['frames']} frames at {core.FPS} fps")
    for sh in tl["shots"]:
        a = sh["start"] / core.FPS
        print(f"shot {sh['id']}: {a:.2f}s - {a + sh['frames'] / core.FPS:.2f}s ({sh['frames'] / core.FPS:.2f}s)")
        for ln in sh["lines"]:
            t0 = a + ln["start"]
            print(f"   {ln['id']} at shot+{ln['start']:.2f}s (film {t0:.2f}s), {ln['dur']:.2f}s: {ln['text']}")
            print("      " + "  ".join(f"{w['w']}@{w['t0']:.2f}" for w in ln["words"]))


def contact(video, out, every=1.0, cols=6):
    from PIL import Image, ImageDraw
    tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"fps=1/{every},scale=320:180",
                    os.path.join(tmp, "%04d.png")], check=True)
    files = sorted(glob.glob(os.path.join(tmp, "*.png")))
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 320, rows * 196), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        x, y = (i % cols) * 320, (i // cols) * 196
        sheet.paste(Image.open(f), (x, y + 16))
        d.text((x + 3, y + 2), f"{i * every:.1f}s", fill=(200, 200, 200))
    sheet.save(out, quality=88)
    return out


def checks(pdir, tl, video):
    import pyloudnorm as pyln
    import soundfile as sf
    rep = []
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True, check=True).stdout.strip())
    rep.append(f"duration {dur:.2f}s (timeline {tl['seconds']:.2f}s)"
               + ("" if abs(dur - tl["seconds"]) <= 0.1 else "  (DURATION WARNING: the mp4 and the timeline differ)"))
    a, sr = sf.read(os.path.join(pdir, "build", "mix.wav"))
    rep.append(f"loudness {pyln.Meter(sr).integrated_loudness(a):.1f} LUFS, peak {20 * np.log10(np.abs(a).max() + 1e-9):.1f} dBFS")
    luma = []
    for p in sorted(glob.glob(os.path.join(pdir, "build", "seg", "*.luma.json"))):
        with open(p) as f:
            luma += json.load(f)["luma"]
    if luma:
        L = np.array(luma)
        jumps = np.where(np.abs(np.diff(L)) > 0.18)[0]
        for j in jumps[:10]:
            rep.append(f"FLASH/CUT WARNING: brightness jumps {L[j]:.2f} -> {L[j + 1]:.2f} at {(j + 1) / core.FPS:.2f}s "
                       f"(fade in after bright cuts)")
        rep.append(f"brightness: max {L.max():.2f} at {L.argmax() / core.FPS:.2f}s; last frame {L[-1]:.3f}"
                   + ("" if L[-1] < 0.02 else "  (WARNING: the film does not end on black)"))
        if L[0] > 0.02:
            rep.append("note: the film does not start from black")
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(prog="animkit.finish")
    ap.add_argument("project")
    ap.add_argument("--every", type=float, default=1.0)
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a check prints a WARNING")
    a = ap.parse_args(argv)
    pdir = os.path.abspath(a.project)
    core.set_project(pdir)
    if a.info:
        info(pdir)
        return
    tl = timeline.build(pdir)
    od = os.path.join(pdir, "output")
    os.makedirs(od, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", (tl["title"] or "film").lower()).strip("_")
    video = os.path.join(od, f"{slug}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(pdir, "build", "picture.mp4"),
                    "-i", os.path.join(pdir, "build", "mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", video],
                   check=True)
    print("wrote", video)
    print("contact sheet:", contact(video, os.path.join(od, "contact.jpg"), a.every))
    rep = checks(pdir, tl, video)
    with open(os.path.join(od, "checks.txt"), "w") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))
    if a.strict and any("WARNING" in r for r in rep):
        sys.exit(1)


if __name__ == "__main__":
    main()

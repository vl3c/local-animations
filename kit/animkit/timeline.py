"""animkit.timeline: project.json -> build/timeline.json, and cue specs resolved from word timings.

Timing comes from the voice, never from guesses: each shot is padded around the lines it carries, and visual
beats are cue specs like "L2:spark" (the start of the word "spark" in line L2), "L2:spark+0.2", "L2:end-0.5",
"L2:start", "L3:fire#2" (second occurrence of "fire"). Plain numbers are seconds from the shot start."""
import json
import os
import re

import soundfile as sf

from . import core

FPS = core.FPS
GAP = 0.35  # default silence between consecutive lines inside one shot (s)


def _norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def load_project(pdir):
    with open(os.path.join(pdir, "project.json"), encoding="utf-8") as f:
        return json.load(f)


def build(pdir, write=True):
    """Lay out shots and lines; returns the timeline dict (and writes build/timeline.json)."""
    P = load_project(pdir)
    lines = {ln["id"]: ln for ln in P.get("lines", [])}
    shots, frame = [], 0
    for sh in P["shots"]:
        placed, t = [], float(sh.get("pre", 0.5))
        for lid in sh.get("lines", []):
            ln = lines[lid]
            info = sf.info(os.path.join(pdir, ln["audio"]))
            dur = info.frames / info.samplerate
            words = []
            wp = ln.get("words")
            if wp and os.path.exists(os.path.join(pdir, wp)):
                with open(os.path.join(pdir, wp), encoding="utf-8") as f:
                    words = json.load(f)
            t = float(ln.get("at", t))  # optional fixed position inside the shot
            placed.append(dict(id=lid, start=round(t, 4), dur=round(dur, 4), words=words, text=ln.get("text", "")))
            t += dur + float(ln.get("gap_after", GAP))
        if "dur" in sh:
            length = float(sh["dur"])
        else:
            last_end = max([p["start"] + p["dur"] for p in placed], default=0.0)
            length = last_end + float(sh.get("post", 0.6))
        n = max(1, int(round(length * FPS)))
        shots.append(dict(id=str(sh["id"]), start=frame, frames=n, lines=placed,
                          fade_in=float(sh.get("fade_in", 0)), fade_out=float(sh.get("fade_out", 0))))
        frame += n
    target = P.get("duration")
    if target:  # stretch or trim the last shot so the film is exactly `duration` seconds
        want = int(round(float(target) * FPS))
        diff = want - frame
        if shots[-1]["frames"] + diff < FPS // 2:
            raise ValueError(f"duration {target}s is too short for the voice: needs {frame / FPS:.2f}s")
        shots[-1]["frames"] += diff
        frame = want
    tl = dict(title=P.get("title", ""), fps=FPS, frames=frame, seconds=round(frame / FPS, 3), shots=shots,
              end_fade=float(P.get("end_fade", 0)), grain=float(P.get("grain", 0.0)))
    if write:
        os.makedirs(os.path.join(pdir, "build"), exist_ok=True)
        with open(os.path.join(pdir, "build", "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(tl, f, indent=1)
    return tl


def shot_by_id(tl, sid):
    for s in tl["shots"]:
        if s["id"] == str(sid):
            return s
    raise KeyError(f"no shot {sid!r}; shots are {[s['id'] for s in tl['shots']]}")


def find_line(tl, lid):
    for s in tl["shots"]:
        for ln in s["lines"]:
            if ln["id"] == lid:
                return s, ln
    raise KeyError(f"no line {lid!r} in any shot")


_SPEC = re.compile(r"^\s*([A-Za-z0-9_]+):([A-Za-z0-9'_]+)(?:#(\d+))?\s*([+-]\s*[0-9.]+)?\s*$")


def cue_global(tl, spec):
    """Absolute time (s, from the film start) of a cue spec like 'L2:spark+0.2'."""
    m = _SPEC.match(spec)
    if not m:
        raise ValueError(f"bad cue spec {spec!r} (use 'L2:word', 'L2:word+0.3', 'L2:start', 'L2:end-0.5', 'L2:word#2')")
    lid, word, nth, off = m.group(1), m.group(2), int(m.group(3) or 1), m.group(4)
    sh, ln = find_line(tl, lid)
    base = sh["start"] / FPS + ln["start"]
    if word == "start":
        t = 0.0
    elif word == "end":
        t = ln["words"][-1]["t1"] if ln["words"] else ln["dur"]
    else:
        hits = [w for w in ln["words"] if _norm(w["w"]) == _norm(word)]
        if len(hits) < nth:
            raise KeyError(f"word {word!r} (#{nth}) not in {lid}: {[w['w'] for w in ln['words']]}")
        t = hits[nth - 1]["t0"]
    return base + t + (float(off.replace(" ", "")) if off else 0.0)


def cue(tl, shot, spec):
    """Time of a cue relative to the start of `shot` (a timeline shot dict). Numbers pass through."""
    if isinstance(spec, (int, float)):
        return float(spec)
    try:
        return float(spec)
    except ValueError:
        pass
    return cue_global(tl, spec) - shot["start"] / FPS

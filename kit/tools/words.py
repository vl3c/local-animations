"""Word timestamps for voice lines (Whisper large-v3-turbo, word level), from the exact file that will play.
Run with the local-voice venv (it has torch, transformers and the Whisper weights):
    ~/.claude/skills/local-voice/.venv/Scripts/python.exe kit/tools/words.py PROJECT [LINE_IDS...]
Reads project.json lines ({"id", "audio", "words"}) and writes each line's "words" JSON: [{w, t0, t1}] in seconds."""
import json
import os
import sys

import numpy as np
import soundfile as sf
import torch
from transformers import pipeline

pdir = os.path.abspath(sys.argv[1])
only = set(sys.argv[2:])
MODEL = os.path.expanduser("~/.claude/skills/local-voice/models/whisper-large-v3-turbo")
pipe = pipeline("automatic-speech-recognition", model=MODEL, torch_dtype=torch.float16, device="cuda:0")
with open(os.path.join(pdir, "project.json"), encoding="utf-8") as f:
    P = json.load(f)
for ln in P["lines"]:
    if only and ln["id"] not in only:
        continue
    a, sr = sf.read(os.path.join(pdir, ln["audio"]), dtype="float32")
    if a.ndim > 1:
        a = a.mean(1)
    if sr != 16000:
        from scipy.signal import resample_poly
        a = resample_poly(a, 16000, sr).astype(np.float32)
    r = pipe({"raw": a, "sampling_rate": 16000}, return_timestamps="word",
             generate_kwargs={"language": "en", "task": "transcribe"})
    words = [dict(w=ch["text"].strip(), t0=round(float(ch["timestamp"][0]), 3),
                  t1=round(float(ch["timestamp"][1] if ch["timestamp"][1] is not None else ch["timestamp"][0] + 0.3), 3))
             for ch in r["chunks"]]
    out = os.path.join(pdir, ln.get("words") or f"assets/vo/{ln['id']}.words.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=0)
    print(ln["id"], " ".join(f"{w['w']}@{w['t0']}" for w in words))

"""Make the smoke project's assets procedurally (no models): a plate, a voice stand-in, its word timings, a tick.

    python projects/_smoke/make_assets.py [DEST]     # DEST defaults to this folder; writes DEST/assets/..."""
import json
import os
import sys

import numpy as np
import soundfile as sf
from PIL import Image

SR = 48000
dest = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
a = os.path.join(dest, "assets")
for d in ("plates", "vo", "sfx"):
    os.makedirs(os.path.join(a, d), exist_ok=True)

# plate: a dusk gradient with a dark horizon band, 1664x928 like a local-image plate
h, w = 928, 1664
y = np.linspace(0, 1, h)[:, None, None]
sky = (1 - y) * np.array([0.10, 0.12, 0.30]) + y * np.array([0.85, 0.45, 0.25])
img = np.where(y > 0.72, np.array([0.05, 0.04, 0.06]), sky) * np.ones((h, w, 3))
Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(a, "plates", "bg.png"))

# voice stand-in: two tone bursts where the words are, 2.0 s
words = [{"w": "hello", "t0": 0.1, "t1": 0.6}, {"w": "world.", "t0": 0.8, "t1": 1.6}]
t = np.arange(int(2.0 * SR)) / SR
vo = np.zeros_like(t)
for wd, f0 in zip(words, (180, 150)):
    m = (t >= wd["t0"]) & (t < wd["t1"])
    env = np.sin(np.pi * (t[m] - wd["t0"]) / (wd["t1"] - wd["t0"]))
    vo[m] = 0.3 * env * np.sin(2 * np.pi * f0 * t[m]) * (1 + 0.5 * np.sin(2 * np.pi * 3 * f0 * t[m]))
sf.write(os.path.join(a, "vo", "L1.wav"), vo.astype(np.float32), SR, subtype="PCM_24")
with open(os.path.join(a, "vo", "L1.words.json"), "w", encoding="utf-8") as f:
    json.dump(words, f)

# tick: a short decaying click, 0.1 s
tt = np.arange(int(0.1 * SR)) / SR
tick = 0.6 * np.exp(-tt * 60) * np.sin(2 * np.pi * 2000 * tt)
sf.write(os.path.join(a, "sfx", "tick.wav"), tick.astype(np.float32), SR, subtype="PCM_24")
print("wrote", a)

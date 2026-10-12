"""Faithful 4x upscale with Real-ESRGAN x4plus (spandrel + torch; run with local-image's ComfyUI venv).

    PY=~/.claude/skills/local-image/ComfyUI/.venv/Scripts/python.exe
    $PY -I kit/tools/upscale.py IN OUT [--weights PATH] [--out-size 3840x2160] [--tile 256] [--cpu]

The weights (RealESRGAN_x4plus.pth, from the Real-ESRGAN v0.1.0 GitHub release) go in
~/.claude/skills/local-image/ComfyUI/models/upscale_models/_dl_realesrgan/ by default (or --weights). They are
loaded with torch.load(weights_only=True), so no pickled code runs. Tiled with overlap, so it fits beside a loaded
ComfyUI; --tile 512 is faster on the GPU. Optionally resized to an exact delivery size afterwards.
"""
import argparse
import os

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

W_DEFAULT = os.path.expanduser("~/.claude/skills/local-image/ComfyUI/models/upscale_models/_dl_realesrgan/RealESRGAN_x4plus.pth")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--weights", default=W_DEFAULT)
    ap.add_argument("--out-size", help="WxH: resize the 4x result to exactly this (Lanczos)")
    ap.add_argument("--tile", type=int, default=256)
    ap.add_argument("--cpu", action="store_true")
    o = ap.parse_args()
    dev = torch.device("cpu" if o.cpu or not torch.cuda.is_available() else "cuda")
    sd = torch.load(o.weights, map_location="cpu", weights_only=True)
    if "params_ema" in sd:
        sd = sd["params_ema"]
    model = ModelLoader().load_from_state_dict(sd).eval().to(dev)
    s = model.scale
    img = np.asarray(Image.open(o.inp).convert("RGB")).astype(np.float32) / 255
    H, W = img.shape[:2]
    out = np.zeros((H * s, W * s, 3), np.float32)
    wsum = np.zeros((H * s, W * s, 1), np.float32)
    t, pad = o.tile, 16
    for y in range(0, H, t):
        for x in range(0, W, t):
            y0, x0 = max(y - pad, 0), max(x - pad, 0)
            y1, x1 = min(y + t + pad, H), min(x + t + pad, W)
            tin = torch.from_numpy(img[y0:y1, x0:x1].transpose(2, 0, 1))[None].to(dev)
            with torch.no_grad():
                r = model(tin)[0].clamp(0, 1).cpu().numpy().transpose(1, 2, 0)
            h, w = r.shape[:2]
            # feathered weights so tile seams vanish
            wy = np.minimum(np.arange(h) + 1, np.arange(h)[::-1] + 1).astype(np.float32)
            wx = np.minimum(np.arange(w) + 1, np.arange(w)[::-1] + 1).astype(np.float32)
            wt = np.minimum(np.minimum(wy[:, None], 2 * pad * s), np.minimum(wx[None, :], 2 * pad * s))[..., None]
            out[y0 * s:y1 * s, x0 * s:x1 * s] += r * wt
            wsum[y0 * s:y1 * s, x0 * s:x1 * s] += wt
    out = out / np.maximum(wsum, 1e-6)
    im = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
    if o.out_size:
        im = im.resize(tuple(map(int, o.out_size.split("x"))), Image.LANCZOS)
    im.save(o.out)
    print(f"{o.inp} {W}x{H} -> {o.out} {im.size[0]}x{im.size[1]} on {dev}")


if __name__ == "__main__":
    main()

"""Cut a cartoon cel drawing off its plain background, keeping pale insides (skin, hair, gloves, eye whites).

    python kit/tools/cel_matte.py src.png out.png [--pocket 4000] [--tol 26] [--fill] [--crop]

local-image's cutout.py keys on the background colour everywhere, so on inked cel drawings over cream it also cut
out the doll's skin and hair, the hero's face and the white gloves (Puff Ahoy). This floods the background from
the image border instead, so the ink outlines protect everything inside them:

- the ink is thickened 2 px first so the flood can't leak through small gaps in an outline, then the flood grows
  back into the background-coloured fringe (no cream halo);
- enclosed background pockets larger than --pocket px go too (the gaps in a deck chair's frame); eye whites and
  gloves are smaller. The ship's wheel needed --pocket 150 (the gaps between its spokes);
- --tol is the colour distance to the background; a white subject on cream needs a smaller one (the gull: 12);
- --fill fills the outer silhouette instead, for a shape with no holes and thin, gappy outlines (the gull);
- the output keeps the full canvas unless --crop: pose variants made by editing one drawing keep its geometry, so
  full-canvas cels stay aligned when they are swapped like replacement drawings.

Needs numpy, OpenCV and Pillow.
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image


def matte(a, pocket=4000, tol=26.0, fill=False):
    """a: float RGB (h, w, 3) in 0-255. Returns the alpha in [0, 1]."""
    border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3),
                             a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    d = np.sqrt(((a - bg) ** 2).sum(-1))

    ink = cv2.dilate((a.mean(-1) < 110).astype(np.uint8), np.ones((5, 5), np.uint8))
    loose = ((d < tol) & (ink == 0)).astype(np.uint8)
    _, lab, _, _ = cv2.connectedComponentsWithStats(loose, connectivity=4)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(edge))
    for _ in range(2):
        bgm |= (cv2.dilate(bgm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (d < tol)

    tight = ((d < min(12, tol * 0.6)) & ~bgm).astype(np.uint8)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(tight, connectivity=4)
    for i in range(1, n2):
        if st2[i, cv2.CC_STAT_AREA] > pocket:
            bgm |= lab2 == i

    fg = (~bgm).astype(np.uint8)
    if fill:
        m = cv2.morphologyEx(((d >= tol) | (a.mean(-1) < 150)).astype(np.uint8), cv2.MORPH_CLOSE,
                             np.ones((11, 11), np.uint8))
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        fg = np.zeros_like(m)
        cv2.drawContours(fg, [c for c in cnts if cv2.contourArea(c) > 2000], -1, 1, thickness=cv2.FILLED)
    n3, lab3, st3, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if n3 > 1:
        big = st3[1:, cv2.CC_STAT_AREA].max()
        fg = np.isin(lab3, [i for i in range(1, n3) if st3[i, cv2.CC_STAT_AREA] > 0.01 * big]).astype(np.uint8)
    fg = cv2.erode(fg, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 0.8)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--pocket", type=int, default=4000)
    ap.add_argument("--tol", type=float, default=26.0)
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--crop", action="store_true")
    o = ap.parse_args(argv)
    a = np.asarray(Image.open(o.src).convert("RGB")).astype(np.float32)
    al = matte(a, o.pocket, o.tol, o.fill)
    rgba = np.dstack([a, al * 255]).astype(np.uint8)
    ys, xs = np.nonzero(al > 0.5)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    if o.crop:
        rgba = rgba[max(box[1] - 4, 0):box[3] + 4, max(box[0] - 4, 0):box[2] + 4]
    Image.fromarray(rgba, "RGBA").save(o.out)
    print(o.out, "box", box)
    return 0


if __name__ == "__main__":
    sys.exit(main())

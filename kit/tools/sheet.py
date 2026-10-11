"""Lettered contact sheets for checkpoints: one row per subject, a letter in every tile.

    python kit/tools/sheet.py OUT.jpg "Spoon" drafts/c1_spoon -- "Ship" drafts/c1_ship
    python kit/tools/sheet.py OUT.jpg "3-drive" a.png b.png c.png

Each row is a label followed by image files or folders (every *.png in a folder, sorted, cut-out masks and checks
skipped); `--` starts the next row. Tiles are labelled "<first word of the label> A/B/C...", so a pick names one
image ("Spoon B"). Transparent images are shown on a neutral background. Wide images get 16:9 tiles.
Needs Pillow. From Puff Ahoy (2026-10-11), where every checkpoint used it.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SKIP = ("_check.png", "_mask.png", "_cutout.png")


def font(size, bold=False):
    for name in (("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def rows_from(args):
    rows, cur = [], None
    for a in args:
        if a == "--":
            cur = None
            continue
        if cur is None:
            cur = [a, []]
            rows.append(cur)
            continue
        if os.path.isdir(a):
            cur[1] += [f for f in sorted(glob.glob(os.path.join(a, "*.png"))) if not f.endswith(SKIP)]
        else:
            cur[1].append(a)
    return rows


def tile(path, t):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (235, 228, 210, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    im.thumbnail((t * 16 // 9 if im.width > im.height * 1.3 else t, t))
    return im


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 3:
        print(__doc__)
        return 2
    out, rows = argv[0], rows_from(argv[1:])
    T, P, LW = 360, 8, 170
    cells = [[tile(p, T) for p in files] for _, files in rows]
    ncol = max(len(r) for r in cells)
    cw = max(c.width for row in cells for c in row)
    sheet = Image.new("RGB", (LW + ncol * (cw + P) + P, len(rows) * (T + P + 36) + P), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    big, small = font(30, True), font(22)
    for i, ((label, _), row) in enumerate(zip(rows, cells)):
        y = P + i * (T + P + 36)
        d.text((10, y + T // 2 - 15), label, fill="white", font=small)
        for j, im in enumerate(row):
            x = LW + P + j * (cw + P)
            sheet.paste(im, (x, y))
            d.text((x + 6, y + T + 2), f"{label.split()[0]} {chr(65 + j)}", fill=(255, 210, 120), font=big)
    sheet.save(out, quality=90)
    print(out, sheet.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Cut an exploded-view image (flat key-colour background) into one transparent PNG per part.

    cut_parts.py <image> --names a,b,c,d [--grid 2x2] [--key 00FFFF] [--min-area 0.004] [--out DIR]

--grid splits a Gemini grid into cells (left to right, top to bottom; one name per cell). Without it the image is
one cell. In each cell the largest key-colour field is the frame; every connected part inside it becomes
<name>--pN.png (left to right, top to bottom) and <name>.json keeps each part's box in the cell, so the build can
reassemble the object in place and then move the parts apart. See references/layered-scenes.md.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def keyness(a, key):
    """0..1: how close each pixel is to the key colour (distance in RGB, soft edge)"""
    d = np.sqrt(((a - key) ** 2).sum(axis=2)) / 441.7
    return np.clip(1 - d / 0.35, 0, 1)


def frame_box(a, key):
    """box of the largest key-colour field, ignoring grid borders and bits of the neighbouring cells"""
    field = keyness(a, key) > 0.6
    lab, n = ndimage.label(field)
    big = 1 + int(np.argmax(ndimage.sum(field, lab, range(1, n + 1))))
    ys, xs = np.where(ndimage.binary_fill_holes(lab == big))
    return ys.min() + 4, ys.max() - 3, xs.min() + 4, xs.max() - 3


def matte(cell, key):
    a = cell.astype(np.float32)
    alpha = 1 - np.clip((keyness(a, key) - 0.20) / 0.45, 0, 1)
    # despill: the key's strong channels above its weak ones is reflected background; remove it (cyan: G,B over R)
    hi, lo = key > 128, key <= 128
    if hi.any() and lo.any():
        spill = np.clip(a[..., hi].min(axis=2) - a[..., lo].max(axis=2), 0, None)
        a[..., hi] -= spill[..., None]
    return np.dstack([np.clip(a, 0, 255), alpha * 255]).astype(np.uint8)


def cut(cell, name, key, min_area, out):
    y0, y1, x0, x1 = frame_box(cell, key)
    cell = cell[y0:y1, x0:x1]
    rgba = matte(cell, key)
    alpha = rgba[..., 3].astype(np.float32) / 255
    lab, n = ndimage.label(ndimage.binary_closing(alpha > 0.1, iterations=2))
    areas = ndimage.sum(np.ones_like(alpha), lab, range(n + 1))
    boxes = ndimage.find_objects(lab)
    parts = [k for k in range(1, n + 1) if areas[k] > min_area * alpha.size]
    parts.sort(key=lambda k: (round(boxes[k - 1][0].start / (alpha.shape[0] / 3)), boxes[k - 1][1].start))
    meta = {"cell": [int(cell.shape[1]), int(cell.shape[0])], "parts": []}
    for i, k in enumerate(parts, 1):
        ys, xs = boxes[k - 1]
        piece = rgba[ys, xs].copy()
        piece[..., 3] = (piece[..., 3] * (lab[ys, xs] == k)).astype(np.uint8)
        Image.fromarray(piece).save(out / f"{name}--p{i}.png")
        meta["parts"].append({"file": f"{name}--p{i}.png", "x": int(xs.start), "y": int(ys.start),
                              "w": int(xs.stop - xs.start), "h": int(ys.stop - ys.start)})
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1))
    print(name, len(parts), "parts", [(p["w"], p["h"]) for p in meta["parts"]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--names", required=True)
    ap.add_argument("--grid", default="1x1")
    ap.add_argument("--key", default="00FFFF")
    ap.add_argument("--min-area", type=float, default=0.004)
    ap.add_argument("--out", default="parts")
    o = ap.parse_args()
    key = np.array([int(o.key[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
    cols, rows = (int(v) for v in o.grid.lower().split("x"))
    names = o.names.split(",")
    assert len(names) == cols * rows, f"--grid {o.grid} needs {cols * rows} names"
    out = Path(o.out)
    out.mkdir(parents=True, exist_ok=True)
    img = np.asarray(Image.open(o.image).convert("RGB"))
    h, w = img.shape[0] // rows, img.shape[1] // cols
    for i, name in enumerate(names):
        if name in ("", "-"):
            continue
        r, c = divmod(i, cols)
        cut(img[r * h:(r + 1) * h, c * w:(c + 1) * w], name, key, o.min_area, out)


if __name__ == "__main__":
    main()

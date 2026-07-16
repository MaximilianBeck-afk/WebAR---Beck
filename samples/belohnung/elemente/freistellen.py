#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
freistellen.py — deterministisches Freistellen der Higgsfield-Hero-Elemente.

Die Bilder wurden auf einem flachen Solid-Cyan-Hintergrund (#00FFFF) generiert.
Freistellen per Farbdistanz zur Key-Farbe (kein rembg verfuegbar, kein ML noetig
bei einer garantiert flachen Studio-Farbe) + Floodfill von den 4 Ecken, damit
cyan-aehnliche Bildanteile IM Motiv (z.B. hellblaue Konfetti-Stueckchen) nicht
mit entfernt werden. Kanten leicht federn (Anti-Halo), auf enge Bounding-Box
zuschneiden, auf <=1024px Kantenlaenge begrenzen.

Nutzung:
    python3 freistellen.py roh/pokal-01.png cutout/pokal.png
"""
import sys
import os
from PIL import Image, ImageDraw, ImageFilter

KEY = (0, 255, 255)  # cyan Studio-Hintergrund
THRESH = 46          # Floodfill-Toleranz (Farbabstand je Kanal-Summe)
MAX_SIDE = 1024


def color_dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def cutout(src_path):
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    marker = (1, 2, 3)  # unwahrscheinliche Sentinel-Farbe fuer den Floodfill-Fund
    fill = im.copy()
    for seed in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]:
        ImageDraw.floodfill(fill, seed, marker, thresh=THRESH)
    fpx = fill.load()
    spx = im.load()

    rgba = im.convert("RGBA")
    alpha = Image.new("L", (w, h), 255)
    apx = alpha.load()
    for y in range(h):
        for x in range(w):
            if fpx[x, y] == marker:
                apx[x, y] = 0
            else:
                # Rest-Cyan-Saum an Kanten (Anti-Aliasing-Pixel des Renderers)
                d = color_dist(spx[x, y], KEY)
                if d < 60:
                    apx[x, y] = 0
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    rgba.putalpha(alpha)

    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)

    # auf max. Kantenlaenge begrenzen (Payload-Budget)
    rw, rh = rgba.size
    scale = min(1.0, MAX_SIDE / max(rw, rh))
    if scale < 1.0:
        rgba = rgba.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
    return rgba


def main():
    if len(sys.argv) != 3:
        print("Nutzung: python3 freistellen.py <input.png> <output.png>")
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    out = cutout(src)
    out.save(dst)
    print(f"OK  {src} -> {dst}  {out.size}  alpha={'ja' if out.mode == 'RGBA' else 'nein'}")


if __name__ == "__main__":
    main()

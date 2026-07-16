#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
konfetti-teile.py — schneidet aus dem generierten Konfetti-Sheet (viele Einzelteile
auf einem Bild, Cyan-Hintergrund) die einzelnen Partikel als eigene Texturen aus.

Schritte:
  1. Cyan-Hintergrund per Farbdistanz entfernen (gleiche Logik wie freistellen.py).
  2. Zusammenhaengende Komponenten (Connected Components, eigene BFS-Implementierung,
     kein scipy noetig) auf der Alpha-Maske finden.
  3. Je Komponente > MIN_AREA Pixel: enger Zuschnitt + kleiner Rand, als eigenes PNG
     speichern (fuer Vielfalt in der AR-Szene — mehrere <a-plane>-Partikel greifen auf
     eine Auswahl dieser Dateien zurueck).

Nutzung (im molgeo-venv wegen numpy):
    _tools/_venvs/molgeo/bin/python3 konfetti-teile.py roh/konfetti-01.png cutout/konfetti-teile
"""
import sys
import os
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

KEY = np.array([0, 255, 255])
BG_THRESH = 60
MIN_AREA = 250      # Mindestflaeche in Pixel, um Anti-Alias-Krümel auszuschliessen
PAD = 3
MAX_PARTICLES = 18


def load_alpha_mask(src_path):
    im = Image.open(src_path).convert("RGB")
    arr = np.array(im).astype(np.int16)
    dist = np.abs(arr - KEY.reshape(1, 1, 3)).sum(axis=2)
    fg = dist > BG_THRESH  # True = Vordergrund (Partikel)
    return im, arr, fg


def connected_components(fg):
    h, w = fg.shape
    labels = np.zeros((h, w), dtype=np.int32)
    current = 0
    comps = []
    visited = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(w):
            if fg[y, x] and not visited[y, x]:
                current += 1
                q = deque([(y, x)])
                visited[y, x] = True
                pts = []
                while q:
                    cy, cx = q.popleft()
                    pts.append((cy, cx))
                    labels[cy, cx] = current
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and fg[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            q.append((ny, nx))
                comps.append(pts)
    return comps


def main():
    if len(sys.argv) != 3:
        print("Nutzung: konfetti-teile.py <input.png> <out_dir>")
        sys.exit(1)
    src, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    im, arr, fg = load_alpha_mask(src)
    h, w = fg.shape
    comps = connected_components(fg)
    comps = [p for p in comps if len(p) >= MIN_AREA]
    comps.sort(key=len, reverse=True)

    # Vielfalt statt nur der groessten Stuecke: gleichmaessig ueber den Groessenbereich
    # sampeln (grosse Baender UND kleine Sterne/Kreise/Dreiecke landen in der Auswahl).
    if len(comps) > MAX_PARTICLES:
        step = len(comps) / MAX_PARTICLES
        picked = [comps[int(i * step)] for i in range(MAX_PARTICLES)]
    else:
        picked = comps

    rgba_full = im.convert("RGBA")
    # Alpha global: Vordergrund=255, Rest=0 (mit leichtem Federn je Partikel spaeter)
    saved = 0
    for pts in picked:
        if saved >= MAX_PARTICLES:
            break
        ys = [p[0] for p in pts]
        xs = [p[1] for p in pts]
        y0, y1 = max(0, min(ys) - PAD), min(h, max(ys) + PAD + 1)
        x0, x1 = max(0, min(xs) - PAD), min(w, max(xs) + PAD + 1)

        crop = rgba_full.crop((x0, y0, x1, y1))
        crop_arr = np.array(crop)
        # lokale Alpha-Maske: cyan-Distanz je Pixel im Crop
        sub = crop_arr[:, :, :3].astype(np.int16)
        dist = np.abs(sub - KEY.reshape(1, 1, 3)).sum(axis=2)
        alpha = np.where(dist > BG_THRESH, 255, 0).astype(np.uint8)
        crop_arr[:, :, 3] = alpha
        out_im = Image.fromarray(crop_arr, mode="RGBA")
        # Kanten leicht federn
        a_chan = out_im.getchannel("A").filter(ImageFilter.GaussianBlur(0.5))
        out_im.putalpha(a_chan)

        saved += 1
        out_path = os.path.join(out_dir, f"teil-{saved:02d}.png")
        out_im.save(out_path)
        print(f"  {out_path}  {out_im.size}  area={len(pts)}")

    print(f"OK  {saved} Partikel aus {len(comps)} Komponenten gespeichert -> {out_dir}")


if __name__ == "__main__":
    main()

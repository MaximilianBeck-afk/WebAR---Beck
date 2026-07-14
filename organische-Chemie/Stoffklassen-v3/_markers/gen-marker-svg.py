#!/usr/bin/env python3
"""
gen-marker-svg.py — Barcode-Marker als streifenfreie SVG in zwei Farbschemata.
Fix gegen graue Nahtstreifen: EINE durchgehende dunkle Flaeche + nur die hellen Zellen darueber
(keine Dunkel-Dunkel-Kanten mehr). Raster verlustfrei aus dem Quell-PNG (8x8) extrahiert.
Quiet-Zone (2 Zellen) in der hellen Farbe -> selbst-enthaltener Marker.
"""
from PIL import Image
from pathlib import Path
HERE = Path(__file__).parent
CELL_PX = 118; N = 8; QZ = 2                     # 8x8 Raster, 2 Zellen Ruhezone
SCHEMES = {"bw":    {"dark": "#000000", "light": "#FFFFFF"},
           "braun": {"dark": "#241A12", "light": "#F7F1E1"}}

def matrix(png):
    im = Image.open(png).convert("L"); px = im.load()
    M = []
    for r in range(N):
        row = []
        for c in range(N):
            blk = tot = 0
            for yy in range(r*CELL_PX+30, r*CELL_PX+CELL_PX-30, 12):
                for xx in range(c*CELL_PX+30, c*CELL_PX+CELL_PX-30, 12):
                    tot += 1; blk += 1 if px[xx, yy] < 128 else 0
            row.append(1 if blk*2 > tot else 0)          # 1 = dunkel
        M.append(row)
    return M

def svg(M, dark, light):
    V = N + 2*QZ
    out = [f'<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{V}" height="{V}" viewBox="0 0 {V} {V}" shape-rendering="crispEdges">',
           f'  <rect x="0" y="0" width="{V}" height="{V}" fill="{light}"/>',                 # Ruhezone (hell)
           f'  <rect x="{QZ}" y="{QZ}" width="{N}" height="{N}" fill="{dark}"/>']            # durchgehende dunkle Flaeche
    for r in range(N):
        for c in range(N):
            if not M[r][c]:                                                                  # nur helle Zellen zeichnen
                out.append(f'  <rect x="{c+QZ}" y="{r+QZ}" width="1" height="1" fill="{light}"/>')
    out.append('</svg>')
    return "\n".join(out) + "\n"

for mid in ("0", "27"):
    M = matrix(HERE / f"{mid}.png")
    for name, col in SCHEMES.items():
        p = HERE / f"{mid}_{name}.svg"
        p.write_text(svg(M, col["dark"], col["light"]))
        print("SVG:", p.name)

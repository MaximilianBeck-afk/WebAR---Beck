#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-banner.py — baut das transparente Banner-PNG "SUPER GEMACHT!" fuer die
AR-Szene (Layer L3, poppt zuletzt ein). Text ist deterministisch als SVG-Text
gesetzt (NIE aus dem Bildmodell), Schrift Arial Rounded MT Bold (macOS-System-
Font, geprueft vorhanden). Sterne sind Vektor-Polygone.

Export:
    /Applications/Inkscape.app/Contents/MacOS/inkscape banner.svg \
      --export-type=png --export-filename=banner.png
"""
import math

W, H = 1200, 300


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        ang = math.radians(rot + i * 360 / (n * 2))
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def build():
    star_l = star_points(96, 150, 38, 16)
    star_r = star_points(W - 96, 150, 38, 16)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="banner-fill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF6FA0"/>
      <stop offset="100%" stop-color="#FF3D78"/>
    </linearGradient>
  </defs>

  <!-- Banner-Grundform: abgerundete Pille im Sticker-Look (dicker weisser Rand) -->
  <rect x="34" y="34" width="{W - 68}" height="{H - 68}" rx="116" ry="116"
        fill="url(#banner-fill)" stroke="#FFFFFF" stroke-width="20"/>
  <rect x="34" y="34" width="{W - 68}" height="{H - 68}" rx="116" ry="116"
        fill="none" stroke="#B3184F" stroke-width="4" opacity="0.5"/>

  <!-- Sterne links/rechts -->
  <polygon points="{star_l}" fill="#FFD400" stroke="#FFFFFF" stroke-width="7"/>
  <polygon points="{star_r}" fill="#FFD400" stroke="#FFFFFF" stroke-width="7"/>

  <!-- Text: deterministisch, keine KI-Schrift -->
  <text x="{W/2}" y="{H/2 + 34}" text-anchor="middle"
        font-family="Arial Rounded MT Bold, Arial Black, sans-serif"
        font-size="86" fill="#FFFFFF" stroke="#B3184F" stroke-width="6"
        paint-order="stroke" letter-spacing="1">SUPER GEMACHT!</text>
</svg>
'''
    with open("banner.svg", "w") as f:
        f.write(svg)
    print("banner.svg geschrieben", W, H)


if __name__ == "__main__":
    build()

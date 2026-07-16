#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-druck.py — baut karte.svg (A6 Druckkarte) und sticker.svg (runder Sticker)
fuer das Belohnungssticker-Sample. Marker = ID 41 aus der zentralen Registry
(_tools/webar-marker-registry/markers/41_braun.svg), als Inline-Vektor eingebettet
(kein Zwischen-Raster, keine externe Pfadabhaengigkeit beim Druck). Alle Texte
deterministisch als SVG-Text (Arial Rounded MT Bold), keine KI-Schrift.

Export je Datei:
    /Applications/Inkscape.app/Contents/MacOS/inkscape karte.svg \
      --export-type=png --export-dpi=300 --export-filename=karte.png
    /Applications/Inkscape.app/Contents/MacOS/inkscape sticker.svg \
      --export-type=png --export-dpi=300 --export-filename=sticker.png
"""
import re
import os

REGISTRY_MARKER = "/Users/maximilianbeck/Desktop/brain/_tools/webar-marker-registry/markers/41_braun.svg"
OUT_DIR = "/Users/maximilianbeck/Desktop/brain/05_Claude-Output/WebAR/samples/belohnung"

DPI = 300
PX_PER_MM = DPI / 25.4

# Marken-Palette (Belohnungs-Linie): warmer Cream-Grund, Pink/Gold-Akzente
COL_BG        = "#FFF7EA"
COL_BG2       = "#FFEFF6"
COL_TITLE     = "#FF3D78"
COL_TITLE_STR = "#7A1339"
COL_SUB       = "#3A2E22"
COL_ACCENT_A  = "#FFC93C"
COL_ACCENT_B  = "#39C5BB"
COL_ACCENT_C  = "#FF8FB1"


def parse_marker_rects():
    """Liest die 12x12-Rects aus der Registry-SVG (Wahrheitsquelle, nicht kopiert)."""
    with open(REGISTRY_MARKER, "r", encoding="utf-8") as f:
        content = f.read()
    rects = re.findall(
        r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" fill="(#[0-9A-Fa-f]{6})"\s*/>',
        content,
    )
    return rects  # Liste (x,y,w,h,fill) in 12-Einheiten-Koordinaten


def marker_group(rects, size_px, cx, cy):
    """Marker zentriert bei (cx, cy) mit Kantenlaenge size_px, aus 12-Einheiten-Quelle skaliert."""
    scale = size_px / 12.0
    x0 = cx - size_px / 2
    y0 = cy - size_px / 2
    g = [f'<g transform="translate({x0:.2f},{y0:.2f}) scale({scale:.5f})" shape-rendering="crispEdges">']
    for x, y, w, h, fill in rects:
        g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
    g.append("</g>")
    return "\n".join(g)


def image_tag(rel_path, x, y, w, h):
    return f'<image href="{rel_path}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" preserveAspectRatio="xMidYMid meet"/>'


# ---------------------------------------------------------------- karte.svg
def build_karte():
    W, H = 1240, 1748  # A6 @300dpi
    rects = parse_marker_rects()

    marker_mm = 48
    marker_px = marker_mm * PX_PER_MM
    quiet_mm = 11  # zusaetzliche helle Ruhezone rund um den Marker (ueber die im Marker-SVG bereits enthaltene hinaus)
    quiet_px = quiet_mm * PX_PER_MM
    cx, cy = W / 2, H * 0.565

    quiet_size = marker_px + 2 * quiet_px

    svg = []
    svg.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    svg.append(f'''<defs>
    <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{COL_BG}"/>
      <stop offset="100%" stop-color="{COL_BG2}"/>
    </linearGradient>
  </defs>''')

    # Hintergrund + dekorativer Rahmen
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg-grad)"/>')
    svg.append(f'<rect x="26" y="26" width="{W - 52}" height="{H - 52}" rx="46" ry="46" '
                f'fill="none" stroke="{COL_ACCENT_A}" stroke-width="10"/>')
    svg.append(f'<rect x="46" y="46" width="{W - 92}" height="{H - 92}" rx="34" ry="34" '
                f'fill="none" stroke="{COL_ACCENT_C}" stroke-width="4" opacity="0.8"/>')

    # Titel + Untertitel (deterministischer SVG-Text)
    svg.append(f'<text x="{W/2}" y="215" text-anchor="middle" '
                f'font-family="Arial Rounded MT Bold, Arial Black, sans-serif" font-size="112" '
                f'fill="{COL_TITLE}" stroke="{COL_TITLE_STR}" stroke-width="5" paint-order="stroke">'
                f'Belohnungskarte</text>')
    svg.append(f'<text x="{W/2}" y="300" text-anchor="middle" '
                f'font-family="Arial Rounded MT Bold, Arial Black, sans-serif" font-size="54" '
                f'fill="{COL_SUB}">Scannen &amp; feiern!</text>')

    # Kleine Deko-Sterne unter dem Untertitel
    svg.append(f'<circle cx="{W/2 - 260}" cy="330" r="10" fill="{COL_ACCENT_A}"/>')
    svg.append(f'<circle cx="{W/2 + 260}" cy="330" r="10" fill="{COL_ACCENT_A}"/>')

    # Ruhezone (helles Feld) + Marker mittig
    svg.append(f'<rect x="{cx - quiet_size/2:.1f}" y="{cy - quiet_size/2:.1f}" '
                f'width="{quiet_size:.1f}" height="{quiet_size:.1f}" rx="28" ry="28" '
                f'fill="#FFFDF8" stroke="{COL_ACCENT_B}" stroke-width="6"/>')
    svg.append(marker_group(rects, marker_px, cx, cy))

    # Eck-/Rand-Illustrationen (klar ausserhalb der Ruhezone), aus den freigestellten Hero-Assets
    icon_pokal_w, icon_pokal_h = 190, 190 * (905/803)
    svg.append(image_tag("elemente/cutout/pokal.png", 70, H - icon_pokal_h - 90, icon_pokal_w, icon_pokal_h))

    icon_burst_w, icon_burst_h = 170, 170 * (971/876)
    svg.append(image_tag("elemente/cutout/sterneburst.png", W - icon_burst_w - 60, H - icon_burst_h - 100,
                          icon_burst_w, icon_burst_h))

    icon_rak_w, icon_rak_h = 140, 140 * (870/598)
    svg.append(image_tag("elemente/cutout/rakete.png", 60, 360, icon_rak_w, icon_rak_h))

    # ein paar Konfetti-Teilchen verstreut (rein dekorativ, weit weg von der Ruhezone)
    confetti_spots = [
        ("elemente/cutout/konfetti-teile/teil-05.png", W - 170, 380, 70, 71),
        ("elemente/cutout/konfetti-teile/teil-09.png", W - 260, 470, 60, 61),
        ("elemente/cutout/konfetti-teile/teil-13.png", 200, 470, 55, 55),
        ("elemente/cutout/konfetti-teile/teil-03.png", W - 210, H - 260, 82, 102),
    ]
    for rel, x, y, w, h in confetti_spots:
        svg.append(image_tag(rel, x, y, w, h))

    # Fusszeile
    svg.append(f'<text x="{W/2}" y="{H - 60}" text-anchor="middle" '
                f'font-family="Arial Rounded MT Bold, Arial Black, sans-serif" font-size="30" '
                f'fill="{COL_SUB}" opacity="0.75">Marker-ID 41 · AR-Belohnungssticker — Muster</text>')

    svg.append("</svg>")

    path = os.path.join(OUT_DIR, "karte.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("karte.svg geschrieben:", path, f"{W}x{H}px  marker={marker_px:.1f}px (~{marker_mm}mm)")


# ------------------------------------------------------------- sticker.svg
def build_sticker():
    D = 591  # Ø50mm @300dpi
    R = D / 2
    rects = parse_marker_rects()

    marker_mm = 30
    marker_px = marker_mm * PX_PER_MM
    quiet_mm = 4.5
    quiet_px = quiet_mm * PX_PER_MM
    quiet_size = marker_px + 2 * quiet_px
    cx, cy = R, R

    ring_outer = R - 6
    ring_inner = R - 24

    svg = []
    svg.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{D}" height="{D}" viewBox="0 0 {D} {D}">')
    svg.append(f'''<defs>
    <clipPath id="rund"><circle cx="{cx}" cy="{cy}" r="{R - 2}"/></clipPath>
    <linearGradient id="ring-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{COL_ACCENT_C}"/>
      <stop offset="33%" stop-color="{COL_ACCENT_A}"/>
      <stop offset="66%" stop-color="{COL_ACCENT_B}"/>
      <stop offset="100%" stop-color="{COL_TITLE}"/>
    </linearGradient>
  </defs>''')

    # Sticker-Inhalt geclippt auf den Kreis
    svg.append(f'<g clip-path="url(#rund)">')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{COL_BG}"/>')
    # schmaler bunter Zierring aussen
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{ring_outer}" fill="none" '
                f'stroke="url(#ring-grad)" stroke-width="{ring_outer - ring_inner:.1f}"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{ring_inner - 2:.1f}" fill="{COL_BG}"/>')

    # kleine Konfetti-Akzente im Ring-Innenraum (ausserhalb der Marker-Ruhezone)
    accents = [
        ("elemente/cutout/konfetti-teile/teil-15.png", cx - ring_inner + 30, cy - ring_inner + 26, 34, 34),
        ("elemente/cutout/konfetti-teile/teil-17.png", cx + ring_inner - 62, cy - ring_inner + 22, 34, 36),
        ("elemente/cutout/konfetti-teile/teil-11.png", cx - ring_inner + 26, cy + ring_inner - 62, 40, 41),
        ("elemente/cutout/konfetti-teile/teil-08.png", cx + ring_inner - 64, cy + ring_inner - 62, 38, 42),
    ]
    for rel, x, y, w, h in accents:
        svg.append(image_tag(rel, x, y, w, h))

    # Ruhezone + Marker mittig
    svg.append(f'<rect x="{cx - quiet_size/2:.1f}" y="{cy - quiet_size/2:.1f}" '
                f'width="{quiet_size:.1f}" height="{quiet_size:.1f}" rx="14" ry="14" fill="#FFFDF8"/>')
    svg.append(marker_group(rects, marker_px, cx, cy))

    svg.append("</g>")  # Ende Clip

    # dekorativer Aussenrand (Druckkante, sichtbar)
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 2}" fill="none" stroke="#FFFFFF" stroke-width="4"/>')

    # Schnittkontur als EIGENER Pfad/Layer (fuer den Druckdienstleister, nicht sichtbar eingefaerbt)
    svg.append(f'<g id="schnittkontur" data-role="cut-line">')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 0.5:.1f}" fill="none" stroke="#FF00FF" stroke-width="0.75"/>')
    svg.append(f'</g>')

    svg.append("</svg>")

    path = os.path.join(OUT_DIR, "sticker.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("sticker.svg geschrieben:", path, f"{D}x{D}px  marker={marker_px:.1f}px (~{marker_mm}mm)")


if __name__ == "__main__":
    build_karte()
    build_sticker()

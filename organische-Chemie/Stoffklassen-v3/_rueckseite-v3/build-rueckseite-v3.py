#!/usr/bin/env python3
"""
build-rueckseite-v3.py — Karten-Rückseite (A6, 1240x1748) aus den vektorisierten
Canva-v3-Ornamenten: zentraler Hexagon-Rahmen UM den QR, Banner oben/unten mit Text.
Ecken bewusst weggelassen (User, Sitzung 171). QR = echter AR-Link (segno, EC-H).

Ornamente werden als Inline-Vektor eingebettet (potrace-<g> mit Platzierungs-Transform).
Deterministisch; Text im SVG (nicht aus einem Bildmodell). Export via Inkscape.

Usage:
  python3 build-rueckseite-v3.py --url "https://…/organische-Chemie/v3/"
"""
import argparse, re, subprocess
from pathlib import Path
import segno

def est_width(s, f, bold=False):
    w = 0.0
    for ch in s:
        if ch == " ": w += 0.30*f
        elif ch in "·.": w += 0.40*f
        elif ch.isupper() or ch.isdigit(): w += (0.66 if bold else 0.60)*f
        else: w += (0.56 if bold else 0.50)*f
    return w

def fit_font(s, maxw, start, minf, ls=0, bold=False):
    f = start
    while f > minf and est_width(s, f, bold) + max(0, len(s)-1)*ls > maxw:
        f -= 1
    return f

HERE = Path(__file__).parent
INK = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
W, H = 1240, 1748
PERG = "#F7F1E1"; PANEL = "#FBF7EC"; BRONZE = "#7A5A32"; DARK = "#241A12"; TEXT = "#3A2E1E"; GOLD = "#C9A24B"

def ornament_group(svg_path, tx, ty, tw, th):
    """potrace-SVG einbetten: inneres <g fill=…>…</g> extrahieren, in Zielbox skalieren/verschieben."""
    s = Path(svg_path).read_text()
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s)
    ow, oh = float(m.group(1)), float(m.group(2))
    g = re.search(r'(<g\s+transform=.*?</g>)', s, re.S).group(1)
    scale = min(tw/ow, th/oh)
    # zentrieren in der Box
    ox = tx + (tw - ow*scale)/2
    oy = ty + (th - oh*scale)/2
    return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({scale:.5f})">{g}</g>', (ow*scale, oh*scale, ox, oy)

def qr_group(url, cx, cy, target):
    """QR (EC-H) als dunkelbraune Module, zentriert auf (cx,cy), Kantenlänge ~target px."""
    q = segno.make(url, error="h")
    mat = [list(row) for row in q.matrix]
    n = len(mat)
    mod = target / n
    x0 = cx - target/2; y0 = cy - target/2
    rects = [f'<rect x="{x0+c*mod:.2f}" y="{y0+r*mod:.2f}" width="{mod:.2f}" height="{mod:.2f}" fill="{DARK}"/>'
             for r in range(n) for c in range(n) if mat[r][c]]
    return "\n".join(rects), target

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://maximilianbeck-afk.github.io/WebAR---Beck/organische-Chemie/v3/")
    ap.add_argument("--top-text", default="3D-MODELL SCANNEN")
    ap.add_argument("--bottom-text", default="WebAR · kein App-Download nötig")
    a = ap.parse_args()

    # --- Platzierung ---
    banner_oben, _ = ornament_group(HERE/"ornament-banner-oben.svg", tx=240, ty=118, tw=760, th=300)
    frame, (fw, fh, fx, fy) = ornament_group(HERE/"ornament-zentral.svg", tx=255, ty=468, tw=730, th=740)
    banner_unten, _ = ornament_group(HERE/"ornament-banner-unten.svg", tx=270, ty=1338, tw=700, th=316)

    # QR + Pergament-Panel in die Mitte des Rahmens (Panel = Ruhezone ≥ 4 Module)
    cx, cy = fx + fw/2, fy + fh/2
    qr_target = min(fw, fh) * 0.56          # etwas kleiner → mehr Ruhezone innerhalb der Öffnung
    panel = qr_target * 1.24
    qr_rects, _ = qr_group(a.url, cx, cy, qr_target)

    # Text-Positionen (in den Banner-Namensschildern) + Auto-Fit auf die Schild-Breite
    top_cy = 118 + 300/2
    bot_cy = 1338 + 316/2
    top_ls = 2
    top_fs = fit_font(a.top_text, maxw=470, start=48, minf=26, ls=top_ls, bold=True)
    bot_fs = fit_font(a.bottom_text, maxw=520, start=34, minf=22, ls=0, bold=False)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="105mm" height="148mm" viewBox="0 0 {W} {H}">
  <rect x="0" y="0" width="{W}" height="{H}" fill="{PERG}"/>
  <rect x="30" y="30" width="{W-60}" height="{H-60}" rx="26" ry="26" fill="none" stroke="{BRONZE}" stroke-width="4" opacity="0.55"/>
  <rect x="46" y="46" width="{W-92}" height="{H-92}" rx="18" ry="18" fill="none" stroke="{GOLD}" stroke-width="1.5" opacity="0.5"/>

  <!-- Kopfzeile -->
  <text x="{W/2}" y="96" text-anchor="middle" font-family="Georgia, serif" font-size="25" letter-spacing="7" fill="{BRONZE}">ORGANISCHE CHEMIE &#183; SAMMELKARTE</text>

  <!-- Banner oben + Text -->
  {banner_oben}
  <text x="{W/2}" y="{top_cy+top_fs*0.34:.0f}" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="{top_fs}" letter-spacing="{top_ls}" fill="{TEXT}">{a.top_text}</text>

  <!-- Zentraler Hexagon-Rahmen mit QR -->
  <rect x="{cx-panel/2:.1f}" y="{cy-panel/2:.1f}" width="{panel:.1f}" height="{panel:.1f}" rx="24" ry="24" fill="{PANEL}" stroke="{GOLD}" stroke-width="2" opacity="0.95"/>
  {qr_rects}
  {frame}

  <!-- Banner unten + Text -->
  {banner_unten}
  <text x="{W/2}" y="{bot_cy+bot_fs*0.34:.0f}" text-anchor="middle" font-family="Georgia, serif" font-size="{bot_fs}" fill="{TEXT}">{a.bottom_text}</text>

  <!-- Fußhinweis -->
  <text x="{W/2}" y="{H-64}" text-anchor="middle" font-family="Georgia, serif" font-size="22" fill="{BRONZE}">Handykamera öffnen — das Molekül erscheint in 3D über der Karte.</text>
</svg>
'''
    out_svg = HERE/"rueckseite-v3.svg"; out_svg.write_text(svg)
    print("SVG:", out_svg)
    png = HERE/"rueckseite-v3.png"
    r = subprocess.run([INK, str(out_svg), "--export-type=png", f"--export-filename={png}",
                        "--export-width=1240", "--export-height=1748"], capture_output=True, text=True)
    if r.returncode != 0:
        print("Inkscape-Fehler:\n"+r.stderr[:800]); return
    print("PNG:", png)

if __name__ == "__main__":
    main()

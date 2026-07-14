#!/usr/bin/env python3
"""
build-card.py — erzeugt eine finale Sammelkarte (M1 Monopoli klassisch) aus
card-data.json + Woodblock-Kunstbild, als SVG -> Inkscape-PNG (A6 1240x1748 @300dpi).

Template = Sieger-Layout M1 (Sitzung 168), parametrisiert. EIN Ort für alle 39 Karten.
Nur die Blau-Familie leitet sich aus der Stoffklassen-Akzentfarbe ab; Gold/Pergament fix.

Usage:
  python3 build-card.py --data card-data.json --slug ethanol \
      --art <woodblock.png> --out <ordner> [--no-render]
Inkscape (nicht im PATH): /Applications/Inkscape.app/Contents/MacOS/inkscape
"""
import argparse, hashlib, json, math, random, subprocess, sys
from pathlib import Path

INKSCAPE = "/Applications/Inkscape.app/Contents/MacOS/inkscape"

# Pro-Karte-Fingerabdruck fürs AR-Tracking: eindeutiges GUILLOCHÉ-Muster aus feinen Linien
# (kontrastreiche Kanten/Kreuzungen = starke, unterscheidbare Tracking-Features; „mystisch",
# dezent). Deterministisch aus dem slug geseedet -> jede Karte ein eigenes Muster.
PAT_OPACITY = 0.20   # Deckkraft der Musterebene (Trennschärfe vs. Dezenz). Tunable.
PAT_CURVES = 7       # Anzahl überlagerter Rosetten-Kurven

def texture_svg(slug, accent):
    rnd = random.Random(int(hashlib.md5(slug.encode()).hexdigest()[:8], 16))
    col = scale(accent, 0.42)  # dunkle Variante der Klassenfarbe
    out = [f'<g opacity="{PAT_OPACITY}" fill="none" stroke="{col}">']
    cx, cy = 620, 874
    for _ in range(PAT_CURVES):
        k = rnd.randint(3, 9)                      # Blütenblätter
        A = rnd.uniform(430, 900)                  # Amplitude (reicht in die Ränder)
        ph = rnd.uniform(0, 2*math.pi)
        ox = cx + rnd.uniform(-130, 130); oy = cy + rnd.uniform(-190, 190)
        period = rnd.choice([1, 2, 2, 3])
        sw = rnd.uniform(0.6, 1.05)
        steps = 900
        pts = []
        for i in range(steps + 1):
            th = 2*math.pi*period*i/steps
            r = A*math.cos(k*th + ph)
            pts.append(f"{ox + r*math.cos(th):.1f},{oy + r*math.sin(th):.1f}")
        out.append(f'<polyline points="{" ".join(pts)}" stroke-width="{sw:.2f}"/>')
    # ein paar exzentrische Kreise für zusätzliche Kreuzungs-Features
    for _ in range(rnd.randint(2, 4)):
        out.append(f'<circle cx="{cx+rnd.uniform(-200,200):.0f}" cy="{cy+rnd.uniform(-260,260):.0f}" '
                   f'r="{rnd.uniform(300,760):.0f}" stroke-width="{rnd.uniform(0.5,0.9):.2f}"/>')
    out.append('</g>')
    return "".join(out)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def hx(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)

def to_rgb(h):
    h = h.lstrip("#"); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def scale(h, f):
    return hx(tuple(c*f for c in to_rgb(h)))

def formula_tspans(s, small, dy):
    """Digits -> Subscript (dy-Technik). small = Subscript-Größe, dy = Absenkung."""
    out, shifted = [], False
    for ch in s:
        if ch.isdigit():
            if not shifted:
                out.append(f'<tspan font-size="{small}" dy="{dy}">{ch}</tspan>'); shifted = True
            else:
                out.append(f'<tspan font-size="{small}">{ch}</tspan>')
        else:
            if shifted:
                out.append(f'<tspan dy="-{dy}">{esc(ch)}</tspan>'); shifted = False
            else:
                out.append(f'<tspan>{esc(ch)}</tspan>')
    return "".join(out)

def est_width(s, F):
    """Grobe Pixelbreite der Formelzeile bei Basis-Schriftgröße F."""
    w = 0.0
    for ch in s:
        if ch.isdigit(): w += 0.42 * F
        elif ch in "–-•": w += 0.50 * F
        elif ch in "=≡": w += 0.55 * F
        else: w += 0.60 * F
    return w

def wrap_two(items):
    """Items an ' · '-Grenzen auf <=2 Zeilen verteilen, balanciert
    (minimiert die längere Zeile; bei Gleichstand Zeile 1 länger)."""
    n = len(items)
    if n == 1:
        return items[0], ""
    best = None
    for k in range(1, n):
        l1 = " · ".join(items[:k]); l2 = " · ".join(items[k:])
        score = max(len(l1), len(l2))
        if best is None or score < best[0] or (score == best[0] and len(l1) > len(best[1])):
            best = (score, l1, l2)
    return best[1], best[2]

def build_svg(m):
    acc = m["accent"]
    dark = scale(acc, 0.66)
    band_top = scale(acc, 1.16)
    band_bot = scale(acc, 0.83)
    art = m["art"].replace("&", "&amp;")
    marker = m["marker"].replace("&", "&amp;")
    same = m["halbstruktur"] == m["formel"]
    raw = m["formel"] if same else m["formel"] + "  ·  " + m["halbstruktur"]
    ff = 44.0
    w = est_width(raw, ff)
    maxw = 1080.0
    if w > maxw:
        ff = max(28.0, 44.0 * maxw / w)
    ff = int(round(ff))
    small = int(round(ff * 0.68))
    dy = max(7, int(round(small * 0.40)))
    formel = formula_tspans(m["formel"], small, dy)
    if same:
        formel_line = formel
    else:
        halb = formula_tspans(m["halbstruktur"], small, dy)
        formel_line = formel + f'<tspan font-size="{small}">&#160;&#160;&#8226;&#160;&#160;</tspan>' + halb
    mk1, mk2 = wrap_two(m["merkmale"])
    vw1, vw2 = wrap_two(m["verwendung"])
    tex = texture_svg(m["slug"], acc) if m.get("texture") else ""
    name = esc(m["name"])
    klasse = esc(m["klasse"]).upper()
    pos, tot = m["pos"], m["tot"]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="105mm" height="148mm" viewBox="0 0 1240 1748">
  <defs>
    <clipPath id="imgClip"><rect x="192" y="342" width="856" height="856" rx="10" ry="10"/></clipPath>
    <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{band_top}"/><stop offset="1" stop-color="{band_bot}"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="1240" height="1748" fill="#F7F1E1"/>
  <rect x="30" y="30" width="1180" height="1688" rx="26" ry="26" fill="#FBF7EC" stroke="{dark}" stroke-width="7"/>
  <rect x="50" y="50" width="1140" height="1648" rx="16" ry="16" fill="none" stroke="{acc}" stroke-width="3"/>
  <rect x="60" y="60" width="1120" height="1628" rx="12" ry="12" fill="none" stroke="#C9A24B" stroke-width="1.5" opacity="0.55"/>
  {tex}
  <rect x="74" y="76" width="1092" height="214" rx="12" ry="12" fill="url(#bandGrad)"/>
  <rect x="86" y="88" width="1068" height="190" rx="8" ry="8" fill="none" stroke="#E9D8A6" stroke-width="1.5" opacity="0.6"/>
  <text x="620" y="134" text-anchor="middle" font-family="Georgia, serif" font-size="25" letter-spacing="7" fill="#DCEBF5">ORGANISCHE CHEMIE &#183; SAMMELKARTE</text>
  <line x1="466" y1="152" x2="774" y2="152" stroke="#C9A24B" stroke-width="1.5" opacity="0.85"/>
  <text x="620" y="248" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="84" letter-spacing="9" fill="#FFFFFF">{klasse}</text>
  <circle cx="1112" cy="140" r="40" fill="#FBF7EC" stroke="{dark}" stroke-width="4"/>
  <text x="1112" y="138" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="40" fill="{dark}">{pos}</text>
  <text x="1112" y="166" text-anchor="middle" font-family="Georgia, serif" font-size="18" fill="{acc}">/ {tot}</text>
  <rect x="170" y="320" width="900" height="900" rx="20" ry="20" fill="#FFFFFF" stroke="{dark}" stroke-width="5"/>
  <rect x="182" y="332" width="876" height="876" rx="14" ry="14" fill="none" stroke="{acc}" stroke-width="2" opacity="0.7"/>
  <image x="192" y="342" width="856" height="856" clip-path="url(#imgClip)" preserveAspectRatio="xMidYMid slice" xlink:href="{art}"/>
  <circle cx="170" cy="320" r="9" fill="#C9A24B"/><circle cx="1070" cy="320" r="9" fill="#C9A24B"/>
  <circle cx="170" cy="1220" r="9" fill="#C9A24B"/><circle cx="1070" cy="1220" r="9" fill="#C9A24B"/>
  <text x="620" y="1318" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="92" fill="{dark}">{name}</text>
  <text x="620" y="1368" text-anchor="middle" font-family="Georgia, serif" font-size="{ff}" fill="#3A2E1E">{formel_line}</text>
  <line x1="95" y1="1400" x2="852" y2="1400" stroke="{acc}" stroke-width="2" opacity="0.6"/>
  <rect x="95" y="1408" width="228" height="46" rx="23" ry="23" fill="{acc}"/>
  <text x="209" y="1439" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="26" letter-spacing="3" fill="#FFFFFF">MERKMALE</text>
  <text x="95" y="1498" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(mk1)}</text>
  <text x="95" y="1536" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(mk2)}</text>
  <rect x="95" y="1552" width="262" height="46" rx="23" ry="23" fill="{dark}"/>
  <text x="226" y="1583" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="26" letter-spacing="3" fill="#FFFFFF">VERWENDUNG</text>
  <text x="95" y="1642" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(vw1)}</text>
  <text x="95" y="1680" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(vw2)}</text>
  <rect x="871" y="1385" width="295" height="295" rx="14" ry="14" fill="#FFFFFF" stroke="{acc}" stroke-width="3"/>
  <image x="907" y="1421" width="223" height="223" image-rendering="pixelated" style="image-rendering:pixelated;image-rendering:crisp-edges" preserveAspectRatio="xMidYMid meet" xlink:href="{marker}"/>
</svg>
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--art", required=True)
    ap.add_argument("--marker", required=True, help="Barcode-Marker-PNG (4x4_BCH_13_9_3)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--texture", action="store_true", help="Pro-Karte-Mikro-Muster fürs AR-Tracking (v2)")
    a = ap.parse_args()
    data = json.loads(Path(a.data).read_text())
    m = next((x for x in data["karten"] if x["slug"] == a.slug), None)
    if not m:
        print(f"slug {a.slug} nicht in {a.data}", file=sys.stderr); sys.exit(1)
    m = dict(m); m["art"] = str(Path(a.art).resolve()); m["marker"] = str(Path(a.marker).resolve()); m["texture"] = a.texture
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    svg = out / f"{a.slug}.svg"; png = out / f"{a.slug}.karte.png"
    svg.write_text(build_svg(m))
    print(f"SVG: {svg}")
    if not a.no_render:
        r = subprocess.run([INKSCAPE, str(svg), "--export-type=png",
                            f"--export-filename={png}", "--export-width=1240", "--export-height=1748"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("Inkscape-Fehler:\n" + r.stderr[:600], file=sys.stderr); sys.exit(1)
        print(f"PNG: {png}")

if __name__ == "__main__":
    main()

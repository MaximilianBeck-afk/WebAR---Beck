#!/usr/bin/env python3
"""
build-ornament-zentral-v2-1.py — Weiterentwicklung von v2.1 (Hybrid).

  ornament-zentral-v2.1.1.svg  saubere Ecken (durchgehendes Guilloche-Band mit
                               runden Ecken, klare Eck-Rosetten)
  ornament-zentral-v2.1.2.svg  Chemie IN den Ringen (RDKit: Aromat/Doppelbindung,
                               Keto, Hydroxy, ... gemischt -> stoffgruppen-neutral)
  _v2-previews/v2.1.1.png / v2.1.2.png

venv: /Users/maximilianbeck/Desktop/brain/_tools/_venvs/molgeo/bin/python
"""
import math, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE / "_v2-previews"; PREV.mkdir(exist_ok=True)
INK = "/Applications/Inkscape.app/Contents/MacOS/inkscape"

SIZE = 720
GOLD = "#C9A24B"
BRONZE = "#7A5A32"
PERG = "#F7F1E1"

# ---------- Helfer ----------
def hexagon(cx, cy, R, pointy=True, w=2.0, col=GOLD):
    pts = [(cx + R*math.cos(math.radians(60*k + (90 if pointy else 0))),
            cy + R*math.sin(math.radians(60*k + (90 if pointy else 0)))) for k in range(6)]
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"/>'

def hex_row(a, b, const, pointy, R=25, w=2.0):
    out, step = [], R*math.sqrt(3)
    t = a
    while t <= b + 0.1:
        out.append(hexagon(t, const, R, True, w) if pointy else hexagon(const, t, R, False, w))
        t += step
    return out

def circle(cx, cy, r, w=2.0, col=GOLD, fill="none"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="{w}"/>'

def rrect(x, y, wd, ht, rad, w, col=GOLD):
    return f'<rect x="{x}" y="{y}" width="{wd}" height="{ht}" rx="{rad}" ry="{rad}" fill="none" stroke="{col}" stroke-width="{w}"/>'

def rounded_rect_walk(P, rr, step=2.0):
    """Punkte + Aussen-Normale entlang eines abgerundeten Rechtecks."""
    x0, x1 = P + rr, SIZE - P - rr
    y0, y1 = P + rr, SIZE - P - rr
    pts = []
    x = x0
    while x <= x1: pts.append((x, P, 0, -1)); x += step
    da = step / rr * 57.29578
    a = -90
    while a <= 0: r = math.radians(a); pts.append((x1+rr*math.cos(r), y0+rr*math.sin(r), math.cos(r), math.sin(r))); a += da
    y = y0
    while y <= y1: pts.append((SIZE-P, y, 1, 0)); y += step
    a = 0
    while a <= 90: r = math.radians(a); pts.append((x1+rr*math.cos(r), y1+rr*math.sin(r), math.cos(r), math.sin(r))); a += da
    x = x1
    while x >= x0: pts.append((x, SIZE-P, 0, 1)); x -= step
    a = 90
    while a <= 180: r = math.radians(a); pts.append((x0+rr*math.cos(r), y1+rr*math.sin(r), math.cos(r), math.sin(r))); a += da
    y = y1
    while y >= y0: pts.append((P, y, -1, 0)); y -= step
    a = 180
    while a <= 270: r = math.radians(a); pts.append((x0+rr*math.cos(r), y0+rr*math.sin(r), math.cos(r), math.sin(r))); a += da
    return pts

def guilloche_loop(P=168, rr=46, amp=8.5, target_lam=46, w=1.3, col=GOLD):
    """durchgehendes Flechtband (zwei Straenge) mit runden Ecken, nahtlos."""
    pts = rounded_rect_walk(P, rr)
    # Bogenlaenge
    s, S = [0.0], 0.0
    for i in range(1, len(pts)):
        S += math.dist(pts[i][:2], pts[i-1][:2]); s.append(S)
    L = S + math.dist(pts[0][:2], pts[-1][:2])
    n = max(1, round(L / target_lam)); lam = L / n
    strands = []
    for phase in (0.0, math.pi):
        d = []
        for (x, y, nx, ny), si in zip(pts, s):
            o = amp*math.sin(2*math.pi*si/lam + phase)
            d.append((x+nx*o, y+ny*o))
        path = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in d) + " Z"
        strands.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}"/>')
    return strands

def corner_rosette(cx, cy, inx, iny):
    """klare Ecke: Atom-Knoten + eine diagonal einwaerts zeigende Sechseck-Rosette."""
    e = [circle(cx, cy, 6.5, 2.0, GOLD)]
    e.append(hexagon(cx + inx*22, cy + iny*22, 17, True, 1.9, GOLD))
    e.append(f'<line x1="{cx+inx*8:.1f}" y1="{cy+iny*8:.1f}" x2="{cx+inx*13:.1f}" y2="{cy+iny*13:.1f}" stroke="{GOLD}" stroke-width="1.8"/>')
    return e

def frame_lines():
    return [rrect(40, 40, SIZE-80, SIZE-80, 26, 2.6),
            rrect(198, 198, SIZE-396, SIZE-396, 16, 1.8)]

def hex_border(R=25, w=2.0):
    e = []
    e += hex_row(150, 570, 100, True, R, w)
    e += hex_row(150, 570, 620, True, R, w)
    e += hex_row(150, 570, 100, False, R, w)
    e += hex_row(150, 570, 620, False, R, w)
    return e

def corners():
    return (corner_rosette(70, 70, 1, 1) + corner_rosette(650, 70, -1, 1)
            + corner_rosette(70, 650, 1, -1) + corner_rosette(650, 650, -1, -1))

def svg_wrap(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}pt" height="{SIZE}pt" '
            f'viewBox="0 0 {SIZE} {SIZE}">\n' + "\n".join(body) + "\n</svg>\n")

# ---------- RDKit ----------
def rdkit_group(smiles, px=190, col=BRONZE, lw=2):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem.Draw import rdMolDraw2D
    m = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(m)
    d = rdMolDraw2D.MolDraw2DSVG(px, px)
    o = d.drawOptions()
    o.clearBackground = False
    o.bondLineWidth = lw
    o.useBWAtomPalette()
    d.DrawMolecule(m)
    d.FinishDrawing()
    svg = d.GetDrawingText()
    inner = svg[svg.index('>', svg.index('<svg')) + 1: svg.rindex('</svg>')]
    for black in ("#000000", "#000", "black"):
        inner = inner.replace(black, col)
    inner = inner.replace("fill:#FFFFFF", "fill:none").replace("fill:#ffffff", "fill:none")
    return inner, px

def adamantan_medaillons():
    mol, px = rdkit_group("C1C2CC3CC1CC(C2)C3", px=200)
    e = []
    for (mx, my) in [(360, 100), (360, 620)]:
        e.append(f'<circle cx="{mx}" cy="{my}" r="46" fill="{PERG}" stroke="{GOLD}" stroke-width="2.4"/>')
        e.append(f'<g transform="translate({mx},{my}) scale(0.42) translate({-px/2},{-px/2})">{mol}</g>')
    return e

# ---------- Variante 2.1.1: saubere Ecken ----------
def variant_211():
    body = frame_lines() + hex_border() + guilloche_loop() + corners() + adamantan_medaillons()
    return svg_wrap(body)

# ---------- Variante 2.1.2: Chemie in den Ringen ----------
def variant_212():
    body = frame_lines()
    # gemischte funktionelle Ringe (neutral, weil gemischt): Aromat, Keto, Hydroxy, En, Diol, Aldehyd
    motifs = [
        ("c1ccccc1",      "arom"),   # Aromat (Doppelbindungen)
        ("O=C1CCCCC1",    "keto"),   # Ketogruppe
        ("OC1CCCCC1",     "hydroxy"),# Hydroxygruppe
        ("C1CCC=CC1",     "en"),     # Ring-Doppelbindung
        ("OC1CCCCC1O",    "diol"),   # zwei Hydroxy
        ("O=CC1CCCCC1",   "aldehyd"),# Aldehyd am Ring
    ]
    defs = ['<defs>']
    for smi, tag in motifs:
        inner, px = rdkit_group(smi, px=170)
        defs.append(f'<g id="m_{tag}"><g transform="translate({-px/2},{-px/2})">{inner}</g></g>')
    defs.append('</defs>')
    body = defs + body
    scale = 0.34
    xs = list(range(150, 571, 84))   # 6 Positionen je Seite
    def place(x, y, i):
        tag = motifs[i % len(motifs)][1]
        body.append(f'<use href="#m_{tag}" transform="translate({x},{y}) scale({scale})"/>')
    i = 0
    for x in xs: place(x, 100, i); i += 1
    for y in xs: place(620, y, i); i += 1
    for x in reversed(xs): place(x, 620, i); i += 1
    for y in reversed(xs): place(100, y, i); i += 1
    body += guilloche_loop() + corners() + adamantan_medaillons()
    return svg_wrap(body)

# ---------- Vorschau ----------
def preview(svg_path, png_path):
    t = svg_path.read_text()
    inner = t[t.index('>', t.index('<svg'))+1: t.rindex('</svg>')]
    wrap = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<rect width="{SIZE}" height="{SIZE}" fill="{PERG}"/>'
            f'<rect x="228" y="228" width="264" height="264" fill="#e9e0c8"/>'
            f'<text x="360" y="368" font-family="monospace" font-size="20" fill="#9a8a63" text-anchor="middle">QR</text>'
            f'{inner}</svg>')
    tmp = png_path.with_suffix(".tmp.svg"); tmp.write_text(wrap)
    subprocess.run([INK, str(tmp), "--export-type=png", f"--export-filename={png_path}", "-w", "720", "-h", "720"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp.unlink()

def main():
    out = {"ornament-zentral-v2.1.1.svg": variant_211(),
           "ornament-zentral-v2.1.2.svg": variant_212()}
    for name, svg in out.items():
        p = HERE / name; p.write_text(svg)
        png = PREV / (name.replace("ornament-zentral-", "").replace(".svg", ".png"))
        preview(p, png)
        print(f"OK {name} ({len(svg)} B) -> {png.name}")

if __name__ == "__main__":
    main()

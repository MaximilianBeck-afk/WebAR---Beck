#!/usr/bin/env python3
"""
build-ornament-zentral-v2.py — drei deterministische Neubauten des zentralen
QR-Rahmen-Ornaments, strich-basiert (kein potrace-Silhouetten-Trace).

Erzeugt in DIESEM Ordner (_rueckseite-v3):
  ornament-zentral-v2.1.svg  Hybrid   (Sechseck-Kette + Guilloche + RDKit-Medaillon)
  ornament-zentral-v2.2.svg  Geometrisch (Sechseck-Kette + Guilloche, keine Formeln)
  ornament-zentral-v2.3.svg  RDKit    (echte neutrale Skelettformeln als Motiv)
  _v2-previews/v2.1.png v2.2.png v2.3.png  (Pergament + Platzhalter-QR)

Laeuft im RDKit-venv: /Users/maximilianbeck/Desktop/brain/_tools/_venvs/molgeo/bin/python
Neutralitaet: nur Kohlenwasserstoffe/Aromaten (verraten keine Stoffgruppe).
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

# ---------- Geometrie-Helfer ----------
def hexagon(cx, cy, R, pointy=True, w=2.0, col=GOLD):
    pts = []
    for k in range(6):
        ang = math.radians(60*k + (90 if pointy else 0))
        pts.append((cx + R*math.cos(ang), cy + R*math.sin(ang)))
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"/>'

def hex_row(x0, x1, y, R, pointy, w=2.0):
    """fusionierte Sechseck-Kette entlang einer Achse (horizontal wenn pointy)."""
    out = []
    step = R*math.sqrt(3)
    if pointy:
        x = x0
        while x <= x1 + 0.1:
            out.append(hexagon(x, y, R, True, w))
            x += step
    else:
        yv = x0
        while yv <= x1 + 0.1:
            out.append(hexagon(y, yv, R, False, w))
            yv += step
    return out

def guilloche_line(a, b, const, horizontal, amp, lam, w=1.4, col=GOLD):
    """zwei phasenverschobene Sinusstraenge -> Flechtband."""
    strands = []
    for phase in (0.0, math.pi):
        pts = []
        t = a
        n = 0
        while t <= b + 0.1:
            off = amp*math.sin(2*math.pi*(t-a)/lam + phase)
            if horizontal:
                pts.append((t, const + off))
            else:
                pts.append((const + off, t))
            t += 4; n += 1
        d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        strands.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}"/>')
    return strands

def circle(cx, cy, r, w=2.0, col=GOLD, fill="none"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="{w}"/>'

def rrect(x, y, wd, ht, rad, w, col=GOLD):
    return f'<rect x="{x}" y="{y}" width="{wd}" height="{ht}" rx="{rad}" ry="{rad}" fill="none" stroke="{col}" stroke-width="{w}"/>'

# ---------- RDKit ----------
def rdkit_group(smiles, px=220, col=BRONZE, lw=2):
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
    # RDKit-Schwarz auf unsere Farbe umsetzen, Hintergrundrechteck entfernen
    for black in ("#000000", "#000", "black"):
        inner = inner.replace(black, col)
    # RDKit setzt evtl. ein fill:#FFFFFF Rechteck -> unsichtbar machen
    inner = inner.replace("fill:#FFFFFF", "fill:none").replace("fill:#ffffff", "fill:none")
    return inner, px

# ---------- Rahmen-Grundgeruest (geometrisch) ----------
def frame_lines():
    e = []
    e.append(rrect(40, 40, SIZE-80, SIZE-80, 26, 2.6))          # aeusserer Rahmen
    e.append(rrect(190, 190, SIZE-380, SIZE-380, 16, 1.8))      # innerer QR-Rand
    return e

def hex_border(R=25, w=2.0):
    e = []
    e += hex_row(120, 600, 100, R, True, w)     # oben
    e += hex_row(120, 600, 620, R, True, w)     # unten
    e += hex_row(120, 600, 100, R, False, w)    # links (pointy=False -> vertikal, y=100 ist x)
    e += hex_row(120, 600, 620, R, False, w)    # rechts
    return e

def guilloche_border(amp=9, lam=54, w=1.3):
    e = []
    e += guilloche_line(150, 570, 150, True, amp, lam, w)   # oben innen
    e += guilloche_line(150, 570, 570, True, amp, lam, w)   # unten innen
    e += guilloche_line(150, 570, 150, False, amp, lam, w)  # links innen
    e += guilloche_line(150, 570, 570, False, amp, lam, w)  # rechts innen
    return e

def corner_nodes():
    e = []
    for (cx, cy) in [(70, 70), (650, 70), (70, 650), (650, 650)]:
        e.append(circle(cx, cy, 7, 2.0, GOLD))
        e.append(hexagon(cx + (18 if cx < 360 else -18), cy + (18 if cy < 360 else -18), 16, True, 1.8, GOLD))
    return e

def svg_wrap(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}pt" height="{SIZE}pt" '
            f'viewBox="0 0 {SIZE} {SIZE}">\n' + "\n".join(body) + "\n</svg>\n")

# ---------- Varianten ----------
def variant_22():
    body = frame_lines() + hex_border() + guilloche_border() + corner_nodes()
    return svg_wrap(body)

def variant_21():
    body = frame_lines() + hex_border(R=25) + guilloche_border() + corner_nodes()
    # Medaillons oben/unten Mitte: Pergament-Disc als Maske + echte Formel (Adamantan, neutral)
    mol, px = rdkit_group("C1C2CC3CC1CC(C2)C3", px=200, col=BRONZE)  # Adamantan
    for (mx, my) in [(360, 100), (360, 620)]:
        body.append(f'<circle cx="{mx}" cy="{my}" r="46" fill="{PERG}" stroke="{GOLD}" stroke-width="2.4"/>')
        s = 0.42
        body.append(f'<g transform="translate({mx},{my}) scale({s}) translate({-px/2},{-px/2})">{mol}</g>')
    return svg_wrap(body)

def variant_23():
    body = frame_lines()
    # Rand-Motiv: echte Naphthalin-Skelette (fusionierter Bicyclus, neutral)
    naph, px = rdkit_group("c1ccc2ccccc2c1", px=180, col=BRONZE)
    defs = f'<defs><g id="naph"><g transform="translate({-px/2},{-px/2})">{naph}</g></g></defs>'
    body.insert(0, defs)
    s = 0.34
    xs = list(range(150, 601, 90))
    for x in xs:
        body.append(f'<use href="#naph" transform="translate({x},100) scale({s})"/>')
        body.append(f'<use href="#naph" transform="translate({x},620) scale({s})"/>')
    for y in xs:
        body.append(f'<use href="#naph" transform="translate(100,{y}) scale({s})"/>')
        body.append(f'<use href="#naph" transform="translate(620,{y}) scale({s})"/>')
    # zentrales Emblem oben/unten: Steroid-Grundgeruest (Gonan, neutral)
    gon, gpx = rdkit_group("C1CCC2C(C1)CCC3C2CCC4CCCCC34", px=220, col=BRONZE)
    for (mx, my) in [(360, 100), (360, 620)]:
        body.append(f'<circle cx="{mx}" cy="{my}" r="50" fill="{PERG}" stroke="{GOLD}" stroke-width="2.4"/>')
        gs = 0.42
        body.append(f'<g transform="translate({mx},{my}) scale({gs}) translate({-gpx/2},{-gpx/2})">{gon}</g>')
    body += corner_nodes()
    return svg_wrap(body)

# ---------- Schreiben + Vorschau ----------
def preview(svg_path, png_path):
    inner = svg_path.read_text()
    inner = inner[inner.index('>', inner.index('<svg'))+1: inner.rindex('</svg>')]
    wrap = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<rect width="{SIZE}" height="{SIZE}" fill="{PERG}"/>'
            f'<rect x="220" y="220" width="280" height="280" fill="#e9e0c8"/>'
            f'<text x="360" y="368" font-family="monospace" font-size="20" fill="#9a8a63" text-anchor="middle">QR</text>'
            f'{inner}</svg>')
    tmp = png_path.with_suffix(".tmp.svg")
    tmp.write_text(wrap)
    subprocess.run([INK, str(tmp), "--export-type=png", f"--export-filename={png_path}",
                    "-w", "720", "-h", "720"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp.unlink()

def main():
    variants = {
        "ornament-zentral-v2.1.svg": variant_21(),
        "ornament-zentral-v2.2.svg": variant_22(),
        "ornament-zentral-v2.3.svg": variant_23(),
    }
    for name, svg in variants.items():
        p = HERE / name
        p.write_text(svg)
        png = PREV / (name.replace("ornament-zentral-", "").replace(".svg", ".png"))
        preview(p, png)
        print(f"OK {name}  ({len(svg)} B)  -> {png.name}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
gen-patterns.py — minimalistische Zentangle-Muster als Rand-Band-SVG.

System (Sitzung 169):
  - EIN Motiv-Typ pro Stoffklasse (die "Mustersorte" / Klassen-Signatur).
  - Pro Stoff eine eigene UMSETZUNG: aus dem slug geseedet (Rotation/Phase/Akzent),
    sodass jede Karte sichtbar anders ist -> Tracking-Trennschaerfe + keine Verwechslung.
  - Mono-Linie, Schwarz, transparenter Grund, eine Strichstaerke = Zentangle-Look.

Band-Canvas 1080 x 220 (fuers spaetere Platzieren als Rand/Streifen frei skalierbar).
Ausgabe: eine SVG je (Klasse-Motiv, Stoff). Rein deterministisch.
"""
import hashlib, math, random, sys
from pathlib import Path

W, H = 1080, 220
CY = H / 2
SW = 5.0          # eine Strichstaerke
BLACK = "#1A1A1A"

def seeded(slug, salt=""):
    return random.Random(int(hashlib.md5((slug + salt).encode()).hexdigest()[:12], 16))

def head(title):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'  <title>{title}</title>\n'
            f'  <g fill="none" stroke="{BLACK}" stroke-width="{SW}" '
            f'stroke-linecap="round" stroke-linejoin="round">\n')
FOOT = "  </g>\n</svg>\n"

# ---------- ALKANE ----------
def alkane_kette(slug):
    """Motiv A 'Kettenglieder': ineinandergreifende gerundete Ringe = gesaettigte C-C-Kette.
    Umsetzung pro Stoff: leichte Rotation je Glied + ein akzentuierter Punkt (geseedet)."""
    rnd = seeded(slug, "alk-a")
    lw, lh, rx = 132, 108, 40
    step = 92
    n = (W - 40) // step
    acc = rnd.randrange(n)
    out = []
    for i in range(n):
        cx = 40 + step * i + lw / 2
        dy = 12 if i % 2 == 0 else -12               # Weben: abwechselnd hoch/tief
        rot = rnd.uniform(-5, 5)
        x, y = cx - lw / 2, CY + dy - lh / 2
        out.append(f'    <rect x="{x:.1f}" y="{y:.1f}" width="{lw}" height="{lh}" rx="{rx}" ry="{rx}" '
                   f'transform="rotate({rot:.1f} {cx:.1f} {CY+dy:.1f})"/>')
        if i == acc:
            out.append(f'    <circle cx="{cx:.1f}" cy="{CY+dy:.1f}" r="9" fill="{BLACK}" stroke="none"/>')
    return head(f"Alkane / Kette / {slug}") + "\n".join(out) + "\n" + FOOT

def alkane_zopf(slug):
    """Motiv B 'Zopf' (Bales): zwei verwobene Wellen-Straenge.
    Umsetzung pro Stoff: Phase + Amplitude geseedet."""
    rnd = seeded(slug, "alk-b")
    amp = rnd.uniform(46, 58)
    ph = rnd.uniform(0, math.pi)
    period = rnd.choice([150, 165, 180])
    def strand(sign):
        pts = []
        for x in range(30, W - 20, 6):
            y = CY + sign * amp * math.sin(2 * math.pi * (x) / period + ph)
            pts.append(f"{x},{y:.1f}")
        return f'    <polyline points="{" ".join(pts)}"/>'
    return head(f"Alkane / Zopf / {slug}") + strand(1) + "\n" + strand(-1) + "\n" + FOOT

# ---------- KETONE ----------
def _teardrop(cx, cy, r, rot):
    """Tropfen-Pfad (Spitze oben), zentriert (cx,cy), Kreisradius r, um rot Grad gedreht."""
    a = math.radians(rot)
    # zwei Schulterpunkte auf +-45 Grad, Spitze bei 2r ueber Zentrum
    def rp(px, py):
        dx, dy = px - cx, py - cy
        return (cx + dx * math.cos(a) - dy * math.sin(a),
                cy + dx * math.sin(a) + dy * math.cos(a))
    sr = (cx + 0.707 * r, cy - 0.707 * r)
    sl = (cx - 0.707 * r, cy - 0.707 * r)
    tip = (cx, cy - 2.0 * r)
    sr, sl, tip = rp(*sr), rp(*sl), rp(*tip)
    return (f'M {sr[0]:.1f} {sr[1]:.1f} '
            f'A {r} {r} 0 1 1 {sl[0]:.1f} {sl[1]:.1f} '
            f'L {tip[0]:.1f} {tip[1]:.1f} Z')

def ketone_tropfen(slug):
    """Motiv A 'Karbonyl-Tropfen': Tropfen mit DOPPEL-Kontur (= C=O Doppelbindung).
    Umsetzung pro Stoff: Rotation je Tropfen + ein gefuellter Akzent-Tropfen (geseedet)."""
    rnd = seeded(slug, "ket-a")
    r = 40
    step = 150
    n = (W - 60) // step
    acc = rnd.randrange(n)
    out = []
    for i in range(n):
        cx = 60 + step * i + r
        rot = rnd.uniform(-14, 14)
        out.append(f'    <path d="{_teardrop(cx, CY + 18, r, rot)}"/>')
        out.append(f'    <path d="{_teardrop(cx, CY + 18, r * 0.58, rot)}"/>')   # Doppellinie
        if i == acc:
            out.append(f'    <circle cx="{cx:.1f}" cy="{CY+8:.1f}" r="7" fill="{BLACK}" stroke="none"/>')
    return head(f"Ketone / Tropfen / {slug}") + "\n".join(out) + "\n" + FOOT

def ketone_spirale(slug):
    """Motiv B 'Printemps-Spiralen': minimalistische Spiralen mit Doppel-Kern (C=O).
    Umsetzung pro Stoff: Drehrichtung/Phase geseedet."""
    rnd = seeded(slug, "ket-b")
    step = 165
    n = (W - 60) // step
    out = []
    for i in range(n):
        cx = 60 + step * i + 50
        cw = rnd.choice([1, -1])
        turns = 1.6
        pts = []
        steps = 120
        for k in range(steps + 1):
            th = turns * 2 * math.pi * k / steps
            rr = 6 + 7.2 * th
            pts.append(f"{cx + cw*rr*math.cos(th):.1f},{CY + rr*math.sin(th):.1f}")
        out.append(f'    <polyline points="{" ".join(pts)}"/>')
        out.append(f'    <circle cx="{cx:.1f}" cy="{CY:.1f}" r="10"/>')
        out.append(f'    <circle cx="{cx:.1f}" cy="{CY:.1f}" r="5"/>')            # Doppel-Kern
    return head(f"Ketone / Spirale / {slug}") + "\n".join(out) + "\n" + FOOT

MOTIFS = {
    "alkane_A-kette":   alkane_kette,
    "alkane_B-zopf":    alkane_zopf,
    "ketone_A-tropfen": ketone_tropfen,
    "ketone_B-spirale": ketone_spirale,
}

def main():
    here = Path(__file__).parent
    jobs = [("methan", ["alkane_A-kette", "alkane_B-zopf"]),
            ("propanon", ["ketone_A-tropfen", "ketone_B-spirale"])]
    for slug, keys in jobs:
        for k in keys:
            svg = MOTIFS[k](slug)
            p = here / f"{k}_{slug}.svg"
            p.write_text(svg)
            print("SVG:", p.name)

if __name__ == "__main__":
    main()

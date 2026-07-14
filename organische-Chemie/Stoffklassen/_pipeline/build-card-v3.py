#!/usr/bin/env python3
"""
build-card-v3.py — v3-Pilotkarte mit Barcode-Marker (Bild-Tracking verworfen).
Zwei Slots (Mitte / Ecke) werden je nach Layout mit {Woodblock-Kunst, Marker} gefuellt:
  Layout a: Kunst = Mitte,  Marker = Ecke
  Layout b: Marker = Mitte, Kunst = Ecke
Farbschema: bw (Schwarz/Weiss) | braun (Dunkelbraun #241A12 / Pergament #F7F1E1).
Marker = INLINE-VEKTOR (kein Zwischen-Raster); Zellen ueberlappen leicht -> KEINE Nahtstreifen.
Kein QR (vertagt).
Usage:
  python3 build-card-v3.py --data card-data.json --slug methan \
     --art <woodblock.png> --marker-png <id.png> --layout a --color braun --out <ordner>
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
from PIL import Image

INKSCAPE = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
SCHEMES = {"bw": {"dark": "#000000", "light": "#FFFFFF"},
           "braun": {"dark": "#241A12", "light": "#F7F1E1"}}
CELL_PX, N, QZ = 118, 8, 2      # Quell-Marker 8x8, 2 Zellen Ruhezone

# ---------- Marker: Raster aus PNG, dann Inline-Vektor ----------
def marker_matrix(png):
    im = Image.open(png).convert("L"); px = im.load(); M = []
    for r in range(N):
        row = []
        for c in range(N):
            blk = tot = 0
            for yy in range(r*CELL_PX+30, r*CELL_PX+CELL_PX-30, 12):
                for xx in range(c*CELL_PX+30, c*CELL_PX+CELL_PX-30, 12):
                    tot += 1; blk += 1 if px[xx, yy] < 128 else 0
            row.append(1 if blk*2 > tot else 0)
        M.append(row)
    return M

def marker_group(M, x, y, size, dark, light):
    """Marker als Vektor in Box (x,y,size): heller Grund (Ruhezone) + dunkle Zellen mit Ueberlappung."""
    V = N + 2*QZ; u = size / V; pad = 0.06 * u
    ox, oy = x + QZ*u, y + QZ*u
    out = [f'  <rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" fill="{light}"/>']
    for r in range(N):
        for c in range(N):
            if M[r][c]:
                out.append(f'  <rect x="{ox+c*u-pad:.2f}" y="{oy+r*u-pad:.2f}" '
                           f'width="{u+2*pad:.2f}" height="{u+2*pad:.2f}" fill="{dark}"/>')
    return "\n".join(out)

# ---------- Text-Helfer (aus build-card.py) ----------
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def hx(rgb): return "#%02X%02X%02X" % tuple(max(0,min(255,int(round(c)))) for c in rgb)
def to_rgb(h): h=h.lstrip("#"); return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16))
def scale(h,f): return hx(tuple(c*f for c in to_rgb(h)))
def formula_tspans(s, small, dy):
    out, shifted = [], False
    for ch in s:
        if ch.isdigit():
            out.append(f'<tspan font-size="{small}"{f" dy=\"{dy}\"" if not shifted else ""}>{ch}</tspan>'); shifted=True
        else:
            out.append(f'<tspan{f" dy=\"-{dy}\"" if shifted else ""}>{esc(ch)}</tspan>'); shifted=False
    return "".join(out)
def est_width(s,F):
    w=0.0
    for ch in s:
        w += (0.42 if ch.isdigit() else 0.50 if ch in "–-•" else 0.55 if ch in "=≡" else 0.60)*F
    return w
def wrap_two(items):
    n=len(items)
    if n==1: return items[0],""
    best=None
    for k in range(1,n):
        l1=" · ".join(items[:k]); l2=" · ".join(items[k:]); sc=max(len(l1),len(l2))
        if best is None or sc<best[0] or (sc==best[0] and len(l1)>len(best[1])): best=(sc,l1,l2)
    return best[1],best[2]

def build_svg(m, M, layout, dark, light):
    acc=m["accent"]; darkc=scale(acc,0.66)
    band_top=scale(acc,1.16); band_bot=scale(acc,0.83)
    art=m["art"].replace("&","&amp;")
    same=m["halbstruktur"]==m["formel"]
    raw=m["formel"] if same else m["formel"]+"  ·  "+m["halbstruktur"]
    ff=44.0; w=est_width(raw,ff); maxw=1080.0
    if w>maxw: ff=max(28.0,44.0*maxw/w)
    ff=int(round(ff)); small=int(round(ff*0.68)); dy=max(7,int(round(small*0.40)))
    formel=formula_tspans(m["formel"],small,dy)
    formel_line = formel if same else formel + f'<tspan font-size="{small}">&#160;&#160;&#8226;&#160;&#160;</tspan>' + formula_tspans(m["halbstruktur"],small,dy)
    mk1,mk2=wrap_two(m["merkmale"]); vw1,vw2=wrap_two(m["verwendung"])
    name=esc(m["name"]); klasse=esc(m["klasse"]).upper(); pos,tot=m["pos"],m["tot"]

    # --- Slot-Inhalte ---
    def art_center():
        return (f'  <image x="192" y="342" width="856" height="856" clip-path="url(#imgClip)" '
                f'preserveAspectRatio="xMidYMid slice" xlink:href="{art}"/>')
    def marker_center():
        return marker_group(M, 192, 342, 856, dark, light)
    def art_corner():
        return (f'  <image x="895" y="1409" width="247" height="247" clip-path="url(#cornClip)" '
                f'preserveAspectRatio="xMidYMid slice" xlink:href="{art}"/>')
    def marker_corner():
        return marker_group(M, 895, 1409, 247, dark, light)

    if layout=="a":
        center_inner, corner_inner = art_center(), marker_corner()
        corner_label = "AR-Marker"
    else:
        center_inner, corner_inner = marker_center(), art_corner()
        corner_label = m["name"]

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="105mm" height="148mm" viewBox="0 0 1240 1748">
  <defs>
    <clipPath id="imgClip"><rect x="192" y="342" width="856" height="856" rx="10" ry="10"/></clipPath>
    <clipPath id="cornClip"><rect x="895" y="1409" width="247" height="247" rx="8" ry="8"/></clipPath>
    <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{band_top}"/><stop offset="1" stop-color="{band_bot}"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="1240" height="1748" fill="#F7F1E1"/>
  <rect x="30" y="30" width="1180" height="1688" rx="26" ry="26" fill="#FBF7EC" stroke="{darkc}" stroke-width="7"/>
  <rect x="50" y="50" width="1140" height="1648" rx="16" ry="16" fill="none" stroke="{acc}" stroke-width="3"/>
  <rect x="60" y="60" width="1120" height="1628" rx="12" ry="12" fill="none" stroke="#C9A24B" stroke-width="1.5" opacity="0.55"/>
  <rect x="74" y="76" width="1092" height="214" rx="12" ry="12" fill="url(#bandGrad)"/>
  <rect x="86" y="88" width="1068" height="190" rx="8" ry="8" fill="none" stroke="#E9D8A6" stroke-width="1.5" opacity="0.6"/>
  <text x="620" y="134" text-anchor="middle" font-family="Georgia, serif" font-size="25" letter-spacing="7" fill="#DCEBF5">ORGANISCHE CHEMIE &#183; SAMMELKARTE</text>
  <line x1="466" y1="152" x2="774" y2="152" stroke="#C9A24B" stroke-width="1.5" opacity="0.85"/>
  <text x="620" y="248" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="84" letter-spacing="9" fill="#FFFFFF">{klasse}</text>
  <circle cx="1112" cy="140" r="40" fill="#FBF7EC" stroke="{darkc}" stroke-width="4"/>
  <text x="1112" y="138" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="40" fill="{darkc}">{pos}</text>
  <text x="1112" y="166" text-anchor="middle" font-family="Georgia, serif" font-size="18" fill="{acc}">/ {tot}</text>
  <rect x="170" y="320" width="900" height="900" rx="20" ry="20" fill="#FFFFFF" stroke="{darkc}" stroke-width="5"/>
  <rect x="182" y="332" width="876" height="876" rx="14" ry="14" fill="none" stroke="{acc}" stroke-width="2" opacity="0.7"/>
{center_inner}
  <circle cx="170" cy="320" r="9" fill="#C9A24B"/><circle cx="1070" cy="320" r="9" fill="#C9A24B"/>
  <circle cx="170" cy="1220" r="9" fill="#C9A24B"/><circle cx="1070" cy="1220" r="9" fill="#C9A24B"/>
  <text x="620" y="1318" text-anchor="middle" font-family="Rockwell, Georgia, serif" font-weight="bold" font-size="92" fill="{darkc}">{name}</text>
  <text x="620" y="1368" text-anchor="middle" font-family="Georgia, serif" font-size="{ff}" fill="#3A2E1E">{formel_line}</text>
  <line x1="95" y1="1400" x2="852" y2="1400" stroke="{acc}" stroke-width="2" opacity="0.6"/>
  <rect x="95" y="1408" width="228" height="46" rx="23" ry="23" fill="{acc}"/>
  <text x="209" y="1439" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="26" letter-spacing="3" fill="#FFFFFF">MERKMALE</text>
  <text x="95" y="1498" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(mk1)}</text>
  <text x="95" y="1536" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(mk2)}</text>
  <rect x="95" y="1552" width="262" height="46" rx="23" ry="23" fill="{darkc}"/>
  <text x="226" y="1583" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="26" letter-spacing="3" fill="#FFFFFF">VERWENDUNG</text>
  <text x="95" y="1642" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(vw1)}</text>
  <text x="95" y="1680" font-family="Georgia, serif" font-size="30" fill="#23303A">{esc(vw2)}</text>
  <rect x="871" y="1385" width="295" height="295" rx="14" ry="14" fill="#FFFFFF" stroke="{acc}" stroke-width="3"/>
{corner_inner}
  <text x="1018" y="1420" text-anchor="middle" font-family="Georgia, serif" font-size="19" fill="#9AA6B0">{esc(corner_label)}</text>
</svg>
'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True); ap.add_argument("--slug",required=True)
    ap.add_argument("--art",required=True); ap.add_argument("--marker-png",required=True,dest="marker_png")
    ap.add_argument("--layout",choices=["a","b"],required=True)
    ap.add_argument("--color",choices=["bw","braun"],required=True)
    ap.add_argument("--out",required=True); ap.add_argument("--no-render",action="store_true")
    a=ap.parse_args()
    data=json.loads(Path(a.data).read_text())
    m=next((x for x in data["karten"] if x["slug"]==a.slug),None)
    if not m: print(f"slug {a.slug} nicht in {a.data}",file=sys.stderr); sys.exit(1)
    m=dict(m); m["art"]=str(Path(a.art).resolve())
    M=marker_matrix(a.marker_png); col=SCHEMES[a.color]
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    stem=f"{a.slug}_{a.color}_{a.layout}"
    svg=out/f"{stem}.svg"; png=out/f"{stem}.karte.png"
    svg.write_text(build_svg(m,M,a.layout,col["dark"],col["light"]))
    print(f"SVG: {svg}")
    if not a.no_render:
        r=subprocess.run([INKSCAPE,str(svg),"--export-type=png",f"--export-filename={png}",
                          "--export-width=1240","--export-height=1748"],capture_output=True,text=True)
        if r.returncode!=0: print("Inkscape-Fehler:\n"+r.stderr[:600],file=sys.stderr); sys.exit(1)
        print(f"PNG: {png}")

if __name__=="__main__":
    main()

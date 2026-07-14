#!/usr/bin/env python3
"""Zwei QR-Muster zum Ansehen:
  A) gestylter Standard-QR (runde Module, Dunkelbraun auf Pergament, Molekuel-Icon mittig)
  B) Woodblock-Halftone-QR (das Kunstbild scheint durch, QR bleibt scannbar)
Beide kodieren die AR-Seiten-URL. Farben: Pergament #F7F1E1 / Dunkelbraun #241A12.
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
from pathlib import Path

HERE = Path(__file__).parent
URL = "https://maximilianbeck-afk.github.io/WebAR---Beck/organische-Chemie/v3/"
PARCH = (247, 241, 225); BROWN = (36, 26, 18)
WOODBLOCK = HERE.parent / "Alkane" / "methan" / "methan-woodblock.png"
if not WOODBLOCK.exists():
    WOODBLOCK = Path("/Users/maximilianbeck/Desktop/brain/05_Claude-Output/WebAR/organische-Chemie/Stoffklassen/Alkane/methan/methan-woodblock.png")

# ---------- A) gestylter Standard-QR ----------
def styled():
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=18, border=4)
    qr.add_data(URL); qr.make(fit=True)
    img = qr.make_image(image_factory=StyledPilImage,
                        module_drawer=RoundedModuleDrawer(),
                        color_mask=SolidFillColorMask(back_color=PARCH, front_color=BROWN),
                        embeded_image_path=str(HERE / "_icon.png"))
    img.save(HERE / "A_styled.png")
    print("A_styled.png", img.size)

# ---------- B) Woodblock-Halftone-QR ----------
def halftone():
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4)
    qr.add_data(URL); qr.make(fit=True)
    M = qr.get_matrix()                       # inkl. Rand (border)
    n = len(M); b = qr.border
    sub = 3; s = 8                            # 3x3 Subpixel je Modul, 8px je Subpixel
    size = n * sub * s
    wb = Image.open(WOODBLOCK).convert("L").resize((n*sub, n*sub))
    wpx = wb.load()
    out = Image.new("RGB", (size, size), PARCH)
    px = out.load()
    def lerp(a, c, f): return tuple(int(a[i] + (c[i]-a[i])*f) for i in range(3))
    # Finder-Regionen (7x7 in drei Ecken, jeweils um border versetzt) -> solide, kein Bild
    def in_finder(r, c):
        fr = [(b, b), (b, n-b-7), (n-b-7, b)]
        return any(rr <= r < rr+7 and cc <= c < cc+7 for rr, cc in fr)
    for r in range(n):
        for c in range(n):
            dark = M[r][c]
            quiet = r < b or r >= n-b or c < b or c >= n-b
            for sr in range(sub):
                for sc in range(sub):
                    if quiet:
                        col = PARCH
                    elif sr == 1 and sc == 1:
                        col = BROWN if dark else PARCH        # Kern erzwingt Modulfarbe -> scannbar
                    elif in_finder(r, c):
                        col = BROWN if dark else PARCH        # Finder solide
                    else:
                        t = wpx[c*sub+sc, r*sub+sr]           # Bildton -> Rand-Subpixel
                        col = lerp(PARCH, BROWN, 1 - t/255.0)
                    x0 = (c*sub+sc)*s; y0 = (r*sub+sr)*s
                    for yy in range(y0, y0+s):
                        for xx in range(x0, x0+s):
                            px[xx, yy] = col
    out.save(HERE / "B_woodblock.png")
    print("B_woodblock.png", out.size)

styled(); halftone()

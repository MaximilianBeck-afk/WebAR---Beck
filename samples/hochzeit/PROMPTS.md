# PROMPTS.md — Sample „Hochzeitseinladung" (mehrschichtige animierte WebAR)

> Verkaufsfähiges SAMPLE einer „lebendigen 2D-Karte mit 3D-Effekt": Barcode-Marker (AR.js) +
> 6 gestaffelte, animierte Schichten statt eines einzelnen Video-Overlays. Marker **ID 40**
> (`hochzeit-ringe`) aus der zentralen Registry `_tools/webar-marker-registry/`.

## Pflicht-Lektüre (vor dem Bau)

1. `02_Projekte/Digitale-Bildung-Schule/webar/WORKFLOW.md` — Abschnitt „Barcode-/Fiducial-Schiene (AR.js)".
2. `05_Claude-Output/WebAR/organische-Chemie/v3/index.html` — HTML-Struktur-Vorlage (A-Frame 1.3.0 + AR.js 3.4.5, `matrixCodeType 4x4_BCH_13_9_3`, Z-Fix-Renderer, `?s=`-Regler).
3. `02_Projekte/WebAR-Monetarisierung/TECHNIK.md` Abschnitt 3 — Schichten-Modell + Animations-Techniken.

## 1. Bild-Elemente — Higgsfield CLI (`gpt_image_2`, 1k, quality high)

Alle Elemente auf flachem **Magenta-Hintergrund (`#FF00FF`)** generiert (kein `rembg` auf diesem
System installiert → deterministisches Pillow-Chroma-Key als Fallback, siehe Abschnitt 2).
Kein Text/keine Schrift im Bildmodell-Prompt (Text kommt deterministisch aus SVG).

| # | Datei (roh) | Modell | AR | Kosten | Prompt (gekürzt auf das Wesentliche) |
|---|---|---|---|---|---|
| 1 | `01-ringe-raw.png` | gpt_image_2 | 1:1 | 4 Cr | „Two intertwined elegant gold wedding rings, fine-art product photography, modern romantic style, warm champagne-gold metal with soft highlights, isolated on a flat solid magenta background (#FF00FF), no shadows, no props, no text, no letters, even soft studio lighting from above, crisp clean edges for easy cutout, centered composition, high detail, photorealistic." |
| 2 | `02-ranken-raw.png` | gpt_image_2 | 3:2 | 4 Cr | „An elegant eucalyptus and floral garland arch, modern romantic wedding style, soft blush-pink roses and greenery with delicate gold accents, fine-art botanical illustration, isolated on a flat solid magenta background (#FF00FF), no shadows, no props, no text, no letters, even soft studio lighting, crisp clean edges for easy cutout, wide arch composition, high detail." |
| 3 | `03-partikel-raw.png` | gpt_image_2 | 1:1 | 4 Cr | „A scattered arrangement of five delicate blush-pink rose petals of varying size and soft golden bokeh light circles, floating, fine-art modern romantic wedding style, isolated on a flat solid magenta background (#FF00FF), no shadows, no props, no text, no letters, even soft studio lighting, crisp clean edges for easy cutout, elements spread across the frame with clear gaps between them, high detail, photorealistic." |
| 4 | `04-herz-raw.png` | gpt_image_2 | 1:1 | 4 Cr | „An elegant heart-shaped ornament made of a delicate gold laurel wreath encircling a soft blush-pink heart outline, fine-art modern romantic wedding emblem, symmetrical, isolated on a flat solid magenta background (#FF00FF), no shadows, no props, no text, no letters, no numbers, even soft studio lighting, crisp clean edges for easy cutout, centered composition, high detail." |
| 5 | `05-glow-raw.png` | gpt_image_2 | 1:1 | 4 Cr | „A soft radial glow of warm golden light with a faint delicate veil-like haze and tiny sparkle particles, dreamy fine-art wedding atmosphere effect, isolated on a flat solid magenta background (#FF00FF), no shadows, no props, no text, no letters, centered soft radial gradient glow, crisp clean edges for easy cutout, high detail." |

**Credits verbraucht:** 5 × 4 = **20 Credits** (von ~50 Budget). Alle fünf Läufe liefen im ersten
Versuch durch, keine Fehlschläge, kein Retry nötig.

## 2. Freistellen — Pillow-Chroma-Key (Fallback, da `rembg` nicht installiert)

`import rembg` schlägt auf diesem System fehl (`ModuleNotFoundError`). `numpy` ist ebenfalls
nicht vorhanden (`pip install` durch PEP-668/Homebrew-Schutz blockiert, kein `--break-system-packages`
ohne Rückfrage). Fallback: reines **Pillow `ImageMath`** (kein numpy nötig), Skript
`freistellen.py` (im Scratchpad, Vorgehen dokumentiert):

1. Quadrierte Farbdistanz jedes Pixels zu Magenta `(R-255)² + G² + (B-255)²`.
2. Alpha = weiche Rampe zwischen `low²`/`high²`-Schwellwert (kein hartes Floodfill-Cutout wie
   beim Pokemon-Set — erlaubt weiche Kanten, wichtig für das Glow-Element).
3. **Despill:** Magenta-Überschuss (`min(R,B) − G`) an teiltransparenten Kanten abgezogen
   (Standard-Screen-Compositing-Trick gegen sichtbaren rosa Rand).
4. Zuschnitt auf Bounding-Box (+Padding), Begrenzung auf ≤ 1024 px Kante, RGBA-PNG.

Je Element per Hand kalibrierte `low`/`high`-Rampenbreite (harte Kante bei Ringen/Ranken/Herz,
sehr weiche Rampe beim Glow, da der Glow selbst als Farbverlauf ins Magenta ausläuft):

| Element | low | high | Ergebnis-Datei |
|---|---|---|---|
| Ringe | 36 | 85 | `elemente/ringe.png` (1024×1024) |
| Ranken | 36 | 85 | `elemente/ranken.png` (1024×688) |
| Partikel | 28 | 95 | `elemente/partikel.png` (1024×1024) |
| Herz | 36 | 85 | `elemente/herz.png` (1024×1024) |
| Glow | 8 | 190 | `elemente/glow.png` (1024×1024) |

Sichtprüfung: alle fünf PNGs gegen Weiß **und** Dunkelgrau kompositet geprüft (kein sichtbarer
Magenta-Fringe außer einem minimalen, akzeptablen Saum an den Ring-Außenkanten). Echter
Alpha-Kanal verifiziert (`alpha.getextrema()` → `(0, 255)` bei allen fünf Bildern).

## 3. Text-Banner — deterministisch (SVG → Inkscape)

Kein Bild-Modell-Text. `elemente/banner.svg` mit zwei `<text>`-Elementen:
- Hauptzeile „Wir sagen JA!" — Font **Snell Roundhand** (kalligrafisch, macOS-Systemfont,
  `/System/Library/Fonts/Supplemental/SnellRoundhand.ttc`), 150px.
- Nebenzeile „ANNA & MAX · 12.09.2027" (Platzhalter-Namen) — Optima/Serif, Kapitälchen-Stil,
  Letter-Spacing, 46px.

Export:
```bash
/Applications/Inkscape.app/Contents/MacOS/inkscape elemente/banner.svg \
  --export-type=png --export-dpi=192 --export-background-opacity=0 \
  --export-filename=elemente/banner.png
```
Danach per Pillow auf Bounding-Box zugeschnitten (+20px Padding) und auf 1024 px Kante skaliert
(2000×840 → 1024×297). Sichtprüfung: Font hat sauber gerendert, keine Fallback-Schrift.

## 4. Probekarte — deterministisch (SVG → Inkscape)

`karte.svg` (A6, `width="105mm" height="148mm" viewBox="0 0 1240 1748"`, Export bei 300 dpi →
exakt 1240×1748 px). Alle Texte als SVG `<text>` (Titel „Hochzeitseinladung" in Snell Roundhand,
Subtitle „KARTE SCANNEN & STAUNEN" in Serif-Kapitälchen). Marker 40 als **Original-PNG der
Registry** (`_tools/webar-marker-registry/markers/40.png`, 944×944, unverzerrt, `preserveAspectRatio="none"`
nur zur expliziten Quadrat-Erzwingung bei bereits quadratischem Ausgangsbild) base64-eingebettet,
48 mm (567 px) groß, mittig platziert. **Ruhezone:** 64 mm (760 px) reinweißes Quadrat um den
Marker (Pflicht laut WORKFLOW.md — helle einfarbige Fläche, maximaler Luminanzkontrast zum
schwarz/weißen Marker). Feiner doppelter Goldrahmen + vier Eck-Rauten als Zierrahmen.

Export:
```bash
/Applications/Inkscape.app/Contents/MacOS/inkscape karte.svg \
  --export-type=png --export-dpi=300 --export-filename=karte.png
```
Erster Versuch schlug fehl (XML-Parser-Fehler wegen `--` im HTML-Kommentar „Marker 40 (…) --
unverzerrt…"; behoben durch Doppelpunkt statt Doppel-Bindestrich) und lieferte zunächst
3875×5463 px (width/height ohne Einheit → Inkscape nimmt 96 dpi als Referenz-Dichte an, 300 dpi
Export skaliert dann hoch). Fix: `width="105mm" height="148mm"` statt unitloser Pixelwerte im
Wurzel-`<svg>` → danach exakt 1240×1748 px. Sichtprüfung (Bild gelesen): Titel/Zierrahmen/Marker/
Ruhezone/Subtitle korrekt, Marker scharf und unverzerrt.

## 5. AR-Szene (`index.html`)

Struktur 1:1 von `organische-Chemie/v3/index.html` übernommen: A-Frame 1.3.0 + AR.js 3.4.5,
`arjs="detectionMode: mono_and_matrix; matrixCodeType: 4x4_BCH_13_9_3"`, Z-Fighting-Fix
(`renderer="… logarithmicDepthBuffer: true; precision: highp; antialias: true"`), globaler
`?s=`-Regler (`data-base` je Layer × URL-Parameter `s`).

Sechs Schichten unter `<a-marker type="barcode" value="40">` (Höhe = lokale Z-Achse, wie im
Chemie-Template `position="0 0 z"` kalibriert — **nicht** die Y-Achse aus dem illustrativen
Pseudocode in TECHNIK.md §3.1, da nur die Z-Konvention geräteseitig verifiziert ist):

| Layer | Element | Z-Höhe | Animation |
|---|---|---|---|
| L0 | Glow | 0.02 | Opazitäts-Puls (4,2 s) |
| L1 | Ranken-Bogen | 0.06 | statisch |
| L2 | Ringe (Hero) | 0.22–0.32 | Schweben (2,6 s) + Y-Rotation (9 s/Umdrehung) |
| L3 | Herz-Ornament | 0.46, seitlich versetzt | Herzschlag-Skalierungspuls (1,3 s) + langsame Z-Eigendrehung (16 s) |
| L4 | Partikel (3× Instanzen) | 0.9→0.3, fallend | Positions-Fall (6,4–8,2 s, versetzte Delays 0/1,8/3,2 s) + Opazitäts-Fade |
| L5 | Text-Banner | 1,02–1,09 | sanftes Schweben (3,4 s) |

Alle Planes: `material="shader: flat; transparent: true; alphaTest: …; side: double"` (beidseitig
sichtbar, unlit wie ein Sprite, kein Beleuchtungs-Artefakt).

## 6. Nicht genutzte Alternativen / bewusst verworfen

- **Touch-Gesten** (`gesture-detector`/`gesture-handler` aus dem v3-Template) bewusst weggelassen:
  Aufgabe verlangt primär kontinuierliche Animationen; manuelle Rotation würde mit
  `animation__drehen` konkurrieren (bekannter Konflikt, siehe WORKFLOW.md).
- **rembg / echtes ML-Freistellen**: nicht installierbar ohne System-Python-Eingriff
  (PEP 668) → Chroma-Key-Fallback wie oben, Ergebnis optisch gleichwertig für flächige Motive.

## 7. Qualitäts-Checks vor Abschluss

- Alle relativen Pfade in `index.html` geprüft (`elemente/*.png` existieren) — OK.
- Alpha-Kanal aller Element-PNGs verifiziert (`(0,255)`-Range) — OK.
- Ordnergröße gesamt: **~5,6 MB** (< 8 MB Budget) nach `Image.save(optimize=True)` auf allen PNGs.
- Marker unverzerrt (quadratisch, `preserveAspectRatio="none"` bei quadratischem Quellbild ist
  ein No-Op) und kontrastreich (reinweiße Ruhezone, Original-Schwarz/Weiß-Marker unverändert).

## 8. Offene Justage-Punkte (nicht am Gerät getestet)

- **Skalen/Positionen der 6 Layer sind nicht am Handy kalibriert** (kein Live-Test in diesem
  Lauf) — Startwerte an den `?s=`-Regler und die Chemie-Referenzwerte angelehnt, aber neu.
  Vor Verkauf: am Gerät scannen, `scale`/`position.z` je Layer nachziehen.
- **Partikel-Fade-Timing** ist nur angenähert synchron zum Fall (`dir: alternate` mit eigener,
  unabhängiger Dauer) — kein exaktes „erscheint oben, verschwindet unten"; bei Bedarf auf
  Multi-Keyframe-Timeline (oder drei kürzere sequentielle Animationen) umstellen.
- **Herz-Position** (`0.42 -0.05 0.46`) ist eine Schätzung, um Überlappung mit den Ringen zu
  vermeiden — am Gerät prüfen, ob es den Ranken-Bogen-Rand verlässt oder ins Bild ragt.
- Marker-Ruhezone/Kartenlayout ist nicht gedruckt/gescannt getestet (nur Bildschirm-Sichtprüfung).

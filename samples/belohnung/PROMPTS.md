# PROMPTS.md — Belohnungssticker/-karte „Super gemacht!" (Sample)

> Verkaufsfähiges WebAR-Sample für die Lehrmaterial-Linie **AR-Belohnungssticker/-karte**.
> Marker: **ID 41 (`belohnung-pokal`)** aus der zentralen Registry `_tools/webar-marker-registry/`
> (bereits vergeben, hier nur konsumiert — nicht neu alloziert). Zielbild: Karte/Sticker scannen →
> Pokal poppt federnd auf, Strahlen-Burst + Konfetti-Explosion, Banner „SUPER GEMACHT!" liest sich zuletzt ein.

## Pflicht-Lektüre (vor dem Bau gelesen)

1. `02_Projekte/Digitale-Bildung-Schule/webar/WORKFLOW.md` — Abschnitt „Barcode-/Fiducial-Schiene (AR.js)" (Z-Fighting-Fix, Marker-Ruhezone, Text nie aus dem Bildmodell) + „Bewegter 2D-Sprite".
2. `05_Claude-Output/WebAR/organische-Chemie/v3/index.html` — Struktur-Vorlage (A-Frame 1.3.0 + AR.js 3.4.5, `matrixCodeType: 4x4_BCH_13_9_3`, Renderer-Z-Fix, `?s=`-Regler).
3. `02_Projekte/WebAR-Monetarisierung/TECHNIK.md` §3 — Schichten-Modell (L0 Boden/Burst, L1 Hauptmotiv, L2 Partikel-Overlay, L3 Banner), Animationstechniken, Sticker-Bausteine.

## Werkzeug-Checks (vor dem Generieren)

- `~/.local/bin/hf generate --help` + `~/.local/bin/hf model list` gelesen.
- `python3 -c "import rembg"` → **nicht installiert** (auch nicht im `molgeo`-venv). Freistellen darum per
  deterministischem Farbdistanz-/Floodfill-Verfahren (Pokemon-Vorgehen, siehe `elemente/freistellen.py`)
  auf Basis eines **flachen Solid-Cyan-Hintergrunds (`#00FFFF`)** in allen Higgsfield-Prompts — bewusst
  cyan statt magenta/grün gewählt, weil das Motiv (Gold/Rot/Orange/Gelb/Pink) keine cyanen Anteile hat.
- Inkscape geprüft: `/Applications/Inkscape.app/Contents/MacOS/inkscape` (installiert, nicht im PATH — voller
  Pfad verwendet). Font „Arial Rounded MT Bold" via `fc-match` bestätigt vorhanden
  (`/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf`).
- Kostencheck vorab: `hf generate cost gpt_image_2 --quality high --resolution 1k` → **4 Credits/Bild**
  (Budget-Fit: 4 Bilder × 4 = 16 Credits, deutlich unter dem 40-Credit-Limit).

## Higgsfield-Generierungen (Modell: `gpt_image_2`, `--quality high --resolution 1k --aspect-ratio 1:1`)

Alle sequenziell mit `--wait --wait-timeout 3m --wait-interval 5s`, keine Fehlschläge, kein Hänger.
**Verbrauch: 4 Bilder × 4 Credits = 16 Credits** von ~40 Budget.

1. **Pokal (Hero, L1)**
   > A friendly cheerful golden trophy cup with a bright yellow star on the front, comic sticker
   > illustration style, bold thick white sticker outline around the whole object, glossy
   > highlights, vibrant warm colors, floating centered on a flat solid cyan color background
   > (hex 00FFFF), perfectly flat even background with no gradient and no shadow, no text, no
   > letters, no numbers, kid-friendly clean illustration
   → `elemente/cutout/pokal.png` (freigestellt, 803×905)

2. **Konfetti-Sheet (Quelle für L2-Partikel)**
   > A cheerful cluster of colorful confetti party particles - small triangles, circles, ribbon
   > curls, and tiny stars - in bright red, yellow, blue, green, pink and orange, comic sticker
   > illustration style with thin white outline on each piece, glossy vibrant colors, scattered
   > evenly with visible gaps between pieces, floating on a flat solid cyan color background
   > (hex 00FFFF), perfectly flat even background with no gradient and no shadow, no text, no
   > letters, no numbers, kid-friendly clean illustration
   → per Connected-Components-Zerlegung (`elemente/konfetti-teile.py`, eigene BFS-Implementierung,
   kein `scipy` nötig) in **18 einzelne Partikel-Texturen** geschnitten:
   `elemente/cutout/konfetti-teile/teil-01.png` … `teil-18.png` (Ribbons, Sterne, Dreiecke, Kreise,
   Größen-Streuung statt nur der größten Stücke gewählt für visuelle Vielfalt).

3. **Sterne-Burst (L0, Bodenlayer)**
   > A bright golden yellow star-burst explosion with radiating sparkle rays and a few small
   > twinkling stars around it, comic sticker illustration style, bold thick white outline, glossy
   > vibrant colors, radial symmetric composition centered in frame, floating on a flat solid cyan
   > color background (hex 00FFFF), perfectly flat even background with no gradient and no shadow,
   > no text, no letters, no numbers, kid-friendly clean illustration
   → `elemente/cutout/sterneburst.png` (876×971)

4. **Rakete (optionales Bonus-Element)**
   > A cute small friendly cartoon rocket ship with red and white stripes, a round window, and
   > little flame at the bottom, comic sticker illustration style, bold thick white outline, glossy
   > vibrant colors, floating diagonally centered on a flat solid cyan color background
   > (hex 00FFFF), perfectly flat even background with no gradient and no shadow, no text, no
   > letters, no numbers, kid-friendly clean illustration
   → `elemente/cutout/rakete.png` (598×870) — fliegt in der AR-Szene kurz seitlich hoch und weg.

Alle vier Roh-Ergebnisse wurden nach dem Freistellen gelöscht (`elemente/roh/`), um das Ordner-Budget
(< 8 MB) mit Reserve einzuhalten — die Prompts hier sind reproduzierbar, die Cutouts bleiben erhalten.

## Deterministisches Freistellen

`elemente/freistellen.py` — Floodfill von den 4 Bildecken (Toleranz 46) auf `#00FFFF`, plus
Farbdistanz-Nachschliff (< 60) gegen Anti-Alias-Reste, Alpha-Kante mit 0.6 px Gaussian gefedert,
enger Bbox-Crop, Deckelung auf max. 1024 px Kante. Auf allen 4 Hero-Bildern verifiziert:
Eck-Alpha = 0, Inhalt-Alpha = 255 (Stichprobe per Pixel-Check, nicht nur visuell).

`elemente/konfetti-teile.py` — gleiche Cyan-Distanz-Logik, zusätzlich eigene
Connected-Components-Suche (BFS, 8er-Nachbarschaft, `numpy` aus dem vorhandenen `molgeo`-venv,
kein neues Paket installiert) auf der Alpha-Maske. Aus 89 gefundenen Komponenten wurden 18 über den
gesamten Flächen-Bereich gestreut ausgewählt (nicht nur die größten), damit Bänder **und** kleine
Sterne/Kreise/Dreiecke in der Auswahl landen.

## Banner „SUPER GEMACHT!" — deterministisch, NICHT aus dem Bildmodell

`elemente/gen-banner.py` → `elemente/banner.svg` → Inkscape-Export → `elemente/banner.png` (1200×300,
transparent). Pillen-Banner in Sticker-Optik (Farbverlauf Pink, dicker weißer Rand), zwei
Vektor-Sterne links/rechts, Text in **Arial Rounded MT Bold** mit Kontur. Erste Version hatte
Text/Stern-Überlappung (`S` bzw. `!` schnitt in die Sterne) → Canvas verbreitert (1024→1200px) und
Sterne weiter an den Rand gerückt, Schriftgröße 98→86px; zweite Fassung sauber, keine Überlappung
mehr (Sichtprüfung).

## Druckvorlagen — karte.svg / sticker.svg

`elemente/gen-druck.py` — beide SVGs parametrisch aus derselben Quelle gebaut:

- **Marker als Inline-Vektor**, direkt aus `_tools/webar-marker-registry/markers/41_braun.svg`
  geparst (12×12-Rects) und auf Zielgröße skaliert eingebettet — kein Zwischen-Raster, keine externe
  Pfadabhängigkeit beim Druck (Marker bleibt scharf bei jeder Auflösung).
- **karte.svg** (A6, 1240×1748 px @300dpi): Titel „Belohnungskarte" + Untertitel „Scannen & feiern!"
  als SVG-Text (Arial Rounded MT Bold), Marker 48 mm mittig mit **heller Ruhezone** (helles Feld +
  11 mm Zusatzabstand rund um den Marker, frei von anderen Grafikelementen), Eck-Illustrationen
  (Pokal, Sterne-Burst, Rakete, vereinzelte Konfetti-Teile) bewusst außerhalb der Ruhezone platziert.
- **sticker.svg** (Ø50 mm, 591×591 px @300dpi): Marker 30 mm mittig mit heller Ruhezone, schmaler
  bunter Farbverlaufs-Zierring nahe der Außenkante, vier Konfetti-Akzente im Ring-Innenraum, **eigener
  Schnittkontur-Pfad** (`<g id="schnittkontur">`, Magenta-Linie, Branchen-Konvention für Stanzformen)
  getrennt von der sichtbaren Gestaltung.
- **Export-Fallstrick:** `--export-dpi=300` zusammen mit bereits-in-Zielpixel-Einheiten gesetzten
  `width`/`height` verdoppelt die Auflösung fälschlich (Inkscape nimmt unitless px als 96 dpi an und
  skaliert zusätzlich → 1240×1748 wurde zu 3875×5463). **Korrektur:** kein `--export-dpi` übergeben,
  da die SVG-Maße bereits die exakten 300-dpi-Zielpixel sind. Nach Korrektur: `karte.png` 1240×1748,
  `sticker.png` 591×591 — beide bestätigt.

## AR-Szene (`index.html`)

A-Frame 1.3.0 + AR.js 3.4.5, `<a-marker type="barcode" value="41">`. Renderer-Z-Fix Pflicht-Attribute
übernommen (`logarithmicDepthBuffer: true; precision: highp; antialias: true`). `?s=`-Regler für die
gesamte Effekt-Gruppe wie im Referenz-Beispiel.

**Zwei kleine Inline-Komponenten** (wie in WORKFLOW.md vorgesehen):

- `reward-trigger` (sitzt auf `<a-marker>`) — hört auf `markerFound` und reicht das Signal per
  eigenem Event `fx-restart` an alle `.fx`-Kindelemente weiter (A-Frames `animation`-Komponente hört
  nur auf ihrem eigenen Element, ein Bubbling von der Marker-Elternebene nach unten existiert nicht
  — deshalb der explizite Relay).
- `confetti-emitter` — baut beim Laden 20 Partikel-Planes aus den 18 Konfetti-Texturen (zyklisch),
  mit zufälliger, aber pro Seitenaufruf fester Flugbahn (Auswärts-/Aufwärtsbewegung, dann Fall,
  Rotation, Ein-/Ausblenden), alle über `startEvents: fx-restart` re-startbar.

**Schichten:**

| Layer | Element | Timing | Effekt |
|---|---|---|---|
| L0 | Sterne-Burst | delay 0, dauer 420 ms | `easeOutBack`-Scale-Pop 0→1, danach sanftes Pulsieren (loop) |
| L1 | Pokal (Hero) | delay 160 ms, dauer 900 ms | `easeOutElastic`-Scale-Pop (federnd), danach Schweben (alternate loop) |
| Bonus | Rakete | delay 260 ms | fliegt seitlich hoch und weg, blendet aus |
| L2 | 20 Konfetti-Partikel | gestreute delays 0–320 ms | Scale-in, Flug nach außen/oben, Fall, Rotation (bis zu ±880°), Fade-out |
| L3 | Banner „SUPER GEMACHT!" | delay 980 ms | poppt zuletzt ein (`easeOutBack`), liest sich nach der Explosion |

Billboard-Verhalten (`look-at="[camera]"`) auf Burst/Pokal/Rakete/Banner, damit sie unabhängig vom
Kamerawinkel lesbar bleiben. Konfetti-Partikel bekommen **kein** `look-at` (würde die
Rotationsanimation überschreiben, da `look-at` jeden Frame die volle Rotation neu setzt) — sie
taumeln frei, wie echtes Konfetti.

## Budget & Ergebnis

- **Credits verbraucht:** 16 von ~40 (4 Bilder × 4 Credits, `gpt_image_2`, `--quality high --resolution 1k`).
- **Fehlschläge:** keine — alle 4 Higgsfield-Jobs liefen im ersten Versuch durch (sequenziell, `--wait`,
  keine Retries nötig).
- **Ordnergröße:** 3,0 MB gesamt (nach Löschen von `elemente/roh/`), AR-Seiten-Payload (nur die von
  `index.html` geladenen Dateien) 2,67 MB — beide Budgets deutlich unterschritten.
- **Offene Justage-Punkte** (siehe Abschlussbericht): Konfetti-Partikel-Kanten haben einen minimalen
  Cyan-Saum (Anti-Aliasing-Rest, bei genauem Hinsehen sichtbar); Timing/Positionen der Konfetti-Explosion
  sind nicht am Gerät (Handy-Kamera) validiert, nur im Code/Logik geprüft.

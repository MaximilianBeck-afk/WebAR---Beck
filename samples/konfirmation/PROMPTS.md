# Konfirmation — WebAR-Sample (Sitzung 173)

Verkaufsfähiges SAMPLE einer mehrschichtigen, animierten WebAR-Szene ("lebendige 2D-Karte mit 3D-Effekt")
zum Thema Konfirmation/Kommunion. Marker: **ID 39** (`konfirmation-taube`, zentrale Registry
`_tools/webar-marker-registry/registry.yml`, bereits vergeben — nicht selbst alloziert).

## Pflicht-Lektüre (vor dem Bau)

1. `02_Projekte/Digitale-Bildung-Schule/webar/WORKFLOW.md` — Barcode-/Fiducial-Schiene (AR.js) + Bewegter-2D-Sprite-Abschnitt.
2. `05_Claude-Output/WebAR/organische-Chemie/v3/index.html` — Kopf-/Setup-Vorlage (A-Frame 1.3.0 + AR.js 3.4.5).
3. `02_Projekte/WebAR-Monetarisierung/TECHNIK.md` Abschnitt 3 — Schichten-Modell + Animations-Techniken.

## Bild-Elemente — Higgsfield-CLI (`~/.local/bin/hf`)

Modell: `gpt_image_2` (Quality medium, Resolution 1k, Aspect 1:1 → 2 Credits/Bild) + `image_background_remover`
(1 Credit/Freistellung, direkt in der Higgsfield-CLI verfügbar — kein `rembg` nötig, kein Pillow-Chroma-Key nötig).
Sequenziell mit `--wait --wait-timeout 180s`, idempotent (vorhandene Dateien übersprungen), Skript:
`gen_elements.py` (im Scratchpad der Sitzung, nicht Teil des Deliverables).

Alle 5 Elemente auf einfarbigem (reinem Weiß) Hintergrund generiert, danach mit Higgsfield
`image_background_remover` freigestellt (echter Alpha-Kanal, per Pillow verifiziert), dann per Pillow
auf die Alpha-Bounding-Box zugeschnitten (+12px Padding) und mit `optimize=True` re-komprimiert.

| Element | Datei | Prompt (verkürzt) | Credits |
|---|---|---|---|
| Taube mit Ölzweig (Hero) | `elemente/taube.png` | "Elegant illustration of a single flying white dove carrying a small olive branch…, cream/pale gold watercolor, isolated on pure flat white background, no text" | 2 + 1 |
| Lichtstrahlen-Gloriole | `elemente/gloriole.png` | "Elegant radiating sunburst of soft golden light rays forming a circular gloriole/halo…, isolated on pure flat white background, no text" | 2 + 1 |
| Kreuz-/Fisch-Ornament | `elemente/kreuz-ornament.png` | "Small elegant ornamental cross with a delicate fish symbol beside it, fine gold linework…, isolated on pure flat white background, no text" | 2 + 1 |
| Blüten-/Konfetti-Partikel | `elemente/bluetenkonfetti.png` | "Six small delicate flower blossoms and round confetti dots in cream/white/gold, floating freely spaced apart…, isolated on pure flat white background, no text" | 2 + 1 |
| Regenbogen-Bogen (dezent) | `elemente/regenbogen.png` | "A dainty, understated rainbow arch as thin elegant line-art in pastel gold/cream/rose/blue…, isolated on pure flat white background, no text" | 2 + 1 |

**Credits verbraucht: 15 von ~50 Budget** (5× 2 Credits Generierung + 5× 1 Credit Freistellen). Kein Fehlschlag,
kein Übersprungen — alle 5 Elemente liefen im ersten Durchlauf durch.

Alle Roh-Generate lagen zunächst in `elemente/_raw/` (Zwischenstufe vor dem Freistellen) — nach Abschluss
gelöscht (nicht Teil des Deliverables, hätte das 8-MB-Ordnerbudget gesprengt: 10 MB → 3,9 MB nach Löschen).

## Text-Banner (deterministisch, kein Bildmodell-Text)

`elemente/text-banner.png` (+ `.svg`): "Gottes Segen" (Snell Roundhand, Skript) + "ZUR KONFIRMATION"
(Didot, Versalien mit Letter-Spacing) als SVG-Pfad-Text, Export via
`/Applications/Inkscape.app/Contents/MacOS/inkscape --export-background-opacity=0`. Sichtgeprüft (Read-Tool).

## Probekarte `karte.svg` → `karte.png`

A6, 1240×1748 px @300 dpi (SVG `width="105mm" height="148mm" viewBox="0 0 1240 1748"`, Export via
`--export-width 1240 --export-height 1748`, analog `build-card-v3.py` aus dem Stoffklassen-Set).

- Marker 39 **braun-Schema** (`_tools/webar-marker-registry/markers/39_braun.svg`), Original-Rects 1:1
  übernommen (nicht neu vektorisiert), als `<g transform="translate(…) scale(…)">` auf ~48 mm (567 px)
  skaliert, zentriert bei (620, 900).
- **Ruhezone (Pflicht):** 760×760 px plane einfarbige Fläche (Kartenhintergrundfarbe `#F7F1E1`) rund um
  den Marker, nichts anderes berührt sie.
- Titel "Konfirmation" (Didot) + Subline "Gottes Segen zu deinem Tag" (Snell Roundhand) oben, "Karte
  scannen & staunen" (Snell Roundhand) unter dem Marker, dezenter doppelter Rahmen mit vier Ecken-Punkten.
- Sichtgeprüft (Read-Tool auf `karte.png`): Marker unverzerrt, dunkelbraun auf hellem Pergament, guter
  Kontrast, Ruhezone klar erkennbar.

## AR-Szene `index.html`

Kopf-/Setup-Struktur 1:1 aus `organische-Chemie/v3/index.html` übernommen: A-Frame 1.3.0 + AR.js 3.4.5,
`arjs="detectionMode: mono_and_matrix; matrixCodeType: 4x4_BCH_13_9_3"`, Renderer-Zeile mit
`logarithmicDepthBuffer: true` (Z-Fighting-Fix Pflicht), `?s=`-Skalierungs-Regler (global auf einen
`scene-root`-Wrapper statt pro Objekt, da hier eine ganze Mehrschicht-Szene statt einzelner Modelle skaliert
werden muss), Hinweistext "Karte ins Bild halten" sinngemäß übernommen.

**Koordinaten-Klärung (wichtig für Wiederverwendung):** AR.js legt die Marker-Ebene in die XY-Ebene, die
lokale Z-Achse zeigt aus der Karte heraus zur Kamera (bestätigt durch die funktionierende Chemie-Vorlage:
`position="0 0 0.3"` = Modell schwebt über der Karte). TECHNIK.md Abschnitt 3.1 beschreibt das
Schichten-Modell pseudocode-mäßig mit Y als Höhenachse (generisches Y-up-Weltbild) — hier auf die reale,
am Gerät geprüfte AR.js-Konvention übertragen: **alle Schichten `rotation="0 0 0"`, nur entlang Z gestapelt**
(0.02 … 0.92), X/Y nur für seitlichen Versatz. Ergebnis: flacher, zur Karte paralleler Decal-Stapel — beim
Kippen der Karte/des Telefons entsteht echter Parallax zwischen den Ebenen.

**Schichten (unten → oben, Z-Tiefe):**
1. `z=0.04` — Gloriole (Glow/Strahlenkranz), langsame Rotation (`animation__spin`, 16 s Loop).
2. `z=0.30` — Regenbogen (Akzent), sanftes Wiegen (`animation__sway`, ±4°, 5,2 s).
3. `z=0.34` — Kreuz-/Fisch-Ornament (Akzent, links versetzt), Scale-Puls/"Atmen" (`animation__breathe`, 3 s).
4. `z=0.45` — Taube (Hero), Schweben auf/ab (`animation__float`, 2,4 s) + leichtes Wiegen/Gleitflug-Rotation
   (`animation__glide`, ±4°, 2,6 s).
5. `z=0.58 / 0.62 / 0.66` — drei Blüten-Konfetti-Partikel-Planes, jeweils eigene Float- und
   Opacity-Puls-Loops mit gestaffeltem `delay` (0 / 350 / 700 ms) und leicht unterschiedlicher `dur` für
   asynchrone Lebendigkeit.
6. `z=0.80` — Text-Banner "Gottes Segen zur Konfirmation", **statisch leicht geneigt** (`rotation="-18 0 0"`,
   keine `look-at`-Komponente — robuster innerhalb des Marker-Kindknotens).

Alle Planes mit `material="shader: flat; transparent: true; alphaTest: 0.02; side: double"` (unlit, damit die
Aquarell-Farben nicht von Szenen-Licht verfälscht werden, plus Double-Sided gegen Wegkippen beim Parallax).

## Qualitäts-Gates — Ergebnis

- (a) Alle in `index.html` referenzierten Dateien existieren (relative Pfade `elemente/…`) — geprüft.
- (b) Alle 5 Element-PNGs + Text-Banner haben echten Alpha-Kanal (Pillow `getextrema()` auf dem Alpha-Band
  geprüft, jeweils Bereich 0–255, kein reines 255-Konstant).
- (c) Gesamtgröße Ordner: **3,9 MB** (< 8 MB) — nach Löschen von `elemente/_raw/` (Zwischenstufe).
- (d) `karte.png` zeigt den Marker unverzerrt, dunkel (braun) auf hell (Pergament), sichtgeprüft.

## Offene Justage-Punkte (am Gerät)

- **`?s=`-Startwert kalibrieren:** noch nicht am echten Gerät getestet (kein Headless-Browser lokal,
  siehe WORKFLOW-Fallstrick "HTML→PNG geht nicht"). Startwert `1.0`, Regler bereit; erwartungsgemäß
  liegt der sinnvolle Bereich ähnlich zur Chemie-Vorlage (0.8–1.8), da Marker-Größe (~48 mm, Layout b)
  identisch zum Stoffklassen-Set ist.
- **Z-Tiefen-Abstände (0.04 … 0.92) sind Schätzwerte** aus der Analogie zur Chemie-Vorlage (Skala
  "1 Einheit ≈ Kartenbreite") — am Gerät ggf. stauchen/strecken, falls die Schichten zu weit auseinander
  oder zu dicht wirken.
- **Text-Banner-Neigung (-18°)** ist ein optischer Kompromiss (kippt bei starkem Betrachtungswinkel
  ggf. aus dem Bild) — Alternative wäre eine `look-at`-Komponente auf die Kamera, bewusst nicht gewählt
  (Verhalten von `look-at` innerhalb von `a-marker`-Kindknoten ist in der bisherigen Pipeline nicht
  erprobt; die statische Neigung ist der robustere, dokumentierte Weg).
- **Gesten (Pinch/Rotate)** wurden bewusst NICHT eingebaut (Fokus des Samples liegt auf der animierten
  Mehrschicht-Szene, nicht auf manueller Interaktion) — bei Bedarf 1:1 aus `v3/index.html`
  (`gesture-detector`/`gesture-handler`) nachrüstbar.
- **Nicht live gehostet/getestet:** Dieses Sample wurde NICHT committet/gepusht (Vorgabe) und lief noch
  nicht über HTTPS-Hosting am echten Handy — die strukturelle Korrektheit (Pfade, Marker-ID, Renderer-Fix,
  Schichten-Logik) ist geprüft, der visuelle Live-Eindruck (Parallax-Wirkung, Lesbarkeit des Banners,
  Größenverhältnis Taube:Karte) steht noch aus.

# PROGRESS — Organische-Chemie WebAR-Kartenset

> Zustandsmaschine für Wiedereinstieg nach Abbruch. **Lagebild immer aus der Status-Tabelle lesen, nie aus dem Fließtext-Ende.** Nach jedem abgeschlossenen Schritt Status hier fortschreiben.

## Auftrag (fixiert)

39 Moleküle (8 organische Stoffklassen à 4–5 Vertreter + Wasser/Cl₂/Cl•/O₂) → je **eine Sammelkarte** (Monopoli/Quartett-Layout, Mitte = Molekülbild im **japanischen Woodblock-/Bilderbuch-Stil**) + **Voll-AR** (Scan zeigt das 3D-Modell; multi-target, sodass Karten nebeneinander zusammen ihre Moleküle zeigen). Qualitative Kartendaten (Name, Formel, Stoffklasse, Merkmale) — **keine Zahlen-Stats**. Beide Bild-Dateien (Blender-Referenz + Higgsfield-Kunst) werden behalten (reproduzierbar/nachbesserbar).

**Entscheidungen (User, Sitzung 168):** Voll-AR jetzt · Woodblock via Higgsfield-img2img mit Blender-Referenz · qualitativ ohne Zahlen · alle direkt durchziehen (Votings als Gates).

## Toolchain (Phase 0 verifiziert)

| Werkzeug | Rolle | Status |
|---|---|---|
| RDKit (venv `_tools/_venvs/molgeo`) | SMILES → 3D-Koordinaten | ✓ 39/39 erzeugt |
| Blender 4.1.1 | Kugel-Stab-Modell → Render + glb | ✓ Proof Ethanol (GPU 10,8 s) |
| Higgsfield CLI | Woodblock-Kunst (img2img) | ✓ erreichbar (Credits!) |
| Inkscape 1.3.2 (voller App-Pfad) | Karten-Finalisierung (SVG→PNG) | ✓ verfügbar |
| mind-compiler (Node) | AR-Trackingbild (.mind) | ✓ vorhanden |
| webar-build.py | QR in Karte | ✓ vorhanden |

## Phasen-Status

| Phase | Inhalt | Status |
|---|---|---|
| 0 | Setup: Ordner, Spec (`molecules.json`, `atom-spec.json`), Koordinaten (39), Blender-Builder, **Proof Ethanol** | ✅ fertig |
| 0b | **Atom-Look festgelegt**: vdW-Radius × 0.25 (PyMOL/Chimera-Standard), Stab 0.14; Recherche belegt; Ethanol/Ethen/Ethin verifiziert (Einfach/Doppel/Dreifach korrekt) | ✅ fertig |
| 1 | Woodblock-Stil-Voting: 3 Entwürfe (Ukiyo-e/Bilderbuch/Sumi-e) → **Sieger: B Bilderbuch** (Jury 19; User bestätigt). Stile in `_style-voting/`, für Stil-Bibliothek vorgemerkt | ✅ fertig |
| 2 | Layout-Voting: 4 Entwürfe → **Sieger: M1 Monopoli klassisch** (User-Wahl). Entwürfe in `_layout-voting/` | ✅ fertig |
| 3 | 3D-Modelle: **39/39 gerendert + glb** in `_pipeline/modelle/<slug>/` | ✅ fertig |
| 4 | Woodblock-Kunst: 29/39 von Agenten erzeugt; Rest (10) + Recovery per `finalize-all.py` (deterministisch, idempotent) | 🔄 Batch läuft |
| 5 | Karten finalisieren: `build-card.py`; **2 Bugs gefixt** — (a) lange Formeln liefen ins AR-Feld → dynamische Schriftgröße + Formel höher; (b) Cl-Satz im Stil-Prompt ließ Nicht-Cl-Moleküle grünes Cl halluzinieren → Cl-Satz nur bei Cl-Molekülen. `finalize-all.py` baut ALLE 39 neu | 🔄 Batch läuft |
| — | **Agenten-Lehre:** die 9 Stoffklassen-Agenten nutzten async Higgsfield-Wait-Loops und meldeten teils vorzeitig „warte auf Monitor". 4 Klassen liefen dennoch komplett durch (Aldehyde/Ketone/Anorganisch/Carbonsäuren), 4 gestoppt + per Batch übernommen. Für künftige Bild-Batches: deterministisches `--wait`-Skript statt Agenten | ℹ️ |
| 6 | AR: **ein QR** → eine `targets.mind` (39 Trackingbilder) + `index.html` (maxTrack 8, Auto-Rotation, `?s=`-Regler) + 39 glbs; gepusht `a23c53f`, **live 200** unter `…/organische-Chemie/` | ✅ fertig |
| 7 | Abnahme: 7 Karten quer geprüft (alle Klassen), README + PROGRESS. Offen: Sitzungsprotokoll + Geräte-Feinjustage (`?s=`), Druck | ✅ Kern fertig |

## Artefakte / Orte

- Spec: `_spec/molecules.json` · `_atom-spec/atom-spec.json`
- Koordinaten: `_pipeline/coords/<slug>.coords.json` (39)
- Pipeline-Skripte: `_pipeline/mol-coords.py` (venv) · `_pipeline/mol-render.py` (Blender)
- Proof: `_atom-spec/_proof/ethanol_kugelstab_weiss.png` + `ethanol.glb`
- Voting: `_style-voting/` · `_layout-voting/`
- Ergebnis je Molekül (später): `<Stoffklasse>/<slug>/` (glb, render, woodblock, karte, targets.mind, index.html)

## Offene Punkte / Risiken

- Higgsfield-Credits: Stil-Voting (3 Bilder) + 39 Woodblock-Bilder = ~42+ Generierungen.
- AR-Hosting-Struktur (multi-target): eine `.mind` pro Stoffklasse (≤5 Karten) ist handhabbar; „alle 39 gleichzeitig" ist praktisch nicht nötig — Default: pro Stoffklasse eine Seite + eine QR (Multi-Target-Gerüst `05_Claude-Output/WebAR/_multi-target/` liegt bereit).
- Cl-Radikal: einzelne Cl-Kugel + „•"-Label auf der Karte.

## AR-Tracking-Untersuchung (GELÖST — Sitzung 169)

**Problem:** Mehrere beliebige Karten gleichzeitig scannen + pro Karte das RICHTIGE Modell.

**Befund (MindAR/Bild-Tracking = Sackgasse für „viele gleichzeitig"):**

| Seite | Tracking-Quelle | Ergebnis |
|---|---|---|
| `/` (v1) | 39 Karten, maxTrack 1 | einzeln sauber, aber nur eine gleichzeitig (per Design) |
| `/v2/` | Karten + Guilloché, maxTrack 5 | 2 gleichzeitig ✓ ABER Klassen-interne Verwechslung ✗ |
| `/v3wb/` | 39 Woodblock-Bilder, maxTrack 5 | Verwechslung weg ✓ ABER nur eine gleichzeitig ✗ |

MindAR (Natural Feature Tracking) skaliert prinzipiell schlecht auf viele ähnliche Targets — nicht per Parameter lösbar. **v3mini/v3wb entfernt.**

**Lösung: Pivot auf ARToolKit-Barcode-Marker (AR.js).** Fiducial-Marker sind für „viele distinkte Marker gleichzeitig" gebaut. Am Gerät bestätigt: viele beliebige Karten gleichzeitig, jeweils korrektes Modell, keine Verwechslung, positionsstabil.

**Finales Rezept (Pilot Methan+Propanon, live `…/organische-Chemie/v3/`):**
- Marker-Set: `4x4_BCH_13_9_3` (512 IDs), Marker-ID = kanonischer Molekül-Index (Methan 0 … Sauerstoff 38).
- **Layout b**: großer Marker in der Karten-Mitte, Woodblock in die Ecke (Layout a mit Ecken-Marker war zu klein → Erkennung unzuverlässig).
- **Farbe Dunkelbraun `#241A12` auf Pergament `#F7F1E1`** — scannt zuverlässig, hübscher als S/W. Marker-SVG streifenfrei per Zell-Überlappung.
- Modell über der Marker-Mitte (`position="0 0 0.3"`, `scale 0.45`, `?s=` justiert).
- **Z-Fighting-Fix Pflicht:** `renderer="… logarithmicDepthBuffer: true; precision: highp; antialias: true"` — sonst flackern die Bindungen (AR.js-Kamera hat große Near/Far-Spanne; MindAR nicht).

**Werkzeuge:** `_pipeline/build-card-v3.py` (`--layout a|b --color bw|braun --marker-png <id>.png`), `Stoffklassen-v3/_markers/gen-marker-svg.py` (Marker-SVG 2 Schemata), Marker-Sammlung `4x4_bch_13_9_3` von nicolocarpignoli/artoolkit-barcode-markers-collection.

**Offen:** (1) 39er-Ausrollung als `Stoffklassen-v3` + AR-Seite mit 39 Markern; (2) QR/Seiten-Öffner (auf Karte vertagt — QR-Muster A_styled/B_woodblock in `_qr-muster/` verworfen, evtl. Rückseite); (3) Design-Trade Layout b (Kunst nur in der Ecke) — bewusst zugunsten Funktion gewählt.


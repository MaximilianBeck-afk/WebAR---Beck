# WebAR-Sammelkarten — Design-Exploration

Vier browserbasierte AR-Sammelkarten im gemeinsamen **„Codex"-Format** (Full-Bleed-Motiv + Metadaten-Sidebar
mit Kampfwerten + Typ-Badges + QR), individuell an das jeweilige Motiv angepasst. QR scannen → Karte in die
Kamera → die Figur erscheint bewegt auf der Karte (MindAR-Bild-Tracking, A-Frame). Keine App, keine
personenbezogenen Daten — die Kamera läuft lokal im Handy.

| Karte | Thema | Sprite (Finale) | Live |
|---|---|---|---|
| `glurak/` | Feuer/Flug | bewegtes 3D-Modell | `…/Pokemon/glurak/` |
| `bisaflor/` | Pflanze/Gift | bewegtes 3D-Modell | `…/Pokemon/bisaflor/` |
| `turtok/` | Wasser | bewegtes 3D-Modell | `…/Pokemon/turtok/` |
| `ash/` | Trainer | bewegter 8-bit-Sprite (Flipbook) | `…/Pokemon/ash/` |

Jede Karte trägt beide Sprite-Varianten (2D bewegt + 3D bewegt); im WebAR ist die vom Team gewählte aktiv, die
andere liegt als Alternative bei. Pro Ordner gehostet: `index.html`, `karte-mit-qr.png` (Druck- & Trackingbild),
`targets.mind`, `qr.png`, `sprites/`.

> Interne Design-/Werkzeug-Exploration. Die Motive sind eigenständiges Fan-Artwork zur Bewertung der
> Bild-/3D-Pipeline; für einen echten Einsatz würden sie durch Eigenkreaturen oder lizenzierte Assets ersetzt.

Herkunft/Doku im Brain: `02_Projekte/Digitale-Bildung-Schule/webar/WORKFLOW.md`.

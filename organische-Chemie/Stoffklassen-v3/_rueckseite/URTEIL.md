# Rückseiten-Design — autonome Jury-Entscheidung (Sitzung 169)

**Aufgabe:** Eine Rückseite für alle 39 WebAR-Chemie-Karten — stilpassend zur Vorderseite, streng neutral (verrät KEINE Stoffgruppe), mit ruhigem Mittelfeld (~700×700) für QR **oder** AR-Marker. 3 Agenten-Entwürfe → 3-köpfige KI-Jury (unterschiedliche Schwerpunkte) → autonome Abstimmung, ohne menschliche Abnahme. Alle Entwürfe bleiben erhalten.

## Entwürfe

| # | Ordner | Konzept |
|---|---|---|
| 1 | `entwurf-1/` | Ornamental-Vintage — Guilloché-Bordüre, Eck-Arabesken, Atom-Rosette |
| 2 | `entwurf-2/` | **Minimalistisch-elegant — ein Gold-Hexagon, viel Pergament-Ruhe, feine Goldlinien** |
| 3 | `entwurf-3/` | Chemie-Emblem — Waben-/Sechseck-Gitter-Hintergrund + Atom-Ringe |

## Abstimmung

| Juror (Schwerpunkt) | Rangfolge | Sieger |
|---|---|---|
| A — Ästhetik/Wertigkeit | 2 > 3 > 1 | Entwurf 2 |
| B — Funktion (QR/Marker-Feld) | 2 > 1 > 3 | Entwurf 2 |
| C — Neutralität/Konsistenz (39×) | 2 > 1 > 3 | Entwurf 2 |

**Rangpunkte (Borda 3/2/1):** Entwurf 2 = **9** · Entwurf 1 = 5 · Entwurf 3 = 4.

## Ergebnis: **Entwurf 2 (einstimmig)**

Begründungs-Kern der Jury:
- **A:** greift Eck-Punkte + Doppellinie der Vorderseite am direktesten auf, wirkt am wertigsten und ruhigsten.
- **B:** Mittelfeld ist reines flaches Weiß, Passwinkel liegen *außerhalb* des Feldes, breite saubere Ruhezone → ideale QR-/Marker-Fläche. (Entwurf 3 fiel zurück: Waben-Muster bis an die Feldkante = keine Ruhezone; Entwurf 1: leichter Radial-Gradient + Eck-Ticks in der Ruhezone.)
- **C:** am zeitlosesten/ermüdungsfreiesten bei 39 identischen Karten; das einzelne Hexagon ist abstrakt genug, um NICHT als Benzol/Aromat zu lesen. (Entwurf 3 hatte den stärksten unbeabsichtigten Aromaten-Tell.)

Kanonisch übernommen als `_rueckseite/rueckseite.svg` + `.png`. Entwürfe 1/2/3 bleiben zum Nachschlagen erhalten.

## Offen (nächste Sitzung, a/b-Entscheidung)

Das Mittelfeld nimmt entweder auf:
- **(a) QR-Code** auf der Rückseite → Vorderseite bleibt wie jetzt (Layout b: Marker mittig).
- **(b) AR-Marker** auf der Rückseite → dann käme der QR-Code auf die Vorderseite.

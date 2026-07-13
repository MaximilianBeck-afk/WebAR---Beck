# WebAR — 3D-Modelle für den Unterricht

Öffentliches Hosting für browserbasierte AR-Modelle (Bio/Chemie, BBS). Keine App nötig,
keine personenbezogenen Daten — die Kamera läuft komplett lokal im Handy.

Läuft über **GitHub Pages** (HTTPS ist Pflicht, weil die Kamera nur auf sicheren Seiten startet).

## Modelle

- **`nacl-gitter/`** — NaCl-Ionengitter. AR auf einer gedruckten Lernkarte (MindAR-Bild-Tracking)
  plus „im Raum"-Variante (`im-raum.html`, model-viewer).

## Live-Adresse (nach Pages-Aktivierung)

```
https://maximilianbeck-afk.github.io/WebAR---Beck/
https://maximilianbeck-afk.github.io/WebAR---Beck/nacl-gitter/
```

## Neues Modell hinzufügen

1. Unterordner anlegen mit `index.html`, dem `.glb` (+ optional `.usdz`) und — bei Bild-Tracking —
   `targets.mind` (aus dem MindAR-Compiler) und einem Kartenbild.
2. In die Liste oben + in die Landing-`index.html` eintragen.
3. Committen und pushen — Pages veröffentlicht automatisch.

Quelle/Doku im Brain: `02_Projekte/Digitale-Bildung-Schule/ideen/AR-3D-Modelle-per-QR-WebAR.md`.

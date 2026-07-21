// ar-route.js — Wegpunkt-Tween: ein leuchtender Indikator wandert eine Route
// aus Modell-lokalen Wegpunkten ab (config.json: "route"). Additiv zu v2 —
// bestehende Sets ohne "route" in der Config bleiben unberührt.
//
// Warum Tween statt gebackener Blender-Animation: die Geometrie ist statisch,
// die Route bleibt ohne Neurender justierbar (nur config.json anfassen) und
// das glb bleibt klein. Eigenentwicklung, Stand 2026-07-21.
//
// Config-Format (Auszug):
//   "route": {
//     "punkte": [[x,y,z], …],        // Modell-lokale glTF-Koordinaten (Y-up),
//                                    //   Mittellinie von Eingang bis Ausgang
//     "dauer": 12,                   // Sekunden für die ganze Strecke
//     "radius": 0.09,                // Kugelradius in Modell-Einheiten
//     "farbe": "#ffd75e",
//     "replay_titel": "⟳ Ablauf nochmal"
//   }
// Kapitel-Anbindung analog zu "anim" (ar-clip): Kapitel-Def-Feld "route" mit
//   "start" (Indikator an den Anfang, pausiert), "abspielen" (einmal ablaufen,
//   am Ende halten), "ende" (ans Ende, pausiert), "pause" (anhalten).
// ar-shell.js setzt die Komponente auf die glTF-Entity, wenn die Config
// Wegpunkte enthält, und blendet den Replay-Button ein (Muster von ar-clip).
//
// Globale API (analog window.arAnim):
//   window.arRoute = { dauer, start, abspielen, pause, weiter, ende,
//                      fortschritt(), weltposition() }

(function () {
  "use strict";

  AFRAME.registerComponent("ar-route", {
    init: function () {
      var cfg = (window.AR_CFG && window.AR_CFG.route) || null;
      if (!cfg || !cfg.punkte || cfg.punkte.length < 2) return;
      this.cfg = cfg;
      this.punkte = cfg.punkte.map(function (p) {
        return new THREE.Vector3(p[0], p[1], p[2]);
      });

      // Bogenlängen aufsummieren -> konstantes Tempo entlang der Route
      this.laengen = [0];
      var L = 0;
      for (var i = 1; i < this.punkte.length; i++) {
        L += this.punkte[i].distanceTo(this.punkte[i - 1]);
        this.laengen.push(L);
      }
      this.gesamt = L;
      this.dauer = cfg.dauer || 10;
      this.t = 0;
      this.playing = false;

      // Leuchtende Kugel als Kind der glTF-Entity -> Wegpunkte sind
      // Modell-lokale Koordinaten, Skalierung/Gesten wirken automatisch mit.
      var farbe = new THREE.Color(cfg.farbe || "#ffd75e");
      this.kugel = new THREE.Mesh(
        new THREE.SphereGeometry(cfg.radius || 0.09, 24, 16),
        new THREE.MeshStandardMaterial({
          color: farbe, emissive: farbe, emissiveIntensity: 0.9,
          roughness: 0.35, metalness: 0
        })
      );
      this.el.object3D.add(this.kugel);
      this.setzeT(0);

      var self = this;
      window.arRoute = {
        dauer: this.dauer,
        start: function () { self.t = 0; self.playing = false; self.setzeT(0); },
        abspielen: function () { self.t = 0; self.playing = true; self.setzeT(0); },
        pause: function () { self.playing = false; },
        weiter: function () { self.playing = true; },
        ende: function () { self.t = self.dauer; self.playing = false; self.setzeT(self.dauer); },
        fortschritt: function () { return self.dauer ? self.t / self.dauer : 0; },
        weltposition: function () {
          var v = new THREE.Vector3();
          self.kugel.getWorldPosition(v);
          return [v.x, v.y, v.z];
        }
      };

      // Kapitel-Anbindung: arChapter feuert "ar-chapter" mit der Kapitel-Def;
      // reagiert nur, wenn die Def ein "route"-Feld trägt (sonst Zustand halten).
      window.addEventListener("ar-chapter", function (e) {
        var def = e.detail && e.detail.def;
        if (!def || !def.route || !window.arRoute) return;
        if (def.route === "abspielen") window.arRoute.abspielen();
        else if (def.route === "ende") window.arRoute.ende();
        else if (def.route === "pause") window.arRoute.pause();
        else window.arRoute.start();
      });

      window.dispatchEvent(new CustomEvent("ar-route-ready"));
    },

    // Indikator auf Zeitpunkt t setzen (Bogenlängen-Interpolation)
    setzeT: function (t) {
      var u = this.dauer ? Math.max(0, Math.min(1, t / this.dauer)) : 0;
      var s = u * this.gesamt;
      var i = 1;
      while (i < this.laengen.length - 1 && this.laengen[i] < s) i++;
      var l0 = this.laengen[i - 1], l1 = this.laengen[i];
      var f = l1 > l0 ? (s - l0) / (l1 - l0) : 0;
      this.kugel.position.lerpVectors(this.punkte[i - 1], this.punkte[i], f);
    },

    tick: function (time, dt) {
      if (!this.playing || !this.kugel) return;
      this.t += dt / 1000;
      if (this.t >= this.dauer) { this.t = this.dauer; this.playing = false; }
      this.setzeT(this.t);
    }
  });
})();

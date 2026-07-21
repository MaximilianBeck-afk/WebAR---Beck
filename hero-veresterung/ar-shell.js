// ar-shell.js — config-getriebene Seiten-Shell für die WebAR-Sets.
// Eine Set-Seite ist nur noch: A-Frame + diese Shell + config.json + models/*.glb.
// Die Shell lädt die Config, zieht die restlichen Libs nach und baut Szene, HUD,
// Hinweis und Replay-Button daraus. Eigenentwicklung, Stand 2026-07-21.
//
// Erwartet auf <body>:
//   data-ar-config = Pfad zur config.json des Sets
//   data-lib-arjs  = Pfad/URL zu AR.js (vendored /lib/… bzw. CDN in der Test-Fassung)
//   data-lib-extra = kommagetrennte Pfade weiterer Libs (gestures.js, ar-interactive.js)
//
// URL-Parameter:
//   ?test=1  Desktop-Testmodus: KEIN AR.js, keine Kamera, kein Marker — das Modell
//            steht an fester Transform, Maus dreht (ziehen) und zoomt (Rad), Klick = Tap.
//            Damit sind Tap, Highlight, Kapitel, Panels, Animation und Labels ohne
//            Druck-/Geräte-Zyklus verifizierbar. AR.js wird im Testmodus bewusst gar
//            nicht erst geladen, weil es sonst sofort die Webcam übernimmt.
//   ?s=1.5   Start-Größe (Geräte-Kalibrierung; Pinch justiert danach live)
//
// Config-Format: VORLAGEN.md im Repo-Root.

(function () {
  "use strict";

  var qs = new URLSearchParams(location.search);
  var TEST = qs.get("test") === "1";
  window.AR_TEST = TEST;

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error("Script nicht ladbar: " + src)); };
      document.head.appendChild(s);
    });
  }

  function fehler(msg) {
    var d = document.createElement("div");
    d.style.cssText = "position:fixed;inset:auto 10px 10px 10px;z-index:99;background:#8b1a2b;" +
      "color:#fff;padding:12px 16px;border-radius:10px;font:600 .9rem -apple-system,system-ui,sans-serif;";
    d.textContent = msg;
    document.body.appendChild(d);
  }

  // Maus-Orbit für den Testmodus: ziehen dreht das Modell, Rad zoomt.
  // Wird erst nach dem A-Frame-Load registriert (AFRAME existiert dann sicher).
  function registerTestOrbit() {
    if (AFRAME.components["test-orbit"]) return;
    AFRAME.registerComponent("test-orbit", {
      init: function () {
        var o = this.el.object3D, drag = null;
        window.addEventListener("mousedown", function (e) { drag = { x: e.clientX, y: e.clientY }; });
        window.addEventListener("mouseup", function () { drag = null; });
        window.addEventListener("mousemove", function (e) {
          if (!drag) return;
          o.rotation.y += (e.clientX - drag.x) * 0.008;
          o.rotation.x += (e.clientY - drag.y) * 0.008;
          drag = { x: e.clientX, y: e.clientY };
        });
        window.addEventListener("wheel", function (e) {
          var f = e.deltaY < 0 ? 1.08 : 1 / 1.08;
          o.scale.multiplyScalar(f);
        }, { passive: true });
      }
    });
  }

  function buildHud(cfg) {
    if (!cfg.kapitel || !cfg.kapitel.length) return;
    var hud = document.createElement("div");
    hud.id = "ar-hud";
    cfg.kapitel.forEach(function (k) {
      var b = document.createElement("button");
      b.dataset.chapter = k.id;
      b.textContent = k.titel;
      b.addEventListener("click", function () { window.arChapter(k.id); });
      hud.appendChild(b);
    });
    document.body.appendChild(hud);
  }

  function buildHinweis(cfg) {
    var d = document.createElement("div");
    d.id = "hinweis";
    d.style.cssText = "position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:10;" +
      "background:rgba(20,20,26,.82);color:#fff;padding:.6em 1em;border-radius:999px;" +
      "font:400 .88rem -apple-system,system-ui,sans-serif;max-width:90vw;text-align:center;pointer-events:none;";
    d.textContent = TEST
      ? "Testmodus — ziehen: drehen · Mausrad: zoomen · klicken: antippen"
      : (cfg.hinweis || "Kamera auf die Karte richten · leuchtende Punkte antippen");
    document.body.appendChild(d);
  }

  function buildReplay(cfg) {
    if (!cfg.animation) return;
    var b = document.createElement("button");
    b.id = "ar-replay";
    b.textContent = cfg.animation.replay_titel || "⟳ nochmal abspielen";
    b.addEventListener("click", function () {
      if (window.arAnim) window.arAnim.abspielen();
    });
    document.body.appendChild(b);
    window.addEventListener("ar-chapter", function (e) {
      var def = e.detail.def;
      b.classList.toggle("show", !!(def && def.anim === "abspielen" && window.arAnim));
    });
  }

  function buildScene(cfg) {
    var scene = document.createElement("a-scene");
    scene.setAttribute("vr-mode-ui", "enabled: false");
    scene.setAttribute("device-orientation-permission-ui", "enabled: false");
    scene.setAttribute("renderer",
      "colorManagement: true; physicallyCorrectLights: true; logarithmicDepthBuffer: true; " +
      "antialias: true; precision: highp; sortObjects: true");
    scene.setAttribute("tap-picker", "");
    scene.setAttribute("ar-labels", "");

    if (!TEST) {
      scene.setAttribute("embedded", "");
      scene.setAttribute("gesture-detector", "");
      scene.setAttribute("arjs",
        "trackingMethod: best; sourceType: webcam; detectionMode: mono_and_matrix; " +
        "matrixCodeType: 4x4_BCH_13_9_3; debugUIEnabled: false;");
    } else {
      scene.setAttribute("background", "color: #15151c");
    }

    // Modell-Wrapper (Basis-Größe, Gesten, Position) + glTF-Entity mit Mesh-/Clip-Schicht
    var mod = cfg.modell || {};
    var basis = mod.basis_skalierung || 1;
    var f = parseFloat(qs.get("s"));
    if (f && f > 0) basis *= f;

    var wrap = document.createElement("a-entity");
    wrap.classList.add("mol-group");
    wrap.dataset.base = String(mod.basis_skalierung || 1);
    wrap.setAttribute("scale", basis + " " + basis + " " + basis);
    wrap.setAttribute("position", TEST ? "0 0 -2.6" : (mod.position || "0 0 0.3"));
    if (mod.rotation) wrap.setAttribute("rotation", mod.rotation);
    if (TEST) wrap.setAttribute("test-orbit", "");
    else wrap.setAttribute("gesture-handler", "");

    var gltf = document.createElement("a-entity");
    gltf.setAttribute("gltf-model", "url(" + mod.src + ")");
    gltf.setAttribute("mesh-hotspots", "");
    gltf.setAttribute("ar-clip", "");
    wrap.appendChild(gltf);

    (cfg.punkt_hotspots || []).forEach(function (h) {
      var e = document.createElement("a-entity");
      e.setAttribute("position", h.position);
      // Objekt-Form statt Semikolon-String: Panel-Texte dürfen so jede Interpunktion tragen
      e.setAttribute("hotspot", {
        title: h.titel || "", text: h.text || "", fact: h.fakt || "",
        label: h.label || "", color: h.farbe || "#ff4d67",
        radius: h.radius || 0.08, group: h.kapitel || ""
      });
      wrap.appendChild(e);
    });

    if (TEST) {
      scene.appendChild(wrap);
    } else {
      var marker = document.createElement("a-marker");
      marker.setAttribute("type", cfg.marker && cfg.marker.typ || "barcode");
      marker.setAttribute("value", String(cfg.marker && cfg.marker.wert));
      marker.appendChild(wrap);
      scene.appendChild(marker);
    }

    var cam = document.createElement("a-entity");
    cam.setAttribute("camera", "");
    scene.appendChild(cam);

    document.body.appendChild(scene);
    return scene;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var b = document.body;
    var cfgUrl = b.dataset.arConfig || "config.json";

    fetch(cfgUrl)
      .then(function (r) {
        if (!r.ok) throw new Error("config.json: HTTP " + r.status);
        return r.json();
      })
      .then(function (cfg) {
        window.AR_CFG = cfg;
        if (cfg.titel) document.title = cfg.titel;

        // Kapitel-Definitionen für arChapter bereitstellen
        if (cfg.kapitel && cfg.kapitel.length) {
          window.arChapterDefs = {};
          cfg.kapitel.forEach(function (k) { window.arChapterDefs[k.id] = k; });
        }

        var libs = (b.dataset.libExtra || "").split(",").map(function (s) { return s.trim(); })
          .filter(Boolean);
        if (!TEST && b.dataset.libArjs) libs.unshift(b.dataset.libArjs);

        return libs.reduce(function (p, src) {
          return p.then(function () { return loadScript(src); });
        }, Promise.resolve()).then(function () { return cfg; });
      })
      .then(function (cfg) {
        if (TEST) registerTestOrbit();
        buildHud(cfg);
        buildHinweis(cfg);
        buildReplay(cfg);
        var scene = buildScene(cfg);
        var startKapitel = function () {
          if (cfg.kapitel && cfg.kapitel.length) {
            window.arChapter(cfg.start_kapitel || cfg.kapitel[0].id);
          }
        };
        if (scene.hasLoaded) startKapitel();
        else scene.addEventListener("loaded", startKapitel);
        // Kapitel mit Animations-Zustand ggf. nachziehen, sobald der Mixer steht
        window.addEventListener("ar-anim-ready", function () {
          var active = document.querySelector("#ar-hud button.active");
          if (active && window.arChapterDefs) {
            var def = window.arChapterDefs[active.dataset.chapter];
            if (def && def.anim && def.anim !== "start") window.arChapter(def.id);
          }
        });
      })
      .catch(function (err) {
        console.error(err);
        fehler("Diese AR-Seite konnte nicht geladen werden (" + err.message + "). " +
          "Bitte Verbindung prüfen und neu laden.");
      });
  });
})();

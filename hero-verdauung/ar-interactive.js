// ar-interactive.js — Interaktions-Schicht für die WebAR-Karten (v2, config-getrieben).
// Bausteine: Tap-Hotspots (Kugeln), echtes Sub-Mesh-Raycasting + -Highlight, Info-Panels,
// Beschriftungs-Modus (projizierte DOM-Labels), Kapitel-HUD, Animations-Player für baked
// glTF-Clips (ein Mixer, alle Clips gemeinsam, mit Seek auf Start-/Endzustand).
// Eigenentwicklung. Nutzt ausschließlich A-Frame 1.3 + das darin gebündelte three.js.
//
// v1 (2026-07): Kugel-Hotspots, tap-picker, ar-labels, arChapter.
// v2 (2026-07-21): mesh-hotspots (Tap trifft die echte Teil-Geometrie, Emissive-Highlight),
//                  ar-clip (Animations-Player), Kapitel-Definitionen aus config.json,
//                  Maus-Tap nur ohne Drag (Desktop-Testmodus ?test=1 via ar-shell.js).
//
// Verwendung siehe s/pilot-a-hero/ und PILOTEN.md; Config-Format: VORLAGEN.md im Repo-Root.

(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // Basis-CSS einmalig injizieren (Panel, Labels, HUD) — hält die Seiten schlank
  // ---------------------------------------------------------------------------
  function injectCss() {
    if (document.getElementById("ar-interactive-css")) return;
    var s = document.createElement("style");
    s.id = "ar-interactive-css";
    s.textContent = [
      "#ar-panel{position:fixed;left:50%;bottom:18px;transform:translateX(-50%) translateY(140%);",
      "z-index:20;width:min(92vw,420px);background:rgba(20,20,26,.94);color:#fff;border-radius:16px;",
      "padding:16px 18px 18px;box-shadow:0 8px 30px rgba(0,0,0,.4);transition:transform .28s ease;",
      "font-family:-apple-system,system-ui,sans-serif;}",
      "#ar-panel.show{transform:translateX(-50%) translateY(0);}",
      "#ar-panel h2{margin:.1em 2rem .3em 0;font-size:1.15rem;}",
      "#ar-panel p{margin:.2em 0;font-size:.95rem;line-height:1.4;}",
      "#ar-panel-fact{margin-top:.7em;padding:.55em .7em;background:rgba(255,205,80,.16);",
      "border-left:3px solid #ffcd50;border-radius:6px;font-size:.88rem;}",
      "#ar-panel-close{position:absolute;top:8px;right:10px;width:32px;height:32px;border:none;",
      "background:rgba(255,255,255,.12);color:#fff;border-radius:50%;font-size:1.3rem;line-height:1;",
      "cursor:pointer;}",
      ".ar-label{position:fixed;z-index:15;transform:translate(-50%,-50%);pointer-events:none;",
      "background:rgba(20,20,26,.82);color:#fff;padding:.18em .55em;border-radius:999px;",
      "font:600 .8rem -apple-system,system-ui,sans-serif;white-space:nowrap;display:none;}",
      ".ar-label.show{display:block;}",
      "#ar-hud{position:fixed;left:0;right:0;top:14px;z-index:18;display:flex;gap:8px;justify-content:center;",
      "flex-wrap:wrap;padding:0 10px;}",
      "#ar-hud button{background:rgba(20,20,26,.82);color:#fff;border:1px solid rgba(255,255,255,.18);",
      "border-radius:999px;padding:.5em .9em;font:600 .85rem -apple-system,system-ui,sans-serif;cursor:pointer;}",
      "#ar-hud button.active{background:#ff4d67;border-color:#ff4d67;}",
      "#ar-replay{position:fixed;right:14px;bottom:76px;z-index:18;display:none;",
      "background:rgba(20,20,26,.88);color:#fff;border:1px solid rgba(255,255,255,.25);",
      "border-radius:999px;padding:.55em 1em;font:600 .9rem -apple-system,system-ui,sans-serif;cursor:pointer;}",
      "#ar-replay.show{display:block;}"
    ].join("");
    document.head.appendChild(s);
  }

  // ---------------------------------------------------------------------------
  // Info-Panel (ein globales DOM-Overlay)
  // ---------------------------------------------------------------------------
  function ensurePanel() {
    injectCss();
    var p = document.getElementById("ar-panel");
    if (p) return p;
    p = document.createElement("div");
    p.id = "ar-panel";
    p.innerHTML =
      '<button id="ar-panel-close" aria-label="schließen">&times;</button>' +
      '<h2 id="ar-panel-title"></h2>' +
      '<p id="ar-panel-text"></p>' +
      '<div id="ar-panel-fact"></div>';
    document.body.appendChild(p);
    p.querySelector("#ar-panel-close").addEventListener("click", hidePanel);
    return p;
  }
  function showPanel(title, text, fact) {
    var p = ensurePanel();
    p.querySelector("#ar-panel-title").textContent = title || "";
    p.querySelector("#ar-panel-text").textContent = text || "";
    var f = p.querySelector("#ar-panel-fact");
    if (fact) { f.textContent = fact; f.style.display = "block"; }
    else { f.style.display = "none"; }
    p.classList.add("show");
  }
  function hidePanel() {
    var p = document.getElementById("ar-panel");
    if (p) p.classList.remove("show");
    clearMeshHighlight();
  }
  window.arHidePanel = hidePanel;

  // ---------------------------------------------------------------------------
  // Mesh-Registry: Gruppen echter Teil-Geometrie (benannte glb-Nodes) mit
  // Panel-Inhalt, Label und Kapitel-Zuordnung. Gefüllt von mesh-hotspots.
  // ---------------------------------------------------------------------------
  var meshReg = {
    groups: [],        // { cfg, objects[], labelAnchor }
    ready: false,
    chapter: "",       // aktives Kapitel (für Tap-/Label-Filter)
    showAll: true
  };
  window.arMeshRegistry = meshReg; // für Tests/Diagnose lesbar

  function groupActive(g) {
    var k = g.cfg.kapitel || "";
    return meshReg.showAll || !k || k === meshReg.chapter;
  }

  var highlighted = []; // aktuell eingefärbte THREE.Mesh
  function clearMeshHighlight() {
    highlighted.forEach(function (m) {
      if (m.userData._origMat) m.material = m.userData._origMat;
    });
    highlighted = [];
  }
  window.arClearMeshHighlight = clearMeshHighlight;

  function highlightGroup(g) {
    clearMeshHighlight();
    var farbe = new THREE.Color(g.cfg.farbe || "#ff4d67");
    g.objects.forEach(function (root) {
      root.traverse(function (m) {
        if (!m.isMesh) return;
        if (!m.userData._origMat) m.userData._origMat = m.material;
        if (!m.userData._hlMat) {
          // Klon pro Mesh-Instanz: glTF teilt Materialien (alle C-Atome eine Instanz);
          // ohne Klon würden alle Geschwister mitleuchten.
          m.userData._hlMat = m.userData._origMat.clone();
        }
        var hm = m.userData._hlMat;
        if (hm.emissive) {
          hm.emissive.copy(farbe);
          hm.emissiveIntensity = 0.85;
        } else {
          hm.color = farbe.clone();
        }
        m.material = hm;
        highlighted.push(m);
      });
    });
  }

  // ---------------------------------------------------------------------------
  // mesh-hotspots: auf die glTF-Entity setzen. Liest die Gruppen-Definitionen
  // (knoten → Panel-Inhalt) und löst sie nach model-loaded gegen die echten
  // Objekt-Namen des glb auf. Namen matchen exakt oder als Präfix mit "*".
  // Map kommt aus window.AR_CFG.mesh_hotspots (ar-shell) oder per setMap().
  // ---------------------------------------------------------------------------
  AFRAME.registerComponent("mesh-hotspots", {
    init: function () {
      var self = this;
      this.map = (window.AR_CFG && window.AR_CFG.mesh_hotspots) || [];
      this.el.addEventListener("model-loaded", function () { self.resolve(); });
    },
    setMap: function (map) {
      this.map = map || [];
      if (this.el.getObject3D("mesh")) this.resolve();
    },
    resolve: function () {
      var model = this.el.getObject3D("mesh");
      if (!model || !this.map.length) return;
      meshReg.groups = [];
      this.map.forEach(function (cfg) {
        var objects = [];
        (cfg.knoten || []).forEach(function (pattern) {
          if (pattern.slice(-1) === "*") {
            var prefix = pattern.slice(0, -1);
            model.traverse(function (o) {
              if (o.name && o.name.indexOf(prefix) === 0) objects.push(o);
            });
          } else {
            var o = model.getObjectByName(pattern);
            if (o) objects.push(o);
            else console.warn("[mesh-hotspots] Knoten nicht im Modell:", pattern);
          }
        });
        if (!objects.length) {
          console.warn("[mesh-hotspots] Gruppe ohne Treffer:", cfg.id || cfg.titel);
          return;
        }
        // Label-Anker = erster Knoten der Liste (Konvention: zentrales Atom zuerst nennen)
        meshReg.groups.push({ cfg: cfg, objects: objects, labelAnchor: objects[0] });
      });
      meshReg.ready = true;
      window.dispatchEvent(new CustomEvent("ar-mesh-ready"));
    },
    activate: function (g) {
      highlightGroup(g);
      showPanel(g.cfg.titel, g.cfg.text, g.cfg.fakt);
    }
  });

  // ---------------------------------------------------------------------------
  // Hotspot: kleine leuchtende Kugel an fester Position (relativ zur Gruppe),
  // per Tap anklickbar → öffnet Info-Panel, Highlight-Puls. (Punkt-Variante,
  // weiterhin für Positionen ohne eigene Teil-Geometrie.)
  // ---------------------------------------------------------------------------
  AFRAME.registerComponent("hotspot", {
    schema: {
      title: { default: "" },
      text: { default: "" },
      fact: { default: "" },
      label: { default: "" },      // Kurztext für den Beschriftungs-Modus
      color: { default: "#ff4d67" },
      radius: { default: 0.08 },
      group: { default: "" }        // Kapitel-Zuordnung (HUD)
    },
    init: function () {
      var el = this.el;
      el.setAttribute("geometry", "primitive: sphere; radius: " + this.data.radius);
      el.setAttribute("material",
        "color: " + this.data.color + "; emissive: " + this.data.color +
        "; emissiveIntensity: 0.55; metalness: 0.1; roughness: 0.5");
      el.classList.add("hotspot");
      el.setAttribute("animation__pulse",
        "property: scale; dir: alternate; dur: 900; loop: true; from: 1 1 1; to: 1.3 1.3 1.3");
      if (this.data.group) el.dataset.group = this.data.group;
    },
    activate: function () {
      clearMeshHighlight();
      showPanel(this.data.title, this.data.text, this.data.fact);
      var el = this.el;
      el.setAttribute("material", "emissiveIntensity", 1.0);
      clearTimeout(this._t);
      this._t = setTimeout(function () {
        el.setAttribute("material", "emissiveIntensity", 0.55);
      }, 1400);
    }
  });

  // ---------------------------------------------------------------------------
  // tap-picker: unterscheidet Tap von Dreh-/Zoom-Geste und raycastet auf
  // Kugel-Hotspots UND Mesh-Gruppen (nächster Treffer gewinnt).
  // Auf die <a-scene> setzen.
  // ---------------------------------------------------------------------------
  AFRAME.registerComponent("tap-picker", {
    init: function () {
      this.raycaster = new THREE.Raycaster();
      this.ndc = new THREE.Vector2();
      this.start = null;
      this.sceneEl = this.el.sceneEl;
      this.onStart = this.onStart.bind(this);
      this.onEnd = this.onEnd.bind(this);
      window.addEventListener("touchstart", this.onStart, { passive: true });
      window.addEventListener("touchend", this.onEnd, { passive: true });
      // Desktop (Maus): Klick nur ohne Drag werten, sonst frisst jedes
      // Dreh-Ziehen im Testmodus am Ende ein ungewolltes Tap.
      var self = this;
      window.addEventListener("mousedown", function (e) {
        self.start = { x: e.clientX, y: e.clientY, t: Date.now(), n: 1 };
      });
      window.addEventListener("mouseup", function (e) {
        var st = self.start; self.start = null;
        if (!st) return;
        if (Math.hypot(e.clientX - st.x, e.clientY - st.y) < 8) {
          self.tryPick(e.clientX, e.clientY);
        }
      });
    },
    onStart: function (e) {
      var t = e.touches[0];
      this.start = { x: t.clientX, y: t.clientY, t: Date.now(), n: e.touches.length };
    },
    onEnd: function (e) {
      var st = this.start; this.start = null;
      if (!st || st.n !== 1) return;
      var ct = e.changedTouches && e.changedTouches[0];
      if (!ct) return;
      var moved = Math.hypot(ct.clientX - st.x, ct.clientY - st.y);
      var dt = Date.now() - st.t;
      if (moved < 16 && dt < 450) this.tryPick(ct.clientX, ct.clientY);
    },
    tryPick: function (cx, cy) {
      var cam = this.sceneEl.camera;
      if (!cam) return;
      this.ndc.set((cx / window.innerWidth) * 2 - 1, -(cy / window.innerHeight) * 2 + 1);
      this.raycaster.setFromCamera(this.ndc, cam);

      // Kandidaten: sichtbare Kugel-Hotspots + Objekte aktiver Mesh-Gruppen
      var els = [].slice.call(document.querySelectorAll(".hotspot")).filter(function (el) {
        return el.getAttribute("visible") !== false && el.object3D && el.object3D.visible;
      });
      var objs = els.map(function (el) { return el.object3D; });
      var groups = meshReg.groups.filter(groupActive);
      groups.forEach(function (g) {
        g.objects.forEach(function (o) { objs.push(o); });
      });
      if (!objs.length) return;

      var hits = this.raycaster.intersectObjects(objs, true);
      if (!hits.length) return;

      // Besitzer des nächstliegenden Treffers finden (Kugel-Hotspot oder Mesh-Gruppe)
      var obj = hits[0].object;
      while (obj) {
        for (var i = 0; i < els.length; i++) {
          if (els[i].object3D === obj) {
            els[i].components.hotspot.activate();
            return;
          }
        }
        for (var j = 0; j < groups.length; j++) {
          if (groups[j].objects.indexOf(obj) !== -1) {
            var mh = document.querySelector("[mesh-hotspots]");
            if (mh) mh.components["mesh-hotspots"].activate(groups[j]);
            return;
          }
        }
        obj = obj.parent;
      }
    }
  });

  // ---------------------------------------------------------------------------
  // ar-labels: Beschriftungs-Modus. Projiziert Kugel-Hotspots UND Mesh-Gruppen
  // pro Frame auf den Bildschirm und positioniert DOM-Labels.
  // Toggle über window.arToggleLabels(). Auf die <a-scene> setzen.
  // ---------------------------------------------------------------------------
  AFRAME.registerComponent("ar-labels", {
    init: function () {
      injectCss();
      this.enabled = false;
      this.map = [];   // { obj (THREE.Object3D), el (optional, für Sichtbarkeits-Check), dom }
      this.v = new THREE.Vector3();
      var self = this;
      window.arToggleLabels = function (on) {
        self.enabled = (typeof on === "boolean") ? on : !self.enabled;
        if (!self.enabled) self.map.forEach(function (m) { m.dom.classList.remove("show"); });
        return self.enabled;
      };
      // Mesh-Gruppen kommen ggf. nach dem ersten Aufbau dazu → neu bauen
      window.addEventListener("ar-mesh-ready", function () { self.teardown(); });
    },
    teardown: function () {
      this.map.forEach(function (m) { m.dom.remove(); });
      this.map = [];
      this._built = false;
    },
    build: function () {
      var self = this;
      function add(txt, obj, el, group) {
        if (!txt) return;
        var dom = document.createElement("div");
        dom.className = "ar-label";
        dom.textContent = txt;
        document.body.appendChild(dom);
        self.map.push({ obj: obj, el: el, group: group, dom: dom });
      }
      [].slice.call(document.querySelectorAll(".hotspot")).forEach(function (el) {
        var d = el.components.hotspot && el.components.hotspot.data;
        if (d) add(d.label || d.title, el.object3D, el, null);
      });
      meshReg.groups.forEach(function (g) {
        add(g.cfg.label || g.cfg.titel, g.labelAnchor, null, g);
      });
      this._built = true;
    },
    tick: function () {
      if (!this.enabled) return;
      if (!this._built) this.build();
      var cam = this.el.sceneEl.camera;
      if (!cam) return;
      var w = window.innerWidth, h = window.innerHeight;
      for (var i = 0; i < this.map.length; i++) {
        var m = this.map[i];
        var visible = m.obj && m.obj.visible;
        if (m.el) visible = visible && m.el.object3D.visible;
        if (m.group) visible = visible && groupActive(m.group);
        if (!visible) { m.dom.classList.remove("show"); continue; }
        m.obj.getWorldPosition(this.v);
        this.v.project(cam);
        if (this.v.z > 1) { m.dom.classList.remove("show"); continue; } // hinter Kamera
        m.dom.style.left = ((this.v.x * 0.5 + 0.5) * w) + "px";
        m.dom.style.top = ((-this.v.y * 0.5 + 0.5) * h) + "px";
        m.dom.classList.add("show");
      }
    }
  });

  // ---------------------------------------------------------------------------
  // ar-clip: Animations-Player für baked glTF-Clips. Die Blender-Pipeline
  // exportiert EINEN Clip PRO Objekt (A_C1Action, B_…Action) — alle Clips
  // laufen darum gemeinsam auf einem Mixer. Zustände:
  //   arAnim.start()     → Anfangszustand (t=0, pausiert)  = Edukte
  //   arAnim.abspielen() → einmal abspielen, am Ende halten
  //   arAnim.ende()      → Endzustand (t=Dauer, pausiert)  = Produkte
  // Auf die glTF-Entity setzen.
  // ---------------------------------------------------------------------------
  AFRAME.registerComponent("ar-clip", {
    init: function () {
      var self = this;
      this.mixer = null;
      this.actions = [];
      this.dauer = 0;
      this.el.addEventListener("model-loaded", function (e) {
        var model = e.detail.model || self.el.getObject3D("mesh");
        var clips = (model && model.animations) || [];
        if (!clips.length) return;
        self.mixer = new THREE.AnimationMixer(model);
        self.dauer = 0;
        clips.forEach(function (clip) {
          var a = self.mixer.clipAction(clip);
          a.setLoop(THREE.LoopOnce);
          a.clampWhenFinished = true;
          self.actions.push(a);
          if (clip.duration > self.dauer) self.dauer = clip.duration;
        });
        window.arAnim = {
          dauer: self.dauer,
          seek: function (t, paused) {
            self.actions.forEach(function (a) {
              a.reset().play();
              a.paused = !!paused;
              a.time = t;
            });
            self.mixer.update(0); // Pose sofort anwenden, auch pausiert
          },
          start: function () { window.arAnim.seek(0, true); },
          ende: function () { window.arAnim.seek(self.dauer - 1e-4, true); },
          abspielen: function () { window.arAnim.seek(0, false); }
        };
        window.arAnim.start();
        window.dispatchEvent(new CustomEvent("ar-anim-ready"));
      });
    },
    tick: function (t, dt) {
      if (this.mixer) this.mixer.update(dt / 1000);
    }
  });

  // ---------------------------------------------------------------------------
  // Kapitel-Schaltung. Kapitel-Definitionen kommen aus der Config
  // (window.arChapterDefs = { id: {id, titel, beschriftung, anim} }); ohne
  // Definitionen gilt das v1-Verhalten (alle/uebersicht = alles sichtbar,
  // Labels nur im Kapitel "alle").
  // ---------------------------------------------------------------------------
  window.arChapterDefs = window.arChapterDefs || null;
  window.arChapter = function (name) {
    hidePanel();
    var def = (window.arChapterDefs && window.arChapterDefs[name]) || null;
    var showAll = (name === "alle" || name === "uebersicht" || name === "");

    // Kugel-Hotspots: Sichtbarkeit nach Kapitel-Gruppe
    var spots = [].slice.call(document.querySelectorAll(".hotspot"));
    spots.forEach(function (el) {
      var g = el.dataset.group || "";
      el.setAttribute("visible", showAll || g === name);
    });

    // Mesh-Gruppen: Tap-/Label-Filter (echte Geometrie bleibt natürlich sichtbar)
    meshReg.chapter = name;
    meshReg.showAll = showAll;

    // Beschriftungs-Modus
    var labelsOn = def ? !!def.beschriftung : (name === "alle");
    if (window.arToggleLabels) window.arToggleLabels(labelsOn);

    // Animations-Zustand des Kapitels
    if (def && def.anim && window.arAnim) {
      if (def.anim === "abspielen") window.arAnim.abspielen();
      else if (def.anim === "ende") window.arAnim.ende();
      else window.arAnim.start();
    }

    var btns = document.querySelectorAll("#ar-hud button");
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.toggle("active", btns[i].dataset.chapter === name);
    }
    window.dispatchEvent(new CustomEvent("ar-chapter", { detail: { name: name, def: def } }));
  };
})();

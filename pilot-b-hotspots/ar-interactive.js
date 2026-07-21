// ar-interactive.js — Interaktions-Schicht für die WebAR-Karten (Pilot der kivicube-Funktionen).
// Bausteine: Tap-Hotspots, aufklappende 2D-Info-Panels, Auswahl-Highlight, Beschriftungs-Modus (Labels),
// dazu HUD-Helfer. Eigenentwicklung, Ergänzung zur Pipeline, Stand 2026-07.
// Nutzt ausschließlich A-Frame 1.3 + das darin gebündelte three.js — keine externen Abos/Libs.
//
// Verwendung siehe s/pilot-a-hero/ und s/pilot-b-hotspots/ sowie PILOTEN.md.

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
      "#ar-hud button.active{background:#ff4d67;border-color:#ff4d67;}"
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
  }
  window.arHidePanel = hidePanel;

  // ---------------------------------------------------------------------------
  // Hotspot: kleine leuchtende Kugel an fester Position (relativ zur Gruppe),
  // per Tap anklickbar → öffnet Info-Panel, Highlight-Puls.
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
      showPanel(this.data.title, this.data.text, this.data.fact);
      var el = this.el, self = this;
      el.setAttribute("material", "emissiveIntensity", 1.0);
      clearTimeout(this._t);
      this._t = setTimeout(function () {
        el.setAttribute("material", "emissiveIntensity", 0.55);
      }, 1400);
    }
  });

  // ---------------------------------------------------------------------------
  // tap-picker: unterscheidet Tap von Dreh-/Zoom-Geste und raycastet auf Hotspots.
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
      // Desktop-Test (Maus)
      var self = this;
      window.addEventListener("mousedown", function (e) {
        self.start = { x: e.clientX, y: e.clientY, t: Date.now(), n: 1 };
      });
      window.addEventListener("mouseup", function (e) {
        if (self.start) { self.start = null; self.tryPick(e.clientX, e.clientY); }
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
      var els = [].slice.call(document.querySelectorAll(".hotspot")).filter(function (el) {
        return el.getAttribute("visible") !== false && el.object3D && el.object3D.visible;
      });
      var objs = els.map(function (el) { return el.object3D; });
      var hits = this.raycaster.intersectObjects(objs, true);
      if (!hits.length) return;
      var obj = hits[0].object, target = null;
      while (obj && !target) {
        for (var i = 0; i < els.length; i++) {
          if (els[i].object3D === obj) { target = els[i]; break; }
        }
        obj = obj.parent;
      }
      if (target && target.components.hotspot) target.components.hotspot.activate();
    }
  });

  // ---------------------------------------------------------------------------
  // ar-labels: Beschriftungs-Modus. Projiziert jeden Hotspot pro Frame auf den
  // Bildschirm und positioniert ein DOM-Label. Toggle über window.arToggleLabels().
  // Auf die <a-scene> setzen.
  // ---------------------------------------------------------------------------
  AFRAME.registerComponent("ar-labels", {
    init: function () {
      injectCss();
      this.enabled = false;
      this.map = [];   // { el, dom }
      this.v = new THREE.Vector3();
      var self = this;
      window.arToggleLabels = function (on) {
        self.enabled = (typeof on === "boolean") ? on : !self.enabled;
        if (!self.enabled) self.map.forEach(function (m) { m.dom.classList.remove("show"); });
        return self.enabled;
      };
      // Labels lazy beim ersten Aktivieren aufbauen (Hotspots existieren dann sicher)
    },
    build: function () {
      var els = [].slice.call(document.querySelectorAll(".hotspot"));
      var self = this;
      els.forEach(function (el) {
        var txt = (el.components.hotspot && el.components.hotspot.data.label) ||
                  (el.components.hotspot && el.components.hotspot.data.title) || "";
        if (!txt) return;
        var dom = document.createElement("div");
        dom.className = "ar-label";
        dom.textContent = txt;
        document.body.appendChild(dom);
        self.map.push({ el: el, dom: dom });
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
        var visible = m.el.object3D && m.el.object3D.visible;
        if (!visible) { m.dom.classList.remove("show"); continue; }
        m.el.object3D.getWorldPosition(this.v);
        this.v.project(cam);
        if (this.v.z > 1) { m.dom.classList.remove("show"); continue; } // hinter Kamera
        m.dom.style.left = ((this.v.x * 0.5 + 0.5) * w) + "px";
        m.dom.style.top = ((-this.v.y * 0.5 + 0.5) * h) + "px";
        m.dom.classList.add("show");
      }
    }
  });

  // ---------------------------------------------------------------------------
  // HUD-Helfer: schaltet Kapitel (Hotspot-Gruppen) sichtbar. Rein DOM-getrieben,
  // die Seite ruft arChapter(name) aus den HUD-Buttons.
  // ---------------------------------------------------------------------------
  window.arChapter = function (name) {
    hidePanel();
    var showAll = (name === "alle" || name === "uebersicht" || name === "");
    var spots = [].slice.call(document.querySelectorAll(".hotspot"));
    spots.forEach(function (el) {
      var g = el.dataset.group || "";
      el.setAttribute("visible", showAll || g === name);
    });
    // Beschriftungs-Modus nur im Kapitel "alle"
    if (window.arToggleLabels) window.arToggleLabels(name === "alle");
    var btns = document.querySelectorAll("#ar-hud button");
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.toggle("active", btns[i].dataset.chapter === name);
    }
  };
})();

// gestures.js — Touch-Gesten fuer AR-Seiten: 1 Finger drehen, 2 Finger zoomen.
// Eigenentwicklung (Bestandteil der WebAR-Pipeline), Stand 2026-07.
    // --- Touch-Gesten: 1 Finger = drehen, 2 Finger = zoomen (kein Verschieben) ---
    AFRAME.registerComponent("gesture-detector", {
      schema: { element: { default: "" } },
      init: function () {
        this.targetElement = (this.data.element && document.querySelector(this.data.element)) || this.el;
        this.internalState = { previousState: null };
        this.emitGestureEvent = this.emitGestureEvent.bind(this);
        this.targetElement.addEventListener("touchstart", this.emitGestureEvent);
        this.targetElement.addEventListener("touchend", this.emitGestureEvent);
        this.targetElement.addEventListener("touchmove", this.emitGestureEvent);
      },
      emitGestureEvent: function (event) {
        const currentState = this.getTouchState(event);
        const previousState = this.internalState.previousState;
        const gestureContinues = previousState && currentState && currentState.touchCount == previousState.touchCount;
        const gestureEnded = previousState && !gestureContinues;
        const gestureStarted = currentState && !gestureContinues;
        if (gestureEnded) {
          this.el.emit(this.getEventPrefix(previousState.touchCount) + "fingerend", previousState);
          this.internalState.previousState = null;
        }
        if (gestureStarted) {
          currentState.startPosition = currentState.position;
          currentState.startSpread = currentState.spread;
          this.el.emit(this.getEventPrefix(currentState.touchCount) + "fingerstart", currentState);
          this.internalState.previousState = currentState;
        }
        if (gestureContinues) {
          const detail = { positionChange: {
              x: currentState.position.x - previousState.position.x,
              y: currentState.position.y - previousState.position.y } };
          if (currentState.spread) detail.spreadChange = currentState.spread - previousState.spread;
          Object.assign(previousState, currentState);
          Object.assign(detail, previousState);
          this.el.emit(this.getEventPrefix(currentState.touchCount) + "fingermove", detail);
        }
      },
      getTouchState: function (event) {
        if (event.touches.length === 0) return null;
        const touches = [];
        for (let i = 0; i < event.touches.length; i++) touches.push(event.touches[i]);
        const cx = touches.reduce((s, t) => s + t.clientX, 0) / touches.length;
        const cy = touches.reduce((s, t) => s + t.clientY, 0) / touches.length;
        const scale = 2 / (window.innerWidth + window.innerHeight);
        const st = { touchCount: touches.length, position: { x: cx * scale, y: cy * scale } };
        if (touches.length >= 2) {
          const spread = touches.reduce((s, t) => s + Math.hypot(t.clientX - cx, t.clientY - cy), 0) / touches.length;
          st.spread = spread * scale;
        }
        return st;
      },
      getEventPrefix: function (n) { return ["one", "two", "three", "many"][Math.min(n, 4) - 1]; },
    });

    AFRAME.registerComponent("gesture-handler", {
      schema: { rotationFactor: { default: 6 }, minScale: { default: 0.15 }, maxScale: { default: 8 } },
      init: function () {
        this.handleRotation = this.handleRotation.bind(this);
        this.handleScale = this.handleScale.bind(this);
        this.initialScale = this.el.object3D.scale.clone();
        this.scaleFactor = 1;
        this.el.sceneEl.addEventListener("onefingermove", this.handleRotation);
        this.el.sceneEl.addEventListener("twofingermove", this.handleScale);
      },
      handleRotation: function (e) {
        this.el.object3D.rotation.y += e.detail.positionChange.x * this.data.rotationFactor;
        this.el.object3D.rotation.x += e.detail.positionChange.y * this.data.rotationFactor;
      },
      handleScale: function (e) {
        this.scaleFactor *= 1 + e.detail.spreadChange / e.detail.startSpread;
        this.scaleFactor = Math.min(Math.max(this.scaleFactor, this.data.minScale), this.data.maxScale);
        this.el.object3D.scale.set(
          this.scaleFactor * this.initialScale.x,
          this.scaleFactor * this.initialScale.y,
          this.scaleFactor * this.initialScale.z);
      },
    });
  
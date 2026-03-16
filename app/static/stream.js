(function () {
  // Stream collapse toggle — collapses the right panel to a narrow strip
  var streamToggle = document.getElementById("stream-toggle");
  var rightPanel = streamToggle ? streamToggle.closest(".right") : null;
  var leftPanel = document.querySelector(".panel.left");

  if (streamToggle && rightPanel) {
    streamToggle.addEventListener("click", function () {
      rightPanel.classList.toggle("collapsed");
      if (leftPanel) leftPanel.classList.toggle("stream-collapsed");
      var chevron = streamToggle.querySelector(".stream-chevron");
      if (chevron) {
        chevron.textContent = rightPanel.classList.contains("collapsed") ? "◂" : "▸";
      }
    });
  }

  var streamEl = document.getElementById("stream");
  var ws;
  var reconnectDelay = 1000;

  function formatTime(iso) {
    var d = new Date(iso);
    return d.toLocaleTimeString("en-US", { hour12: false });
  }

  function isYou(id) {
    try {
      return id && window.posthog && id === posthog.get_distinct_id();
    } catch (e) { return false; }
  }

  function updatePresence(count) {
    var el = document.getElementById("presence-count");
    if (!el) return;
    if (count === 1) {
      el.textContent = "1 online";
    } else {
      el.textContent = count + " online";
    }
  }

  function shortVisitor(id) {
    if (!id) return "anon";
    if (isYou(id)) return id.substring(0, 8) + " (you)";
    return id.substring(0, 8);
  }

  function humanizeEvent(ev) {
    var t = ev.event_type;
    if (t === "$pageview") return "viewed the page";
    if (t === "$pageleave") return null; // filter out
    if (t === "$autocapture") {
      if (ev.element_text) return 'clicked "' + ev.element_text + '"';
      if (ev.element_tag) return "clicked <" + ev.element_tag + ">";
      return "clicked something";
    }
    if (t === "fire_event") return "fired an event";
    return t; // unknown custom events: show raw name
  }

  function renderEvent(ev) {
    var description = humanizeEvent(ev);
    if (description === null) return; // filtered out (e.g. $pageleave)

    var line = document.createElement("div");
    line.className = "event-line";

    var time = document.createElement("span");
    time.className = "time";
    time.textContent = formatTime(ev.timestamp);

    var dash = document.createTextNode(" \u2014 ");

    var visitor = document.createElement("span");
    var youEvent = isYou(ev.visitor_id);
    visitor.className = youEvent ? "visitor visitor-you" : "visitor";
    visitor.textContent = shortVisitor(ev.visitor_id);

    var dot = document.createTextNode(" \u00B7 ");

    var desc = document.createElement("span");
    desc.className = "etype";
    desc.textContent = description;

    line.appendChild(time);
    line.appendChild(dash);
    line.appendChild(visitor);
    line.appendChild(dot);
    line.appendChild(desc);

    // Newest at top
    streamEl.insertBefore(line, streamEl.firstChild);

    // Cap visible lines at 200
    while (streamEl.children.length > 200) {
      streamEl.removeChild(streamEl.lastChild);
    }
  }

  function connect() {
    var proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(proto + "//" + location.host + "/ws/events");

    ws.onopen = function () {
      reconnectDelay = 1000;
    };

    ws.onmessage = function (msg) {
      try {
        var ev = JSON.parse(msg.data);

        // Presence update — not an event
        if (ev.type === "presence") {
          updatePresence(ev.count);
          return;
        }

        renderEvent(ev);

        // Check if this is our pending journey event
        if (window.__pendingJourney) {
          if (window.__pendingJourney.eventId && ev.id === window.__pendingJourney.eventId) {
            // eventId already set, direct match
            if (window.__pendingJourney.onStream) window.__pendingJourney.onStream();
          } else if (!window.__pendingJourney.eventId) {
            // eventId not yet set (race: WS arrives before POST response)
            // Buffer this event ID so we can match when POST response arrives
            if (!window.__pendingJourney._wsBuffer) window.__pendingJourney._wsBuffer = [];
            window.__pendingJourney._wsBuffer.push(ev.id);
          }
        }
      } catch (e) {
        // ignore malformed messages
      }
    };

    ws.onclose = function () {
      setTimeout(function () {
        reconnectDelay = Math.min(reconnectDelay * 2, 30000);
        connect();
      }, reconnectDelay);
    };

    ws.onerror = function () {
      ws.close();
    };
  }

  // ── Journey card ──
  function createStepEl(label) {
    var el = document.createElement("div");
    el.className = "journey-step";
    var icon = document.createElement("span");
    icon.className = "step-icon";
    icon.textContent = "\u25CB";
    el.appendChild(icon);
    el.appendChild(document.createTextNode(" " + label));
    el._icon = icon;
    el._label = label;
    return el;
  }

  function markStepDone(el) {
    el.classList.add("done");
    el._icon.textContent = "\u2713";
  }

  function renderJourneyCard(journey) {
    var container = document.getElementById("journey-container");
    while (container.firstChild) container.removeChild(container.firstChild);

    var card = document.createElement("div");
    card.className = "journey-card";

    // Header: timestamp + event name
    var header = document.createElement("div");
    header.className = "journey-header";
    header.textContent = formatTime(journey.timestamp) + " \u00B7 fire_event";
    card.appendChild(header);

    // Real-time confirmation steps
    var steps = [
      { key: "capture", label: "captured by the analytics tracker (PostHog)", promise: journey.capturePromise },
      { key: "store", label: "saved to database (Supabase)", promise: journey.storePromise },
      { key: "stream", label: "broadcast to all visitors (WebSocket)", promise: journey.streamPromise }
    ];

    var stepsEl = document.createElement("div");
    stepsEl.className = "journey-steps";

    steps.forEach(function (step, i) {
      var el = createStepEl(step.label);
      stepsEl.appendChild(el);

      step.promise.then(function () {
        setTimeout(function () {
          markStepDone(el);
          // After all 3 steps done, render transformation + metrics
          if (i === 2) {
            setTimeout(function () { renderTransformSection(card, journey); }, 200);
          }
        }, i * 200);
      });
    });

    card.appendChild(stepsEl);
    container.appendChild(card);
  }

  // Transformation preview — what dbt's stg_events will extract
  function renderTransformSection(card, journey) {
    var props = journey.properties || {};

    var section = document.createElement("div");
    section.className = "journey-section";

    var label = document.createElement("div");
    label.className = "journey-section-label";
    label.textContent = "event details:";
    section.appendChild(label);

    var fields = [
      { key: "event_name", value: "fire_event" },
      { key: "device", value: props.$device_type || "—" },
      { key: "browser", value: (props.$browser || "—") + (props.$browser_version ? " " + props.$browser_version : "") },
      { key: "os", value: props.$os || "—" }
    ];

    var table = document.createElement("div");
    table.className = "journey-fields";

    fields.forEach(function (f) {
      var k = document.createElement("span");
      k.className = "journey-field-key";
      k.textContent = f.key;

      var v = document.createElement("span");
      v.className = "journey-field-value";
      v.textContent = f.value;

      table.appendChild(k);
      table.appendChild(v);
    });

    section.appendChild(table);
    card.appendChild(section);

    // After transform section, render metrics contribution
    renderMetricsSection(card, journey);
  }

  // Metrics contribution — which metrics_daily aggregates this event affects
  function renderMetricsSection(card, journey) {
    var props = journey.properties || {};
    var eventName = "fire_event";
    var device = (props.$device_type || "").toLowerCase();

    var metrics = [];
    // total_events: always +1
    metrics.push({ name: "total_events", change: "+1" });

    // Event type specific
    if (eventName === "$pageview") {
      metrics.push({ name: "pageviews", change: "+1" });
    } else if (eventName === "$autocapture") {
      metrics.push({ name: "clicks", change: "+1" });
    } else {
      metrics.push({ name: "custom_events", change: "+1" });
    }

    // Device sessions
    if (device === "desktop") {
      metrics.push({ name: "desktop_sessions", change: "+1" });
    } else if (device === "mobile") {
      metrics.push({ name: "mobile_sessions", change: "+1" });
    } else if (device === "tablet") {
      metrics.push({ name: "tablet_sessions", change: "+1" });
    }

    // events_per_visitor always increases
    metrics.push({ name: "events_per_visitor", change: "\u2191" });

    var section = document.createElement("div");
    section.className = "journey-section";

    var label = document.createElement("div");
    label.className = "journey-section-label";
    label.textContent = "metric changes:";
    section.appendChild(label);

    var table = document.createElement("div");
    table.className = "journey-fields";

    metrics.forEach(function (m) {
      var k = document.createElement("span");
      k.className = "journey-field-key";
      k.textContent = m.name;

      var v = document.createElement("span");
      v.className = "journey-field-value journey-metric-change";
      v.textContent = m.change;

      table.appendChild(k);
      table.appendChild(v);
    });

    section.appendChild(table);
    card.appendChild(section);
  }

  // Button: fire event + render journey card in left panel
  var fireBtn = document.getElementById("btn-fire");
  if (fireBtn) {
    fireBtn.addEventListener("click", function () {
      // Create journey with promise resolvers
      var journey = { timestamp: new Date().toISOString(), eventId: null, properties: {} };
      journey.capturePromise = new Promise(function (resolve) { journey.onCapture = resolve; });
      journey.storePromise = new Promise(function (resolve) { journey.onStore = resolve; });
      journey.streamPromise = new Promise(function (resolve) { journey.onStream = resolve; });

      // Set pending journey BEFORE posthog.capture so _onCapture can find it
      window.__pendingJourney = journey;

      // Fire the event (posthog is a global from the SDK script)
      window.posthog.capture("fire_event");

      // Render journey card in left panel
      renderJourneyCard(journey);
    });
  }

  // ── Pipeline countdowns ──
  function updateCountdowns() {
    var el = document.getElementById("pipeline-status");
    if (!el) return;

    var config = window.__reflection || {};
    var now = new Date();
    var parts = [];

    // Warehouse export: runs hourly on the hour
    var lastHour = new Date(now);
    lastHour.setMinutes(0, 0, 0);
    var agoMins = Math.max(0, Math.round((now - lastHour) / 60000));
    parts.push("last warehouse export: " + agoMins + "m ago");
    var nextHour = new Date(lastHour.getTime() + 60 * 60 * 1000);
    var bqMins = Math.max(0, Math.round((nextHour - now) / 60000));
    parts.push("next one in " + bqMins + "m");

    // Metrics refresh countdown: next occurrence of :MM past the hour
    var cronMin = config.dbtCronMinute || 30;
    var nextDbt = new Date(now);
    nextDbt.setMinutes(cronMin, 0, 0);
    if (nextDbt <= now) {
      nextDbt.setHours(nextDbt.getHours() + 1);
    }
    var dbtMins = Math.max(0, Math.round((nextDbt - now) / 60000));
    parts.push("metrics refresh in " + dbtMins + "m");

    el.textContent = parts.join(" \u00B7 ");
  }

  updateCountdowns();
  setInterval(updateCountdowns, 60000);

  connect();
})();

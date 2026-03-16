(function () {
  // Tab switching
  var tabs = document.querySelectorAll(".tab");
  var tabContents = document.querySelectorAll(".tab-content");

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      var target = tab.getAttribute("data-tab");
      tabs.forEach(function (t) { t.classList.remove("active"); });
      tabContents.forEach(function (tc) { tc.classList.remove("active"); });
      tab.classList.add("active");
      document.getElementById("tab-" + target).classList.add("active");
    });
  });

  var streamEl = document.getElementById("stream");
  var ws;
  var reconnectDelay = 1000;

  function formatTime(iso) {
    var d = new Date(iso);
    return d.toLocaleTimeString("en-US", { hour12: false });
  }

  function shortVisitor(id) {
    if (!id) return "anon";
    return id.substring(0, 8);
  }

  function describeEvent(ev) {
    var parts = [];
    if (ev.page_path) parts.push(ev.page_path);
    if (ev.element_text) parts.push('"' + ev.element_text + '"');
    if (ev.element_tag && !ev.element_text) parts.push("<" + ev.element_tag + ">");
    return parts.length > 0 ? parts.join(" ") : "";
  }

  function renderEvent(ev) {
    var line = document.createElement("div");
    line.className = "event-line ripple";

    var time = document.createElement("span");
    time.className = "time";
    time.textContent = formatTime(ev.timestamp);

    var dash = document.createTextNode(" \u2014 ");

    var visitor = document.createElement("span");
    visitor.className = "visitor";
    visitor.textContent = shortVisitor(ev.visitor_id);

    var dot = document.createTextNode(" \u00B7 ");

    var etype = document.createElement("span");
    etype.className = "etype";
    etype.textContent = ev.event_type;

    var detail = document.createElement("span");
    detail.className = "detail";
    detail.textContent = " " + describeEvent(ev);

    line.appendChild(time);
    line.appendChild(dash);
    line.appendChild(visitor);
    line.appendChild(dot);
    line.appendChild(etype);
    line.appendChild(detail);

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
        renderEvent(ev);
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

  connect();
})();

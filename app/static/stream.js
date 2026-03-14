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
    line.className = "event-line";

    var time = '<span class="time">' + formatTime(ev.timestamp) + "</span>";
    var etype = '<span class="etype">' + ev.event_type + "</span>";
    var visitor = '<span class="visitor">' + shortVisitor(ev.visitor_id) + "</span>";
    var detail = '<span class="detail">' + describeEvent(ev) + "</span>";

    line.innerHTML = time + " &mdash; " + visitor + " &middot; " + etype + " " + detail;

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

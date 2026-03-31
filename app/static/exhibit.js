(function () {
  var overlay = document.getElementById("exhibit-overlay");
  var steps = overlay.querySelectorAll(".exhibit-step");
  var backBtn = document.getElementById("exhibit-back");
  var nextBtn = document.getElementById("exhibit-next");
  var counter = document.getElementById("exhibit-step-counter");
  var enterBtn = document.getElementById("btn-exhibit");
  var totalSteps = steps.length;
  var currentStep = 0; // 0 = not in exhibit

  var stepNames = ["", "hello", "event-stream", "warehouse", "analytics", "modeling"];

  function isMobile() { return window.innerWidth <= 768; }

  function showStep(n) {
    currentStep = n;
    steps.forEach(function (el) {
      var s = parseInt(el.getAttribute("data-step"), 10);
      el.classList.toggle("active", s === n);
    });

    // Nav visibility
    backBtn.style.display = n <= 1 ? "none" : "";
    var isLast = n >= totalSteps;
    nextBtn.textContent = isLast ? "Exit" : "Next";
    nextBtn.classList.toggle("exhibit-btn-exit", isLast);
    counter.textContent = n + " / " + totalSteps;

    // Hero panel: show only on step 1
    var heroPanel = document.querySelector(".exhibit-hero-panel");
    if (heroPanel) heroPanel.style.display = n === 1 ? "" : "none";

    // On mobile, strips are hidden — content is inlined in exhibit steps.
    // On desktop, toggle strip visibility and auto-expand.
    if (!isMobile()) {
      var streamStrip = document.getElementById("strip-stream");
      var warehouseStrip = document.getElementById("strip-warehouse");
      var analyticsStrip = document.getElementById("strip-analytics");
      var modelingStrip = document.getElementById("strip-modeling");
      if (streamStrip) streamStrip.classList.toggle("exhibit-visible", n >= 2);
      if (warehouseStrip) warehouseStrip.classList.toggle("exhibit-visible", n >= 3);
      if (analyticsStrip) analyticsStrip.classList.toggle("exhibit-visible", n >= 4);
      if (modelingStrip) modelingStrip.classList.toggle("exhibit-visible", n >= 5);

      if (n === 2 && streamStrip && !streamStrip.classList.contains("expanded")) {
        if (window.__toggleStrip) window.__toggleStrip("stream");
      }
      if (n === 3 && warehouseStrip && !warehouseStrip.classList.contains("expanded")) {
        if (window.__toggleStrip) window.__toggleStrip("warehouse");
      }
      if (n === 4 && analyticsStrip && !analyticsStrip.classList.contains("expanded")) {
        if (window.__toggleStrip) window.__toggleStrip("analytics");
      }
      if (n === 5 && modelingStrip && !modelingStrip.classList.contains("expanded")) {
        if (window.__toggleStrip) window.__toggleStrip("modeling");
      }
    }

    // On mobile step 2, populate mini-stream with recent events
    if (isMobile() && n === 2) {
      populateMobileStream();
    }

    // Fire funnel_step event
    if (window.posthog && stepNames[n]) {
      window.posthog.capture("funnel_step", { step: stepNames[n] });
    }
  }

  // Copy recent events from the main stream into the mobile mini-stream
  function populateMobileStream() {
    var mobileStream = document.getElementById("mobile-stream");
    var mainStream = document.getElementById("stream");
    if (!mobileStream || !mainStream) return;
    // Clear and copy the last 8 events
    while (mobileStream.firstChild) mobileStream.removeChild(mobileStream.firstChild);
    var events = mainStream.querySelectorAll(".event-line");
    var count = Math.min(events.length, 8);
    for (var i = 0; i < count; i++) {
      mobileStream.appendChild(events[i].cloneNode(true));
    }
  }

  function enterExhibit() {
    document.body.classList.add("exhibit-mode");
    overlay.classList.add("active");
    var hash = window.location.hash;
    var match = hash && hash.match(/^#exhibit-(\d+)$/);
    var startStep = (match && parseInt(match[1], 10) >= 1 && parseInt(match[1], 10) <= totalSteps)
      ? parseInt(match[1], 10) : 1;
    showStep(startStep);
    if (!match || parseInt(match[1], 10) !== startStep) {
      history.replaceState(null, "", "#exhibit-" + startStep);
    }
  }

  function exitExhibit() {
    document.body.classList.remove("exhibit-mode");
    overlay.classList.remove("active");
    currentStep = 0;
    // Remove exhibit-visible from strips
    document.querySelectorAll(".strip").forEach(function (s) {
      s.classList.remove("exhibit-visible");
    });
    history.replaceState(null, "", window.location.pathname);
  }

  // Navigation
  backBtn.addEventListener("click", function () {
    if (currentStep > 1) {
      var prev = currentStep - 1;
      history.pushState(null, "", "#exhibit-" + prev);
      showStep(prev);
    }
  });

  nextBtn.addEventListener("click", function () {
    if (currentStep >= totalSteps) {
      exitExhibit();
    } else {
      var next = currentStep + 1;
      history.pushState(null, "", "#exhibit-" + next);
      showStep(next);
    }
  });

  // Enter button
  if (enterBtn) {
    enterBtn.addEventListener("click", function () {
      history.pushState(null, "", "#exhibit-1");
      enterExhibit();
    });
  }

  // Exit button (X in top-right corner)
  var closeBtn = document.getElementById("exhibit-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      exitExhibit();
    });
  }

  // Hash routing
  window.addEventListener("hashchange", function () {
    var hash = window.location.hash;
    var match = hash && hash.match(/^#exhibit-(\d+)$/);
    if (match) {
      var n = parseInt(match[1], 10);
      if (n >= 1 && n <= totalSteps) {
        if (!overlay.classList.contains("active")) {
          document.body.classList.add("exhibit-mode");
          overlay.classList.add("active");
        }
        showStep(n);
      }
    } else if (!hash || hash === "#") {
      if (overlay.classList.contains("active")) {
        exitExhibit();
      }
    }
  });

  // Direct load with hash
  if (window.location.hash && window.location.hash.match(/^#exhibit-\d+$/)) {
    enterExhibit();
  }

  // Questionnaire
  var textarea = document.getElementById("questionnaire-text");
  var charCount = document.getElementById("char-count");
  var submitBtn = document.getElementById("btn-questionnaire");
  var confirmation = document.getElementById("questionnaire-confirmation");

  if (textarea && charCount) {
    textarea.addEventListener("input", function () {
      charCount.textContent = textarea.value.length + " / 500";
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", function () {
      var text = textarea.value.trim();
      if (!text) return;
      if (window.posthog) {
        window.posthog.capture("questionnaire_response", { response_text: text });
      }
      textarea.disabled = true;
      submitBtn.disabled = true;
      confirmation.textContent = "Recorded.";
    });
  }

  // Shop buy buttons
  document.querySelectorAll(".shop-buy-btn").forEach(function (btn) {
    var priceInput = btn.getAttribute("data-price-input");
    var fixedPrice = btn.getAttribute("data-price");

    // Enable buttons that have a valid price or a price input
    if (priceInput) {
      // "Pay what you wish" — enable when input has a valid value
      var input = document.getElementById(priceInput);
      if (input) {
        btn.classList.add("active");
        input.addEventListener("input", function () {
          var val = parseFloat(input.value);
          btn.classList.toggle("active", val > 0);
        });
      }
    } else if (fixedPrice && parseFloat(fixedPrice) > 0) {
      btn.classList.add("active");
    }

    btn.addEventListener("click", function () {
      var itemId = btn.getAttribute("data-item-id");
      var itemName = btn.getAttribute("data-item-name");
      var price;

      if (priceInput) {
        var inp = document.getElementById(priceInput);
        price = inp ? parseFloat(inp.value) : 0;
        if (!price || price <= 0) return;
      } else {
        price = parseFloat(fixedPrice);
        if (!price || price <= 0) return;
      }

      // Fire PostHog event
      if (window.posthog) {
        window.posthog.capture("checkout_started", {
          item_id: itemId,
          item_name: itemName,
          price: price
        });
      }

      // For keep-the-lights-on, redirect to Stripe Checkout
      if (itemId === "keep-the-lights-on") {
        btn.disabled = true;
        btn.textContent = "Redirecting...";

        fetch("/api/checkout/create-session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: itemId, item_name: itemName, price: price })
        })
          .then(function (res) { return res.json(); })
          .then(function (data) {
            if (data.url) {
              window.location.href = data.url;
            } else {
              btn.disabled = false;
              btn.textContent = "Buy";
              var errEl = btn.parentElement.querySelector(".shop-checkout-error");
              if (!errEl) {
                errEl = document.createElement("div");
                errEl.className = "shop-checkout-error";
                btn.parentElement.appendChild(errEl);
              }
              errEl.textContent = data.detail || "Something went wrong.";
            }
          })
          .catch(function () {
            btn.disabled = false;
            btn.textContent = "Buy";
            var errEl = btn.parentElement.querySelector(".shop-checkout-error");
            if (!errEl) {
              errEl = document.createElement("div");
              errEl.className = "shop-checkout-error";
              btn.parentElement.appendChild(errEl);
            }
            errEl.textContent = "Network error. Please try again.";
          });
      }
    });
  });

  // Checkout success message
  (function () {
    var params = new URLSearchParams(window.location.search);
    if (params.get("checkout") === "success") {
      // Show a brief thank-you toast
      var toast = document.createElement("div");
      toast.className = "checkout-toast";
      toast.textContent = "Thank you for your contribution.";
      document.body.appendChild(toast);

      // Auto-dismiss after 5 seconds
      setTimeout(function () {
        toast.classList.add("checkout-toast-fade");
        setTimeout(function () { toast.remove(); }, 500);
      }, 5000);

      // Clean the query param
      history.replaceState(null, "", window.location.pathname + window.location.hash);
    }
  })();
})();

(function () {
  var overlay = document.getElementById("exhibit-overlay");
  var steps = overlay.querySelectorAll(".exhibit-step");
  var backBtn = document.getElementById("exhibit-back");
  var nextBtn = document.getElementById("exhibit-next");
  var counter = document.getElementById("exhibit-step-counter");
  var enterBtn = document.getElementById("btn-exhibit");
  var totalSteps = steps.length;
  var currentStep = 0; // 0 = not in exhibit

  var stepNames = ["", "welcome", "the-loop", "the-pipeline", "the-apparatus"];

  function showStep(n) {
    currentStep = n;
    steps.forEach(function (el) {
      var s = parseInt(el.getAttribute("data-step"), 10);
      el.classList.toggle("active", s === n);
    });

    // Nav visibility
    backBtn.style.display = n <= 1 ? "none" : "";
    nextBtn.textContent = n >= totalSteps ? "Exit" : "Next";
    counter.textContent = n + " / " + totalSteps;

    // Strip visibility: stream at step 2+, analytics at step 3+
    var streamStrip = document.getElementById("strip-stream");
    var analyticsStrip = document.getElementById("strip-analytics");
    if (streamStrip) {
      streamStrip.classList.toggle("exhibit-visible", n >= 2);
    }
    if (analyticsStrip) {
      analyticsStrip.classList.toggle("exhibit-visible", n >= 3);
    }

    // Auto-expand the stream strip when it becomes visible at step 2
    if (n === 2 && streamStrip && !streamStrip.classList.contains("expanded")) {
      if (window.__toggleStrip) window.__toggleStrip("stream");
    }

    // Fire funnel_step event
    if (window.posthog && stepNames[n]) {
      window.posthog.capture("funnel_step", { step: stepNames[n] });
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
})();

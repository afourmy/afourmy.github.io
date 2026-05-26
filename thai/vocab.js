(function () {
  var groupsEl = document.getElementById("vocab-groups");
  var countEl = document.getElementById("vocab-count");
  var searchEl = document.getElementById("vocab-search");
  var toggleEl = document.getElementById("vocab-toggle");
  var fontToggleEl = document.getElementById("font-toggle");
  var faceToggleEl = document.getElementById("face-toggle");
  var showCategoryEl = document.getElementById("show-category");
  var showSourcesEl = document.getElementById("show-sources");
  var flipHintEl = document.getElementById("flip-hint");

  var words = [];
  var loaded = false;
  var mode = "frequency"; // or "topic"
  var query = "";
  var face = "both"; // "both" | "thai" | "english"
  var showCategory = true;
  var showSources = true;

  var FREQ_ORDER = ["everyday", "common", "occasional", "rare"];
  var FREQ_LABEL = {
    everyday: "Everyday",
    common: "Common",
    occasional: "Occasional",
    rare: "Rare",
  };
  var TOPIC_LABEL = {
    personality: "Personality",
    emotions: "Emotions",
    family: "Family",
    health: "Health",
    general: "General",
    grammar: "Grammar",
    expressions: "Expressions",
    time: "Time",
    culture: "Culture",
    beliefs: "Beliefs",
    monarchy: "Monarchy",
    nature: "Nature",
  };

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function escAttr(s) {
    return esc(s).replace(/"/g, "&quot;");
  }

  // Small copy-to-clipboard control overlaid on flashcards (front shows a copy
  // glyph, switches to a check briefly after a successful copy via .copied).
  var COPY_BTN =
    '<button class="vocab-copy" type="button" aria-label="Copy word" title="Copy word">' +
    '<svg class="vocab-copy-i vocab-copy-i--copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>' +
    '<svg class="vocab-copy-i vocab-copy-i--check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>' +
    "</button>";

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
    } catch (e) {}
    document.body.removeChild(ta);
  }

  function copyText(text, btn) {
    function done() {
      btn.classList.add("copied");
      setTimeout(function () {
        btn.classList.remove("copied");
      }, 1000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {
        fallbackCopy(text);
        done();
      });
    } else {
      fallbackCopy(text);
      done();
    }
  }

  function lsGet(k) {
    try {
      return localStorage.getItem(k);
    } catch (e) {
      return null;
    }
  }
  function lsSet(k, v) {
    try {
      localStorage.setItem(k, v);
    } catch (e) {}
  }

  function matches(word) {
    if (!query) return true;
    var q = query.toLowerCase();
    return (
      word.thai.indexOf(query) !== -1 ||
      word.english.toLowerCase().indexOf(q) !== -1
    );
  }

  function tagHtml(word) {
    // Complementary dimension: topic when grouped by frequency, else frequency.
    var tag, tagClass;
    if (mode === "frequency") {
      tag = TOPIC_LABEL[word.topic] || word.topic;
      tagClass = "tag-topic";
    } else {
      tag = FREQ_LABEL[word.frequency] || word.frequency;
      tagClass = "tag-freq freq-" + word.frequency;
    }
    return '<span class="vocab-tag ' + tagClass + '">' + esc(tag) + "</span>";
  }

  function sourcesHtml(word) {
    return word.sources
      .map(function (s) {
        return '<span class="vocab-source">' + esc(s) + "</span>";
      })
      .join("");
  }

  function metaHtml(word) {
    var rows = "";
    if (showCategory)
      rows += '<div class="vocab-tags">' + tagHtml(word) + "</div>";
    if (showSources)
      rows += '<div class="vocab-sources">' + sourcesHtml(word) + "</div>";
    return rows ? '<div class="vocab-meta">' + rows + "</div>" : "";
  }

  function thaiHtml(word, extra) {
    return '<div class="vocab-thai' + (extra || "") + '">' + esc(word.thai) + "</div>";
  }
  function enHtml(word, extra) {
    return '<div class="vocab-en' + (extra || "") + '">' + esc(word.english) + "</div>";
  }

  function card(word) {
    if (face === "both") {
      return (
        '<div class="vocab-card">' +
        thaiHtml(word) +
        enHtml(word) +
        metaHtml(word) +
        "</div>"
      );
    }
    // Flashcard: chosen side on the front, the other revealed on flip.
    var front = face === "thai" ? thaiHtml(word) : enHtml(word, " vocab-prompt");
    var back =
      face === "thai"
        ? enHtml(word, " vocab-answer")
        : thaiHtml(word, " vocab-answer");
    var frontInner = front + metaHtml(word);
    var backInner = back;
    // Currently-visible word per face, so the copy button can grab whichever
    // side is showing without re-deriving it from the DOM.
    var frontText = face === "thai" ? word.thai : word.english;
    var backText = face === "thai" ? word.english : word.thai;
    // The rotor holds the two visible faces; the hidden ghost (a normal-flow
    // copy of both) gives the card the height of the taller face. The copy
    // button sits outside the rotor so it stays put during the 3D turn.
    return (
      '<div class="vocab-card vocab-card--flip" data-front="' +
      escAttr(frontText) +
      '" data-back="' +
      escAttr(backText) +
      '">' +
      COPY_BTN +
      '<div class="vocab-flip-rotor">' +
      '<div class="vocab-face vocab-face--front">' + frontInner + "</div>" +
      '<div class="vocab-face vocab-face--back">' + backInner + "</div>" +
      "</div>" +
      '<div class="vocab-flip-ghost" aria-hidden="true">' +
      '<div class="vocab-face">' + frontInner + "</div>" +
      '<div class="vocab-face">' + backInner + "</div>" +
      "</div>" +
      "</div>"
    );
  }

  function buildGroups(list) {
    var buckets = {};
    list.forEach(function (word) {
      var key = mode === "frequency" ? word.frequency : word.topic;
      (buckets[key] = buckets[key] || []).push(word);
    });

    var keys;
    if (mode === "frequency") {
      keys = FREQ_ORDER.filter(function (k) {
        return buckets[k];
      });
    } else {
      // Topics ordered by size, largest first.
      keys = Object.keys(buckets).sort(function (a, b) {
        return buckets[b].length - buckets[a].length;
      });
    }

    return keys.map(function (key) {
      var label =
        mode === "frequency" ? FREQ_LABEL[key] : TOPIC_LABEL[key] || key;
      return { key: key, label: label, items: buckets[key] };
    });
  }

  function render() {
    if (!loaded) return;
    var list = words.filter(matches);
    countEl.textContent =
      list.length + (list.length === 1 ? " word" : " words");

    if (!list.length) {
      groupsEl.innerHTML = '<p class="vocab-empty">No matching words.</p>';
      return;
    }

    var groups = buildGroups(list);
    groupsEl.innerHTML = groups
      .map(function (group) {
        var freqMod =
          mode === "frequency" ? " vocab-group--" + group.key : "";
        return (
          '<section class="vocab-group' + freqMod + '">' +
          '<h2 class="vocab-group-title">' +
          esc(group.label) +
          '<span class="vocab-group-count">' +
          group.items.length +
          "</span>" +
          "</h2>" +
          '<div class="vocab-cards">' +
          group.items.map(card).join("") +
          "</div>" +
          "</section>"
        );
      })
      .join("");
  }

  toggleEl.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-mode]");
    if (!btn) return;
    mode = btn.getAttribute("data-mode");
    toggleEl.querySelectorAll("button").forEach(function (b) {
      b.classList.toggle("active", b === btn);
    });
    render();
  });

  searchEl.addEventListener("input", function () {
    query = searchEl.value.trim();
    render();
  });

  // Flip a card on click (single-side modes): a two-phase 3D turn. The front
  // rotates to its edge (90 deg); while invisible we swap the visible face and
  // jump to the opposite edge (-90 deg); then the new face rotates flat. Each
  // face only ever shows within +/-90 deg, so no backface-visibility is needed.
  var TURN_MS = 200;
  groupsEl.addEventListener("click", function (e) {
    var card = e.target.closest(".vocab-card--flip");
    if (!card) return;
    var rotor = card.querySelector(".vocab-flip-rotor");
    if (!rotor || rotor.dataset.turning) return; // ignore clicks mid-turn
    rotor.dataset.turning = "1";

    rotor.style.transition = "transform " + TURN_MS + "ms ease-in";
    rotor.style.transform = "rotateY(90deg)";

    setTimeout(function () {
      card.classList.toggle("flipped"); // swap faces while edge-on
      rotor.style.transition = "none";
      rotor.style.transform = "rotateY(-90deg)";
      void rotor.offsetWidth; // force reflow so the next change animates
      rotor.style.transition = "transform " + TURN_MS + "ms ease-out";
      rotor.style.transform = "rotateY(0deg)";
      setTimeout(function () {
        rotor.style.transition = "";
        delete rotor.dataset.turning;
      }, TURN_MS);
    }, TURN_MS);
  });

  // ── Display options (card face + what metadata to show), persisted ──
  function setFace(f, doRender) {
    face = f;
    faceToggleEl.querySelectorAll("button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-face") === f);
    });
    flipHintEl.style.display = f === "both" ? "none" : "";
    lsSet("vocabFace", f);
    if (doRender) render();
  }

  faceToggleEl.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-face]");
    if (btn) setFace(btn.getAttribute("data-face"), true);
  });

  showCategoryEl.addEventListener("change", function () {
    showCategory = showCategoryEl.checked;
    lsSet("vocabShowCategory", showCategory ? "1" : "0");
    render();
  });

  showSourcesEl.addEventListener("change", function () {
    showSources = showSourcesEl.checked;
    lsSet("vocabShowSources", showSources ? "1" : "0");
    render();
  });

  // Thai font preference (default Sarabun, the book style), persisted.
  function applyFont(font) {
    document.body.setAttribute("data-thai-font", font);
    fontToggleEl.querySelectorAll("button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-font") === font);
    });
    lsSet("thaiFont", font);
  }

  fontToggleEl.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-font]");
    if (btn) applyFont(btn.getAttribute("data-font"));
  });

  // Restore saved preferences before the first render.
  applyFont(lsGet("thaiFont") || "sarabun");
  showCategory = lsGet("vocabShowCategory") !== "0";
  showSources = lsGet("vocabShowSources") !== "0";
  showCategoryEl.checked = showCategory;
  showSourcesEl.checked = showSources;
  setFace(lsGet("vocabFace") || "both", false);

  // Resolve the data file next to this script, so it works both on a direct
  // visit and when the page is loaded via the site's SPA navigation (which
  // leaves the document base at the site root).
  var thisScript = document.querySelector('script[src$="vocab.js"]');
  var dataUrl = thisScript
    ? new URL("vocab.json", thisScript.src).href
    : "vocab.json";

  fetch(dataUrl)
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      words = data;
      loaded = true;
      render();
    })
    .catch(function () {
      groupsEl.innerHTML =
        '<p class="vocab-empty">Could not load vocabulary data.</p>';
    });
})();

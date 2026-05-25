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
    return (
      '<div class="vocab-card vocab-card--flip">' +
      '<div class="vocab-flip-inner">' +
      '<div class="vocab-face vocab-face--front">' + front + metaHtml(word) + "</div>" +
      '<div class="vocab-face vocab-face--back">' + back + "</div>" +
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

  // Flip a card on click (only in single-side modes).
  groupsEl.addEventListener("click", function (e) {
    var c = e.target.closest(".vocab-card--flip");
    if (c) c.classList.toggle("flipped");
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

  fetch("vocab.json")
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

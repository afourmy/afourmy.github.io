(function () {
  var groupsEl = document.getElementById("vocab-groups");
  var countEl = document.getElementById("vocab-count");
  var searchEl = document.getElementById("vocab-search");
  var toggleEl = document.getElementById("vocab-toggle");
  var filterEl = document.getElementById("vocab-filter");
  var fontToggleEl = document.getElementById("font-toggle");
  var faceToggleEl = document.getElementById("face-toggle");
  var showCategoryEl = document.getElementById("show-category");
  var showSourcesEl = document.getElementById("show-sources");
  var flipHintEl = document.getElementById("flip-hint");

  var words = [];
  var loaded = false;
  var mode = "frequency"; // grouping axis (sections); both axes are filtered below
  // Independent visibility filters per dimension: { key: bool }. Built (all on)
  // once on load and kept while regrouping. Not saved to localStorage.
  var filters = { frequency: {}, topic: {} };
  var query = "";
  var face = "both"; // "both" | "thai" | "english"
  var showCategory = true;
  var showSources = false;

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
    law: "Legal",
    economy: "Economy",
    transport: "Transport",
    weather: "Weather",
    travel: "Travel",
    food: "Food",
    slang: "Slang",
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

  // Suspend control: toggles indefinite suspension on the word. A suspended
  // card stays visible on this page with a soft-red background; the flashcards
  // page skips it. Shared state lives at localStorage["thaiSuspended"].
  var SUSPEND_BTN =
    '<button class="vocab-suspend" type="button" aria-label="Suspend word" title="Suspend / Unsuspend">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><line x1="5.5" y1="5.5" x2="18.5" y2="18.5"/></svg>' +
    "</button>";

  // Speaker control: plays the word's Thai pronunciation (audio is Thai-only),
  // rendered only for words with a generated mp3 (see speakerBtn / word.audio).
  var SPEAKER_SVG =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';

  var currentAudio = null;
  var playingBtn = null;
  function stopAudio() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    if (playingBtn) {
      playingBtn.classList.remove("playing");
      playingBtn = null;
    }
  }
  function playAudio(btn) {
    var src = btn.getAttribute("data-audio");
    if (!src) return;
    stopAudio();
    currentAudio = new Audio(src);
    playingBtn = btn;
    btn.classList.add("playing");
    currentAudio.addEventListener("ended", stopAudio);
    currentAudio.play().catch(stopAudio);
  }

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

  // Suspended-words state (shared with flashcards page). { wordId: true }.
  var SUSPENDED_KEY = "thaiSuspended";
  var suspended = {};
  function loadSuspended() {
    var raw = lsGet(SUSPENDED_KEY);
    if (!raw) return {};
    try { return JSON.parse(raw) || {}; } catch (e) { return {}; }
  }
  function saveSuspended() {
    lsSet(SUSPENDED_KEY, JSON.stringify(suspended));
  }
  function isSuspended(word) { return suspended[word.id] === true; }

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

  function speakerBtn(word) {
    // Only show when the Thai side is visible by default (Both / Thai modes).
    if (face === "english") return "";
    return (
      '<button class="vocab-speak" type="button" aria-label="Play pronunciation"' +
      ' title="Play pronunciation" data-audio="' +
      escAttr(audioBase + word.id + ".mp3") +
      '">' +
      SPEAKER_SVG +
      "</button>"
    );
  }

  function toolsHtml(word) {
    return '<div class="vocab-tools">' + speakerBtn(word) + COPY_BTN + SUSPEND_BTN + '</div>';
  }

  function cardClasses(word, extra) {
    return (
      "vocab-card" +
      (extra || "") +
      " vocab-card--freq-" + word.frequency +
      (isSuspended(word) ? " vocab-card--suspended" : "")
    );
  }

  function card(word) {
    if (face === "both") {
      // Both-faces card: copy button is fixed to the Thai word (no flip).
      return (
        '<div class="' + cardClasses(word) + '" data-id="' + escAttr(word.id) +
        '" data-copy="' + escAttr(word.thai) + '">' +
        '<div class="vocab-card-body">' +
        thaiHtml(word) +
        enHtml(word) +
        metaHtml(word) +
        '</div>' +
        toolsHtml(word) +
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
    // button lives inside the rotor so it turns with the card.
    return (
      '<div class="' + cardClasses(word, " vocab-card--flip") +
      '" data-id="' + escAttr(word.id) +
      '" data-front="' + escAttr(frontText) +
      '" data-back="' + escAttr(backText) +
      '">' +
      '<div class="vocab-flip-stage">' +
        '<div class="vocab-flip-rotor">' +
          '<div class="vocab-face vocab-face--front">' + frontInner + "</div>" +
          '<div class="vocab-face vocab-face--back">' + backInner + "</div>" +
        "</div>" +
        '<div class="vocab-flip-ghost" aria-hidden="true">' +
          '<div class="vocab-face">' + frontInner + "</div>" +
          '<div class="vocab-face">' + backInner + "</div>" +
        "</div>" +
      "</div>" +
      toolsHtml(word) +
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

  // Distinct keys present for a dimension, in chip order: frequencies in
  // canonical order, topics largest-first (matching how topic mode sections).
  function keysForDim(dim) {
    if (dim === "frequency") {
      var present = {};
      words.forEach(function (word) {
        present[word.frequency] = true;
      });
      return FREQ_ORDER.filter(function (k) {
        return present[k];
      });
    }
    var counts = {};
    words.forEach(function (word) {
      counts[word.topic] = (counts[word.topic] || 0) + 1;
    });
    return Object.keys(counts).sort(function (a, b) {
      return counts[b] - counts[a];
    });
  }

  function labelForDim(dim, key) {
    return dim === "frequency"
      ? FREQ_LABEL[key] || key
      : TOPIC_LABEL[key] || key;
  }

  function chipColorClass(dim, key) {
    return dim === "frequency" ? "tag-freq freq-" + key : "tag-topic";
  }

  // A selected chip wears its tag color; a deselected one is muted.
  function applyChipState(btn, dim, on) {
    btn.className = on
      ? "vocab-chip " + chipColorClass(dim, btn.getAttribute("data-key"))
      : "vocab-chip vocab-chip--off";
  }

  // Build both chip rows (frequency and topic) from the data, all selected.
  function buildFilterBar() {
    filterEl.querySelectorAll(".vocab-filter-group").forEach(function (group) {
      var dim = group.getAttribute("data-dim");
      filters[dim] = {};
      group.querySelector(".vocab-filter-chips").innerHTML = keysForDim(dim)
        .map(function (key) {
          filters[dim][key] = true;
          return (
            '<button type="button" class="vocab-chip ' +
            chipColorClass(dim, key) +
            '" data-key="' +
            escAttr(key) +
            '">' +
            esc(labelForDim(dim, key)) +
            "</button>"
          );
        })
        .join("");
    });
  }

  // Shown only if both its frequency and its topic are still selected.
  function passesFilter(word) {
    return (
      filters.frequency[word.frequency] !== false &&
      filters.topic[word.topic] !== false
    );
  }

  // Lazy materialization: each group renders only its header + an empty,
  // height-reserved card container; the cards themselves are built on demand
  // when the group nears the viewport. Keeps the DOM small even with ~10k
  // entries, so search/filter re-renders stay snappy.
  var currentGroups = [];
  var groupObserver = null;

  function teardownObserver() {
    if (groupObserver) {
      groupObserver.disconnect();
      groupObserver = null;
    }
  }

  function estimateGroupHeight(count) {
    var containerW = groupsEl.clientWidth || window.innerWidth || 800;
    var gap = 13; // ~0.8rem
    var minCol = 200;
    var cols = Math.max(1, Math.floor((containerW + gap) / (minCol + gap)));
    var rows = Math.ceil(count / cols);
    return rows * 92; // ~card height incl. gap
  }

  function materializeGroup(container) {
    if (container.dataset.materialized) return;
    var idx = parseInt(container.dataset.gi, 10);
    var items = currentGroups[idx] && currentGroups[idx].items;
    if (!items) return;
    container.innerHTML = items.map(card).join("");
    container.style.minHeight = "";
    container.dataset.materialized = "1";
  }

  function render() {
    if (!loaded) return;
    var list = words.filter(function (word) {
      return matches(word) && passesFilter(word);
    });
    countEl.textContent =
      list.length + (list.length === 1 ? " word" : " words");

    teardownObserver();

    if (!list.length) {
      currentGroups = [];
      groupsEl.innerHTML = '<p class="vocab-empty">No matching words.</p>';
      return;
    }

    currentGroups = buildGroups(list);
    groupsEl.innerHTML = currentGroups
      .map(function (group, i) {
        var freqMod =
          mode === "frequency" ? " vocab-group--" + group.key : "";
        var minH = estimateGroupHeight(group.items.length);
        return (
          '<section class="vocab-group' + freqMod + '">' +
          '<h2 class="vocab-group-title">' +
          esc(group.label) +
          '<span class="vocab-group-count">' +
          group.items.length +
          "</span>" +
          "</h2>" +
          '<div class="vocab-cards" data-gi="' + i +
          '" style="min-height:' + minH + 'px"></div>' +
          "</section>"
        );
      })
      .join("");

    groupObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            materializeGroup(entry.target);
            groupObserver.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "600px 0px" }
    );
    groupsEl.querySelectorAll(".vocab-cards").forEach(function (c) {
      groupObserver.observe(c);
    });
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

  // One delegated handler for both rows: toggle a single chip, or flip a whole
  // row via its Select all / Unselect all. The dimension comes from the group.
  filterEl.addEventListener("click", function (e) {
    var group = e.target.closest(".vocab-filter-group");
    if (!group) return;
    var dim = group.getAttribute("data-dim");

    var chip = e.target.closest(".vocab-chip");
    if (chip) {
      var key = chip.getAttribute("data-key");
      filters[dim][key] = !filters[dim][key];
      applyChipState(chip, dim, filters[dim][key]);
      render();
      return;
    }

    var bulk = e.target.closest("button[data-bulk]");
    if (bulk) {
      var on = bulk.getAttribute("data-bulk") === "all";
      Object.keys(filters[dim]).forEach(function (k) {
        filters[dim][k] = on;
      });
      group.querySelectorAll(".vocab-chip").forEach(function (c) {
        applyChipState(c, dim, on);
      });
      render();
    }
  });

  var searchTimer = null;
  searchEl.addEventListener("input", function () {
    query = searchEl.value.trim();
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(render, 120);
  });

  // Flip a card on click (single-side modes): a two-phase 3D turn. The front
  // rotates to its edge (90 deg); while invisible we swap the visible face and
  // jump to the opposite edge (-90 deg); then the new face rotates flat. Each
  // face only ever shows within +/-90 deg, so no backface-visibility is needed.
  var TURN_MS = 200;
  groupsEl.addEventListener("click", function (e) {
    // Speaker works in every mode, so handle it before any mode-specific return.
    var speakBtn = e.target.closest(".vocab-speak");
    if (speakBtn) {
      playAudio(speakBtn);
      return;
    }

    // Suspend toggle: light-red background, no flip, no re-render.
    var suspendBtn = e.target.closest(".vocab-suspend");
    if (suspendBtn) {
      var sCard = e.target.closest(".vocab-card");
      if (!sCard) return;
      var id = sCard.getAttribute("data-id");
      if (!id) return;
      if (suspended[id]) {
        delete suspended[id];
        sCard.classList.remove("vocab-card--suspended");
      } else {
        suspended[id] = true;
        sCard.classList.add("vocab-card--suspended");
      }
      saveSuspended();
      return;
    }

    // Copy button: works in both-mode (data-copy) and flip-mode (visible side).
    var copyBtn = e.target.closest(".vocab-copy");
    if (copyBtn) {
      var anyCard = e.target.closest(".vocab-card");
      if (!anyCard) return;
      var text = anyCard.classList.contains("vocab-card--flip")
        ? anyCard.getAttribute(anyCard.classList.contains("flipped") ? "data-back" : "data-front")
        : anyCard.getAttribute("data-copy");
      copyText(text, copyBtn);
      return;
    }

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
  suspended = loadSuspended();
  showCategory = lsGet("vocabShowCategory") !== "0";
  showSources = lsGet("vocabShowSources") === "1";
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
  var audioBase = thisScript
    ? new URL("audio/", thisScript.src).href
    : "audio/";

  fetch(dataUrl)
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      words = data;
      loaded = true;
      buildFilterBar();
      render();
    })
    .catch(function () {
      groupsEl.innerHTML =
        '<p class="vocab-empty">Could not load vocabulary data.</p>';
    });
})();

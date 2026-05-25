(function () {
  var groupsEl = document.getElementById("vocab-groups");
  var countEl = document.getElementById("vocab-count");
  var searchEl = document.getElementById("vocab-search");
  var toggleEl = document.getElementById("vocab-toggle");
  var fontToggleEl = document.getElementById("font-toggle");

  var words = [];
  var mode = "frequency"; // or "topic"
  var query = "";

  var FREQ_ORDER = ["most", "sometimes", "rarely"];
  var FREQ_LABEL = {
    most: "Most used",
    sometimes: "Sometimes used",
    rarely: "Rarely used",
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
    religion: "Beliefs",
    monarchy: "Monarchy",
    nature: "Nature",
  };

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function matches(word) {
    if (!query) return true;
    var q = query.toLowerCase();
    return (
      word.thai.indexOf(query) !== -1 ||
      word.english.toLowerCase().indexOf(q) !== -1
    );
  }

  function card(word) {
    // Show the complementary dimension as a tag (topic when grouped by
    // frequency, frequency when grouped by topic), plus the source(s).
    var tag, tagClass;
    if (mode === "frequency") {
      tag = TOPIC_LABEL[word.topic] || word.topic;
      tagClass = "tag-topic";
    } else {
      tag = FREQ_LABEL[word.frequency] || word.frequency;
      tagClass = "tag-freq freq-" + word.frequency;
    }
    var sources = word.sources
      .map(function (s) {
        return '<span class="vocab-source">' + esc(s) + "</span>";
      })
      .join("");
    return (
      '<div class="vocab-card">' +
      '<div class="vocab-thai">' + esc(word.thai) + "</div>" +
      '<div class="vocab-en">' + esc(word.english) + "</div>" +
      '<div class="vocab-meta">' +
      '<div class="vocab-tags">' +
      '<span class="vocab-tag ' + tagClass + '">' + esc(tag) + "</span>" +
      "</div>" +
      '<div class="vocab-sources">' + sources + "</div>" +
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

  // Thai font preference (default Sarabun, the book style), persisted.
  function applyFont(font) {
    document.body.setAttribute("data-thai-font", font);
    fontToggleEl.querySelectorAll("button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-font") === font);
    });
    try {
      localStorage.setItem("thaiFont", font);
    } catch (e) {}
  }

  fontToggleEl.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-font]");
    if (btn) applyFont(btn.getAttribute("data-font"));
  });

  var savedFont;
  try {
    savedFont = localStorage.getItem("thaiFont");
  } catch (e) {}
  applyFont(savedFont || "sarabun");

  fetch("vocab.json")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      words = data;
      render();
    })
    .catch(function () {
      groupsEl.innerHTML =
        '<p class="vocab-empty">Could not load vocabulary data.</p>';
    });
})();

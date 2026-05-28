// Thai flashcards: FSRS-scheduled review over the vocabulary in vocab.json.
//
// Each vocabulary word becomes two independent cards — Thai->English ("t2e")
// and English->Thai ("e2t") — each with its own FSRS state. All progress lives
// in localStorage (no backend, no cross-device sync). Audio (Thai only) plays
// on whichever face shows the Thai word; missing mp3s simply no-op.
(function () {
  var DAY = 86400000;
  var DIRS = ["t2e", "e2t"];

  // ── Labels (kept in step with vocab.js) ───────────────────────────────────
  var FREQ_ORDER = ["everyday", "common", "occasional", "rare"];
  var FREQ_LABEL = {
    everyday: "Everyday",
    common: "Common",
    occasional: "Occasional",
    rare: "Rare",
  };
  var TOPIC_LABEL = {
    personality: "Personality", emotions: "Emotions", family: "Family",
    health: "Health", general: "General", grammar: "Grammar",
    expressions: "Expressions", time: "Time", culture: "Culture",
    beliefs: "Beliefs", monarchy: "Monarchy", nature: "Nature",
    law: "Legal", economy: "Economy", transport: "Transport",
    weather: "Weather", travel: "Travel", food: "Food",
  };

  // ── Storage ────────────────────────────────────────────────────────────────
  var STATE_KEY = "thaiFsrsState";
  var CONFIG_KEY = "thaiFsrsConfig";

  function lsGet(k) {
    try { return localStorage.getItem(k); } catch (e) { return null; }
  }
  function lsSet(k, v) {
    try { localStorage.setItem(k, v); } catch (e) {}
  }
  function loadJSON(k, fallback) {
    var raw = lsGet(k);
    if (!raw) return fallback;
    try { return JSON.parse(raw); } catch (e) { return fallback; }
  }

  var states = loadJSON(STATE_KEY, {}); // cardId -> FSRS card state
  var config = loadJSON(CONFIG_KEY, null) || {
    newPerDay: 15,
    excluded: { frequency: { rare: true, occasional: true }, topic: {} },
    day: null,
  };
  config.excluded = config.excluded || { frequency: {}, topic: {} };
  config.excluded.frequency = config.excluded.frequency || {};
  config.excluded.topic = config.excluded.topic || {};

  function saveStates() { lsSet(STATE_KEY, JSON.stringify(states)); }
  function saveConfig() { lsSet(CONFIG_KEY, JSON.stringify(config)); }

  // Local-midnight day key, so a card due "today" rolls over at midnight.
  function dayKey(now) {
    var d = new Date(now || Date.now());
    return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
  }

  // Per-day session bookkeeping: which words were already reviewed today (to
  // bury siblings) and how many new cards have been introduced today.
  function today() {
    var key = dayKey();
    if (!config.day || config.day.key !== key) {
      config.day = { key: key, seen: {}, newCount: 0 };
      saveConfig();
    }
    return config.day;
  }

  // ── DOM ──────────────────────────────────────────────────────────────────
  var $ = function (id) { return document.getElementById(id); };
  var homeEl = $("fc-home");
  var reviewEl = $("fc-review");
  var doneEl = $("fc-done");

  function show(el) {
    [homeEl, reviewEl, doneEl].forEach(function (s) { s.hidden = s !== el; });
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // ── Data + card construction ───────────────────────────────────────────────
  var words = [];
  var wordById = {};
  var audioBase = "audio/";

  function cardId(word, dir) { return word.id + ":" + dir; }
  function getState(id) { return states[id] || window.FSRS.emptyCard(); }

  function isExcluded(word) {
    return (
      config.excluded.frequency[word.frequency] === true ||
      config.excluded.topic[word.topic] === true
    );
  }

  // The Thai-facing text and prompt/answer for a direction.
  function faces(word, dir) {
    if (dir === "t2e") {
      return { front: word.thai, back: word.english, frontThai: true };
    }
    return { front: word.english, back: word.thai, frontThai: false };
  }

  // ── Queue building ───────────────────────────────────────────────────────
  // One card per word per day (sibling burial). Due cards first (shuffled),
  // then up to the remaining new-card allowance. Excluded words contribute
  // nothing — their cards are effectively suspended until re-included.
  function buildQueue(now) {
    now = now || Date.now();
    var day = today();
    var dueCards = [];
    var newCards = [];

    words.forEach(function (word) {
      if (isExcluded(word)) return;
      if (day.seen[word.id]) return; // a direction was already done today

      // Among the word's directions, prefer a due card; else offer it as new.
      var dueHere = [];
      var newHere = [];
      DIRS.forEach(function (dir) {
        var id = cardId(word, dir);
        var st = states[id];
        if (st && st.due != null && st.reps > 0) {
          if (st.due <= now) dueHere.push(id);
        } else {
          newHere.push(id);
        }
      });

      if (dueHere.length) {
        dueCards.push(pick(dueHere));
      } else if (newHere.length) {
        newCards.push(pick(newHere));
      }
    });

    shuffle(dueCards);
    shuffle(newCards);

    var allowance = Math.max(0, config.newPerDay - day.newCount);
    newCards = newCards.slice(0, allowance);

    return { due: dueCards, fresh: newCards, queue: dueCards.concat(newCards) };
  }

  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
  function shuffle(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
    return arr;
  }

  // ── Stats (mirror what Start would build) ──────────────────────────────────
  // Due / New are today's session counts; Left is the deck's remaining unseen
  // pool (cards never reviewed yet that aren't excluded), which decreases as
  // new cards get introduced. Excluded counts what filters hide right now.
  function refreshStats() {
    var built = buildQueue();
    var excluded = 0;
    var left = 0;
    words.forEach(function (word) {
      if (isExcluded(word)) {
        excluded += DIRS.length;
        return;
      }
      DIRS.forEach(function (dir) {
        var st = states[cardId(word, dir)];
        if (!st || st.reps === 0) left += 1;
      });
    });
    homeEl.querySelector('[data-stat="due"]').textContent = built.due.length;
    homeEl.querySelector('[data-stat="new"]').textContent = built.fresh.length;
    homeEl.querySelector('[data-stat="left"]').textContent = left;
    homeEl.querySelector('[data-stat="excluded"]').textContent = excluded;

    var empty = built.queue.length === 0;
    $("fc-start").hidden = empty;
    $("fc-home-note").hidden = !empty;
  }

  // ── Session state ──────────────────────────────────────────────────────────
  var queue = [];
  var sessionTotal = 0;
  var reviewed = 0;
  var revealed = false;
  var curId = null;
  var currentAudio = null;

  function parseId(id) {
    var bits = id.split(":");
    var dir = bits.pop();
    return { word: wordById[bits.join(":")], dir: dir };
  }

  function startSession() {
    var built = buildQueue();
    queue = built.queue;
    sessionTotal = queue.length;
    reviewed = 0;
    if (!queue.length) return finishSession();
    show(reviewEl);
    nextCard();
  }

  function nextCard() {
    if (!queue.length) return finishSession();
    curId = queue.shift();
    revealed = false;
    renderCard();
  }

  function renderCard() {
    var info = parseId(curId);
    var word = info.word;
    var f = faces(word, info.dir);

    var frontEl = $("fc-front");
    var backEl = $("fc-back");
    frontEl.className = "fc-card-face fc-card-front" + (f.frontThai ? " fc-thai" : " fc-en");
    frontEl.innerHTML = esc(f.front);
    backEl.className = "fc-card-face fc-card-back" + (f.frontThai ? " fc-en" : " fc-thai");
    backEl.innerHTML = esc(f.back);
    backEl.hidden = true;
    $("fc-divider").hidden = true;

    // Speaker is available whenever this card has a Thai side to hear.
    var speak = $("fc-speak");
    speak.hidden = false;
    speak.dataset.src = audioBase + word.id + ".mp3";

    // Copy: before reveal, copies the visible (front) side; after reveal both
    // sides are visible so copying targets the Thai word (matching vocab Both).
    var copy = $("fc-copy");
    copy.hidden = false;
    copy.classList.remove("copied");
    copy.dataset.front = f.front;
    copy.dataset.thai = word.thai;

    $("fc-show").hidden = false;
    $("fc-grades").hidden = true;

    updateProgress();

    // Autoplay Thai when it is on the front (Thai->English cards).
    stopAudio();
    if (f.frontThai) playAudio();
  }

  function copyCurrent() {
    var btn = $("fc-copy");
    var text = revealed ? btn.dataset.thai : btn.dataset.front;
    if (!text) return;
    function done() {
      btn.classList.add("copied");
      setTimeout(function () { btn.classList.remove("copied"); }, 1000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {
        fallbackCopy(text); done();
      });
    } else {
      fallbackCopy(text); done();
    }
  }
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }

  function revealAnswer() {
    if (revealed) return;
    revealed = true;
    $("fc-back").hidden = false;
    $("fc-divider").hidden = false;
    $("fc-show").hidden = true;

    // Fill projected intervals and reveal the grade buttons.
    var preview = window.FSRS.preview(getState(curId));
    var grades = $("fc-grades");
    grades.querySelectorAll(".fc-grade-ivl").forEach(function (span) {
      var g = +span.getAttribute("data-ivl");
      span.textContent = window.FSRS.formatInterval(preview[g]);
    });
    grades.hidden = false;

    // Autoplay Thai when it lives on the back (English->Thai cards).
    var info = parseId(curId);
    if (!faces(info.word, info.dir).frontThai) playAudio();
  }

  function grade(g) {
    if (!revealed) return;
    var info = parseId(curId);
    var prev = states[curId];
    var wasNew = !prev || prev.reps === 0;

    states[curId] = window.FSRS.review(prev, g, Date.now());

    var day = today();
    day.seen[info.word.id] = true; // bury the sibling direction for today
    if (wasNew) day.newCount += 1;
    saveStates();
    saveConfig();

    reviewed += 1;
    // "Again" comes back this session: a few cards later, or at the end.
    if (g === 1) {
      var pos = Math.min(queue.length, 3 + Math.floor(Math.random() * 3));
      queue.splice(pos, 0, curId);
    }
    nextCard();
  }

  // Shown only when the queue empties on its own (nothing left due today).
  function finishSession() {
    var sub = $("fc-done-sub");
    sub.textContent = reviewed
      ? "Reviewed " + reviewed + (reviewed === 1 ? " card." : " cards.")
      : "";
    show(doneEl);
  }

  // Leave the session early (the × button): graded cards are already saved, so
  // just return to the start screen with refreshed counts.
  function goHome() {
    refreshStats();
    show(homeEl);
  }

  function updateProgress() {
    var done = sessionTotal - queue.length - 1; // current card not yet graded
    var pct = sessionTotal ? Math.max(0, (done / sessionTotal) * 100) : 0;
    $("fc-progress-bar").style.width = pct + "%";
    $("fc-remaining").textContent = (queue.length + 1) + " left";
  }

  // ── Audio ──────────────────────────────────────────────────────────────────
  function stopAudio() {
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    $("fc-speak").classList.remove("playing");
  }
  function playAudio() {
    var speak = $("fc-speak");
    var src = speak.dataset.src;
    if (!src) return;
    stopAudio();
    currentAudio = new Audio(src);
    speak.classList.add("playing");
    currentAudio.addEventListener("ended", stopAudio);
    // Missing files (none generated yet) reject silently.
    currentAudio.play().catch(stopAudio);
  }

  // ── Settings UI (chips, stepper, font) ─────────────────────────────────────
  function presentTopics() {
    var counts = {};
    words.forEach(function (w) { counts[w.topic] = (counts[w.topic] || 0) + 1; });
    return Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; });
  }

  function chipClass(dim, key, included) {
    if (!included) return "fc-chip fc-chip--off";
    return dim === "frequency" ? "fc-chip tag-freq freq-" + key : "fc-chip tag-topic";
  }

  function buildChips() {
    homeEl.querySelectorAll(".fc-chips").forEach(function (box) {
      var dim = box.getAttribute("data-dim");
      var keys = dim === "frequency"
        ? FREQ_ORDER.filter(function (k) { return words.some(function (w) { return w.frequency === k; }); })
        : presentTopics();
      var labelOf = dim === "frequency"
        ? function (k) { return FREQ_LABEL[k] || k; }
        : function (k) { return TOPIC_LABEL[k] || k; };
      box.innerHTML = keys.map(function (key) {
        var included = config.excluded[dim][key] !== true;
        return '<button type="button" class="' + chipClass(dim, key, included) +
          '" data-key="' + esc(key) + '">' + esc(labelOf(key)) + "</button>";
      }).join("");
    });
  }

  function setChip(dim, key, included) {
    if (included) delete config.excluded[dim][key];
    else config.excluded[dim][key] = true;
  }

  function applyFont(font) {
    document.body.setAttribute("data-thai-font", font);
    $("fc-font-toggle").querySelectorAll("button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-font") === font);
    });
    lsSet("thaiFont", font);
  }

  function wireSettings() {
    var newPerDayEl = $("fc-new-per-day");
    newPerDayEl.value = config.newPerDay;

    // Manual typing: accept any non-negative integer up to 999. Empty/garbage
    // is left untouched while typing (don't snap to 0 mid-edit); blur restores
    // the displayed value to the committed setting.
    newPerDayEl.addEventListener("input", function () {
      var v = parseInt(this.value, 10);
      if (isNaN(v) || v < 0) return;
      if (v > 99999) v = 99999;
      config.newPerDay = v;
      this.value = v;
      saveConfig();
      refreshStats();
    });
    newPerDayEl.addEventListener("blur", function () {
      this.value = config.newPerDay;
    });

    $("fc-settings").addEventListener("click", function (e) {
      var step = e.target.closest("button[data-step]");
      if (step) {
        config.newPerDay = Math.max(0, config.newPerDay + +step.getAttribute("data-step"));
        newPerDayEl.value = config.newPerDay;
        saveConfig();
        refreshStats();
        return;
      }

      var chip = e.target.closest(".fc-chip");
      if (chip) {
        var box = chip.closest(".fc-chips");
        var dim = box.getAttribute("data-dim");
        var key = chip.getAttribute("data-key");
        var included = config.excluded[dim][key] === true; // currently off -> turn on
        setChip(dim, key, included);
        chip.className = chipClass(dim, key, included);
        saveConfig();
        refreshStats();
        return;
      }

      var bulk = e.target.closest("button[data-bulk]");
      if (bulk) {
        var group = bulk.closest(".fc-setting");
        var dim2 = group.getAttribute("data-dim");
        var on = bulk.getAttribute("data-bulk") === "all";
        group.querySelectorAll(".fc-chip").forEach(function (c) {
          setChip(dim2, c.getAttribute("data-key"), on);
          c.className = chipClass(dim2, c.getAttribute("data-key"), on);
        });
        saveConfig();
        refreshStats();
        return;
      }

      var font = e.target.closest("button[data-font]");
      if (font) applyFont(font.getAttribute("data-font"));
    });
  }

  // ── Wiring ───────────────────────────────────────────────────────────────
  function wire() {
    $("fc-start").addEventListener("click", startSession);
    $("fc-home-link").addEventListener("click", goHome);
    $("fc-exit").addEventListener("click", goHome);
    $("fc-show").addEventListener("click", revealAnswer);

    // Tap the card to reveal (mobile-friendly); speaker/copy don't reveal.
    $("fc-card").addEventListener("click", function (e) {
      if (e.target.closest("#fc-speak")) { playAudio(); return; }
      if (e.target.closest("#fc-copy")) { copyCurrent(); return; }
      if (!revealed) revealAnswer();
    });

    $("fc-grades").addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-grade]");
      if (btn) grade(+btn.getAttribute("data-grade"));
    });

    // Keyboard: space/enter reveals, 1-4 grade (desktop convenience).
    document.addEventListener("keydown", function (e) {
      if (reviewEl.hidden) return;
      if (!revealed && (e.key === " " || e.key === "Enter")) {
        e.preventDefault();
        revealAnswer();
      } else if (revealed && e.key >= "1" && e.key <= "4") {
        grade(+e.key);
      }
    });
  }

  // ── Boot ───────────────────────────────────────────────────────────────────
  applyFont(lsGet("thaiFont") || "sarabun");

  var thisScript = document.querySelector('script[src$="flashcards.js"]');
  var dataUrl = thisScript ? new URL("vocab.json", thisScript.src).href : "vocab.json";
  audioBase = thisScript ? new URL("audio/", thisScript.src).href : "audio/";

  fetch(dataUrl)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      words = data;
      words.forEach(function (w) { wordById[w.id] = w; });
      buildChips();
      wireSettings();
      wire();
      refreshStats();
      show(homeEl);
    })
    .catch(function () {
      homeEl.hidden = false;
      homeEl.innerHTML = '<p class="vocab-empty">Could not load vocabulary data.</p>';
    });
})();

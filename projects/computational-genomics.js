/* Interactive visualizations for the Computational Genomics project page.
   Each widget exposes an init() that is safe to call again after SPA
   navigation: it re-queries the freshly swapped DOM and an epoch counter
   stops any animation loop left over from a previous page instance. */
(function () {
  'use strict';

  var SKEW = {};
  window.SKEW = SKEW;

  // ── Skew diagram: locate the replication origin from the running G - C count ──

  var skewEpoch = 0;  // bumped on every init so stale animation frames stop themselves

  function mulberry32(seedValue) {
    return function () {
      seedValue |= 0; seedValue = (seedValue + 0x6D2B79F5) | 0;
      var t = Math.imul(seedValue ^ (seedValue >>> 15), 1 | seedValue);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  SKEW.init = function () {
    var root = document.querySelector('.skew-viz');
    if (!root) { return; }

    var myEpoch = ++skewEpoch;

    var canvas = root.querySelector('.skew-canvas');
    var ctx = canvas.getContext('2d');
    var playButton = root.querySelector('.skew-play');
    var stepButton = root.querySelector('.skew-step');
    var resetButton = root.querySelector('.skew-reset');
    var newButton = root.querySelector('.skew-new');
    var lengthSelect = root.querySelector('.skew-length');
    var speedSelect = root.querySelector('.skew-speed');
    var outPos = root.querySelector('.skew-pos');
    var outSkew = root.querySelector('.skew-skew');
    var outOri = root.querySelector('.skew-ori');
    var inputField = root.querySelector('.skew-input');

    var MAX_LENGTH = 10000;  // guard against pasting an entire chromosome

    var COLOR_G = '#2e7d32', COLOR_C = '#c0392b', COLOR_AT = '#d9d9d9';
    var COLOR_CURVE = '#1f6fb2', COLOR_ORI = '#d35400', COLOR_TEXT = '#555';

    var genomeLength = parseInt(lengthSelect.value, 10) || 600;
    var seed = 1;
    var genome = '';
    var skewValues = [];        // skewValues[p] = running G - C over the first p bases
    var prefixMinIndex = [];    // prefixMinIndex[p] = position of the minimum seen in 0..p
    var minValue = 0, maxValue = 0;

    var position = 0, playing = false, lastTime = 0, carry = 0, rafId = 0;
    var viewWidth = 760, viewHeight = 270;

    // Build a random sequence with a C-rich first half and a G-rich second half.
    function randomGenome(currentSeed, length) {
      var rng = mulberry32(currentSeed);
      var oriPlant = Math.floor(length * (0.5 + rng() * 0.25));
      var bases = '';
      for (var idx = 0; idx < length; idx++) {
        var roll = rng();
        var probC = idx < oriPlant ? 0.36 : 0.16;  // C-rich before ori (curve falls)
        var probG = idx < oriPlant ? 0.16 : 0.36;  // G-rich after ori (curve rises)
        var base;
        if (roll < probC) { base = 'C'; }
        else if (roll < probC + probG) { base = 'G'; }
        else if (roll < probC + probG + 0.24) { base = 'A'; }
        else { base = 'T'; }
        bases += base;
      }
      return bases;
    }

    // Recompute the skew array and its running minimum from the current genome.
    function computeSkew() {
      var n = genome.length;
      skewValues = new Array(n + 1);
      prefixMinIndex = new Array(n + 1);
      var running = 0, best = 0, bestIndex = 0;
      skewValues[0] = 0; prefixMinIndex[0] = 0;
      minValue = 0; maxValue = 0;
      for (var pos = 0; pos < n; pos++) {
        var symbol = genome.charAt(pos);
        if (symbol === 'G') { running += 1; }
        else if (symbol === 'C') { running -= 1; }
        skewValues[pos + 1] = running;
        if (running < best) { best = running; bestIndex = pos + 1; }
        prefixMinIndex[pos + 1] = bestIndex;
        if (running < minValue) { minValue = running; }
        if (running > maxValue) { maxValue = running; }
      }
    }

    // Keep only A/C/G/T (uppercased), capped to a drawable length.
    function sanitizeSequence(text) {
      var cleaned = (text || '').toUpperCase().replace(/[^ACGT]/g, '');
      return cleaned.length > MAX_LENGTH ? cleaned.slice(0, MAX_LENGTH) : cleaned;
    }

    // Grow the textarea to fit its content so the whole genome shows without a scrollbar.
    function fitInput() {
      if (!inputField) { return; }
      inputField.style.height = 'auto';
      inputField.style.height = inputField.scrollHeight + 'px';
    }

    // Adopt a clean sequence as the current genome and redraw from the start.
    function setGenome(sequence, writeField) {
      genome = sequence;
      genomeLength = genome.length;
      computeSkew();
      position = 0;
      if (writeField && inputField) { inputField.value = genome; }
      fitInput();
      resizeCanvas();
      draw();
    }

    // Generate a random genome at the length chosen in the select.
    function generate() {
      var length = parseInt(lengthSelect.value, 10) || 600;
      setGenome(randomGenome(seed, length), true);
    }

    function resizeCanvas() {
      var cssWidth = canvas.clientWidth || 760;
      var dpr = window.devicePixelRatio || 1;
      viewWidth = cssWidth;
      canvas.width = Math.round(cssWidth * dpr);
      canvas.height = Math.round(viewHeight * dpr);
      canvas.style.height = viewHeight + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function draw() {
      var plotLeft = 46, plotTop = 16, plotBottom = 212;
      var plotRight = viewWidth - 16;
      var plotW = Math.max(10, plotRight - plotLeft);
      var plotH = plotBottom - plotTop;
      var stripTop = 226, stripH = 20, stripBottom = stripTop + stripH;

      var range = maxValue - minValue;
      var pad = Math.max(1, range * 0.08);
      var top = maxValue + pad, bottom = minValue - pad;

      function xAt(pos) { return plotLeft + (pos / genomeLength) * plotW; }
      function yAt(value) { return plotTop + (top - value) / (top - bottom) * plotH; }

      ctx.clearRect(0, 0, viewWidth, viewHeight);

      // horizontal reference lines and y-axis labels
      ctx.font = "12px 'Inconsolata', monospace";
      ctx.textBaseline = 'middle';
      [maxValue, 0, minValue].forEach(function (value) {
        var y = yAt(value);
        ctx.fillStyle = COLOR_TEXT;
        ctx.textAlign = 'right';
        ctx.fillText(String(value), plotLeft - 8, y);
        ctx.strokeStyle = value === 0 ? '#bbb' : '#eee';
        ctx.setLineDash(value === 0 ? [4, 4] : []);
        ctx.beginPath();
        ctx.moveTo(plotLeft, y); ctx.lineTo(plotRight, y); ctx.stroke();
        ctx.setLineDash([]);
      });

      // genome strip, coloured by base, with 5' / 3' ends
      for (var idx = 0; idx < genomeLength; idx++) {
        var symbol = genome.charAt(idx);
        ctx.fillStyle = symbol === 'G' ? COLOR_G : (symbol === 'C' ? COLOR_C : COLOR_AT);
        var leftX = xAt(idx), rightX = xAt(idx + 1);
        ctx.fillRect(leftX, stripTop, Math.max(0.8, rightX - leftX + 0.4), stripH);
      }
      ctx.fillStyle = COLOR_TEXT;
      ctx.textBaseline = 'middle';
      ctx.textAlign = 'right';
      ctx.fillText("5'", plotLeft - 8, stripTop + stripH / 2);
      ctx.textAlign = 'left';
      ctx.fillText("3'", plotRight + 4, stripTop + stripH / 2);

      // skew curve revealed up to the current position
      ctx.strokeStyle = COLOR_CURVE;
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      for (var step = 0; step <= position; step++) {
        var curveX = xAt(step), curveY = yAt(skewValues[step]);
        if (step === 0) { ctx.moveTo(curveX, curveY); } else { ctx.lineTo(curveX, curveY); }
      }
      ctx.stroke();

      // predicted ori: the running minimum so far
      var oriPos = prefixMinIndex[position];
      var oriX = xAt(oriPos);
      ctx.strokeStyle = COLOR_ORI;
      ctx.lineWidth = 1.2;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.moveTo(oriX, plotTop); ctx.lineTo(oriX, stripBottom); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = COLOR_ORI;
      ctx.beginPath();
      ctx.arc(oriX, yAt(skewValues[oriPos]), 3.5, 0, Math.PI * 2); ctx.fill();
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      ctx.fillText('ori', oriX, plotTop + 1);

      // current walk position
      var cursorX = xAt(position);
      ctx.strokeStyle = '#999';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cursorX, plotTop); ctx.lineTo(cursorX, stripBottom); ctx.stroke();
      ctx.fillStyle = COLOR_CURVE;
      ctx.beginPath();
      ctx.arc(cursorX, yAt(skewValues[position]), 3, 0, Math.PI * 2); ctx.fill();

      if (outPos) { outPos.textContent = position + ' / ' + genomeLength; }
      if (outSkew) { outSkew.textContent = String(skewValues[position]); }
      if (outOri) { outOri.textContent = String(oriPos); }
    }

    function setPlaying(on) {
      playing = on;
      playButton.innerHTML = on ? '&#10074;&#10074; Pause' : '&#9654; Play';
      if (on) {
        if (position >= genomeLength) { position = 0; }
        lastTime = 0; carry = 0;
        rafId = requestAnimationFrame(frame);
      } else if (rafId) {
        cancelAnimationFrame(rafId); rafId = 0;
      }
    }

    function frame(time) {
      if (myEpoch !== skewEpoch || !canvas.isConnected) { playing = false; return; }
      if (!playing) { return; }
      if (!lastTime) { lastTime = time; }
      var dt = (time - lastTime) / 1000;
      lastTime = time;
      carry += dt * (parseInt(speedSelect.value, 10) || 250);
      var steps = Math.floor(carry);
      if (steps > 0) {
        position = Math.min(genomeLength, position + steps);
        carry -= steps;
        draw();
      }
      if (position >= genomeLength) { setPlaying(false); return; }
      rafId = requestAnimationFrame(frame);
    }

    playButton.onclick = function () { setPlaying(!playing); };
    stepButton.onclick = function () {
      setPlaying(false);
      position = Math.min(genomeLength, position + 1);
      draw();
    };
    resetButton.onclick = function () { setPlaying(false); position = 0; draw(); };
    newButton.onclick = function () { setPlaying(false); seed += 1; generate(); };
    lengthSelect.onchange = function () { setPlaying(false); generate(); };
    inputField.oninput = function () {
      setPlaying(false);
      var cleaned = sanitizeSequence(inputField.value);
      if (cleaned.length > 0) { setGenome(cleaned, false); }
      fitInput();
    };
    inputField.onchange = function () {
      var cleaned = sanitizeSequence(inputField.value);
      if (cleaned.length > 0) { setGenome(cleaned, true); }   // normalize the field
      else { inputField.value = genome; }                     // restore last valid sequence
    };
    window.onresize = function () {
      if (!canvas.isConnected) { return; }
      fitInput(); resizeCanvas(); draw();
    };

    generate();
  };

  // ── Greedy motif search: build a shared motif one string at a time ──

  var GREEDY = {};
  window.GREEDY = GREEDY;

  var greedyEpoch = 0;
  var GREEDY_T = 6;    // number of DNA strings
  var GREEDY_N = 24;   // length of each string
  var GREEDY_BASES = ['A', 'C', 'G', 'T'];

  function greedyCounts(motifs, k) {
    var counts = { A: [], C: [], G: [], T: [] };
    for (var col = 0; col < k; col++) {
      counts.A[col] = 0; counts.C[col] = 0; counts.G[col] = 0; counts.T[col] = 0;
    }
    for (var i = 0; i < motifs.length; i++) {
      for (var col2 = 0; col2 < k; col2++) { counts[motifs[i].charAt(col2)][col2] += 1; }
    }
    return counts;
  }

  function greedyConsensus(counts, k) {
    var result = '';
    for (var col = 0; col < k; col++) {
      var bestBase = 'A', bestVal = -1;
      for (var b = 0; b < 4; b++) {
        if (counts[GREEDY_BASES[b]][col] > bestVal) {
          bestVal = counts[GREEDY_BASES[b]][col]; bestBase = GREEDY_BASES[b];
        }
      }
      result += bestBase;
    }
    return result;
  }

  function greedyScore(motifs, k) {
    if (motifs.length === 0) { return 0; }
    var counts = greedyCounts(motifs, k), total = 0;
    for (var col = 0; col < k; col++) {
      var maxVal = 0;
      for (var b = 0; b < 4; b++) {
        if (counts[GREEDY_BASES[b]][col] > maxVal) { maxVal = counts[GREEDY_BASES[b]][col]; }
      }
      total += motifs.length - maxVal;
    }
    return total;
  }

  // Probability of one window of text under the profile, using Laplace pseudocounts.
  function greedyWindowProb(text, start, counts, numMotifs, k) {
    var prob = 1;
    for (var col = 0; col < k; col++) {
      prob *= (counts[text.charAt(start + col)][col] + 1) / (numMotifs + 4);
    }
    return prob;
  }

  GREEDY.init = function () {
    var root = document.querySelector('.greedy-viz');
    if (!root) { return; }
    var myEpoch = ++greedyEpoch;

    var stringsBox = root.querySelector('.greedy-strings');
    var countsTable = root.querySelector('.greedy-counts');
    var profileTable = root.querySelector('.greedy-profile');
    var statusBox = root.querySelector('.greedy-status');
    var bestBox = root.querySelector('.greedy-best');
    var playButton = root.querySelector('.greedy-play');
    var stepButton = root.querySelector('.greedy-step');
    var resetButton = root.querySelector('.greedy-reset');
    var newButton = root.querySelector('.greedy-new');
    var kSelect = root.querySelector('.greedy-k');
    var speedSelect = root.querySelector('.greedy-speed');

    var seed = 1;
    var k = parseInt(kSelect.value, 10) || 4;
    var dna = [];
    var seedIndex = 0;       // which k-mer of the first string is the current seed
    var starts = [];         // committed start positions for the seed currently building
    var bestStarts = null;   // best complete set found (length GREEDY_T)
    var bestScore = Infinity;
    var done = false;
    var playing = false, rafId = 0, lastTime = 0, carry = 0;

    // Sub-step state for the row currently being chosen.
    var phase = 'seed';      // 'seed' | 'scan' | 'commit' | 'scored'
    var scanRow = 0;         // string being scanned (equals starts.length during a scan)
    var scanPos = 0;         // window start under the scan cursor
    var scanBestPos = 0;     // best window seen so far this scan
    var scanBestProb = -1;
    var lastProb = 0;        // probability of the window just evaluated

    function buildStrings() {
      var rng = mulberry32(seed);
      var motif = '';
      for (var c = 0; c < k; c++) { motif += GREEDY_BASES[Math.floor(rng() * 4)]; }
      dna = [];
      for (var s = 0; s < GREEDY_T; s++) {
        var arr = [];
        for (var i = 0; i < GREEDY_N; i++) { arr.push(GREEDY_BASES[Math.floor(rng() * 4)]); }
        var start = Math.floor(rng() * (GREEDY_N - k + 1));
        for (var c2 = 0; c2 < k; c2++) { arr[start + c2] = motif.charAt(c2); }
        if (rng() < 0.7) { arr[start + Math.floor(rng() * k)] = GREEDY_BASES[Math.floor(rng() * 4)]; }
        dna.push(arr.join(''));
      }
    }

    function motifsFrom(startList) {
      var motifs = [];
      for (var r = 0; r < startList.length; r++) { motifs.push(dna[r].substr(startList[r], k)); }
      return motifs;
    }

    function reset() {
      seedIndex = 0; starts = []; bestStarts = null; bestScore = Infinity; done = false;
      phase = 'seed'; scanRow = 0; scanPos = 0; scanBestPos = 0; scanBestProb = -1; lastProb = 0;
    }

    function startScan() {
      scanRow = starts.length;
      scanPos = 0; scanBestPos = 0; scanBestProb = -1; lastProb = 0;
      phase = 'scan';
      if (scanRow >= GREEDY_T) { phase = 'scored'; }
    }

    function advance() {
      if (done) { return; }
      if (phase === 'seed') {
        starts = [seedIndex];                          // seed from the first string
        startScan();
      } else if (phase === 'scan') {
        // Score one window of the current string against the profile of committed rows.
        var counts = greedyCounts(motifsFrom(starts), k);
        lastProb = greedyWindowProb(dna[scanRow], scanPos, counts, starts.length, k);
        if (lastProb > scanBestProb) { scanBestProb = lastProb; scanBestPos = scanPos; }
        if (scanPos >= GREEDY_N - k) { phase = 'commit'; } else { scanPos += 1; }
      } else if (phase === 'commit') {
        starts.push(scanBestPos);                      // keep the most-probable window
        startScan();
      } else {                                         // 'scored': full set complete
        var s = greedyScore(motifsFrom(starts), k);
        if (s < bestScore) { bestScore = s; bestStarts = starts.slice(); }
        seedIndex += 1;
        starts = [];
        if (seedIndex > GREEDY_N - k) { done = true; } else { phase = 'seed'; }
      }
    }

    // Wrap one or more non-overlapping k-length windows of text in spans.
    function highlightRanges(text, ranges) {
      ranges = ranges.slice().sort(function (a, b) { return a.start - b.start; });
      var out = '', pos = 0;
      for (var i = 0; i < ranges.length; i++) {
        var s = ranges[i].start;
        if (s < pos) { continue; }
        out += text.slice(pos, s) + '<span class="' + ranges[i].cls + '">' +
          text.slice(s, s + k) + '</span>';
        pos = s + k;
      }
      return out + text.slice(pos);
    }

    // Highlight windows for one string plus whether the row is dimmed (not yet reached).
    function rowState(row) {
      var seedCls = 'greedy-kmer greedy-seed';
      if (done && bestStarts) {
        return { ranges: [{ start: bestStarts[row], cls: row === 0 ? seedCls : 'greedy-kmer' }] };
      }
      if (phase === 'seed') {
        return row === 0 ? { ranges: [{ start: seedIndex, cls: seedCls }] } : { dim: true };
      }
      if (row < starts.length) {
        return { ranges: [{ start: starts[row], cls: row === 0 ? seedCls : 'greedy-kmer' }] };
      }
      if (row === scanRow && phase === 'scan') {
        if (Math.abs(scanPos - scanBestPos) < k) {
          return { ranges: [{ start: scanPos, cls: 'greedy-scan' }] };
        }
        return { ranges: [
          { start: scanPos, cls: 'greedy-scan' },
          { start: scanBestPos, cls: 'greedy-scanbest' }
        ] };
      }
      if (row === scanRow && phase === 'commit') {
        return { ranges: [{ start: scanBestPos, cls: 'greedy-kmer' }] };
      }
      return { dim: true };
    }

    function render() {
      var html = '';
      for (var row = 0; row < GREEDY_T; row++) {
        var st = rowState(row);
        var rowCls = st.dim ? 'greedy-row greedy-dim' : 'greedy-row';
        var body = st.dim ? dna[row] : highlightRanges(dna[row], st.ranges);
        html += '<div class="' + rowCls + '">' + body + '</div>';
      }
      stringsBox.innerHTML = html;

      var shownStarts = (done && bestStarts) ? bestStarts : (starts.length ? starts : [seedIndex]);
      var counts = greedyCounts(motifsFrom(shownStarts), k);
      var numRows = shownStarts.length;   // m: rows folded into the profile

      function headerRow() {
        var h = '<tr><th></th>';
        for (var col = 0; col < k; col++) { h += '<th>' + (col + 1) + '</th>'; }
        return h + '</tr>';
      }

      // The column max is the same cell for counts and probabilities (constant denominator).
      function isColMax(base, col) {
        var value = counts[base][col];
        if (value <= 0) { return false; }
        for (var bb = 0; bb < 4; bb++) {
          if (counts[GREEDY_BASES[bb]][col] > value) { return false; }
        }
        return true;
      }

      var countsHtml = headerRow();
      for (var b = 0; b < 4; b++) {
        countsHtml += '<tr><th>' + GREEDY_BASES[b] + '</th>';
        for (var col2 = 0; col2 < k; col2++) {
          countsHtml += '<td class="' + (isColMax(GREEDY_BASES[b], col2) ? 'max' : '') + '">' +
            counts[GREEDY_BASES[b]][col2] + '</td>';
        }
        countsHtml += '</tr>';
      }
      var cons = greedyConsensus(counts, k);
      countsHtml += '<tr class="greedy-consensus"><td></td>';
      for (var col3 = 0; col3 < k; col3++) { countsHtml += '<td>' + cons.charAt(col3) + '</td>'; }
      countsHtml += '</tr>';
      countsTable.innerHTML = countsHtml;

      var profHtml = headerRow();
      for (var pb = 0; pb < 4; pb++) {
        profHtml += '<tr><th>' + GREEDY_BASES[pb] + '</th>';
        for (var pc = 0; pc < k; pc++) {
          var prob = (counts[GREEDY_BASES[pb]][pc] + 1) / (numRows + 4);
          profHtml += '<td class="' + (isColMax(GREEDY_BASES[pb], pc) ? 'max' : '') + '">' +
            prob.toFixed(2) + '</td>';
        }
        profHtml += '</tr>';
      }
      profileTable.innerHTML = profHtml;

      var seedLabel = 'Seed ' + (seedIndex + 1) + ' / ' + (GREEDY_N - k + 1);
      if (done) {
        statusBox.innerHTML = 'Done. All ' + (GREEDY_N - k + 1) + ' seeds tried.';
      } else if (phase === 'seed') {
        statusBox.innerHTML = seedLabel + ' &middot; place the seed k-mer of string 1';
      } else if (phase === 'scan') {
        statusBox.innerHTML = seedLabel + ' &middot; scanning string ' + (scanRow + 1) +
          ': window at column ' + (scanPos + 1) + ', P = ' + lastProb.toExponential(1) +
          ' &middot; best so far column ' + (scanBestPos + 1);
      } else if (phase === 'commit') {
        statusBox.innerHTML = seedLabel + ' &middot; string ' + (scanRow + 1) +
          ': most probable k-mer is at column ' + (scanBestPos + 1) + ', add it';
      } else {
        statusBox.innerHTML = seedLabel + ' &middot; set complete, score ' +
          greedyScore(motifsFrom(starts), k);
      }
      bestBox.innerHTML = bestStarts
        ? 'Best so far: <b>' + greedyConsensus(greedyCounts(motifsFrom(bestStarts), k), k) +
          '</b> (score ' + bestScore + ')'
        : 'Best so far: none yet';
    }

    function setPlaying(on) {
      playing = on;
      playButton.innerHTML = on ? '&#10074;&#10074; Pause' : '&#9654; Play';
      if (on) {
        if (done) { reset(); }
        lastTime = 0; carry = 0;
        rafId = requestAnimationFrame(frame);
      } else if (rafId) {
        cancelAnimationFrame(rafId); rafId = 0;
      }
    }

    function frame(time) {
      if (myEpoch !== greedyEpoch || !root.isConnected) { playing = false; return; }
      if (!playing) { return; }
      if (!lastTime) { lastTime = time; }
      carry += ((time - lastTime) / 1000) * (parseInt(speedSelect.value, 10) || 6);
      lastTime = time;
      var advanced = false;
      while (carry >= 1 && !done) { advance(); carry -= 1; advanced = true; }
      if (advanced) { render(); }
      if (done) { setPlaying(false); return; }
      rafId = requestAnimationFrame(frame);
    }

    playButton.onclick = function () { setPlaying(!playing); };
    stepButton.onclick = function () { setPlaying(false); advance(); render(); };
    resetButton.onclick = function () { setPlaying(false); reset(); render(); };
    newButton.onclick = function () { setPlaying(false); seed += 1; buildStrings(); reset(); render(); };
    kSelect.onchange = function () {
      setPlaying(false); k = parseInt(kSelect.value, 10) || 4; buildStrings(); reset(); render();
    };

    buildStrings();
    reset();
    render();
  };
})();

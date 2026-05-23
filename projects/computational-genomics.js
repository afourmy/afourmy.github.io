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

    // Adopt a clean sequence as the current genome and redraw from the start.
    function setGenome(sequence, writeField) {
      genome = sequence;
      genomeLength = genome.length;
      computeSkew();
      position = 0;
      if (writeField && inputField) { inputField.value = genome; }
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
    };
    inputField.onchange = function () {
      var cleaned = sanitizeSequence(inputField.value);
      if (cleaned.length > 0) { setGenome(cleaned, true); }   // normalize the field
      else { inputField.value = genome; }                     // restore last valid sequence
    };
    window.onresize = function () {
      if (!canvas.isConnected) { return; }
      resizeCanvas(); draw();
    };

    generate();
  };
})();

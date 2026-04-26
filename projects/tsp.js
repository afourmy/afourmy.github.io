(function () {
  "use strict";

  // ── Haversine distance (km) ──
  function haversine(a, b) {
    var R = 6371;
    var dLat = (b[0] - a[0]) * Math.PI / 180;
    var dLon = (b[1] - a[1]) * Math.PI / 180;
    var lat1 = a[0] * Math.PI / 180;
    var lat2 = b[0] * Math.PI / 180;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1) * Math.cos(lat2) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  // ── Build distance matrix ──
  function buildDistances(cities) {
    var n = cities.length;
    var d = [];
    for (var i = 0; i < n; i++) {
      d[i] = [];
      for (var j = 0; j < n; j++) {
        d[i][j] = i === j ? Infinity : haversine(cities[i], cities[j]);
      }
    }
    return d;
  }

  // ── Compute tour length ──
  function tourLength(tour, dist) {
    var len = 0;
    for (var i = 0; i < tour.length - 1; i++) {
      len += dist[tour[i]][tour[i + 1]];
    }
    len += dist[tour[tour.length - 1]][tour[0]];
    return len;
  }

  // ── Format a tour as a closed loop of [lat,lng] ──
  function formatTour(tour, cities) {
    var coords = tour.map(function (i) { return cities[i]; });
    coords.push(cities[tour[0]]);
    return coords;
  }

  // ── Insertion cost: inserting k between i and j ──
  function insertionCost(dist, i, j, k) {
    return dist[i][k] + dist[k][j] - dist[i][j];
  }

  // ── ALGORITHMS ──
  // Each returns { steps: [ [latlng, ...], ... ], lengths: [number, ...] }

  function nearestNeighbor(cities, dist) {
    var n = cities.length;
    var start = Math.floor(Math.random() * n);
    var visited = new Array(n).fill(false);
    var tour = [start];
    visited[start] = true;
    var steps = [];
    var lengths = [];
    var len = 0;

    while (tour.length < n) {
      var last = tour[tour.length - 1];
      var bestIdx = -1, bestDist = Infinity;
      for (var j = 0; j < n; j++) {
        if (!visited[j] && dist[last][j] < bestDist) {
          bestDist = dist[last][j];
          bestIdx = j;
        }
      }
      tour.push(bestIdx);
      visited[bestIdx] = true;
      len += bestDist;
      steps.push(formatTour(tour, cities));
      lengths.push(len + dist[bestIdx][start]);
    }
    return { steps: steps, lengths: lengths };
  }

  function nearestInsertion(cities, dist, farthest) {
    var n = cities.length;
    var start = Math.floor(Math.random() * n);
    var inTour = new Array(n).fill(false);
    inTour[start] = true;
    var tour = [start];
    var steps = [];
    var lengths = [];

    // Find nearest (or farthest) neighbor to start
    var bestN = -1, bestND = farthest ? -1 : Infinity;
    for (var j = 0; j < n; j++) {
      if (j === start) continue;
      if (farthest ? dist[start][j] > bestND : dist[start][j] < bestND) {
        bestND = dist[start][j];
        bestN = j;
      }
    }
    tour.push(bestN);
    inTour[bestN] = true;
    steps.push(formatTour(tour, cities));
    lengths.push(tourLength(tour, dist));

    while (tour.length < n) {
      // Selection: find node closest/farthest to tour
      var bestCity = -1, bestCityDist = farthest ? -1 : Infinity;
      for (var c = 0; c < n; c++) {
        if (inTour[c]) continue;
        // Distance to nearest node in tour
        var minToTour = Infinity;
        for (var t = 0; t < tour.length; t++) {
          if (dist[c][tour[t]] < minToTour) minToTour = dist[c][tour[t]];
        }
        if (farthest ? minToTour > bestCityDist : minToTour < bestCityDist) {
          bestCityDist = minToTour;
          bestCity = c;
        }
      }

      // Insertion: find best position
      var bestPos = 0, bestInsCost = Infinity;
      for (var i = 0; i < tour.length; i++) {
        var next = (i + 1) % tour.length;
        var cost = insertionCost(dist, tour[i], tour[next], bestCity);
        if (cost < bestInsCost) {
          bestInsCost = cost;
          bestPos = i + 1;
        }
      }
      tour.splice(bestPos, 0, bestCity);
      inTour[bestCity] = true;
      steps.push(formatTour(tour, cities));
      lengths.push(tourLength(tour, dist));
    }
    return { steps: steps, lengths: lengths };
  }

  function farthestInsertion(cities, dist) {
    return nearestInsertion(cities, dist, true);
  }

  function cheapestInsertion(cities, dist) {
    var n = cities.length;
    var start = Math.floor(Math.random() * n);
    var inTour = new Array(n).fill(false);
    inTour[start] = true;
    var tour = [start];
    var steps = [];
    var lengths = [];

    // Find nearest neighbor to start
    var bestN = -1, bestND = Infinity;
    for (var j = 0; j < n; j++) {
      if (j === start) continue;
      if (dist[start][j] < bestND) { bestND = dist[start][j]; bestN = j; }
    }
    tour.push(bestN);
    inTour[bestN] = true;
    steps.push(formatTour(tour, cities));
    lengths.push(tourLength(tour, dist));

    while (tour.length < n) {
      // Find the city+position whose insertion costs the least
      var bestCity = -1, bestPos = 0, bestCost = Infinity;
      for (var c = 0; c < n; c++) {
        if (inTour[c]) continue;
        for (var i = 0; i < tour.length; i++) {
          var next = (i + 1) % tour.length;
          var cost = insertionCost(dist, tour[i], tour[next], c);
          if (cost < bestCost) {
            bestCost = cost;
            bestCity = c;
            bestPos = i + 1;
          }
        }
      }
      tour.splice(bestPos, 0, bestCity);
      inTour[bestCity] = true;
      steps.push(formatTour(tour, cities));
      lengths.push(tourLength(tour, dist));
    }
    return { steps: steps, lengths: lengths };
  }

  // ── Map & visualization ──
  var map, cityMarkers = [], cities = [];
  var tourLine = null;
  var animTimer = null;

  // Default cities: major US cities
  var defaultCities = [
    [40.7128, -74.0060],   // New York
    [34.0522, -118.2437],  // Los Angeles
    [41.8781, -87.6298],   // Chicago
    [29.7604, -95.3698],   // Houston
    [33.4484, -112.0740],  // Phoenix
    [29.4241, -98.4936],   // San Antonio
    [32.7157, -117.1611],  // San Diego
    [32.7767, -96.7970],   // Dallas
    [37.3382, -121.8863],  // San Jose
    [30.2672, -97.7431],   // Austin
    [39.7392, -104.9903],  // Denver
    [47.6062, -122.3321],  // Seattle
    [38.9072, -77.0369],   // Washington DC
    [25.7617, -80.1918],   // Miami
    [42.3601, -71.0589],   // Boston
  ];

  function initMap() {
    map = L.map("tsp-map").setView([39.5, -98.35], 4);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 18
    }).addTo(map);

    map.on("click", function (e) {
      addCity([e.latlng.lat, e.latlng.lng]);
    });

    loadCities(defaultCities);
  }

  function addCity(latlng) {
    cities.push(latlng);
    var marker = L.circleMarker(latlng, {
      radius: 6, color: "#036", fillColor: "#036", fillOpacity: 1, weight: 1
    }).addTo(map);
    cityMarkers.push(marker);
    updateCityCount();
  }

  function loadCities(list) {
    clearAll();
    for (var i = 0; i < list.length; i++) addCity(list[i]);
    if (list.length > 1) map.fitBounds(L.latLngBounds(list).pad(0.1));
  }

  function clearAll() {
    stopAnimation();
    for (var i = 0; i < cityMarkers.length; i++) map.removeLayer(cityMarkers[i]);
    if (tourLine) { map.removeLayer(tourLine); tourLine = null; }
    cityMarkers = [];
    cities = [];
    updateCityCount();
    updateStatus("");
  }

  function updateCityCount() {
    var el = document.getElementById("tsp-city-count");
    if (el) el.textContent = cities.length;
  }

  function updateStatus(text) {
    var el = document.getElementById("tsp-status");
    if (el) el.textContent = text;
  }

  function drawTour(coords) {
    if (tourLine) map.removeLayer(tourLine);
    tourLine = L.polyline(coords, {
      color: "#c44", weight: 2.5, opacity: 0.85
    }).addTo(map);
  }

  function stopAnimation() {
    if (animTimer) { clearInterval(animTimer); animTimer = null; }
  }

  function runAlgorithm(algoFn) {
    stopAnimation();
    if (cities.length < 3) {
      updateStatus("Add at least 3 cities.");
      return;
    }
    var dist = buildDistances(cities);
    var result = algoFn(cities, dist);
    var steps = result.steps;
    var lengths = result.lengths;
    var speed = parseInt(document.getElementById("tsp-speed").value, 10) || 300;
    var idx = 0;

    updateStatus("Step 1 / " + steps.length +
      " — Tour: " + Math.round(lengths[0]) + " km");
    drawTour(steps[0]);

    animTimer = setInterval(function () {
      idx++;
      if (idx >= steps.length) {
        stopAnimation();
        updateStatus("Done — " + steps.length + " steps — Tour: " +
          Math.round(lengths[lengths.length - 1]) + " km");
        return;
      }
      drawTour(steps[idx]);
      updateStatus("Step " + (idx + 1) + " / " + steps.length +
        " — Tour: " + Math.round(lengths[idx]) + " km");
    }, speed);
  }

  // ── Generate random cities ──
  function generateRandom(n) {
    var pts = [];
    for (var i = 0; i < n; i++) {
      var lat = 25 + Math.random() * 23;  // ~25-48 (continental US)
      var lng = -122 + Math.random() * 57; // ~-122 to -65
      pts.push([lat, lng]);
    }
    loadCities(pts);
  }

  // ── Expose to page ──
  window.TSP = {
    init: initMap,
    clear: clearAll,
    generateRandom: generateRandom,
    runNearestNeighbor: function () { runAlgorithm(nearestNeighbor); },
    runNearestInsertion: function () { runAlgorithm(nearestInsertion); },
    runFarthestInsertion: function () { runAlgorithm(farthestInsertion); },
    runCheapestInsertion: function () { runAlgorithm(cheapestInsertion); }
  };
})();

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

  function tourLength(tour, dist) {
    var len = 0;
    for (var i = 0; i < tour.length - 1; i++) len += dist[tour[i]][tour[i + 1]];
    len += dist[tour[tour.length - 1]][tour[0]];
    return len;
  }

  function formatTour(tour, cities) {
    var coords = tour.map(function (i) { return cities[i]; });
    coords.push(cities[tour[0]]);
    return coords;
  }

  function insertionCost(dist, i, j, k) {
    return dist[i][k] + dist[k][j] - dist[i][j];
  }

  // ── ALGORITHMS ──

  function nearestNeighbor(cities, dist) {
    var n = cities.length;
    var start = Math.floor(Math.random() * n);
    var visited = new Array(n).fill(false);
    var tour = [start];
    visited[start] = true;
    var steps = [], lengths = [], len = 0;

    while (tour.length < n) {
      var last = tour[tour.length - 1];
      var bestIdx = -1, bestDist = Infinity;
      for (var j = 0; j < n; j++) {
        if (!visited[j] && dist[last][j] < bestDist) {
          bestDist = dist[last][j]; bestIdx = j;
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
    var steps = [], lengths = [];

    var bestN = -1, bestND = farthest ? -1 : Infinity;
    for (var j = 0; j < n; j++) {
      if (j === start) continue;
      if (farthest ? dist[start][j] > bestND : dist[start][j] < bestND) {
        bestND = dist[start][j]; bestN = j;
      }
    }
    tour.push(bestN);
    inTour[bestN] = true;
    steps.push(formatTour(tour, cities));
    lengths.push(tourLength(tour, dist));

    while (tour.length < n) {
      var bestCity = -1, bestCityDist = farthest ? -1 : Infinity;
      for (var c = 0; c < n; c++) {
        if (inTour[c]) continue;
        var minToTour = Infinity;
        for (var t = 0; t < tour.length; t++) {
          if (dist[c][tour[t]] < minToTour) minToTour = dist[c][tour[t]];
        }
        if (farthest ? minToTour > bestCityDist : minToTour < bestCityDist) {
          bestCityDist = minToTour; bestCity = c;
        }
      }
      var bestPos = 0, bestInsCost = Infinity;
      for (var i = 0; i < tour.length; i++) {
        var next = (i + 1) % tour.length;
        var cost = insertionCost(dist, tour[i], tour[next], bestCity);
        if (cost < bestInsCost) { bestInsCost = cost; bestPos = i + 1; }
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
    var steps = [], lengths = [];

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
      var bestCity = -1, bestPos = 0, bestCost = Infinity;
      for (var c = 0; c < n; c++) {
        if (inTour[c]) continue;
        for (var i = 0; i < tour.length; i++) {
          var next = (i + 1) % tour.length;
          var cost = insertionCost(dist, tour[i], tour[next], c);
          if (cost < bestCost) { bestCost = cost; bestCity = c; bestPos = i + 1; }
        }
      }
      tour.splice(bestPos, 0, bestCity);
      inTour[bestCity] = true;
      steps.push(formatTour(tour, cities));
      lengths.push(tourLength(tour, dist));
    }
    return { steps: steps, lengths: lengths };
  }

  // ── Per-section map instances ──

  var algorithms = {
    "nearest-neighbor": nearestNeighbor,
    "nearest-insertion": function (c, d) { return nearestInsertion(c, d, false); },
    "cheapest-insertion": cheapestInsertion,
    "farthest-insertion": farthestInsertion
  };

  var instances = {};

  function generateCities(n) {
    var pts = [];
    for (var i = 0; i < n; i++) {
      pts.push([25 + Math.random() * 23, -122 + Math.random() * 57]);
    }
    return pts;
  }

  // Shared city set so all maps show the same problem
  var sharedCities = generateCities(20);

  function createInstance(id) {
    var container = document.getElementById("tsp-" + id);
    if (!container) return;

    var inst = { markers: [], tourLine: null, timer: null, cities: [] };

    inst.map = L.map(container.querySelector(".tsp-map"), {
      scrollWheelZoom: false
    }).setView([39.5, -98.35], 4);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 18
    }).addTo(inst.map);

    inst.map.on("click", function (e) {
      addCity(inst, [e.latlng.lat, e.latlng.lng]);
    });

    var statusEl = container.querySelector(".tsp-status");
    var countEl = container.querySelector(".tsp-city-count");

    inst.updateStatus = function (t) { if (statusEl) statusEl.textContent = t; };
    inst.updateCount = function () { if (countEl) countEl.textContent = inst.cities.length; };

    // Wire up buttons
    container.querySelector(".tsp-btn-random").addEventListener("click", function () {
      sharedCities = generateCities(20);
      reloadAll();
    });
    container.querySelector(".tsp-btn-clear").addEventListener("click", function () {
      sharedCities = [];
      reloadAll();
    });
    container.querySelector(".tsp-btn-run").addEventListener("click", function () {
      runOn(inst, id);
    });

    instances[id] = inst;
    loadCities(inst, sharedCities);
  }

  function addCity(inst, latlng) {
    inst.cities.push(latlng);
    var m = L.circleMarker(latlng, {
      radius: 5, color: "#036", fillColor: "#036", fillOpacity: 1, weight: 1
    }).addTo(inst.map);
    inst.markers.push(m);
    inst.updateCount();
    // Also add to shared set so new maps get it
    sharedCities = inst.cities.slice();
    syncOthers(inst);
  }

  function loadCities(inst, list) {
    clearInstance(inst);
    for (var i = 0; i < list.length; i++) {
      inst.cities.push(list[i]);
      var m = L.circleMarker(list[i], {
        radius: 5, color: "#036", fillColor: "#036", fillOpacity: 1, weight: 1
      }).addTo(inst.map);
      inst.markers.push(m);
    }
    inst.updateCount();
    if (list.length > 1) inst.map.fitBounds(L.latLngBounds(list).pad(0.15));
  }

  function clearInstance(inst) {
    if (inst.timer) { clearInterval(inst.timer); inst.timer = null; }
    for (var i = 0; i < inst.markers.length; i++) inst.map.removeLayer(inst.markers[i]);
    if (inst.tourLine) { inst.map.removeLayer(inst.tourLine); inst.tourLine = null; }
    inst.markers = [];
    inst.cities = [];
    inst.updateCount();
    inst.updateStatus("");
  }

  function syncOthers(source) {
    var list = source.cities.slice();
    for (var id in instances) {
      if (instances[id] !== source) loadCities(instances[id], list);
    }
  }

  function reloadAll() {
    var list = sharedCities.slice();
    for (var id in instances) loadCities(instances[id], list);
  }

  function runOn(inst, id) {
    if (inst.timer) { clearInterval(inst.timer); inst.timer = null; }
    if (inst.tourLine) { inst.map.removeLayer(inst.tourLine); inst.tourLine = null; }

    if (inst.cities.length < 3) {
      inst.updateStatus("Place at least 3 cities.");
      return;
    }

    var dist = buildDistances(inst.cities);
    var result = algorithms[id](inst.cities, dist);
    var steps = result.steps, lengths = result.lengths;
    var speedEl = document.getElementById("tsp-" + id).querySelector(".tsp-speed");
    var speed = speedEl ? parseInt(speedEl.value, 10) : 300;
    var idx = 0;

    inst.tourLine = L.polyline(steps[0], {
      color: "#c44", weight: 2.5, opacity: 0.85
    }).addTo(inst.map);
    inst.updateStatus("Step 1 / " + steps.length +
      " | Tour: " + Math.round(lengths[0]) + " km");

    inst.timer = setInterval(function () {
      idx++;
      if (idx >= steps.length) {
        clearInterval(inst.timer); inst.timer = null;
        inst.updateStatus("Done | " + steps.length + " steps | Tour: " +
          Math.round(lengths[lengths.length - 1]) + " km");
        return;
      }
      inst.tourLine.setLatLngs(steps[idx]);
      inst.updateStatus("Step " + (idx + 1) + " / " + steps.length +
        " | Tour: " + Math.round(lengths[idx]) + " km");
    }, speed);
  }

  // ── Init all sections ──
  window.TSP = {
    init: function () {
      var ids = ["nearest-neighbor", "nearest-insertion", "cheapest-insertion", "farthest-insertion"];
      for (var i = 0; i < ids.length; i++) createInstance(ids[i]);
    }
  };
})();

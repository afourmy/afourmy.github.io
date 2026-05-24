(function () {
  "use strict";

  // ── network datasets: [name, lat, lng] for nodes, [source, dest] for the rest ──
  var RAW = {
    usa: {
      center: [39.5, -98.35], zoom: 4,
      nodes: [["Jackson", 32.29876, -90.18481], ["Palo Alto", 37.44188, -122.14302], ["Austin", 30.26715, -97.74306], ["Washington", 38.89511, -77.03637], ["Chicago", 41.85003, -87.65005], ["San Jose", 37.33939, -121.89496], ["San Diego", 32.71533, -117.15726], ["Dallas", 32.78306, -96.80667], ["Philadelphia", 39.95234, -75.16379], ["Los Angeles", 34.05223, -118.24368], ["Detroit", 42.33143, -83.04575], ["Richmond", 37.55376, -77.46026], ["Atlanta", 33.749, -84.38798], ["Boston", 42.35843, -71.05977], ["Houston", 29.76328, -95.36327], ["Baltimore", 39.29038, -76.61219], ["Cleveland", 41.4995, -81.69541], ["Columbus", 39.96118, -82.99879], ["Cincinnati", 39.162, -84.45689], ["Cambridge", 42.3751, -71.10561], ["Minneapolis", 44.97997, -93.26384], ["New York", 40.71427, -74.00597], ["Sacramento", 38.58157, -121.4944], ["San Francisco", 37.77493, -122.41942], ["Orange", 33.78779, -117.85311], ["Oakland", 37.80437, -122.2708], ["Denver", 39.73915, -104.9847]],
      fibers: [["Houston", "Dallas"], ["Jackson", "Atlanta"], ["Baltimore", "Washington"], ["Cleveland", "Chicago"], ["Cleveland", "Columbus"], ["Cleveland", "Detroit"], ["Cleveland", "Cincinnati"], ["Cleveland", "New York"], ["Palo Alto", "San Jose"], ["Cambridge", "New York"], ["Minneapolis", "Chicago"], ["New York", "Philadelphia"], ["New York", "Washington"], ["Austin", "Dallas"], ["Washington", "San Jose"], ["Washington", "Richmond"], ["Washington", "Atlanta"], ["Sacramento", "Oakland"], ["Chicago", "Boston"], ["Chicago", "Denver"], ["San Jose", "Los Angeles"], ["San Jose", "Oakland"], ["San Diego", "Los Angeles"], ["San Francisco", "Oakland"], ["Dallas", "Los Angeles"], ["Dallas", "Atlanta"], ["Orange", "Los Angeles"], ["Oakland", "Denver"]],
      traffic: [["Dallas", "Philadelphia"], ["Sacramento", "Atlanta"], ["Sacramento", "Austin"], ["San Diego", "Boston"], ["Minneapolis", "Jackson"], ["Orange", "Minneapolis"], ["Cincinnati", "Richmond"], ["Palo Alto", "Columbus"], ["San Francisco", "New York"], ["Boston", "Philadelphia"], ["Houston", "Chicago"]]
    },
    europe: {
      center: [47, 6], zoom: 4,
      nodes: [["router5", 47.40379, -0.40801], ["router6", 48.42125, 2.3669], ["router7", 49.98884, 4.55399], ["router8", 50.41434, 8.0845], ["router9", 45.55973, 2.01376], ["router10", 46.38621, 4.53389], ["router11", 46.31282, 7.62321], ["router12", 47.28163, 10.39033], ["router13", 48.0505, 6.50843], ["router14", 49.35693, 9.7413], ["router15", 49.22507, 10.10994], ["router16", 44.6986, 5.59525], ["router17", 44.09842, 2.15113], ["router18", 51.16509, 12.04148], ["router19", 53.00251, 14.63773], ["router20", 52.89891, 9.62091], ["router21", 51.1307, 15.32225], ["router22", 46.86709, 14.50996], ["router23", 48.2265, 16.39424], ["router24", 49.84703, 15.23113], ["router25", 49.20979, -0.93635], ["router26", 48.49234, -3.30473], ["router27", 43.45728, -0.07442], ["router28", 41.41868, -7.34192], ["router29", 42.18726, -5.11537], ["router30", 39.02974, -6.8319], ["router31", 40.25315, -4.39981], ["router32", 37.72767, -4.65515], ["router33", 40.43266, -2.26973], ["router34", 44.93342, 10.16825], ["router35", 42.03686, -0.12209], ["router36", 42.78305, -2.89561], ["router37", 39.19071, -2.36072]],
      fibers: [["router30", "router32"], ["router32", "router31"], ["router31", "router33"], ["router33", "router35"], ["router35", "router36"], ["router36", "router31"], ["router31", "router28"], ["router28", "router29"], ["router29", "router36"], ["router28", "router30"], ["router36", "router27"], ["router35", "router17"], ["router27", "router17"], ["router17", "router16"], ["router16", "router34"], ["router34", "router12"], ["router12", "router22"], ["router22", "router23"], ["router23", "router24"], ["router15", "router24"], ["router15", "router12"], ["router15", "router18"], ["router18", "router19"], ["router19", "router21"], ["router21", "router24"], ["router19", "router20"], ["router20", "router18"], ["router20", "router8"], ["router14", "router8"], ["router14", "router12"], ["router12", "router13"], ["router13", "router11"], ["router11", "router10"], ["router10", "router16"], ["router10", "router7"], ["router13", "router6"], ["router7", "router8"], ["router14", "router21"], ["router6", "router25"], ["router25", "router5"], ["router5", "router26"], ["router5", "router9"], ["router9", "router17"], ["router9", "router10"], ["router16", "router11"], ["router32", "router37"], ["router37", "router33"], ["router26", "router25"]],
      traffic: [["router30", "router19"], ["router33", "router21"], ["router26", "router24"], ["router26", "router32"], ["router22", "router5"], ["router20", "router16"], ["router23", "router30"]]
    },
    line: {
      center: [49, 9], zoom: 5,
      nodes: [["1", 46.88154, 1.70621], ["2", 48.96864, 4.78896], ["3", 50.60287, 8.55541], ["4", 49.52448, 12.73052], ["5", 47.91226, 17.06544]],
      fibers: [["1", "2"], ["2", "3"], ["3", "4"], ["4", "5"]],
      traffic: [["3", "5"], ["2", "4"], ["1", "5"], ["1", "2"], ["1", "3"]]
    }
  };

  // ── geographic distance (km) between two [lat, lng] points ──
  function haversine(a, b) {
    var R = 6371;
    var dLat = (b[0] - a[0]) * Math.PI / 180;
    var dLon = (b[1] - a[1]) * Math.PI / 180;
    var lat1 = a[0] * Math.PI / 180, lat2 = b[0] * Math.PI / 180;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  // turn a raw dataset into a network: node coordinates plus fibers with lengths
  function buildNet(raw) {
    var nodes = {};
    raw.nodes.forEach(function (n) { nodes[n[0]] = [n[1], n[2]]; });
    var fibers = raw.fibers.map(function (f) {
      return { a: f[0], b: f[1], d: haversine(nodes[f[0]], nodes[f[1]]) };
    });
    return { nodes: nodes, names: Object.keys(nodes), fibers: fibers,
      traffic: raw.traffic, center: raw.center, zoom: raw.zoom };
  }

  // ── shortest path by linear programming ──
  //
  // Each fiber becomes two directed arcs (one per direction), each a binary
  // variable whose cost is the fiber length. Flow-conservation constraints make
  // the chosen arcs form a single path: outgoing minus incoming flow is +1 at
  // the source and 0 at every other switch except the destination, whose
  // equation (-1) is implied by the rest and therefore omitted. Minimizing the
  // total cost then yields the shortest path.
  function shortestPath(net, source, dest) {
    if (typeof solver === "undefined") return null;

    var arcs = [];
    net.fibers.forEach(function (f, idx) {
      arcs.push({ u: f.a, v: f.b, d: f.d, fiber: idx });
      arcs.push({ u: f.b, v: f.a, d: f.d, fiber: idx });
    });

    var variables = {}, binaries = {};
    arcs.forEach(function (arc, i) {
      var v = { cost: arc.d };
      if (arc.u !== dest) v["n_" + arc.u] = 1;   // arc leaves u
      if (arc.v !== dest) v["n_" + arc.v] = -1;  // arc enters v
      variables["a" + i] = v;
      binaries["a" + i] = 1;
    });

    var constraints = {};
    net.names.forEach(function (name) {
      if (name === dest) return;
      constraints["n_" + name] = { equal: name === source ? 1 : 0 };
    });

    var sol = solver.Solve({ optimize: "cost", opType: "min",
      constraints: constraints, variables: variables, binaries: binaries });
    if (!sol.feasible) return null;

    var next = {}, fibers = [];
    arcs.forEach(function (arc, i) {
      if (sol["a" + i] > 0.5) { next[arc.u] = arc.v; fibers.push(arc.fiber); }
    });

    var order = [source], cur = source, guard = 0;
    while (cur !== dest && next[cur] !== undefined && guard++ <= net.names.length) {
      cur = next[cur]; order.push(cur);
    }
    var distance = 0;
    fibers.forEach(function (fi) { distance += net.fibers[fi].d; });
    return { order: order, fibers: fibers, distance: distance };
  }

  // ── conflict graph ──
  // route every connection, then make one vertex per connection and join two
  // vertices whenever their routes share at least one fiber
  function conflictGraph(net) {
    var fibersOf = net.traffic.map(function (d) {
      var r = shortestPath(net, d[0], d[1]);
      return r ? r.fibers : [];
    });
    var nodes = net.traffic.map(function (d, i) {
      return { id: i, label: "P" + (i + 1), endpoints: d[0] + " → " + d[1] };
    });
    var links = [];
    for (var i = 0; i < fibersOf.length; i++) {
      var used = {};
      fibersOf[i].forEach(function (f) { used[f] = true; });
      for (var j = i + 1; j < fibersOf.length; j++) {
        if (fibersOf[j].some(function (f) { return used[f]; })) {
          links.push({ source: i, target: j });
        }
      }
    }
    return { nodes: nodes, links: links };
  }

  // ── map ──
  var map, baseLayer, routeLayer, net, statusEl;

  function latlngs(net, names) {
    return names.map(function (name) { return net.nodes[name]; });
  }

  function setStatus(left, right) {
    if (!statusEl) return;
    statusEl.innerHTML = "<span>" + left + "</span><span>" + (right || "") + "</span>";
  }

  function drawNetwork() {
    baseLayer.clearLayers();
    net.fibers.forEach(function (f) {
      L.polyline([net.nodes[f.a], net.nodes[f.b]],
        { color: "#9aa7b4", weight: 2, opacity: 0.9 }).addTo(baseLayer);
    });
    net.names.forEach(function (name) {
      L.circleMarker(net.nodes[name],
        { radius: 4, color: "#036", fillColor: "#036", fillOpacity: 1, weight: 1 })
        .bindTooltip(name, { permanent: false }).addTo(baseLayer);
    });
    map.fitBounds(L.latLngBounds(net.names.map(function (n) { return net.nodes[n]; })).pad(0.12));
  }

  function routeOne(index) {
    routeLayer.clearLayers();
    var demand = net.traffic[index];
    var source = demand[0], dest = demand[1];

    // the demand itself: a straight dashed line from source to destination,
    // drawn over a white casing so it stands out against the fibers and the route
    var demandLine = [net.nodes[source], net.nodes[dest]];
    L.polyline(demandLine,
      { color: "#fff", weight: 6, opacity: 0.9 }).addTo(routeLayer);
    L.polyline(demandLine,
      { color: "#0a3cff", weight: 3, opacity: 1, dashArray: "10 8" }).addTo(routeLayer);

    var result = shortestPath(net, source, dest);
    if (!result || result.order[result.order.length - 1] !== dest) {
      setStatus(source + " &rarr; " + dest, "No path found");
      return;
    }
    L.polyline(latlngs(net, result.order),
      { color: "#c44", weight: 4, opacity: 0.9 }).addTo(routeLayer);

    setStatus(source + " &rarr; " + dest,
      "Shortest route: " + Math.round(result.distance) + " km, " +
      result.fibers.length + " fiber" + (result.fibers.length === 1 ? "" : "s"));
  }

  function fillDemands(select) {
    select.innerHTML = "";
    net.traffic.forEach(function (demand, i) {
      var opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = demand[0] + " → " + demand[1];
      select.appendChild(opt);
    });
  }

  function loadNetwork(key, demandSelect) {
    net = buildNet(RAW[key]);
    drawNetwork();
    fillDemands(demandSelect);
    demandSelect.value = "0";
    routeOne(0);
  }

  function initRouting() {
    var container = document.getElementById("swap-routing");
    if (!container) return;
    statusEl = container.querySelector(".tsp-status");

    map = L.map(container.querySelector(".tsp-map")).setView([39.5, -98.35], 4);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors", maxZoom: 18
    }).addTo(map);
    baseLayer = L.layerGroup().addTo(map);
    routeLayer = L.layerGroup().addTo(map);

    var networkSelect = container.querySelector(".swap-network");
    var demandSelect = container.querySelector(".swap-demand");

    networkSelect.addEventListener("change", function () {
      loadNetwork(networkSelect.value, demandSelect);
    });
    demandSelect.addEventListener("change", function () {
      routeOne(parseInt(demandSelect.value, 10));
    });

    loadNetwork(networkSelect.value, demandSelect);
  }

  // ── transformed-graph view (D3 force layout) ──
  function initGraph() {
    var container = document.getElementById("swap-graph");
    if (!container || typeof d3 === "undefined") return;
    var canvas = container.querySelector(".swap-graph-canvas");
    var graphStatus = container.querySelector(".tsp-status");
    var select = container.querySelector(".swap-graph-network");
    var sim = null;

    function render(graph) {
      if (sim) sim.stop();
      canvas.innerHTML = "";
      var width = canvas.clientWidth || 600, height = 420;
      var svg = d3.select(canvas).append("svg")
        .attr("width", width).attr("height", height);

      var link = svg.append("g")
        .attr("stroke", "#9aa7b4").attr("stroke-width", 1.6).attr("stroke-opacity", 0.9)
        .selectAll("line").data(graph.links).join("line");

      var node = svg.append("g").selectAll("g").data(graph.nodes).join("g")
        .style("cursor", "grab").call(drag());
      node.append("circle").attr("r", 18)
        .attr("fill", "#cfe0fb").attr("stroke", "#4a90d9").attr("stroke-width", 2);
      node.append("text").text(function (d) { return d.label; })
        .attr("text-anchor", "middle").attr("dy", 4)
        .attr("font-size", 13).attr("font-weight", 600).attr("fill", "#1b2733");
      node.append("title").text(function (d) { return d.endpoints; });

      sim = d3.forceSimulation(graph.nodes)
        .force("link", d3.forceLink(graph.links).id(function (d) { return d.id; })
          .distance(120).strength(1))
        .force("charge", d3.forceManyBody().strength(-1500).distanceMax(width))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("x", d3.forceX(width / 2).strength(0.06))
        .force("y", d3.forceY(height / 2).strength(0.06))
        .force("collide", d3.forceCollide(30))
        .alphaDecay(0.015)
        .on("tick", function () {
          link.attr("x1", function (d) { return d.source.x; })
            .attr("y1", function (d) { return d.source.y; })
            .attr("x2", function (d) { return d.target.x; })
            .attr("y2", function (d) { return d.target.y; });
          node.attr("transform", function (d) {
            d.x = Math.max(20, Math.min(width - 20, d.x));
            d.y = Math.max(20, Math.min(height - 20, d.y));
            return "translate(" + d.x + "," + d.y + ")";
          });
        });

      function drag() {
        return d3.drag()
          .on("start", function (e, d) { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on("drag", function (e, d) { d.fx = e.x; d.fy = e.y; })
          .on("end", function (e, d) { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; });
      }
    }

    function build(key) {
      var graph = conflictGraph(buildNet(RAW[key]));
      if (graphStatus) {
        graphStatus.innerHTML = "<span>" + graph.nodes.length + " connections</span><span>" +
          graph.links.length + " sharing a fiber</span>";
      }
      render(graph);
    }

    select.addEventListener("change", function () { build(select.value); });
    build(select.value);
  }

  window.SWAP = {
    init: function () { initRouting(); initGraph(); }
  };
})();

(function () {
  "use strict";

  // ── US cities dataset [lat, lng, population, name] ──
  var US_CITIES = [
    [40.7127837,-74.0059413,8405837,"New York"],
    [34.0522342,-118.2436849,3884307,"Los Angeles"],
    [41.8781136,-87.6297982,2718782,"Chicago"],
    [29.7604267,-95.3698028,2195914,"Houston"],
    [39.9525839,-75.1652215,1553165,"Philadelphia"],
    [33.4483771,-112.0740373,1513367,"Phoenix"],
    [29.4241219,-98.4936282,1409019,"San Antonio"],
    [32.715738,-117.1610838,1355896,"San Diego"],
    [32.7766642,-96.7969879,1257676,"Dallas"],
    [37.3382082,-121.8863286,998537,"San Jose"],
    [30.267153,-97.7430608,885400,"Austin"],
    [39.768403,-86.158068,843393,"Indianapolis"],
    [30.3321838,-81.6556510,842583,"Jacksonville"],
    [37.7749295,-122.4194155,837442,"San Francisco"],
    [39.9611755,-82.9987942,822553,"Columbus"],
    [35.2270869,-80.8431267,792862,"Charlotte"],
    [32.7554883,-97.3307658,792727,"Fort Worth"],
    [42.331427,-83.0457538,688701,"Detroit"],
    [31.7775757,-106.4424559,674433,"El Paso"],
    [35.1495343,-90.0489801,653450,"Memphis"],
    [47.6062095,-122.3320708,652405,"Seattle"],
    [39.7392358,-104.990251,649495,"Denver"],
    [38.9071923,-77.0368707,646449,"Washington"],
    [42.3600825,-71.0588801,645966,"Boston"],
    [36.1626638,-86.7816016,634464,"Nashville"],
    [39.2903848,-76.6121893,622104,"Baltimore"],
    [35.4675602,-97.5164276,610613,"Oklahoma City"],
    [38.2526647,-85.7584557,609893,"Louisville"],
    [45.5230622,-122.6764816,609456,"Portland"],
    [36.1699412,-115.1398296,603488,"Las Vegas"],
    [43.0389025,-87.9064736,599164,"Milwaukee"],
    [35.0853336,-106.6055534,556495,"Albuquerque"],
    [32.2217429,-110.926479,526116,"Tucson"],
    [36.7468422,-119.7725868,509924,"Fresno"],
    [38.5815719,-121.4943996,479686,"Sacramento"],
    [33.7700504,-118.1937395,469428,"Long Beach"],
    [39.0997265,-94.5785667,467007,"Kansas City"],
    [33.4151843,-111.8314724,457587,"Mesa"],
    [36.8529263,-75.9779850,448479,"Virginia Beach"],
    [33.7489954,-84.3879824,447841,"Atlanta"],
    [38.8338816,-104.8213634,439886,"Colorado Springs"],
    [41.2523634,-95.9979883,434353,"Omaha"],
    [35.7795897,-78.6381787,431746,"Raleigh"],
    [25.7616798,-80.1917902,417650,"Miami"],
    [37.8043637,-122.2711137,406253,"Oakland"],
    [44.977753,-93.2650108,400070,"Minneapolis"],
    [36.1539816,-95.9927750,398121,"Tulsa"],
    [41.49932,-81.6943605,390113,"Cleveland"],
    [37.688889,-97.336111,386552,"Wichita"],
    [32.735687,-97.1080656,379577,"Arlington"],
    [29.9510658,-90.0715323,378715,"New Orleans"],
    [35.3732921,-119.0187125,363630,"Bakersfield"],
    [27.950575,-82.4571776,352957,"Tampa"],
    [21.3069444,-157.8583333,347884,"Honolulu"],
    [39.7294319,-104.8319195,345803,"Aurora"],
    [33.8352932,-117.9145036,345012,"Anaheim"],
    [33.7455731,-117.8678338,334227,"Santa Ana"],
    [38.6270025,-90.1994042,318416,"St. Louis"],
    [33.9533487,-117.3961564,316619,"Riverside"],
    [27.8005828,-97.3963810,316381,"Corpus Christi"],
    [38.0405837,-84.5037164,308428,"Lexington"],
    [40.4406248,-79.9958864,305841,"Pittsburgh"],
    [61.2180556,-149.9002778,300950,"Anchorage"],
    [37.9577016,-121.2907796,298118,"Stockton"],
    [39.1031182,-84.5120196,297517,"Cincinnati"],
    [44.9537029,-93.0899578,294873,"St. Paul"],
    [41.6639383,-83.5552120,282313,"Toledo"],
    [36.0726354,-79.7919754,279639,"Greensboro"],
    [40.735657,-74.1723667,278427,"Newark"],
    [33.0198431,-96.6988856,274409,"Plano"],
    [36.0395247,-114.9817213,270811,"Henderson"],
    [40.8257625,-96.6851982,268738,"Lincoln"],
    [42.8864468,-78.8783689,258959,"Buffalo"],
    [40.7281575,-74.0776417,257342,"Jersey City"],
    [32.6400541,-117.0841955,256780,"Chula Vista"],
    [41.079273,-85.1393513,256496,"Fort Wayne"],
    [28.5383355,-81.3792365,255483,"Orlando"],
    [27.773056,-82.64,249688,"St. Petersburg"],
    [33.3061605,-111.8412502,249146,"Chandler"],
    [27.5305671,-99.4803241,248142,"Laredo"],
    [36.8507689,-76.2858726,246139,"Norfolk"],
    [35.9940329,-78.898619,245475,"Durham"],
    [43.0730517,-89.4012302,243344,"Madison"],
    [33.5778631,-101.8551665,239538,"Lubbock"],
    [33.6839473,-117.7946942,236716,"Irvine"],
    [36.0998596,-80.244216,236441,"Winston-Salem"],
    [33.5386523,-112.1859866,234632,"Glendale"],
    [32.912624,-96.6388833,234566,"Garland"],
    [25.8575963,-80.2781057,233394,"Hialeah"],
    [39.5296329,-119.8138027,233294,"Reno"],
    [36.7682088,-76.2874927,230571,"Chesapeake"],
    [33.3528264,-111.789027,229972,"Gilbert"],
    [30.4582829,-91.1403196,229426,"Baton Rouge"],
    [32.8140177,-96.9488945,228653,"Irving"],
    [33.4941704,-111.9260519,226918,"Scottsdale"],
    [36.1988592,-115.1175013,226877,"North Las Vegas"],
    [37.5482697,-121.9885719,224922,"Fremont"],
    [43.6187102,-116.2146068,214237,"Boise"],
    [37.5407246,-77.4360481,214114,"Richmond"],
    [34.1083449,-117.2897652,213708,"San Bernardino"],
    [33.5206608,-86.8024900,212113,"Birmingham"],
    [47.6587802,-117.4260466,210721,"Spokane"],
    [43.16103,-77.6109219,210358,"Rochester"],
    [41.6005448,-93.6091064,207510,"Des Moines"],
    [37.6390972,-120.9968782,204933,"Modesto"],
    [35.0526641,-78.8783585,204408,"Fayetteville"],
    [47.2528768,-122.4442906,203446,"Tacoma"],
    [34.1975048,-119.1770516,203007,"Oxnard"],
    [34.0922335,-117.435048,203003,"Fontana"],
    [32.4609764,-84.9877094,202824,"Columbus"],
    [32.3668052,-86.2999689,201332,"Montgomery"],
    [33.9424658,-117.2296717,201175,"Moreno Valley"],
    [32.5251516,-93.7501789,200327,"Shreveport"],
    [41.7605849,-88.3200715,199963,"Aurora"],
    [40.9312099,-73.8987469,199766,"Yonkers"],
    [41.0814447,-81.5190053,198100,"Akron"],
    [33.660297,-117.9992265,197575,"Huntington Beach"],
    [34.7464809,-92.2895948,197357,"Little Rock"],
    [33.4734978,-82.0105148,197350,"Augusta"],
    [35.2219971,-101.8312969,196429,"Amarillo"],
    [34.1425078,-118.255075,196021,"Glendale"],
    [30.6953657,-88.0398912,194899,"Mobile"],
    [42.9633599,-85.6680863,192294,"Grand Rapids"],
    [40.7607793,-111.8910474,191180,"Salt Lake City"],
    [30.4382559,-84.2807329,186411,"Tallahassee"],
    [34.7303688,-86.5861037,186254,"Huntsville"],
    [32.7459645,-96.9977846,183372,"Grand Prairie"],
    [35.9606384,-83.9207392,183270,"Knoxville"],
    [42.2625932,-71.8022934,182544,"Worcester"],
    [37.0870821,-76.4730122,182020,"Newport News"],
    [25.9017472,-97.4974838,181860,"Brownsville"],
    [38.9822282,-94.6707917,181260,"Overland Park"],
    [34.3916641,-118.542586,179590,"Santa Clarita"],
    [41.8239891,-71.4128343,177994,"Providence"],
    [33.7739053,-117.9414477,175140,"Garden Grove"],
    [35.0456297,-85.3096801,173366,"Chattanooga"],
    [33.1958696,-117.3794834,172794,"Oceanside"],
    [32.2987573,-90.1848103,172638,"Jackson"],
    [26.1224386,-80.1373174,172389,"Fort Lauderdale"],
    [38.440429,-122.7140548,171990,"Santa Rosa"],
    [34.1063989,-117.5931084,171386,"Rancho Cucamonga"],
    [27.2730492,-80.3582261,171016,"Port St. Lucie"],
    [33.4255104,-111.9400054,168228,"Tempe"],
    [34.0633443,-117.6508876,167500,"Ontario"],
    [45.6387281,-122.6614861,167405,"Vancouver"],
    [26.5628537,-81.9495331,165831,"Cape Coral"],
    [43.5445959,-96.7311034,164676,"Sioux Falls"],
    [37.2089572,-93.2922989,164122,"Springfield"],
    [33.5805955,-112.2373779,162592,"Peoria"],
    [26.007765,-80.2962555,162329,"Pembroke Pines"],
    [38.4087993,-121.3716178,161007,"Elk Grove"],
    [44.9428975,-123.0350963,160614,"Salem"],
    [34.6867846,-118.1541632,159523,"Lancaster"],
    [33.8752935,-117.5664384,159503,"Corona"],
    [44.0520691,-123.0867536,159190,"Eugene"],
    [34.5794343,-118.1164613,157161,"Palmdale"],
    [36.6777372,-121.6555013,155662,"Salinas"],
    [42.1014831,-72.589811,153703,"Springfield"],
    [29.6910625,-95.2091006,152735,"Pasadena"],
    [40.5852602,-105.084423,152061,"Fort Collins"],
    [37.6688205,-122.0807964,151574,"Hayward"],
    [34.055103,-117.7499909,151348,"Pomona"],
    [35.79154,-78.7811169,151088,"Cary"],
    [42.2711311,-89.0939952,150251,"Rockford"],
    [38.8048355,-77.0469214,148892,"Alexandria"],
    [33.1192068,-117.086421,148738,"Escondido"],
    [33.1972465,-96.6397822,148559,"McKinney"],
    [39.114053,-94.6274636,148483,"Kansas City"],
    [41.525031,-88.0817251,147806,"Joliet"],
    [37.36883,-122.0363496,147559,"Sunnyvale"],
    [33.8358492,-118.3406288,147478,"Torrance"],
    [41.1865478,-73.1951767,147216,"Bridgeport"],
    [39.7047095,-105.0813734,147214,"Lakewood"],
    [26.0112014,-80.1494901,146526,"Hollywood"],
    [40.9167654,-74.1718110,145948,"Paterson"],
    [41.7508391,-88.1535352,144864,"Naperville"],
    [43.0481221,-76.1474244,144669,"Syracuse"],
    [32.7667955,-96.5991593,143484,"Mesquite"],
    [39.7589478,-84.1916069,143355,"Dayton"],
    [32.0835407,-81.0998342,142772,"Savannah"],
    [36.5297706,-87.3594528,142357,"Clarksville"],
    [33.7877944,-117.8531119,139969,"Orange"],
    [34.1477849,-118.1445155,139731,"Pasadena"],
    [33.8703596,-117.9242966,138981,"Fullerton"],
    [31.1171194,-97.7277959,137147,"Killeen"],
    [33.1506744,-96.8236116,136791,"Frisco"],
    [37.0298687,-76.3452218,136699,"Hampton"],
    [26.2034071,-98.2300124,136639,"McAllen"],
    [42.5144566,-83.0146526,134873,"Warren"],
    [47.610377,-122.2006786,133992,"Bellevue"],
    [40.6916132,-112.0010501,133579,"West Valley City"],
    [34.0007104,-81.0348144,133358,"Columbia"],
    [38.8813958,-94.8191285,131885,"Olathe"],
    [42.5803122,-83.0302033,131224,"Sterling Heights"],
    [41.308274,-72.9278835,130660,"New Haven"],
    [25.9860762,-80.3035602,130288,"Miramar"],
    [31.549333,-97.1466695,129030,"Waco"],
    [34.1705609,-118.8375937,128731,"Thousand Oaks"],
    [41.9778795,-91.6656232,128429,"Cedar Rapids"],
    [32.7764749,-79.9310512,127999,"Charleston"],
    [36.3302284,-119.2920585,127763,"Visalia"],
    [39.0558235,-95.6890185,127679,"Topeka"],
    [40.6639916,-74.2107006,127558,"Elizabeth"],
    [29.6516344,-82.3248262,127488,"Gainesville"],
    [39.8680412,-104.9719243,127359,"Thornton"],
    [38.7521235,-121.2880059,127035,"Roseville"],
    [32.9756415,-96.8899636,126700,"Carrollton"],
    [26.271192,-80.2706044,126604,"Coral Springs"],
    [41.0534302,-73.5387341,126456,"Stamford"],
    [34.2694474,-118.781482,126181,"Simi Valley"],
    [37.9779776,-122.0310733,125880,"Concord"],
    [41.7637111,-72.6850932,125017,"Hartford"],
    [47.3809335,-122.2348431,124435,"Kent"],
    [30.2240897,-92.0198427,124276,"Lafayette"],
    [31.9973456,-102.0779146,123933,"Midland"],
    [33.6292337,-112.3679279,123546,"Surprise"],
    [33.2148412,-97.1330683,123099,"Denton"],
    [34.5362184,-117.2927641,121096,"Victorville"],
    [37.9715592,-87.5710898,120310,"Evansville"],
    [37.3541079,-121.9552356,120245,"Santa Clara"],
    [32.4487364,-99.7331439,120099,"Abilene"],
    [33.9519347,-83.357567,119980,"Athens"],
    [38.1040864,-122.2566367,118837,"Vallejo"],
    [40.6084305,-75.4901833,118577,"Allentown"],
    [35.2225668,-97.4394777,118197,"Norman"],
    [30.080174,-94.1265562,117796,"Beaumont"],
    [39.0911161,-94.4155068,117240,"Independence"],
    [35.8456213,-86.39027,117044,"Murfreesboro"],
    [42.2808256,-83.7430378,117025,"Ann Arbor"],
    [39.7817213,-89.6501481,117006,"Springfield"],
    [37.8715926,-122.272747,116768,"Berkeley"],
    [40.6936488,-89.5889864,116513,"Peoria"],
    [40.2338438,-111.6585337,116288,"Provo"],
    [34.0686206,-118.0275667,115708,"El Monte"],
    [38.9517053,-92.3340724,115276,"Columbia"],
    [42.732535,-84.5555347,113972,"Lansing"],
    [46.8771863,-96.7898034,113658,"Fargo"],
    [33.9401088,-118.1331593,113242,"Downey"],
    [33.6411316,-117.9186689,112174,"Costa Mesa"],
    [34.2257255,-77.9447102,112067,"Wilmington"],
    [39.8027644,-105.0874842,111707,"Arvada"],
    [33.9616801,-118.3531311,111542,"Inglewood"],
    [25.9420377,-80.2456045,111378,"Miami Gardens"],
    [33.1580933,-117.3505939,110972,"Carlsbad"],
    [39.8366528,-105.0372046,110945,"Westminster"],
    [44.0121221,-92.4801989,110742,"Rochester"],
    [31.8456816,-102.3676431,110720,"Odessa"],
    [42.9956397,-71.4547891,110378,"Manchester"],
    [42.0354084,-88.2825668,110145,"Elgin"],
    [40.6096698,-111.9391031,110077,"West Jordan"],
    [30.5082551,-97.678896,109821,"Round Rock"],
    [27.9658533,-82.8001026,109703,"Clearwater"],
    [41.5581525,-73.0514965,109676,"Waterbury"],
    [45.5001357,-122.4302013,109397,"Gresham"],
    [38.2493581,-122.0399663,109320,"Fairfield"],
    [45.7832856,-108.5006904,109059,"Billings"],
    [42.6334247,-71.3161718,108861,"Lowell"],
    [34.274646,-119.2290316,108817,"Ventura"],
    [38.2544472,-104.6091409,108249,"Pueblo"],
    [35.9556923,-80.0053176,107741,"High Point"],
    [34.0686208,-117.9389526,107740,"West Covina"],
    [37.9357576,-122.3477486,107571,"Richmond"],
    [33.5539143,-117.2139232,107479,"Murrieta"],
    [42.3736158,-71.1097335,107289,"Cambridge"],
    [38.0049214,-121.805789,107100,"Antioch"],
    [33.4936391,-117.1483648,106780,"Temecula"],
    [33.9022367,-118.081733,106589,"Norwalk"],
    [39.5807452,-104.8771726,106114,"Centennial"],
    [47.9789848,-122.2020794,105370,"Everett"],
    [28.0344621,-80.5886646,104898,"Palm Bay"],
    [33.9137085,-98.4933873,104898,"Wichita Falls"],
    [44.5191590,-88.019826,104779,"Green Bay"],
    [37.6879241,-122.4702079,104739,"Daly City"],
    [34.1808392,-118.3089661,104709,"Burbank"],
    [32.9483335,-96.7298519,104475,"Richardson"],
    [26.2378597,-80.1247667,104410,"Pompano Beach"],
    [32.8546197,-79.9748103,104054,"North Charleston"],
    [36.060949,-95.7974526,103500,"Broken Arrow"],
    [40.0149856,-105.2705456,103166,"Boulder"],
    [26.7153424,-80.0533746,102436,"West Palm Beach"],
    [34.9530337,-120.4357191,102216,"Santa Maria"],
    [32.7947731,-116.9625269,102211,"El Cajon"],
    [41.5236437,-90.5776367,102157,"Davenport"],
    [34.1064001,-117.3703235,101910,"Rialto"],
    [32.3199396,-106.7636538,101324,"Las Cruces"],
    [37.5629917,-122.3255254,101128,"San Mateo"],
    [33.046233,-96.994174,101074,"Lewisville"],
    [41.6763545,-86.2519898,100886,"South Bend"],
    [28.0394654,-81.9498042,100710,"Lakeland"],
    [42.1292241,-80.085059,100671,"Erie"],
    [32.3512601,-95.3010624,100223,"Tyler"],
    [29.5635666,-95.2860474,100065,"Pearland"],
    [30.627977,-96.3344068,100050,"College Station"]
  ];

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
    var tour = [start];
    var steps = [], lengths = [];

    // minDist[c] = distance from c to its nearest tour city
    var minDist = new Array(n);
    var inTour = new Array(n).fill(false);
    inTour[start] = true;
    for (var c = 0; c < n; c++) {
      minDist[c] = inTour[c] ? -1 : dist[c][start];
    }

    while (tour.length < n) {
      // selection: pick closest (or farthest) city to the tour
      var bestCity = -1, bestCityDist = farthest ? -1 : Infinity;
      for (var c = 0; c < n; c++) {
        if (inTour[c]) continue;
        if (farthest ? minDist[c] > bestCityDist : minDist[c] < bestCityDist) {
          bestCityDist = minDist[c]; bestCity = c;
        }
      }
      // insertion: find the position that minimizes tour length increase
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
      // update minDist with the newly added city
      for (var c = 0; c < n; c++) {
        if (!inTour[c] && dist[c][bestCity] < minDist[c]) {
          minDist[c] = dist[c][bestCity];
        }
      }
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

  // ── OPTIMIZATION HEURISTICS ──

  function nodeInsertion(cities, dist) {
    // build an initial tour with nearest neighbor (no animation)
    var n = cities.length;
    var start = Math.floor(Math.random() * n);
    var visited = new Array(n).fill(false);
    var tour = [start];
    visited[start] = true;
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
    }

    var best = tourLength(tour, dist);
    var steps = [formatTour(tour, cities)];
    var lengths = [best];
    var stable = false;

    while (!stable) {
      stable = true;
      for (var i = 0; i < n; i++) {
        for (var j = 0; j < n; j++) {
          if (j === i) continue;
          // remove node at position i, reinsert at position j
          var node = tour[i];
          var candidate = tour.slice();
          candidate.splice(i, 1);
          var insertAt = j > i ? j - 1 : j;
          candidate.splice(insertAt, 0, node);
          var len = tourLength(candidate, dist);
          if (len < best) {
            tour = candidate;
            best = len;
            steps.push(formatTour(tour, cities));
            lengths.push(best);
            stable = false;
          }
        }
      }
    }
    return { steps: steps, lengths: lengths };
  }

  // ── Per-section map instances ──

  var algorithms = {
    "nearest-neighbor": nearestNeighbor,
    "nearest-insertion": function (c, d) { return nearestInsertion(c, d, false); },
    "cheapest-insertion": cheapestInsertion,
    "farthest-insertion": farthestInsertion,
    "node-insertion": nodeInsertion
  };

  var instances = {};

  function citiesForThreshold(threshold) {
    var pts = [];
    for (var i = 0; i < US_CITIES.length; i++) {
      if (US_CITIES[i][2] >= threshold) {
        pts.push([US_CITIES[i][0], US_CITIES[i][1]]);
      }
    }
    return pts;
  }

  var currentThreshold = 500000;
  var sharedCities = citiesForThreshold(currentThreshold);

  function createInstance(id) {
    var container = document.getElementById("tsp-" + id);
    if (!container) return;

    var inst = { markers: [], tourLine: null, timer: null, cities: [] };

    inst.map = L.map(container.querySelector(".tsp-map")).setView([39.5, -98.35], 4);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 18
    }).addTo(inst.map);

    inst.map.on("click", function (e) {
      addCity(inst, [e.latlng.lat, e.latlng.lng]);
    });

    var statusEl = container.querySelector(".tsp-status");
    var countEl = container.querySelector(".tsp-city-count");

    inst.updateStatus = function (left, right) {
      if (!statusEl) return;
      if (arguments.length === 0) { statusEl.innerHTML = ""; return; }
      statusEl.innerHTML = "<span>" + left + "</span><span>" + right + "</span>";
    };
    inst.updateCount = function () { if (countEl) countEl.textContent = inst.cities.length; };

    var datasetSelect = container.querySelector(".tsp-dataset");
    datasetSelect.value = String(currentThreshold);
    datasetSelect.addEventListener("change", function () {
      currentThreshold = parseInt(datasetSelect.value, 10);
      sharedCities = citiesForThreshold(currentThreshold);
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
    if (inst.timer) { clearTimeout(inst.timer); inst.timer = null; }
    for (var i = 0; i < inst.markers.length; i++) inst.map.removeLayer(inst.markers[i]);
    if (inst.tourLine) { inst.map.removeLayer(inst.tourLine); inst.tourLine = null; }
    inst.markers = [];
    inst.cities = [];
    inst.updateCount();
    inst.updateStatus();
  }

  function syncOthers(source) {
    var list = source.cities.slice();
    for (var id in instances) {
      if (instances[id] !== source) loadCities(instances[id], list);
    }
  }

  function reloadAll() {
    var list = sharedCities.slice();
    for (var id in instances) {
      loadCities(instances[id], list);
      // Sync all dropdown values
      var sel = document.getElementById("tsp-" + id).querySelector(".tsp-dataset");
      if (sel) sel.value = String(currentThreshold);
    }
  }

  function runOn(inst, id) {
    if (inst.timer) { clearTimeout(inst.timer); inst.timer = null; }
    if (inst.tourLine) { inst.map.removeLayer(inst.tourLine); inst.tourLine = null; }

    if (inst.cities.length < 3) {
      inst.updateStatus("Place at least 3 cities.");
      return;
    }

    var dist = buildDistances(inst.cities);
    var result = algorithms[id](inst.cities, dist);
    var steps = result.steps, lengths = result.lengths;
    var speedEl = document.getElementById("tsp-" + id).querySelector(".tsp-speed");
    var idx = 0;

    inst.tourLine = L.polyline(steps[0], {
      color: "#c44", weight: 2.5, opacity: 0.85
    }).addTo(inst.map);
    inst.updateStatus("Step 1 / " + steps.length,
      "Tour: " + Math.round(lengths[0]) + " km");

    function tick() {
      idx++;
      if (idx >= steps.length) {
        inst.timer = null;
        inst.updateStatus("Done | " + steps.length + " steps",
          "Tour: " + Math.round(lengths[lengths.length - 1]) + " km");
        return;
      }
      inst.tourLine.setLatLngs(steps[idx]);
      inst.updateStatus("Step " + (idx + 1) + " / " + steps.length,
        "Tour: " + Math.round(lengths[idx]) + " km");
      var curSpeed = speedEl ? parseInt(speedEl.value, 10) : 300;
      inst.timer = setTimeout(tick, curSpeed);
    }
    inst.timer = setTimeout(tick, speedEl ? parseInt(speedEl.value, 10) : 300);
  }

  // ── Init all sections ──
  window.TSP = {
    init: function () {
      var ids = ["nearest-neighbor", "nearest-insertion", "cheapest-insertion", "farthest-insertion", "node-insertion"];
      for (var i = 0; i < ids.length; i++) createInstance(ids[i]);
    }
  };
})();

(function () {
  // Apply the saved theme as early as possible to avoid a flash of the wrong one.
  try {
    document.documentElement.setAttribute(
      "data-theme",
      localStorage.getItem("theme") || "light"
    );
  } catch (e) {
    document.documentElement.setAttribute("data-theme", "light");
  }

  var menu = [
    { en: "Mathematics", cssClass: "submenu-sections", columns: [
      [
        { href: "math/bases.html", en: "Foundations" },
        { href: "math/suites.html", en: "Sequences" },
        { href: "math/fonctions-usuelles.html", en: "Standard Functions" },
        { href: "math/comparaisons.html", en: "Asymptotic Comparison" },
        { href: "math/polynomes.html", en: "Polynomials" },
        { href: "math/linear-algebra.html", en: "Linear Algebra" },
        { href: "math/groups.html", en: "Groups" },
        { href: "math/topologie.html", en: "Topology" },
      ],
      [
        { href: "math/complexes.html", en: "Complex Numbers" },
        { href: "math/continuite.html", en: "Continuity" },
        { href: "math/ensembles.html", en: "Sets" },
        { href: "math/convexite.html", en: "Convexity" },
        { href: "math/equations-differentielles.html", en: "Differential Equations" },
        { href: "math/matrices.html", en: "Matrices" },
        { href: "math/anneaux-corps.html", en: "Rings and Fields" },
        { href: "math/reduction.html", en: "Reduction" },
      ],
      [
        { href: "math/denombrement.html", en: "Combinatorics" },
        { href: "math/derivation.html", en: "Differentiation" },
        { href: "math/calcul-integral.html", en: "Integral Calculus" },
        { href: "math/arithmetique.html", en: "Arithmetic" },
        { href: "math/probabilites.html", en: "Probability" },
        { href: "math/determinants.html", en: "Determinants" },
        { href: "math/espaces-euclidiens.html", en: "Euclidean Spaces" },
      ]
    ]},
    { en: "Computer Science", columns: [
      [
        { href: "cs/algorithmics.html", en: "Algorithmics" },
        { href: "cs/automata.html", en: "Formal Languages" },
        { href: "cs/graph-theory.html", en: "Graph Theory" },
      ]
    ]},
    { en: "Bioinformatics", columns: [
      [
        { href: "bioinformatics/index.html", en: "Overview" },
        { href: "bioinformatics/replication-origins.html", en: "Chapter 1: Replication Origins" },
        { href: "bioinformatics/motif-finding.html", en: "Chapter 2: Motif Finding" },
        { href: "bioinformatics/genome-assembly.html", en: "Chapter 3: Genome Assembly" },
        { href: "bioinformatics/antibiotic-sequencing.html", en: "Chapter 4: Antibiotic Sequencing" },
        { href: "bioinformatics/sequence-alignment.html", en: "Chapter 5: Sequence Alignment" },
        { href: "bioinformatics/genome-rearrangements.html", en: "Chapter 6: Genome Rearrangements" },
        { href: "bioinformatics/evolutionary-trees.html", en: "Chapter 7: Evolutionary Trees" },
        { href: "bioinformatics/clustering.html", en: "Chapter 8: Gene Clustering" },
        { href: "bioinformatics/read-mapping.html", en: "Chapter 9: Read Mapping" },
      ]
    ]},
    { en: "Thailand", columns: [
      [
        // The Thai app lives in its own repo/site (afourmy.github.io/thailand).
        // Absolute URLs so the SPA leaves the main site and loads it directly.
        // ?full=1 tells that site to show the integrated full menu (its default,
        // for direct visits, is the stripped thai-only app view).
        { href: "https://afourmy.github.io/thailand/index.html?full=1", en: "Vocabulary" },
        { href: "https://afourmy.github.io/thailand/etymology.html?full=1", en: "Etymology" },
        { href: "https://afourmy.github.io/thailand/flashcards.html?full=1", en: "Flashcards" },
        { href: "https://afourmy.github.io/thailand/culture.html?full=1", en: "Culture" },
      ]
    ]},
    { en: "Projects", columns: [
      [
        { href: "projects/tsp.html", en: "Traveling Salesman Problem" },
        { href: "projects/swap.html", en: "Wavelength Assignment Problem" },
        { href: "projects/computational-genomics.html", en: "Pattern Finding in DNA" },
      ]
    ]},
    { en: "Books", columns: [
      [
        { href: "books/aops.html", en: "The Art of Problem Solving" },
        { href: "books/long-form-math-textbook.html", en: "A Long-Form Mathematics Textbook" },
      ]
    ]},
  ];

  // Compute relative prefix from current page to site root.
  // nav.js is at the root, so we find how many directory levels deep we are.
  var scripts = document.querySelectorAll('script[src$="nav.js"]');
  var prefix = "";
  if (scripts.length) {
    var src = scripts[scripts.length - 1].getAttribute("src");
    // Count how many "../" are in the script src to determine depth
    var parts = src.split("/");
    for (var i = 0; i < parts.length - 1; i++) {
      if (parts[i] === "..") prefix += "../";
    }
  }

  // Absolute (cross-site) hrefs are used as-is; only local hrefs get the
  // root-relative prefix.
  function withPrefix(href) {
    return /^https?:\/\//.test(href) ? href : prefix + href;
  }

  function esc(s) {
    return s.replace(/&/g, "&amp;");
  }

  var html = '<nav><div class="nav-inner">';
  html += '<a href="' + prefix + 'index.html" class="nav-link nav-home">Home</a>';

  // Hamburger button (mobile only; CSS hides it on desktop).
  html += '<button class="nav-toggle" id="navToggle" aria-label="Toggle menu">';
  html += '<span></span><span></span><span></span>';
  html += '</button>';

  // Mobile-only flex spacer: pushes the toggles + theme toggle to the right of
  // the bar (hamburger stays left). Hidden on desktop (see CSS).
  html += '<div class="nav-spacer" aria-hidden="true"></div>';

  // EN/FR language toggle: a top-bar sibling (shown only on math pages, hidden
  // until then). On desktop it floats to the left gutter; on mobile it sits in
  // the top bar right of the hamburger.
  html += '<div class="lang-toggle" id="lang-toggle" style="display:none">';
  html += '<button onclick="setLang(\'en\')" id="lang-en" class="active">EN</button>';
  html += '<button onclick="setLang(\'fr\')" id="lang-fr">FR</button>';
  html += '</div>';

  // Collapsible menu: the hamburger shows/hides these on mobile without
  // affecting the desktop layout.
  html += '<div class="nav-links" id="navLinks">';

  for (var m = 0; m < menu.length; m++) {
    var item = menu[m];
    html += '<div class="nav-item">';
    html += '<a href="#" class="nav-link" onclick="return false;">' + esc(item.en) + '</a>';
    html += '<div class="submenu' + (item.cssClass ? " " + item.cssClass : "") + '">';
    for (var c = 0; c < item.columns.length; c++) {
      html += '<ul class="submenu-col">';
      var col = item.columns[c];
      for (var i = 0; i < col.length; i++) {
        var link = col[i];
        html += '<li><a href="' + withPrefix(link.href) + '" data-path="' + esc(link.href) + '">' + esc(link.en) + '</a></li>';
      }
      html += '</ul>';
    }
    html += '</div></div>';
  }

  html += '</div>'; // close .nav-links

  // Theme toggle (right side)
  html += '<button class="theme-toggle" id="themeToggle" aria-label="Toggle dark mode">';
  html += '<span class="toggle-track">';
  html += '<svg class="icon-sun" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" stroke-width="2"/><line x1="12" y1="21" x2="12" y2="23" stroke="currentColor" stroke-width="2"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke="currentColor" stroke-width="2"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke="currentColor" stroke-width="2"/><line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="2"/><line x1="21" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="2"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke="currentColor" stroke-width="2"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke="currentColor" stroke-width="2"/></svg>';
  html += '<svg class="icon-moon" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>';
  html += '<span class="toggle-thumb"></span>';
  html += '</span>';
  html += '</button>';
  html += '</div></nav>';

  // Insert nav at the beginning of <body>
  var container = document.createElement("div");
  container.innerHTML = html;
  var nav = container.firstChild;
  document.body.insertBefore(nav, document.body.firstChild);

  // Theme toggle: flip data-theme on <html> and remember the choice.
  var themeToggle = nav.querySelector("#themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var next =
        document.documentElement.getAttribute("data-theme") === "dark"
          ? "light"
          : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
    });
  }

  // Mobile menu: the hamburger shows/hides the collapsible nav; tapping a
  // category expands its submenu (accordion); tapping a real link closes it.
  var navToggle = nav.querySelector("#navToggle");
  var navLinks = nav.querySelector("#navLinks");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      var open = navLinks.classList.toggle("open");
      navToggle.classList.toggle("active", open);
    });
    navLinks.addEventListener("click", function (e) {
      var topLink = e.target.closest(".nav-item > .nav-link");
      if (topLink) {
        topLink.parentNode.classList.toggle("open");
        return;
      }
      if (e.target.closest(".submenu a[href]")) {
        navLinks.classList.remove("open");
        navToggle.classList.remove("active");
      }
    });
  }

  // Highlight the top-level item whose submenu contains the current page.
  // Exposed globally so SPA navigation can refresh it after each page change.
  function strip(url) {
    return url.split("#")[0].split("?")[0];
  }
  window.setActiveNav = function () {
    // Compare against the stable data-path (e.g. "math/groups.html") rather
    // than the anchor's resolved .href, which drifts when SPA navigation
    // changes the document base URL.
    var path = strip(window.location.pathname);
    var items = nav.querySelectorAll(".nav-item");
    for (var k = 0; k < items.length; k++) {
      var topLink = items[k].querySelector(".nav-link");
      var links = items[k].querySelectorAll(".submenu a");
      var match = false;
      for (var l = 0; l < links.length; l++) {
        var p = links[l].getAttribute("data-path");
        if (p && path.endsWith(p)) { match = true; break; }
      }
      if (topLink) topLink.classList.toggle("nav-active", match);
    }
  };
  window.setActiveNav();

  // French content exists only in the Mathematics section, so the EN/FR toggle
  // is shown there and nowhere else (not on Home or any other section). Driven
  // by the current path so it stays correct across SPA navigation. Exposed
  // globally so the SPA can refresh it after each page change.
  var langToggleEl = nav.querySelector("#lang-toggle");
  window.updateLangToggle = function () {
    if (!langToggleEl) return;
    var path = strip(window.location.pathname);
    langToggleEl.style.display = path.indexOf("/math/") !== -1 ? "" : "none";
  };
  window.updateLangToggle();

  // Wire thm-labels as proof toggles (event delegation – works with SPA)
  document.addEventListener("click", function (e) {
    var label = e.target.closest(".thm-label");
    if (!label) return;
    var block = label.closest(".thm-block");
    if (!block) return;
    var proofs = [];
    var sibling = block.nextElementSibling;
    while (sibling && sibling.classList.contains("proof")) {
      proofs.push(sibling);
      sibling = sibling.nextElementSibling;
    }
    if (!proofs.length) return;
    label.classList.add("has-proof");
    var open = label.classList.toggle("proof-open");
    proofs.forEach(function (p) {
      p.open = open;
    });
  });

  // Mark labels that have proofs
  window.initProofToggles = function () {
    document.querySelectorAll(".thm-block").forEach(function (block) {
      var sibling = block.nextElementSibling;
      var hasProof = false;
      while (sibling && sibling.classList.contains("proof")) {
        hasProof = true;
        sibling = sibling.nextElementSibling;
      }
      if (hasProof) {
        block.querySelectorAll(".thm-label").forEach(function (label) {
          label.classList.add("has-proof");
        });
      }
    });
  };
  document.addEventListener("DOMContentLoaded", window.initProofToggles);
})();

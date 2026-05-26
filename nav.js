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
    { en: "Mathematics", fr: "Mathématiques", cssClass: "submenu-sections", columns: [
      [
        { href: "math/suites.html", en: "Sequences", fr: "Suites" },
        { href: "math/fonctions-usuelles.html", en: "Standard Functions", fr: "Fonctions usuelles" },
        { href: "math/continuite.html", en: "Continuity", fr: "Continuité" },
        { href: "math/derivation.html", en: "Differentiation", fr: "Dérivation" },
        { href: "math/topologie.html", en: "Topology", fr: "Topologie" },
        { href: "math/complexes.html", en: "Complex Numbers", fr: "Nombres complexes" },
      ],
      [
        { href: "math/ensembles.html", en: "Sets", fr: "Ensembles" },
        { href: "math/bases.html", en: "Foundations", fr: "Bases" },
        { href: "math/groups.html", en: "Groups", fr: "Groupes" },
        { href: "math/arithmetique.html", en: "Arithmetic", fr: "Arithmétique" },
        { href: "math/anneaux-corps.html", en: "Rings and Fields", fr: "Anneaux et corps" },
        { href: "math/polynomes.html", en: "Polynomials", fr: "Polynômes" },
      ],
      [
        { href: "math/linear-algebra.html", en: "Linear Algebra", fr: "Algèbre linéaire" },
        { href: "math/matrices.html", en: "Matrices", fr: "Matrices" },
        { href: "math/determinants.html", en: "Determinants", fr: "Déterminants" },
        { href: "math/reduction.html", en: "Reduction", fr: "Réduction" },
        { href: "math/probabilites.html", en: "Probability", fr: "Probabilités" },
        { href: "math/denombrement.html", en: "Combinatorics", fr: "Dénombrement" },
      ]
    ]},
    { en: "Computer Science", fr: "Informatique", columns: [
      [
        { href: "cs/algorithmics.html", en: "Algorithmics", fr: "Algorithmique" },
        { href: "cs/automata.html", en: "Formal Languages", fr: "Langages formels" },
        { href: "cs/graph-theory.html", en: "Graph Theory", fr: "Théorie des graphes" },
      ]
    ]},
    { en: "Bioinformatics", fr: "Bio-informatique", columns: [
      [
        { href: "bio/genomics.html", en: "Genomics", fr: "Génomique" },
        { href: "bio/transcriptomics.html", en: "Transcriptomics", fr: "Transcriptomique" },
        { href: "bio/proteomics.html", en: "Proteomics", fr: "Protéomique" },
      ]
    ]},
    { en: "Thailand", fr: "Thaïlande", columns: [
      [
        { href: "thai/index.html", en: "Vocabulary", fr: "Vocabulaire" },
      ]
    ]},
    { en: "Projects", fr: "Projets", columns: [
      [
        { href: "projects/tsp.html", en: "Traveling Salesman Problem", fr: "Voyageur de commerce" },
        { href: "projects/swap.html", en: "Wavelength Assignment Problem", fr: "Affectation de longueurs d'onde" },
        { href: "projects/computational-genomics.html", en: "Computational Genomics", fr: "Génomique computationnelle" },
      ]
    ]},
    { en: "Books", fr: "Livres", columns: [
      [
        { href: "books/aops.html", en: "The Art of Problem Solving", fr: "L'Art de la résolution de problèmes" },
        { href: "books/bioinformatics-algorithms.html", en: "Bioinformatics Algorithms", fr: "Algorithmes en bioinformatique" },
        { href: "books/long-form-math-textbook.html", en: "A Long-Form Mathematics Textbook", fr: "A Long-Form Mathematics Textbook" },
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

  function esc(s) {
    return s.replace(/&/g, "&amp;");
  }

  var html = '<nav><div class="nav-inner">';
  html += '<a href="' + prefix + 'index.html" class="nav-link nav-home">Home</a>';

  // Language toggle (left side, next to Home)
  html += '<div class="lang-toggle">';
  html += '<button onclick="setLang(\'en\')" id="lang-en" class="active">EN</button>';
  html += '<button onclick="setLang(\'fr\')" id="lang-fr">FR</button>';
  html += '</div>';

  for (var m = 0; m < menu.length; m++) {
    var item = menu[m];
    html += '<div class="nav-item">';
    html += '<a href="#" class="nav-link" data-en="' + esc(item.en) + '" data-fr="' + esc(item.fr) + '" onclick="return false;">' + esc(item.en) + '</a>';
    html += '<div class="submenu' + (item.cssClass ? " " + item.cssClass : "") + '">';
    for (var c = 0; c < item.columns.length; c++) {
      html += '<ul class="submenu-col">';
      var col = item.columns[c];
      for (var i = 0; i < col.length; i++) {
        var link = col[i];
        html += '<li><a href="' + prefix + link.href + '" data-path="' + esc(link.href) + '" data-en="' + esc(link.en) + '" data-fr="' + esc(link.fr) + '">' + esc(link.en) + '</a></li>';
      }
      html += '</ul>';
    }
    html += '</div></div>';
  }

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

  // Hide the EN/FR toggle on pages that aren't bilingual. Driven by the
  // current path so it stays correct across SPA navigation. Exposed globally
  // so the SPA can refresh it after each page change.
  var langToggleEl = nav.querySelector(".lang-toggle");
  var HIDE_LANG_TOGGLE = ["thai/", "books/", "projects/", "bio/", "cs/"];
  window.updateLangToggle = function () {
    if (!langToggleEl) return;
    var path = strip(window.location.pathname);
    var hide = HIDE_LANG_TOGGLE.some(function (p) {
      return path.indexOf(p) !== -1;
    });
    langToggleEl.style.display = hide ? "none" : "";
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

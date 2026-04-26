(function () {
  var menu = [
    { en: "Mathematics", fr: "Math\u00e9matiques", cssClass: "submenu-sections", columns: [
      [
        { href: "math/l1/bases.html", en: "Foundations", fr: "Bases" },
        { href: "math/l1/complexes.html", en: "Complex Numbers", fr: "Nombres complexes" },
        { href: "math/l1/arithmetique.html", en: "Arithmetic", fr: "Arithm\u00e9tique" },
        { href: "math/l1/fonctions_usuelles.html", en: "Usual Functions", fr: "Fonctions usuelles" },
        { href: "math/l1/polynomes.html", en: "Polynomials", fr: "Polyn\u00f4mes" },
        { href: "math/l1/suites.html", en: "Sequences", fr: "Suites" },
        { href: "math/l1/continuite.html", en: "Continuity", fr: "Continuit\u00e9" },
        { href: "math/l1/derivation.html", en: "Differentiation", fr: "D\u00e9rivation" },
        { href: "math/l1/denombrement.html", en: "Combinatorics", fr: "D\u00e9nombrement" },
      ],
      [
        { href: "math/l1/probabilites.html", en: "Probability", fr: "Probabilit\u00e9s" },
        { href: "math/l1/groups.html", en: "Groups", fr: "Groupes" },
        { href: "math/l1/anneaux_corps.html", en: "Rings & Fields", fr: "Anneaux & Corps" },
        { href: "math/l1/algebre_lineaire.html", en: "Linear Algebra", fr: "Alg\u00e8bre lin\u00e9aire" },
        { href: "math/l1/matrices.html", en: "Matrices", fr: "Matrices" },
        { href: "math/l1/determinant.html", en: "Determinants", fr: "D\u00e9terminants" },
        { href: "math/l2/algebra.html", en: "Algebra", fr: "Alg\u00e8bre" },
        { href: "math/l2/analysis.html", en: "Analysis", fr: "Analyse" },
      ]
    ]},
    { en: "Computer Science", fr: "Informatique", columns: [
      [
        { href: "cs/theory/logic.html", en: "Logic", fr: "Logique" },
        { href: "cs/theory/automata.html", en: "Automata", fr: "Automates" },
      ]
    ]},
    { en: "Algorithmics", fr: "Algorithmique", columns: [
      [
        { href: "cs/algo/sorting.html", en: "Sorting", fr: "Tri" },
        { href: "cs/algo/graphs.html", en: "Graphs", fr: "Graphes" },
      ]
    ]},
    { en: "Projects", fr: "Projets", columns: [
      [
        { href: "projects/tsp.html", en: "Traveling Salesman", fr: "Voyageur de commerce" },
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

  for (var m = 0; m < menu.length; m++) {
    var item = menu[m];
    html += '<div class="nav-item">';
    html += '<a href="#" class="nav-link" data-en="' + esc(item.en) + '" data-fr="' + esc(item.fr) + '">' + esc(item.en) + '</a>';
    html += '<div class="submenu' + (item.cssClass ? " " + item.cssClass : "") + '">';
    for (var c = 0; c < item.columns.length; c++) {
      html += '<ul class="submenu-col">';
      var col = item.columns[c];
      for (var i = 0; i < col.length; i++) {
        var link = col[i];
        html += '<li><a href="' + prefix + link.href + '" data-en="' + esc(link.en) + '" data-fr="' + esc(link.fr) + '">' + esc(link.en) + '</a></li>';
      }
      html += '</ul>';
    }
    html += '</div></div>';
  }

  html += '<div class="lang-toggle">';
  html += '<button onclick="setLang(\'en\')" id="lang-en" class="active">EN</button>';
  html += '<button onclick="setLang(\'fr\')" id="lang-fr">FR</button>';
  html += '</div></div></nav>';

  // Insert nav at the beginning of <body>
  var container = document.createElement("div");
  container.innerHTML = html;
  var nav = container.firstChild;
  document.body.insertBefore(nav, document.body.firstChild);
})();

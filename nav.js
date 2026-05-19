(function () {
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
        { href: "cs/automata.html", en: "Formal Languages & Automata", fr: "Langages formels & Automates" },
        { href: "cs/graph-theory.html", en: "Graph Theory", fr: "Théorie des graphes" },
        { href: "cs/algorithmics.html", en: "Algorithmics", fr: "Algorithmique" },
      ]
    ]},
    { en: "Bioinformatics", fr: "Bio-informatique", columns: [
      [
        { href: "bio/genomics.html", en: "Genomics", fr: "Génomique" },
        { href: "bio/transcriptomics.html", en: "Transcriptomics", fr: "Transcriptomique" },
        { href: "bio/proteomics.html", en: "Proteomics", fr: "Protéomique" },
      ]
    ]},
    { en: "Projects", fr: "Projets", columns: [
      [
        { href: "projects/tsp.html", en: "Traveling Salesman Problem", fr: "Voyageur de commerce" },
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

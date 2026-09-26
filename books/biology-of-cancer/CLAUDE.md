# The Biology of Cancer

Notes on *The Biology of Cancer* by Robert A. Weinberg, 3rd edition (2023). The book is in
`~/Downloads/Weinberg R. The Biology of Cancer 3ed 2023/`; `pdftotext` extracts its text. The reading
notes for each chapter, with the book's numbers, are in `notes/chNN.md`; they are the source for
writing a chapter. The reusable generation prompt is `biology-of-cancer.prompt.md`.

## Layout
One page per book chapter, named by slug (`tumor-suppressors.html`), plus `index.html` as the
landing page. The Books menu in `nav.js` has a single entry, "The Biology of Cancer", pointing to
`index.html`; the chapters are listed on `index.html` as `Chapter N: Short Title` (at most three words)
with a one-paragraph description, and are not in `nav.js`. Pages sit two levels deep, so they load
`../../style.css` and `../../nav.js`; the canonical URL is
`https://afourmy.github.io/books/biology-of-cancer/<slug>.html`.

Each page puts `Chapter N: Title` in its `<h1>` inside `<header class="page-banner">`, `<h2>` per
section, `<h3>` for subsections. The title names the content, never the book's playful chapter titles
("Crowd Control", "Eternal Life"). Chapters link to each other by slug.

| N | Slug | Index label |
|---|---|---|
| 1 | cells-and-genes | Cells and Genes |
| 2 | nature-of-cancer | Nature of Cancer |
| 3 | tumor-viruses | Tumor Viruses |
| 4 | cellular-oncogenes | Cellular Oncogenes |
| 5 | growth-factors | Growth Factors |
| 6 | signaling-pathways | Signaling Pathways |
| 7 | tumor-suppressors | Tumor Suppressors |
| 8 | cell-cycle-control | Cell Cycle Control |
| 9 | p53-and-apoptosis | p53 and Apoptosis |
| 10 | cell-immortality | Cell Immortality |
| 11 | multi-step-tumorigenesis | Multi-Step Tumorigenesis |
| 12 | genome-instability | Genome Instability |
| 13 | stroma-and-angiogenesis | Stroma and Angiogenesis |
| 14 | invasion-and-metastasis | Invasion and Metastasis |
| 15 | tumor-immunology | Tumor Immunology |
| 16 | cancer-immunotherapy | Cancer Immunotherapy |
| 17 | cancer-treatment | Cancer Treatment |

## Reader and scope
The reader knows computer science and mathematics and no biology. Every biological term is defined in
plain words the first time it is used, only as deeply as the chapter needs. English only, no French.

The notes keep the gist: every main idea of the chapter, developed, with the evidence that
established it. They are not a summary of every paragraph. Agreed drops (2026-09-25):
1. General biology in chapter 1 that later chapters do not use (history of genetics, chromatin detail,
   miRNA machinery).
2. The online supplementary sidebars, except the one on the mathematics of multi-step incidence.
3. Catalogs of genes, drugs and trials: one or two representative examples, not the list.
4. Laboratory techniques as topics (cell sorting, making monoclonal antibodies, sequencing chemistry,
   CRISPR screens): one sentence where a result depends on them.
5. The secondary pathways of chapter 6 (JAK-STAT, Notch, Hedgehog, Hippo, GPCRs): keep Ras-MAPK and
   PI3K-Akt, and Wnt and TGF-beta where later chapters use them.
6. Immunology detail in chapter 15 beyond what the tumor story uses (gene-segment counts, the five
   helper-cell subsets).
7. The drug-development procedure of chapter 17 (trial phases, pharmacokinetics, response criteria):
   one short section.
8. Cell-motility machinery in chapter 14 and nerves in tumors in chapter 13.

## Writing
The factual-writing rules of `books/CLAUDE.md` and `bioinformatics/CLAUDE.md` apply: every sentence
states a fact, a definition, a mechanism or a number; no rhetorical questions, no metaphors in place of
the mechanism (the book's own nicknames, like "guardian of the genome", at most once as a name), no
filler transitions, no sentences about the page's own structure, no dramatic framing, no rare words,
no historical storytelling beyond who showed what and when. Develop each idea: about six sentences and
three hundred characters per paragraph.

Plain English above all (2026-09-25, after the user found the first drafts "not even proper English"):
one fact per sentence, about 15 words on average and none over 30; plain word order with the subject
first; no clause as subject, no rare senses of common words ("to found"), no semicolons chaining facts,
no stacked appositives; never start a sentence with a lowercase gene name ("The src gene was...");
never mention "the book" on a page, state the fact instead. Reread every paragraph for readability
before publishing, not only for accuracy. Never use the em dash. No code and no `<pre>`: the book has no
algorithms. Math is inline KaTeX, `$...$` only.

## Figures
Look for the drawing first: each main idea gets a figure that makes it visible, and a chapter without
figures is not finished. All rules of `bioinformatics/CLAUDE.md` apply: inline `<svg class="figure">`
in `<figure class="figure-block">` with a `<figcaption>`; only the existing `fig-*` classes; no colour
attributes; a second kind of line in `fig-free` with a legend; no KaTeX in SVG; prose in the caption,
two-or-three-word panel labels above panels; nothing touches; width at most 812px; coordinates from a
throwaway script; every figure rendered and looked at before shipping.

Data policy (agreed 2026-09-25): a figure plots either a model computed by a script (Knudson's
one-hit and two-hit curves, telomere loss, error rates, the probability of a resistant cell) or numbers
stated in the book's text. Never values read off the book's plotted figures, never outside datasets.
Every number in prose or a caption comes from the book's text (recorded in `notes/chNN.md`) or from a
computation checked with an assertion; never from memory.

Where the book contradicts itself, say which value is used or give the range. Known cases: cells in an
adult body (3x10^13 in chapter 2, 4x10^13 in chapter 12, 5x10^13 in chapter 14, almost 10^14 in
chapters 8 and 10); HER2-positive breast cancers (15 to 20% in chapter 16, over 20% in chapter 15, 30%
in chapter 17).

## Rendering
Render a figure or a page with headless Chrome:
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --screenshot=out.png
--window-size=900,2000 file:///path/page.html`, then look at the PNG.

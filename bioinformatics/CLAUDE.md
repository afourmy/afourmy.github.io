# Bioinformatics course

Notes on *Bioinformatics Algorithms* by Compeau and Pevzner. One page per chapter, named by slug
(`genome-assembly.html`), listed in `nav.js` under the **Bioinformatics** menu as
`Chapter N: Short Title` with at most three words in the title. `index.html` is the section landing
page. The reusable generation prompt is `bioinformatics-algorithms.prompt.md`.

Each page keeps the book's full question as its `<h1>` inside `<header class="page-banner">`,
`<h2>` per section, `<h3>` for subsections. Chapters link to each other by slug.

## Factual writing only
These pages read as factual technical writing, not as a book. Every sentence states a fact, a
definition, a cost, or a mechanism. Banned:

- **Rhetorical questions** ("Wouldn't so many mutations damage the genome?"). State the fact directly.
- **Filler transitions that sound like reasoning but assert nothing**: "The remedy follows from the cost", "Note what was given up along the way", "The pieces now assemble into".
- **Sentences narrating the page's own structure** rather than its subject: "This is where the second strand, deferred earlier, is finally accounted for", "The code above does not do this yet". Never announce that something was postponed or is now being resolved, just state the technical point where it belongs.
- **Metaphors in place of the technical statement**: "a short message written in the DNA", "a physical fingerprint of which way replication ran", C's being "destroyed".
- **Dramatic or colloquial framing**: "It is not a free win", "the dictionary version wins", "a decisive improvement".
- **Bookish headings** ("Back to the Clock"). Headings name the content: "Application: the Evening Element".
- **Rare, obscure, or abstract words** where a common one works, and long sentences the reader has to read twice. Keep the wording simple and direct. This covers the prose only: technical terms stay exact.

When tempted to write a transition, either state the technical point it was decorating or delete the sentence.

## Notation
Never introduce notation the page has not defined. Before using a symbol, check it is either defined
where it appears or already established on the page with that same meaning, `grep` for it.

## Figures
A drawing that makes the idea visible beats a paragraph describing it, and a visualization is the
explanation rather than decoration. See `ARTISTIC_DIRECTION.md` at the site root.

- **Data is drawn, not typeset in a monospace block.** Alignments, scoring matrices, count and
  profile matrices, weight grids, spectra and comparison tables are all `<figure>` elements. A plain
  `<pre><code>` block is for things that genuinely are text, such as an adjacency listing.
- Figures are hand-generated inline `<svg class="figure">` inside
  `<figure class="figure-block">` with a `<figcaption>`.
- **Use only classes that already exist in `style.css`**: `fig-cell`, `fig-cell-alt`, `fig-axis`,
  `fig-guide`, `fig-curve`, `fig-accent`, `fig-band`, `fig-shape`, `fig-dot`, `fig-hole`, `fig-arc`,
  `fig-text fig-tick`, `fig-text fig-note`. No inline `<style>`, no presentation attributes for
  colour or stroke.
- **KaTeX does not run inside `<svg>`.** Never put `$...$` in SVG text; it renders literally. Math
  belongs in the prose and in the `<figcaption>`, which is ordinary HTML.
- Multi-panel captions use `<span class="cap-part">` with `<span class="cap-lead">Left.</span>`.
- In an alignment figure, matched columns are filled and tied with a vertical rule so the eye counts
  them; mismatches and gaps are left plain.

## Verifying the code
Every algorithm matches a problem in the Rosalind textbook track, whose pages publish sample input
and output and need no account. Extract the Python from the rendered page rather than retyping it,
and read the sample data off the problem page rather than recalling it. For randomized algorithms
compare the score reached, not the exact output. Cross-checking a fast algorithm against the slow one
it replaced, or against brute force on random inputs, is worth more than any single sample.

Numbers quoted in the prose (genome lengths, positions, scores, counts) are computed or fetched, not
recalled.

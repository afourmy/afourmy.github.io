# Bioinformatics course

Notes on *Bioinformatics Algorithms* by Compeau and Pevzner. One page per chapter, named by slug
(`genome-assembly.html`), listed in `nav.js` under the **Bioinformatics** menu as
`Chapter N: Short Title` with at most three words in the title. `index.html` is the section landing
page. The reusable generation prompt is `bioinformatics-algorithms.prompt.md`.

Each page keeps the book's full question as its `<h1>` inside `<header class="page-banner">`,
`<h2>` per section, `<h3>` for subsections. Chapters link to each other by slug.

## Develop the notes, do not transcribe them
The user's notes are shorthand. A line like "Theorem: limblength(j) = Min(...)" is a reminder to
them, not a paragraph of a course: it has to be turned into what the quantity is, why it is
recoverable from the matrix at all, what the minimum is doing, and a proof. A bolded restatement of
the note with nothing around it is the recurring failure. The written chapters run about six
sentences and three hundred characters per paragraph, developing each idea rather than naming it.

## Answer the chapter's question by computation
Where it can be done, fetch the real sequences (NCBI, UniProt) and run the chapter's own code:
the skew of the real *E. coli* genome, the homeobox recovered by local alignment, the coronavirus
tree from neighbour-joining. A computed answer beats a cited one and proves the code works. Where
it genuinely cannot be computed, say plainly that the result is quoted, and say what the method can
and cannot establish.

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
A drawing that makes the idea visible beats a paragraph describing it, and a figure is the
explanation rather than decoration. Look for the drawing first, for every section. A chapter with
no figure in it is not finished.

`ARTISTIC_DIRECTION.md` at the site root is written for the mathematics course. What carries over
here is the general idea rather than the coverage, what a result says about the fabric of reality,
and above all the visual form. The prose rules above still win over it.

- **`<pre>` is for code and for nothing else.** Python goes in
  `<pre><code class="language-python">`.
- **Anything that is data is a figure, not a monospace block.** Alignments, scoring matrices, count
  and profile matrices, weight grids, spectra, comparison tables and worked examples are all
  `<figure>` elements. A plain `<pre><code>` is acceptable only for something that genuinely is
  text, such as an adjacency listing.
- Figures are hand-generated inline `<svg class="figure">` inside
  `<figure class="figure-block">` with a `<figcaption>`. Compute the coordinates with a throwaway
  script, and render the result to look at it before shipping it.
- **Use only classes that already exist in `style.css`**: `fig-cell`, `fig-cell-alt`, `fig-axis`,
  `fig-guide`, `fig-curve`, `fig-accent`, `fig-band`, `fig-shape`, `fig-dot`, `fig-hole`, `fig-arc`,
  `fig-free`, `fig-free-solid`, `fig-hole-alt`, `fig-text fig-tick`, `fig-text fig-note`. No inline
  `<style>`, no presentation attributes for colour or stroke.
- **Two kinds of edge need two colours and a legend.** Draw the second kind in the second hue
  (`fig-free`, driven by `--fig-alt`) and put a legend inside the figure naming every kind of line
  it uses. A figure dense with links and only one colour is unreadable.
- **KaTeX does not run inside `<svg>`.** Never put `$...$` in SVG text; it renders literally. Math
  belongs in the prose and in the `<figcaption>`, which is ordinary HTML.
- Multi-panel captions use `<span class="cap-part">` with `<span class="cap-lead">Left.</span>`.
- In an alignment figure, matched columns are filled and tied with a vertical rule so the eye counts
  them; mismatches and gaps are left plain.

## Figure layout
The recurring mistakes, all of which the user has had to point out at least once:

- **Nothing touches anything.** Edge labels are offset *perpendicular* to their edge, not nudged
  vertically from the midpoint, which lands them on diagonal lines. Coincident leaf labels get
  nudged apart.
- **Prose goes in the `<figcaption>`, never inside the SVG.** In the drawing put only short panel
  labels of two or three words. Derivations and conclusions go in the caption; a column of text
  beside a drawing is a caption in the wrong place.
- **Panel labels go above their panel and nothing goes below it.** Never both.
- **Arrows between panels use `fig-curve` weight and sit centred** on the gap they span.
- **Render every figure and look at it** before shipping. Right-anchored text falling off the
  canvas is the usual failure.
- **Nothing exceeds the 812px content column**, or the browser scales it down and shrinks the text.

## Theorems
Match the chapters already written: flowing prose, no special markup. The statement is a bolded
lead-in inside an ordinary paragraph, named where it has one (`Euler's Theorem.`, `Cycle Theorem.`,
`Limb Length Theorem.`) and plain `Theorem.` where it does not. The proof is the paragraph that
follows, announcing itself in its first clause, as Chapter 3 does with "The proof is constructive,
and it is the algorithm."

Do **not** use `thm-block`, `<details class="proof">` or the other theorem markup, even though
`cs/graph-theory.html` and the mathematics pages do. This course does not.

Every theorem the notes mark "Proof" gets a real proof written out. Where the real argument is long
machinery, give the idea it turns on and say plainly that the full argument is not reproduced.

## Verifying the code
Every algorithm matches a problem in the Rosalind textbook track, whose pages publish sample input
and output and need no account. Extract the Python from the rendered page rather than retyping it,
and read the sample data off the problem page rather than recalling it. For randomized algorithms
compare the score reached, not the exact output. Cross-checking a fast algorithm against the slow one
it replaced, or against brute force on random inputs, is worth more than any single sample.

Every number in the prose or in a figure caption is computed or fetched, never recalled: genome
lengths, positions, scores, counts, and the intermediate matrices of a traced algorithm. Write the
check as an assertion and run it. Hand-typed intermediate values have been the single most reliable
source of errors in this course, and every one was caught this way rather than by reading.

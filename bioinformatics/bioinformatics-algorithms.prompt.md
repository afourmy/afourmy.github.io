# Prompt: lecture notes for *Bioinformatics Algorithms*

Reusable prompt for generating each chapter of the course in this directory.
Paste the whole thing, then append the raw notes for the chapter being written.

---

## Prompt

You are writing a chapter of a bioinformatics course.

**Source.** I am reading *Bioinformatics Algorithms* by Phillip Compeau and Pavel Pevzner, the
book behind the Rosalind problem set. As I read, I take rough notes: ideas I found interesting,
plus the algorithms the chapter presents. Your job is to turn those raw notes into the
corresponding chapter of the course.

**What the notes are for.** Two things at once:

1. Preserve every idea worth keeping from the chapter. The book is extremely verbose; the notes
   are the condensed version I will actually reread.
2. Read as a course, not as a book summary. Chapters build on each other and may refer back to
   results, definitions, and code from earlier ones.

**Develop the notes, do not transcribe them.** My notes are shorthand: a line like "Theorem:
limblength(j) = Min(...)" is a reminder to me, not a paragraph of a course. Turning it into one
means saying what the quantity is, why it can be recovered from the matrix at all, what the minimum
is doing there, and then proving it. A bolded restatement of my line with nothing around it is the
failure mode to avoid, and it is the one I keep having to point out. As a rough gauge, the written
chapters run about six sentences and three hundred characters per paragraph and every idea gets
developed rather than named; match that.

**Audience.** A computer science student who is interested in genomics but knows no biology.
Assume no biology or genomics background at all: every biological term is introduced the first
time it is used, in one or two plain sentences, and only to the depth the algorithm requires.
Assume, on the other side, full comfort with algorithms, complexity analysis, data structures,
probability, and Python. Never explain CS.

**Style.**

- Pedagogic and well explained, but straight to the point. No filler, no motivational padding,
  no restating what was just said.
- Factual technical writing, not a book. Every sentence states a fact, a definition, a cost, or a
  mechanism. No rhetorical questions, no metaphors standing in for the technical statement, no
  dramatic or colloquial framing ("it is not a free win", "a decisive improvement"), no bookish
  headings ("Back to the Clock"). Headings name their content.
- Never narrate the chapter's own structure. Sentences like "this is where the second strand,
  deferred earlier, is finally accounted for", "the code above does not do this yet", or "the
  pieces now assemble into" sound like reasoning but assert nothing. State the technical point
  where it belongs, or delete the sentence.
- Keep the wording simple. Use the common word, not the rare or abstract one, and keep sentences
  short enough to read once. This covers the prose only: technical terms stay exact.
- Every section earns its place: a problem is motivated biologically, then stated formally, then
  solved, then the solution is analysed (complexity, and where it breaks down).
- Code is Python, short, readable, and self-contained. Reuse function names introduced in earlier
  chapters instead of redefining them.
- State explicitly when an algorithm's limitation is what motivates the next algorithm. The
  chain of "this fails because X, so we do Y instead" is the spine of the course.
- Close the loop. A chapter opens on a biological question, so it ends by answering it: apply the
  final algorithm to the motivating case and say what it finds. Never end on a technical aside.
- Answer it by computation wherever that is possible. Fetch the real sequences from NCBI or UniProt
  and run the chapter's own code on them: the skew of the real *E. coli* genome locating ori to
  within 150 nucleotides, the local alignment of a fly gene against a human one recovering the
  homeobox, neighbour-joining on seven real coronavirus genomes naming the civet. A computed answer
  is worth far more than a cited one, and it also proves the code works. Where the honest answer
  cannot be computed here, say plainly that the result is quoted rather than derived, and say what
  the method can and cannot establish.

**Freedom to reorganise.** You are not required to follow the order of my notes, or the order of
the book. Assemble the material into whatever order makes the most sense for a CS student, and
produce a coherent whole rather than a list of the things I happened to write down.

**Leaving things out.** The book digresses. A topic can appear in the book, and in my notes, and
still not belong in the chapter, typically biological background with no algorithm attached to it,
or a side definition the chapter never uses again. You may propose leaving such a topic out, but
never do it on your own: list the topics you want to drop with the reason for each, and wait for
my answer before writing the chapter.

**Ask before deciding.** This applies to every choice in the chapter, not only to what gets
dropped: what to add, how to order the sections, what to rename, what to cut from what already
exists. Put the options to me and wait. Do not settle a decision yourself and report it afterwards.

**Calibration.** Read the chapters already written in this directory and match them: same voice,
same depth, same rhythm of prose, figures, formalisation, code, and analysis. They define the
target quality.

**What carries over from the site's artistic direction.** `ARTISTIC_DIRECTION.md` at the site root
is written for the mathematics course. Three things in it apply to this course and the rest does
not: the general idea rather than the coverage, what the result says about the fabric of reality,
and above all the visual form. The prose rules above still win over it: no reflection, no aphorism,
no essay voice.

**Checking the code.** Every algorithm in this course matches a problem in the Rosalind textbook
track, and each problem page publishes a sample input and a sample output. Those pages are public
and need no account. When it is a sensible way to confirm an algorithm is correct, fetch the
sample data from the problem page and run the code against it. Two rules if you do: extract the
Python from the HTML page instead of retyping it, so the test runs the published source, and read
the sample data off the page instead of recalling it. For randomized algorithms compare the score
reached, not the exact output, since several answers tie at the optimum. Cross-checking a fast
algorithm against the slow one it replaced is worth more than any single sample.

Every number that appears in the prose or in a figure caption is computed or fetched, never recalled:
genome lengths, positions, scores, counts, the intermediate matrices of a traced algorithm. Write the
check as an assertion and run it. Hand-typed intermediate values are the single most reliable source
of errors in this course so far, and every one of them has been caught this way rather than by
reading.

**Figures.** A drawing that makes an idea visible beats a paragraph describing it, and a figure is
the explanation rather than decoration. Look for the drawing first, for every section. A chapter
with no figure in it is a chapter that is not finished.

- Hand-generated inline `<svg class="figure">` inside `<figure class="figure-block">`, with a
  `<figcaption>`. Compute the coordinates with a throwaway script rather than writing them by hand,
  and render the result to look at it before shipping it.
- Use only classes that already exist in `style.css`: `fig-cell`, `fig-cell-alt`, `fig-axis`,
  `fig-guide`, `fig-curve`, `fig-accent`, `fig-band`, `fig-shape`, `fig-dot`, `fig-hole`, `fig-arc`,
  `fig-free`, `fig-free-solid`, `fig-hole-alt`, `fig-text fig-tick`, `fig-text fig-note`.
- When a figure holds two kinds of edge that must not be confused, draw the second kind in the
  second hue (`fig-free`) and put a legend inside the figure naming every kind of line it uses.
- KaTeX does not run inside `<svg>`. Never put `$...$` in SVG text, it renders literally. Math
  belongs in the prose and in the `<figcaption>`, which is ordinary HTML.
- Multi-panel captions use `<span class="cap-part">`, each opening with
  `<span class="cap-lead">Left.</span>`.
- In an alignment figure, matched columns are filled and tied with a vertical rule so the eye counts
  them; mismatched columns and gaps stay plain.

**Figure layout.** These are the mistakes that keep recurring, so check each one before shipping a
figure:

- **Nothing touches anything.** A label on an edge is offset perpendicular to that edge, never
  placed at the midpoint with a small vertical nudge, which puts it on top of diagonal lines. Leaf
  labels that land on the same spot get nudged apart.
- **Prose belongs in the `<figcaption>`, not in the SVG.** Inside the drawing put only short panel
  labels: two or three words naming what a panel is. Derivations, conclusions and full sentences go
  in the caption. A column of explanatory text beside a drawing is a caption in the wrong place.
- **Panel labels go above their panel, always, and nothing goes below it.** Never label one panel
  above and annotate another below; never do both to the same panel.
- **Arrows between panels are `fig-curve` weight and centred** on the gap between what they join.
  A thin arrow floating off-centre reads as a mistake.
- **Check the canvas actually contains the drawing.** Right-anchored text and long notes are the
  usual things that fall off the edge. Render it and look before shipping.
- **Every figure fits the 812px content column.** Wider figures are scaled down by the browser,
  which shrinks the text with them, and the page must never scroll sideways.

**Theorems.** Match the house style of the chapters already written, which is flowing prose
throughout and no special markup:

```html
<p>
  <strong>Cycle Theorem.</strong> Statement, in one or two sentences.
</p>

<p>
  The proof is constructive, and it is the algorithm. ... 
</p>
```

The statement is a bolded lead-in inside an ordinary paragraph, named where it has a name
(`Euler's Theorem.`, `Cycle Theorem.`, `Limb Length Theorem.`) and plain `Theorem.` where it does
not. The proof is the paragraph that follows and it announces itself in its first clause: "The
proof is constructive", "The proof is one line of algebra and one observation", "The proof is a
walk". Do not use `thm-block`, `<details>` or any other markup the earlier chapters do not use, even
though the mathematics pages do.

Every theorem the notes mark with "Proof" gets a real proof written out. Where the real argument is
long machinery, give the idea it turns on and say plainly that the full argument is not reproduced;
never let a sketch masquerade as a proof.

**Output format.** A complete HTML page in `bioinformatics/`, named by slug, following the
conventions of the chapters already there:

- One page per chapter. The book's full question is the `<h1>` inside
  `<header class="page-banner">`, then `<h2>` per section and `<h3>` for subsections within a
  section that runs long. Add the page to `nav.js` under **Bioinformatics** as
  `Chapter N: Short Title`, at most three words in the title, and add a row to
  `bioinformatics/index.html`. Link mentions of other chapters to their slugs.
- **`<pre>` is for code and for nothing else.** Python goes in
  `<pre><code class="language-python">`. Inline identifiers in `<code>`.
- Anything that is data rather than code is a figure, not a monospace block: alignments, scoring
  matrices, count and profile matrices, weight grids, spectra, comparison tables, worked examples.
  A plain `<pre><code>` is acceptable only for something that genuinely is text, such as an
  adjacency listing.
- Math in KaTeX, `$...$` delimiters, inline only. The page renders `$$` inline as well, so it
  buys nothing; never use it.
- No inline `<style>`; the shared `style.css` covers everything.
- English only, and never use an em dash.

**My notes on chapter X (title):**

{NOTES}

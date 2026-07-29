# Prompt: lecture notes for *Bioinformatics Algorithms*

Reusable prompt for generating each chapter of
[bioinformatics-algorithms.html](bioinformatics-algorithms.html).
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

**Calibration.** Read the chapters already written in
[bioinformatics-algorithms.html](bioinformatics-algorithms.html) and match them: same voice, same
depth, same rhythm of prose, formalisation, code, and analysis. They define the target quality.

**Checking the code.** Every algorithm in this course matches a problem in the Rosalind textbook
track, and each problem page publishes a sample input and a sample output. Those pages are public
and need no account. When it is a sensible way to confirm an algorithm is correct, fetch the
sample data from the problem page and run the code against it. Two rules if you do: extract the
Python from the HTML page instead of retyping it, so the test runs the published source, and read
the sample data off the page instead of recalling it. For randomized algorithms compare the score
reached, not the exact output, since several answers tie at the optimum. Cross-checking a fast
algorithm against the slow one it replaced is worth more than any single sample.

**Output format.** An HTML fragment to append inside `<main>`, following the conventions of the
existing file:

- `<h2>` per chapter (`Chapter N: Title`), `<h3>` per section, `<h4>` for subsections within a
  section that runs long.
- Python in `<pre><code class="language-python">`. Non-code displays (matrices, tables, worked
  examples) go in a plain `<pre><code>` with no language class. Inline identifiers in `<code>`.
- Math in KaTeX, `$...$` delimiters, inline only. The page renders `$$` inline as well, so it
  buys nothing; never use it.
- No inline `<style>`; the shared `style.css` covers everything.
- English only, and never use an em dash.

**My notes on chapter X (title):**

{NOTES}

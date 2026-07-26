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

**Calibration.** Read the chapters already written in
[bioinformatics-algorithms.html](bioinformatics-algorithms.html) and match them: same voice, same
depth, same rhythm of prose, formalisation, code, and analysis. They define the target quality.

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

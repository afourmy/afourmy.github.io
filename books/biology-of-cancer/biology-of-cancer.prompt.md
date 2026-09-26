# Prompt: lecture notes for *The Biology of Cancer*

Reusable prompt for writing one chapter page of this section. Paste it and name the chapter.

---

You are writing chapter N of my notes on *The Biology of Cancer* by Robert A. Weinberg (3rd edition,
2023), in `website/books/biology-of-cancer/`.

**Source.** The reading notes for the chapter are in `notes/chNN.md`: the chapter's gist, its facts
with the book's numbers, and candidate figures. If a detail is missing, extract the book with
`pdftotext` from `~/Downloads/Weinberg R. The Biology of Cancer 3ed 2023/` and read the chapter.

**What the page is for.** The gist of the chapter, developed: every main idea, the mechanism behind
it, and the evidence that established it, as a course that reads in one piece. It is not a summary
of every paragraph. Leave out the agreed drops listed in `CLAUDE.md`; if another topic seems worth
dropping, list it with a reason and wait for my answer.

**Reader.** Knows computer science and mathematics, knows no biology. Define every biological term
in plain words at its first use, only as deeply as the chapter needs. Never explain the mathematics.

**Style.** Factual writing: every sentence states a fact, a definition, a mechanism or a number. No
rhetorical questions, metaphors in place of mechanisms, filler transitions, sentences about the page's
own structure, dramatic framing, rare words or storytelling. About six sentences per paragraph,
developing each idea rather than naming it. Headings name their content. Never use the em dash. No
code. Inline KaTeX with `$...$` only.

**Plain English.** One fact per sentence, about 15 words on average and none over 30, subject first. No
clause as subject, no rare senses of common words ("to found"), no semicolons chaining facts, no stacked
appositives, no sentence starting with a lowercase gene name, no mention of "the book". Reread every
paragraph for readability before publishing, not only for accuracy.

**Figures.** Look for the drawing first; each main idea gets a figure. Hand-written inline SVG with the
existing `fig-*` classes, coordinates computed by a throwaway script, rendered with headless Chrome and
looked at before shipping. A figure plots a computed model or numbers stated in the book's text,
never values read off the book's plots. Every number is taken from the notes or computed and checked
with an assertion, never recalled.

**Output.** One HTML page named by the slug in `CLAUDE.md`, with the same head as the other pages of
the section (two levels deep: `../../style.css`, `../../nav.js`), and a row for it on `index.html`
(`Chapter N: Short Title` plus a one-paragraph description). All rules in `CLAUDE.md` apply.

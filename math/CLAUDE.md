# Redesigning a math course page

The base guideline for any course redesign is `ARTISTIC_DIRECTION.md` at the website root: read it first and apply it in full (the one idea per result, seeing before computing, encodings, plain simplicity, the reconstruction test). The rules below do not replace it; they are the math-specific layer on top of it, learned while redoing `continuite.html`. Follow both to avoid repeating the same mistakes.

## Content

- The one hard constraint: the new page must never contain fewer ideas than the old one. Statements, proofs, and exercises may all be reworked when that improves them, but every idea of the original must survive; if something seems worth dropping, propose it and wait for approval.
- Structure the course into `h3` sections. End with a "The techniques of this chapter" section: the few reusable techniques, stated as literal facts.
- Substantial proofs may get one "Idea." paragraph (`<em>Idea.</em>` / `<em>Idée.</em>`) at the top, inside the `details`, before the original text.
- Prose goes before a `thm-block`, never between the block and its `details.proof` elements: the proof toggle in `nav.js` walks the sibling chain and anything inserted there breaks it.

## Prose register

- Plain AND short. One step per sentence, minimum words, every word literal.
- No aphorisms, slogans, or metaphors doing load-bearing work. "Commuting with limits makes stability free" was rejected as gibberish; "the limit rules for sequences become rules for continuous functions" is the correct register.
- Test before keeping a sentence: if it needs a second reading to see what it literally claims, rewrite it.
- Every prose addition exists in both languages (`class="en"` and `class="fr"`).

## Figures

Figures are the main vehicle of the redesign: every result whose idea can be drawn gets an SVG figure.

- Use the shared `.figure` / `.fig-*` classes in `style.css` (curve, axis, guide, band, accent, dot, hole, interval). Never inline styles.
- If the text names a function, the curve must be that actual function, plotted from computed coordinates. A generic lookalike captioned as $\sin x / x$ was rejected.
- Every symbol in a figure labels a visible, anchored element: an interval on an axis, a line, a point. Nothing floats near the curve. Floating ε/δ letters were rejected.
- Draw the quantities of the statement itself: name the points ($x$, $y$, $x'$, $a$, $c$) and mark their differences as intervals on the axes. If sample points appear ($x_1, x_2, \dots$), each one gets its guides and its labeled image $f(x_i)$ on the y-axis.
- Keep one visual vocabulary across all figures: shaded bands for output margins, strips or `fig-interval` segments for input margins, dashed `fig-guide` lines for projections, `fig-hole` for removable points.
- Labels are math symbols only, so one SVG serves both languages. A figure placed inside a proof `details` must be duplicated in the `en` and `fr` versions.
- Minus signs in SVG text are U+2212, never a hyphen or dash.
- Test for a figure: the reader should be able to reconstruct the sentence it illustrates from the drawing alone.

## Workflow

- Propose the list of figures (what each would show, where it goes) and wait for approval before drawing.
- Propose any other significant choice (structure changes, new sections) before doing it; silence is not approval.
- No em dashes anywhere, in either language.

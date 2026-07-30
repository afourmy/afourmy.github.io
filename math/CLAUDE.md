# Redesigning a math course page

The base guideline for any course redesign is `ARTISTIC_DIRECTION.md` at the website root: read it first and apply it in full (the one idea per result, seeing before computing, encodings, plain simplicity, the reconstruction test). The rules below do not replace it; they are the math-specific layer on top of it, learned while redoing `continuite.html`. Follow both to avoid repeating the same mistakes.

Before starting, also read the courses already redone and use them as worked examples of the target result: currently `continuite.html` and `complexes.html` (structure, prose register, figures); more will join it over time.

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

Figures are the main vehicle of the redesign: every result whose idea can be drawn gets an SVG figure. Three principles, learned the hard way:

- **A figure draws the actual objects of the statement, not a lookalike.** If the text names a specific object (a function, a graph, a group, a matrix), the figure shows that exact object, computed for real, not a generic shape that resembles it. A generic curve captioned as $\sin x/x$ was rejected.
- **The quantities the statement talks about are the ones marked in the figure.** Whatever the statement quantifies over or compares must be visible and named in the drawing, so the reader can match the symbols of the statement to elements of the picture one for one. (In `continuite.html` this meant naming the points and marking their differences as axis intervals; each course will have its own version of this.)
- **Every symbol labels a visible, anchored element; nothing floats.** A letter in a figure must sit against the interval, line, or point it names. Floating ε/δ letters were rejected. Test for every figure: the reader should be able to reconstruct the sentence it illustrates from the drawing alone.

Practical rules:

- **Text that describes a figure is a caption, placed below it**, never body prose above it. Wrap the SVG in `<figure class="figure-block">` and put the caption in a single `<figcaption>` after it, bilingual via `<span class="en">` and `<span class="fr">` inside that one element (two `figcaption` elements would be invalid HTML). A figure inside a language-specific proof takes a plain `<figcaption>` with no spans, since the enclosing `details` is already language-tagged. Prose above a figure is only for text that advances the mathematics; if it describes the drawing, it belongs underneath.
- Use the shared `.figure` / `.fig-*` classes in `style.css`, extending them in `style.css` if a new kind of mark is needed. Never inline styles.
- Within a page, keep one visual vocabulary: the same kind of quantity is always drawn the same way across figures.
- Reference elements must frame what they contain: an axis has to run past every object drawn on it, never stop inside a circle or a curve. Compute the drawn objects' extent first, then set the axis endpoints beyond it, and check afterwards.
- Labels are math symbols only, so one SVG serves both languages. A figure placed inside a proof `details` must be duplicated in the `en` and `fr` versions.
- Minus signs in SVG text are U+2212, never a hyphen or dash.

## Workflow

- Propose the list of figures (what each would show, where it goes) and wait for approval before drawing.
- Propose any other significant choice (structure changes, new sections) before doing it; silence is not approval.
- No em dashes anywhere, in either language.

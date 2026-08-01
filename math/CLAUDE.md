# Redesigning a math course page

The base guideline for any course redesign is `ARTISTIC_DIRECTION.md` at the website root: read it first and apply it in full (the one idea per result, seeing before computing, encodings, plain simplicity, the reconstruction test). The rules below do not replace it; they are the math-specific layer on top of it, learned while redoing `continuite.html`. Follow both to avoid repeating the same mistakes.

Before starting, also read the courses already redone and use them as worked examples of the target result: currently `continuite.html` and `complexes.html` (structure, prose register, figures); more will join it over time.

## Page layout

Every course page has the same three top-level (`h2`) sections, in this order: **Course**, **Techniques**, **Exercises** (`Cours`, `Techniques`, `Exercices`). Each heading is duplicated in both languages.

**Nothing is done twice on the page.** No object, computation or question appears as an entry in two sections, and no entry redoes something the Course already worked through. Applying a general result the Course proved is exactly what an entry should do; re-solving a specific instance the Course already solved is not. The trap is the Course's own examples and figure captions: `complexes.html` had a caption drawing $f(z) = 2iz+1$ around its fixed point and naming the centre, ratio and angle, which silently turned the matching exercise into a copy of the answer. Before keeping an entry, grep the whole page for its concrete objects (the map, the numbers, the function) and read what comes back, captions included.

**A duplicate is deleted, never relocated.** Moving the offending entry to another section does not fix anything: it was spoiled because the answer is already printed somewhere on the page, and that stays true wherever the entry sits. Do not invoke the never-fewer-ideas constraint to justify keeping it; the idea is on the page already, which is precisely the problem. Either delete the entry outright, or change the concrete object it is built on so that it becomes a real question again. Run the duplicate grep over every section including the Course, not only over the section being edited.

**Within Techniques and Exercises, entries run from easiest to hardest.** The reader meets the one-line case first and the long one last. This ordering wins over every other way of arranging the entries: do not group them by theme, by the order the Course introduces them, or by the order they were written in. When a technique's difficulty and its exercise's difficulty disagree, order by the exercise, since that is what the reader has to do. The one exception is the counterexamples, which open the Exercises section whatever their difficulty; inside that opening group they are again ordered easiest to hardest.

### 1. Course

The mathematics itself, split into `h3` sections: definitions, theorems, proofs, figures. This is what the redone pages already contain.

### 2. Techniques

The few reusable techniques of the chapter, each stated as a literal fact and each followed immediately by a short exercise that puts it to work.

- The technique first, in one or two sentences saying what to do and when, in the register the pages already use: "To solve $z^n = W$, find one root and multiply it by the $n$-th roots of unity."
- Then one énoncé applying it, solution in a `details.proof`. Its job is to show the technique working once, not to test the reader: choose the easiest instance that still exercises the whole technique.
- If an exercise already in the Exercises section demonstrates the technique, move it here instead of writing a second one. Moving is not dropping, so the constraint below is untouched.
- **Never leave a technique without its exercise.** Every technique on the page carries one, with no exceptions: a bare technique is not an acceptable outcome, not even for a framing statement that reads more like a principle than a procedure. If no existing exercise fits and no easy one comes to mind, invent one. If a technique genuinely cannot be exercised it was never a technique: state it in the Course, beside the results it explains, and never as a bare entry here. Do not turn it into a section intro, those are banned. `continuite.html` had "completeness of $\mathbb{R}$ is behind every existence result", which is a true and useful observation and belongs next to the theorems it accounts for, not in a list of things to do.
- A `<ul>` of bullets no longer serves, since a list item cannot carry a `details.proof`. Each technique becomes its own block: statement, then énoncé, then hidden solution.

### 3. Exercises

The chapter's exercises: statement in `thm-block exercise`, solution in `details.proof`.

**The Exercises section opens with the counterexamples**, before any ordinary exercise. A hypothesis earns its place by being necessary, and the way to show that is to delete it and watch the theorem fail. Each such exercise takes one theorem of the Course, drops exactly one of its hypotheses, and asks for an object satisfying everything that is left while breaking the conclusion. They are ordinary exercises in every other respect, labelled `Exercise.` / `Exercice.` like the rest.

- Write it as a task, not a discussion: "Find a counterexample to [theorem] when [hypothesis] is dropped." Same markup as an exercise, statement in a `thm-block`, counterexample hidden in a `details.proof`.
- The énoncé names the hypothesis being removed, so the reader knows which conditions the counterexample still has to satisfy.
- One entry per (theorem, hypothesis) pair. A theorem with three hypotheses may appear three times, once, or not at all.
- **Only mathematically interesting counterexamples. An obvious one is worse than none at all.** This is the first filter and the one that gets ignored: if the reader can see the counterexample straight from the statement, it teaches nothing and must not go on the page. A step function violating the intermediate value theorem, $x^2$ failing to be injective on $[-1,1]$, $f(x) = x$ not attaining its bounds on $]0,1[$: nobody ever believed those statements, so watching them fail is not an insight, it is padding. The bar is whether a competent reader would have hesitated before seeing the answer. Keep the ones where the hypothesis looks removable and the failure is a genuine surprise: $x^2$ is continuous on all of $\mathbb{R}$ and still not uniformly continuous; a continuous strictly increasing bijection can have a discontinuous inverse as soon as its domain stops being an interval.
- **An entry has to teach something. Most hypotheses teach nothing and get no entry.** The test is not whether a failing object exists, it is what the reader learns from the failure. Never add an entry to fill the section out.
- **Reject every hypothesis whose removal only makes an expression undefined.** $a \neq 0$ in $az^2 + bz + c = 0$, $z \neq 0$ before $\arg(z)$ or $1/z$, $W \neq 0$ in $z^n = W$, $C \neq D$ before a quotient of affixes, $n \ge 2$ in a sum of $n$ terms: dropping any of these divides by zero, or asks for the argument of $0$, or degenerates an index range. The answer is always "the formula is meaningless here", which is worth nothing on the page. These look like valid entries and are the main way these exercises go wrong.
- **Keep a hypothesis only when removing it leaves every expression well defined and the statement still comes out false.** Then the counterexample shows what the hypothesis was doing, which is the whole point: real coefficients are what force the roots to come in conjugate pairs, the congruence $[2\pi]$ is what makes arguments add. Two entries of that kind are worth more than five, and a page whose Exercises section opens with no counterexample at all is a legitimate outcome.
- Always the simplest counterexample: a specific function, sequence, or number the reader can check in one line, never a general construction where a particular object does the job.

After the counterexamples come the ordinary exercises, easiest to hardest.

## Content

- The one hard constraint: the new page must never contain fewer ideas than the old one. Statements, proofs, and exercises may all be reworked when that improves them, but every idea of the original must survive; if something seems worth dropping, propose it and wait for approval.
- Substantial proofs may get one "Idea." paragraph (`<em>Idea.</em>` / `<em>Idée.</em>`) at the top, inside the `details`, before the original text.
- Prose goes before a `thm-block`, never between the block and its `details.proof` elements: the proof toggle in `nav.js` walks the sibling chain and anything inserted there breaks it.

## Prose register

- **HARD RULE, broken more often than any other: no editorialising and no bookish phrasing.** A sentence either states a mathematical fact or it is deleted. There is no third category, and "it makes the idea land" is not a defence. Every example below was written for these pages and rejected:
  - *Commentary on the mathematics instead of the mathematics.* "An identity between two counts is never a coincidence", "finding the set is the whole work", "the last line is worth pausing on", "the trap is that", "this is not an accident to be patched", "the next bound says something weaker and much stranger", "neither conclusion can be guessed from its hypothesis". Write the fact: "Two expressions that count the same set are equal."
  - *Narrating the reader, the writer, or the page.* "Counting a set out loud, one, two, three", "nobody knows how to exhibit a single one", "everything below is an instance of a single move", "which is what makes a polynomial identity worth more than the sum it came from".
  - *Rhetorical shapes.* Antithesis ("They are not conventions. They are counts."), doubling for emphasis ("what they all share, and the only thing they all share"; "never more and never fewer"), and the colon followed by a flourish ("uses up the pool:", "counted at different grains").
  - *Verdicts on difficulty, beauty or importance.* "much stranger", "cannot be guessed", "the whole work", "worth pausing on". The reader decides that; the page states facts.
  - *Name the objects. Never describe them in the abstract.* "To count what avoids several forbidden properties, count what has at least one of them" was rejected: "what avoids several forbidden properties" is a noun phrase standing in for objects that were never named, and the reader has to build the picture before the sentence can even be parsed. Give the things letters and say what is done to them: "To count the objects having none of the properties $P_1, \ldots, P_n$, subtract from the total the number having at least one." Same fault in "count the objects with a structure they do not have", "all that survives of a choice is", "the weights the sum carries". If a sentence cannot be read at speed by someone who already knows the mathematics, it is written wrong, however correct it is.
  - *Headings and captions are covered by this rule too.* A heading names what is in the section, in the plainest words available; it is not a thesis, a claim, or a title. "Number is what survives a bijection" was rejected: the reader cannot tell what is in the section, and has to decode a slogan to find out. "The shape of a row" was rejected: it names nothing. Write "Cardinality and the laws of arithmetic", "The distribution of subset sizes". A heading that asserts something is fine when the assertion is literally the content of the section, as in "$\mathbb{C}$ is the plane with a multiplication" or "Multiplying is rotating and scaling"; the test is whether a reader who has not read the section can predict what is in it from the heading alone.
  - The test: could this sentence stand inside a theorem statement or a proof without looking out of place? If not, it is commentary. Delete it, or replace it with the fact it was gesturing at. Prose that gives the idea of a theorem before its statement is still wanted, but the idea must be stated as mathematics, not as an opinion about the mathematics.
- **Never state a definition in prose before its `Definition` block.** Introducing the object twice, once informally and once formally, was rejected twice ("Set $e^{i\theta} = \cos\theta + i\sin\theta$..." written above the definition that says the same thing; and a paragraph describing conjugation and modulus placed before either was defined). Prose before a definition may say what the definition is for and why the reader should care, but must not define, name, or use the object. Put the interpretation *after* the block instead. This does not apply to theorems: prose giving the idea of a theorem before stating it is wanted, and is what the artistic direction asks for.
- Prose that describes a picture must never point at a figure that is not adjacent. Say "below" only when the figure is the next element.
- **Never state a definition in prose before its `Definition` block.** Introducing the object twice, informally then formally, was rejected twice: "Set $e^{i\theta} = \cos\theta + i\sin\theta$..." written above the definition that says the same thing, and a paragraph describing conjugation and modulus placed before either was defined. Prose before a definition may say what the definition is for, but must not define, name, or use the object; put the interpretation after the block. This does not apply to theorems, where prose giving the idea before the statement is wanted.
- Prose describing a picture must never point at a non-adjacent figure. Say "below" only when the figure is the next element.
- **Never refer to the page itself.** No "the chapter", "this chapter", "the chapter reduces to", "a result of the chapter", "the techniques of this chapter", "as we saw above", "we will see". These pages are not a book and do not narrate themselves. Write the mathematics and nothing else: "The techniques" as a heading, not "The techniques of this chapter"; "Removing a hypothesis can make a true statement false", not "each statement below takes a result of the chapter". Where a sentence exists only to announce what the page is doing, delete it. **This bans section intros.** A section never opens with a sentence describing what it contains ("Each technique is followed by an exercise that uses it", "Each exercise names the hypothesis removed"): the heading has already said it, and the entries state their own tasks. A section starts directly with its first entry. Prose inside a section is allowed only when it advances the mathematics.
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

- A caption describing several panels of one figure gets one line per panel, with the panel name in bold: wrap each panel's text in `<span class="cap-part">` and its name in `<span class="cap-lead">` (`Left:`, `Middle:`, `Right:`). Never run the panels together as one paragraph.
- **Text that describes a figure is a caption, placed below it**, never body prose above it. Wrap the SVG in `<figure class="figure-block">` and put the caption in a single `<figcaption>` after it, bilingual via `<span class="en">` and `<span class="fr">` inside that one element (two `figcaption` elements would be invalid HTML). A figure inside a language-specific proof takes a plain `<figcaption>` with no spans, since the enclosing `details` is already language-tagged. Prose above a figure is only for text that advances the mathematics; if it describes the drawing, it belongs underneath.
- Use the shared `.figure` / `.fig-*` classes in `style.css`, extending them in `style.css` if a new kind of mark is needed. Never inline styles. Every stroke-only `.fig-*` class needs `fill: none`, or a `<circle>` or closed `<path>` using it renders as a solid black blob.
- A curve derived from another (an inverse, a reflection) must be computed from the original's points, never drawn a second time by eye.
- Within a page, keep one visual vocabulary: the same kind of quantity is always drawn the same way across figures.
- Never pick the `viewBox` by hand: the leftover canvas ends up lopsided, usually as a wide empty band above the drawing. Measure the rendered content (`svg.getBBox()` in a headless browser) and set the `viewBox` to that box plus a uniform 10px margin, so every figure hugs its content on all four sides.
- Reference elements must frame what they contain: an axis has to run past every object drawn on it, never stop inside a circle or a curve. Compute the drawn objects' extent first, then set the axis endpoints beyond it, and check afterwards.
- Labels are math symbols only, so one SVG serves both languages. A figure placed inside a proof `details` must be duplicated in the `en` and `fr` versions.
- Minus signs in SVG text are U+2212, never a hyphen or dash.

## Checking the result

Static checks are not enough. They passed while a circle rendered as a solid black disk, while $f^{-1}$ was a freehand curve instead of a real reflection, and while a quarter of a figure was empty canvas. Before declaring a page done, serve it (`python3 -m http.server`) and screenshot it with headless Chrome, then look at every figure.

Also script these checks: the three `h2` sections present, in order, in both languages; the counterexamples first inside Exercises; every technique followed by an énoncé; HTML tags balanced; no `details.proof` separated from its block; EN/FR paragraph parity; no em dash; no label out of frame; no two labels overlapping; no axis stopping inside a circle.

## Workflow

- Propose the list of figures (what each would show, where it goes) and wait for approval before drawing.
- Propose any other significant choice (structure changes, new sections) before doing it; silence is not approval.
- No em dashes anywhere, in either language.

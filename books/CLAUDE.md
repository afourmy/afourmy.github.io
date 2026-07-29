# Book pages

## Factual writing only
Book pages read as factual technical writing, not as a book. Every sentence states a fact, a definition, a cost, or a mechanism. Banned:

- **Rhetorical questions** ("Wouldn't so many mutations damage the genome?"). State the fact directly.
- **Filler transitions that sound like reasoning but assert nothing**: "The remedy follows from the cost", "Note what was given up along the way", "The pieces now assemble into".
- **Sentences narrating the page's own structure** rather than its subject: "This is where the second strand, deferred earlier, is finally accounted for", "The code above does not do this yet", "We fold the correction in once mismatches are in place". Never announce that something was postponed or is now being resolved, just state the technical point where it belongs.
- **Metaphors in place of the technical statement**: "a short message written in the DNA", "a physical fingerprint of which way replication ran", C's being "destroyed".
- **Dramatic or colloquial framing**: "It is not a free win", "the dictionary version wins", "a decisive improvement".
- **Bookish headings** ("Back to the Clock"). Headings name the content: "Application: the Evening Element".
- **Rare, obscure, or abstract words** where a common one works, and long sentences the reader has to read twice. Keep the wording simple and direct. This covers the prose only: technical terms stay exact.

When tempted to write a transition, either state the technical point it was decorating or delete the sentence.

## Adding exercises
**Every exercise the user sends gets added to the page. Always.** Do not ask whether they want it added, and do not answer in chat only. Any message containing a problem statement is a request to add it, whatever the wording: "add: ...", "then: ...", "show that ...", or a bare question with no verb at all.

When adding one:

- **Append at the end.** Add it after the last existing exercise, immediately before the trailing HTML comment. Never choose the position yourself, do not insert it next to a related exercise or reorder anything, even if that seems more logical.
- **Change nothing else.** Adding an exercise means adding an exercise. Do not touch existing exercises, solutions, or their order.
- **Keep the solution concise.** One short paragraph: the key idea and the answer. No restating the problem, no listing intermediate quantities the reader can compute, no "equivalently..." or alternative derivations, no sanity checks.
- **Leave the answer in closed form.** End at `\binom{53}{3}` or `\binom{5}{3}^2 \cdot 3!`. Do not expand into products or evaluate to a number. Exception: when the answer is intrinsically a plain count, such as an inclusion-exclusion total.
- **Match the existing markup**, `<div class="thm-block exercise">` for the statement, `<details class="proof">` for the solution.

## Wording of the énoncé
State hypotheses declaratively ("Let $G$ be a connected graph drawn in the plane..."), never as an instruction to the reader ("Draw a connected graph..."). The only imperative belongs to the task itself: "Prove that", "Show that", "Find".

## Notation
Never introduce notation that the page has not defined. Before using a symbol, check it is either defined in the exercise itself or already established on the page with that same meaning, `grep` for it. Prefer plain words ("step right or up") over unexplained symbols.

## Alternate solutions
An alternate solution is an extra `<p>` inside the same `<details>` block, opening with an italic lead-in: `<em>Alternative solution.</em>` (or `<em>Alternative proof.</em>` for a theorem). Never a second `<details>` block, and never a bare "Alternatively, ..." without the lead-in.

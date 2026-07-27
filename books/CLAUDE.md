# Book pages

## Adding exercises
When asked to add an exercise:

- **Append at the end.** Add it after the last existing exercise, immediately before the trailing HTML comment. Never choose the position yourself, do not insert it next to a related exercise or reorder anything, even if that seems more logical.
- **Change nothing else.** Adding an exercise means adding an exercise. Do not touch existing exercises, solutions, or their order.
- **Keep the solution concise.** One short paragraph: the key idea and the answer. No restating the problem, no listing intermediate quantities the reader can compute, no "equivalently..." or alternative derivations, no sanity checks.
- **Leave the answer in closed form.** End at `\binom{53}{3}` or `\binom{5}{3}^2 \cdot 3!`. Do not expand into products or evaluate to a number. Exception: when the answer is intrinsically a plain count, such as an inclusion-exclusion total.
- **Match the existing markup**, `<div class="thm-block exercise">` for the statement, `<details class="proof">` for the solution.

## Alternate solutions
An alternate solution is an extra `<p>` inside the same `<details>` block, opening with an italic lead-in: `<em>Alternative solution.</em>` (or `<em>Alternative proof.</em>` for a theorem). Never a second `<details>` block, and never a bare "Alternatively, ..." without the lead-in.

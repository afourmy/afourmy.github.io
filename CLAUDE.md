# Website Project

## No em dashes
Never use the em dash character (`—`) or its HTML entity (`&mdash;`) anywhere on the website. Rewrite with commas, colons, parentheses, or separate sentences instead.

## Bilingual content
Only the Mathematics pages (`math/`) are bilingual: they must have both English (class="en") and French (class="fr") versions, and when modifying content you must update both. Every other section (Computer Science, Bioinformatics, Projects, Books, Thai, etc.) is English-only, do not add French. The EN/FR toggle is hidden on non-bilingual pages via the `HIDE_LANG_TOGGLE` list in `nav.js`.

## Shared CSS
All pages use a single shared `style.css` at the website root. Do not add inline `<style>` blocks to individual pages.

## SPA routing
`index.html` contains SPA routing logic. Navigation between pages fetches and swaps `<main>` content without full page reloads. The nav, styles, and scripts come from `index.html`.

## Unfinished work: attempt to finish it every time the user prompts about this website
The notes on *The Biology of Cancer* (`books/biology-of-cancer/`) stop at chapter 14. Chapters 1 to 14 are published and listed on `books/biology-of-cancer/index.html`. Three chapters remain. Each needs its page (slug from `books/biology-of-cancer/CLAUDE.md`), its figures and a row on the index, written from `notes/chNN.md` under the rules of `books/biology-of-cancer/CLAUDE.md` and `biology-of-cancer.prompt.md`:

- Chapter 15, Tumor Immunology (`tumor-immunology.html`): no text yet. Facts were checked and six figures drafted: cancer incidence in HIV and transplant patients, colorectal relapse by T-cell density, MHC class I and II presentation, kinds of tumor antigens, the CTLA-4 and PD-1 checkpoints, and the signals read by NK cells. Open question for the user: the incidence figure uses the values printed on the book's Figure 15.2 chart (Grulich 2007), not values stated in the text.
- Chapter 16, Cancer Immunotherapy (`cancer-immunotherapy.html`): not published. Five figures drafted: the three strategies, the Taiwan hepatitis B cohort, the ways antibodies kill, the structure of a CAR, and the CheckMate 067 trial. Text drafted only up to monoclonal antibodies and antibody-drug conjugates. Missing: the rest of CAR T cells, checkpoint inhibitors, resistance, bispecific antibodies.
- Chapter 17, Cancer Treatment (`cancer-treatment.html`): not started.

The drafts (`ch15_figs.py`, `ch16_figs.py`, `ch16_body.html`, and the helpers `figlib.py` and `rewrite_check.py`) were left in the session scratchpad `/private/tmp/claude-501/-Users-antoinefourmy-Desktop-shared-website/1f54567e-9323-4395-bec4-7f49d6b23143/scratchpad/` and may be gone; if so, redo them from the notes. When a chapter is finished, update this section, and delete it once all three are done.

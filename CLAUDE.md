# Website Project

## No em dashes
Never use the em dash character (`—`) or its HTML entity (`&mdash;`) anywhere on the website. Rewrite with commas, colons, parentheses, or separate sentences instead.

## Bilingual content
Only the Mathematics pages (`math/`) are bilingual: they must have both English (class="en") and French (class="fr") versions, and when modifying content you must update both. Every other section (Computer Science, Bioinformatics, Projects, Books, Thai, etc.) is English-only, do not add French. The EN/FR toggle is hidden on non-bilingual pages via the `HIDE_LANG_TOGGLE` list in `nav.js`.

## Shared CSS
All pages use a single shared `style.css` at the website root. Do not add inline `<style>` blocks to individual pages.

## SPA routing
`index.html` contains SPA routing logic. Navigation between pages fetches and swaps `<main>` content without full page reloads. The nav, styles, and scripts come from `index.html`.

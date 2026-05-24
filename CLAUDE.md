# Website Project

## No em dashes
Never use the em dash character (`—`) or its HTML entity (`&mdash;`) anywhere on the website. Rewrite with commas, colons, parentheses, or separate sentences instead.

## Bilingual content
All math, CS, and networking content must have both English (class="en") and French (class="fr") versions. When modifying content, always update both language versions.

## Shared CSS
All pages use a single shared `style.css` at the website root. Do not add inline `<style>` blocks to individual pages.

## SPA routing
`index.html` contains SPA routing logic. Navigation between pages fetches and swaps `<main>` content without full page reloads. The nav, styles, and scripts come from `index.html`.

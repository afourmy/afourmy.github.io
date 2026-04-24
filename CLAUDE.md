# Website Project

## Bilingual content
All math, CS, and networking content must have both English (class="en") and French (class="fr") versions. When modifying content, always update both language versions.

## Shared CSS
All pages use a single shared `style.css` at the website root. Do not add inline `<style>` blocks to individual pages.

## SPA routing
`index.html` contains SPA routing logic. Navigation between pages fetches and swaps `<main>` content without full page reloads. The nav, styles, and scripts come from `index.html`.

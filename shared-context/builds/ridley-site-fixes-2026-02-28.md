# Build Summary — ridley-site-fixes-2026-02-28

## Scope
Address QA findings for ridleyresearch.com (critical + warnings + notes where actionable in repo).

## Completed
1. **Robots file fix at origin**
   - Added `/robots.txt` at site root with valid plain-text directives and sitemap pointer.
   - Goal: ensure static file is served directly instead of SPA/homepage fallback content.

2. **About nav redirect fix (308 cleanup)**
   - Replaced `href="/about"` with `href="/about/"` across site templates/pages (33 HTML files).
   - Eliminates unnecessary redirect hop from nav clicks.

3. **Homepage pricing consistency**
   - Updated homepage “What We Build” Platform Setup price from **$500 one-time** to **$497 one-time** to match “Work With Us” section.

4. **Homepage blog dispatch ordering**
   - Reordered dispatch items to strict newest-first sequence:
     - Feb 25
     - Feb 24
     - Feb 24
     - Feb 24
     - Feb 23
     - Feb 23

5. **Basic CSP header added**
   - Added baseline Content-Security-Policy in `_headers`.

## Deferred / Decision-needed
1. **Cloudflare Content Signal bot blocks (ClaudeBot/GPTBot/Google-Extended/etc.)**
   - Requires Deacon decision before overriding defaults.
   - No change made.

2. **`/products/` vs `/pricing/` sync risk**
   - Confirmed as maintenance concern; no structural content merge done in this patch.

## Files changed
- `ridleyresearch-site-v2/_headers`
- `ridleyresearch-site-v2/robots.txt` (new)
- `ridleyresearch-site-v2/index.html`
- 33 HTML files updated for `/about/` nav path consistency.

## QA checklist mapping
- [x] P0 robots content contamination mitigation (origin file added)
- [x] 308 nav redirect (`/about` -> `/about/`)
- [ ] Bot-block policy decision (awaiting Deacon)
- [x] Homepage price mismatch
- [x] Basic CSP
- [x] Dispatch list ordering
- [~] Pricing-page duplication risk logged

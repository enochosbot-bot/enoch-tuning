# Build Summary — ridleyresearch-site-v2 critical remediation

Date: 2026-02-27
Owner: Bezzy (coder)
Scope: Resolve HOLD blockers from QA report `shared-context/qa-reports/ridleyresearch-site-v2-qa.md`

## Changes completed

### 1) CRITICAL — Open redirect in checkout.js
- File: `functions/checkout.js`
- Removed trust in request `Origin` header.
- Added `getSiteOrigin(env)` helper and now build Stripe `success_url`/`cancel_url` from `PUBLIC_SITE_ORIGIN` (fallback `https://ridleyresearch.com`).

### 2) CRITICAL — chat.js CORS + abuse controls
- File: `functions/chat.js`
- Replaced wildcard CORS with allowlist (`CHAT_ALLOWED_ORIGINS`, default apex+www).
- Added explicit forbidden-origin rejection (`403`).
- Added per-IP in-memory rate limiting (`CHAT_RATE_LIMIT_PER_MIN`, default 5/min).
- Added optional API token check (`CHAT_API_TOKEN` via `X-Chat-Token`).
- Added `Vary: Origin` and strict OPTIONS handling.

### 3) HIGH — Blank CTA on hardware page
- File: `openclaw/hardware.html`
- Added scoped style override:
  - `.page-cta .cta { color: #0d1017 !important; -webkit-text-fill-color: #0d1017; }`
- Updated hardware discovery CTA mailto to include subject.

### 4) HIGH — Missing sitemap.xml
- Added file: `sitemap.xml`
- Includes 36 site routes with lastmod/priority values.

### 5) MEDIUM — Missing OG tags across pages
- Added default OG + Twitter card tags across HTML pages lacking OG metadata.
- Uses canonical URL per page and shared image `/rr-mark.png`.

### 6) MEDIUM — Duplicate /about route
- Removed duplicate file: `about.html`
- Canonical route remains `about/index.html`.

### 7) LOW — Missing email subject on hardware CTA
- File: `openclaw/hardware.html`
- `mailto:hello@ridleyresearch.com?subject=Discovery%20Call`

## Verification run (local checks)
- No wildcard CORS remains in `functions/`
- Checkout now references `PUBLIC_SITE_ORIGIN` (no request header origin usage for redirects)
- Hardware CTA now has explicit visible text color override + subject param
- `sitemap.xml` exists
- `about.html` removed

## Notes for deploy/env
- Set `CHAT_ALLOWED_ORIGINS` explicitly in Cloudflare env (recommended).
- Optional hardening: set `CHAT_API_TOKEN` if using trusted server-side callers.

## Status
Ready for Solomon final review / re-QA.

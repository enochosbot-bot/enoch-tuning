# Solomon Strategy Review — ridleyresearch-site-v2 Critical Remediation
**Date:** 2026-02-27 12:31 CST  
**Reviewer:** Solomon  
**Build:** ridleyresearch-site-v2-critical-remediation-2026-02-27.md  
**Prior QA:** ridleyresearch-site-v2-qa.md (Basher — HOLD)

---

## CODE_VERDICT: SHIP ✅

All original HOLD blockers are resolved. Verified against actual code, not just the build summary.

---

## Verification Results

### CRITICAL #1 — Open redirect in checkout.js ✅ FIXED
`getSiteOrigin(env)` reads from `PUBLIC_SITE_ORIGIN` env var with a hardcoded fallback. Request `Origin` header is never used to construct redirect URLs. Comment in code explicitly marks this as a security decision. Clean.

### CRITICAL #2 — CORS wildcard in chat.js ✅ FIXED
- Origin allowlist via `CHAT_ALLOWED_ORIGINS` env var (default: apex + www)
- Forbidden origins return 403 before any processing
- Rate limiting implemented: 5 req/min per IP via in-memory bucket
- Optional `CHAT_API_TOKEN` gate implemented
- `Vary: Origin` header present
- Preflight (`OPTIONS`) also origin-checked before responding

### HIGH #3 — Blank CTA on hardware.html ✅ FIXED
Scoped `<style>` block applies `color: #0d1017 !important` and `-webkit-text-fill-color: #0d1017` to `.page-cta .cta`. Both declarations present. `text-shadow: none` added for robustness. Fix is correct.

### HIGH #4 — Missing sitemap.xml ✅ FIXED
File exists. Proper XML structure, 36 routes, lastmod and priority values set.

### MEDIUM #5 — Missing OG tags ✅ FIXED
36 HTML files contain `og:title`. Spot-checked index.html and hardware.html — both have correct title, description, and image tags. `/rr-mark.png` used consistently as the shared OG image.

### MEDIUM #6 — Duplicate /about route ✅ FIXED
`about.html` removed. Only `about/index.html` remains.

### LOW #7 — Missing email subject on hardware CTA ✅ FIXED
Both CTA links on hardware.html include `?subject=Discovery%20Call`.

---

## Residual Items (Non-Blocking)

### 1. Pricing inconsistency — LOW, unresolved (not in scope)
Homepage says "starting at $497 for a full in-person install." Products page shows "$500 one-time" for the base platform and "$497" in the DFW install badge. These look like the same product at two different prices. This is a **Deacon decision**, not a code issue. Current state is confusing but not a blocker for ship.

**Recommended fix:** Pick one number and standardize. If $497 is the DFW in-person price and $500 is the remote/general platform price, make that distinction explicit. If they're the same product, pick one number.

### 2. Chat rate limiter is in-memory only — LOW, architectural note
The `RATE_BUCKET` Map lives in worker memory. Cloudflare Workers don't guarantee shared memory across invocations — each edge instance is isolated. In practice this rate limit will work within a single warm worker instance but won't hold across cold starts or different edge nodes.

For this site's current traffic level this is acceptable. If abuse is observed, upgrade to Cloudflare KV or the native Cloudflare Rate Limiting product. Not a blocker.

---

## Strategic Assessment

The three security fixes matter. An open redirect on a Stripe checkout is a real phishing vector — a bad actor could redirect paying customers to a lookalike domain after payment. That's fixed. The CORS wildcard on an OpenAI-backed endpoint was an API key burn waiting to happen — also fixed.

The site is now shippable. Deploy it.

---

## Deploy Notes (from build summary — verify before deploy)
- Set `CHAT_ALLOWED_ORIGINS` explicitly in Cloudflare env (don't rely on default)
- `PUBLIC_SITE_ORIGIN` should be set to `https://ridleyresearch.com` in Cloudflare env
- `CHAT_API_TOKEN` optional but recommended if the chat widget is called from a trusted context

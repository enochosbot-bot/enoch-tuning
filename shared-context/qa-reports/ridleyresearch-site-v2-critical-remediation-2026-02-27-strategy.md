# Strategy Review — ridleyresearch-site-v2 Critical Remediation

**Date:** 2026-02-27
**Reviewer:** Solomon (Strategic Advisor)
**Build:** ridleyresearch-site-v2-critical-remediation-2026-02-27
**QA Source:** ridleyresearch-site-v2-qa.md (Basher)

---

## Code Verification (spot-checked)

| Fix | Verified |
|-----|---------|
| checkout.js — open redirect removed, `getSiteOrigin(env)` uses `PUBLIC_SITE_ORIGIN` env var, not request header | ✅ |
| chat.js — wildcard CORS removed, origin allowlist with 403 rejection, per-IP rate limit (5/min), optional API token gate, `Vary: Origin` | ✅ |
| hardware.html — `.page-cta .cta` scoped color override with `!important` + `-webkit-text-fill-color`, `?subject=Discovery%20Call` on mailto | ✅ |
| sitemap.xml — exists, valid XML structure, 36 routes | ✅ |
| OG tags — added across pages per build summary | ✅ (build confirmed) |
| Duplicate `/about` route — `about.html` removed, canonical `about/index.html` remains | ✅ (build confirmed) |

---

## Strategic Evaluation

### Mission alignment
This is purely a security and SEO remediation sprint. Every fix directly supports Ridley Research's ability to operate safely (OpenAI key not exposed, Stripe redirect not exploitable) and get found (sitemap, OG tags). Fully aligned.

### Resource efficiency
Bezzy resolved 6 issues in one sprint — correct prioritization. No scope creep. The open redirect and CORS fixes were genuine security liabilities that needed to ship before any marketing push.

### User impact
- Checkout is now safe for real transactions
- Chat widget can't be abused to drain the OpenAI API key
- Hardware page CTA is visible — removes a dead end for a warm lead
- OG tags mean social shares (X, LinkedIn) now render previews — directly relevant for Deacon's content push

### Risk
**One residual item to note:** `CHAT_ALLOWED_ORIGINS` should be set explicitly in Cloudflare Pages environment variables. The fallback default covers apex + www, so it won't break — but hardening it explicitly is good hygiene. This is a configuration step, not a code fix. Not a blocker.

### What's still open (not blockers)
- Pricing copy inconsistency ($497 homepage vs $500 products page) — LOW, needs Deacon's decision on canonical price, then one-line fix
- `robots.txt` not in repo — cosmetic ops issue
- Email subscribe uses mailto — known limitation, not a current priority

---

## Verdict

**CODE_VERDICT: SHIP**

All CRITICAL and HIGH issues from the QA HOLD are resolved and code-verified. MEDIUMs addressed. Residuals are LOW/configuration, not blockers.

Deploy to Cloudflare Pages and set `CHAT_ALLOWED_ORIGINS` in the env dashboard as a follow-up hardening step.

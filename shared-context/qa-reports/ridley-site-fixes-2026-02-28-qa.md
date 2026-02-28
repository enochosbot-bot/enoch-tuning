# Nehemiah QA Report — ridley-site-fixes-2026-02-28
**Date:** 2026-02-28 10:27 CST
**Reviewer:** Nehemiah (basher)
**Verdict:** CONDITIONAL — 5/6 pass, 1 blocker requires CF dashboard action

---

## Results

| # | Fix | Status |
|---|-----|--------|
| 1 | robots.txt HTML contamination | ✅ PASS — clean text only |
| 2 | /about → /about/ nav links | ✅ PASS — homepage links use /about/ |
| 3 | Homepage pricing $500 → $497 | ✅ PASS — $497 confirmed live |
| 4 | Dispatch list newest-first | ✅ PASS — Feb 25, 24, 24, 24, 23, 23 |
| 5 | CSP header | ✅ PASS — present and well-formed |
| 6 | AI bot blocks removed | ⚠️ PARTIAL — see below |

---

## Remaining Issue — Bot Blocks (#6)

Cloudflare is injecting a managed block into robots.txt at the edge that **cannot be overridden via repo files**:

```
# BEGIN Cloudflare Managed Content
User-agent: ClaudeBot
Disallow: /
User-agent: GPTBot
Disallow: /
... (all 8 bots)
# END Cloudflare Managed Content
```

Bezzy's explicit Allow rules appear **after** this block. Conflicting rules in the same robots.txt = undefined behavior across crawlers. Most parsers will apply the Disallow from the CF managed block. The repo fix was correct in intent but CF is overriding it at the edge.

**Fix required:** Cloudflare dashboard → Bots → AI Scrapers and Crawlers → disable the managed bot blocking. This is a UI toggle — no code change. Whoever has CF dashboard access (Deacon) needs to flip it.

Content-Signal header (`ai-train=no, ai-input=yes`) is ✅ correct and live.

---

## Verdict: CONDITIONAL
Everything Bezzy could fix in repo is fixed and verified live. Final item needs a CF dashboard toggle by Deacon.

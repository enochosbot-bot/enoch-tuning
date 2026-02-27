# SITE-STATUS.md — ridleyresearch.com

> **Every agent reads this before touching the site. Every agent updates this after.**
> Last updated: 2026-05-26 (Solomon)

---

## 🟢 Live Environment
- **URL:** https://ridleyresearch.com
- **Host:** Cloudflare Pages (project: `ridleyresearch`)
- **Deploy command:** `wrangler pages deploy . --project-name ridleyresearch` (run from this dir)
- ⛔ Netlify (`ridleyresearch-site-v2.netlify.app`) is a DEAD-END staging env — do NOT deploy there

## 📁 Site Path
`/Users/deaconsopenclaw/.openclaw/workspace/ridleyresearch-site-v2-revamped/ridleyresearch-site-v2/`

## ✅ Verification Rule
After ANY deploy: `curl -s "https://ridleyresearch.com/" | grep -i "<expected content>"` — verify against the REAL domain, never netlify.

---

## 🔴 Known Issues (Active — Fix These)

### ISSUE 1: Broken Nav HTML (CRITICAL)
- **What happened:** A multiline find/replace script left orphaned duplicate nav links floating OUTSIDE the dropdown div on every page it touched.
- **Symptoms:** Old "See All Products" and "Pricing" links exist as ghost HTML outside the nav dropdown. Visually may look OK but HTML structure is broken.
- **Scope:** All pages that were touched by the nav replacement script (check all ~33 HTML files)
- **Fix:** Audit nav HTML in every file. Remove all duplicate/orphaned link elements. Ensure exactly ONE nav structure per page with correct dropdown containment.
- **Status:** IN PROGRESS — Bezzy subagent dispatched (2026-05-26)

### ISSUE 2: Homepage Bloat (DESIGN)
- **What happened:** Homepage accumulated 10 sections over multiple edit sessions.
- **Current state:** Hero, About blurb, 3 product cards, Mission prose, Proof block, Blog posts, "Who This Is For" pain grid, 7 automation module cards, Pricing cards, CTA
- **Target state:** 7 sections — Hero → Proof/Credibility → 3 Product Cards → CTA (tight conversion page)
- **What to cut/move:**
  - 7 automation module cards → move to `/small-business/` page
  - "Who This Is For" pain grid → move to `/small-business/` page
  - Mission prose → move to `/about` page
  - About blurb → move to `/about` page
  - Pricing cards → keep only if concise, otherwise cut
  - Blog section → keep only if it renders cleanly
- **Status:** IN PROGRESS — Bezzy subagent dispatched (2026-05-26)

---

## ✅ What's Working (Do Not Break)
- RR.AI chat widget (`chat-widget.js`) — OpenAI gpt-4o-mini
- Blog at `/blog/` — Financial Advisors + Personal Trainers posts live
- Testimonials form at `/testimonials/submit`
- Nav dropdown: Explore (⭐ Leave a Review, About, Blog)
- Dark navy design + brand styles in `styles.css`

---

## 📋 Page Inventory
| Page | Path | Status |
|------|------|--------|
| Homepage | `index.html` | 🔴 Needs trim (10 → 7 sections) |
| About | `about.html` | ✅ Live |
| Blog index | `blog/` | ✅ Live |
| Small Business | `small-business/` | ✅ Live (receives cut homepage content) |
| Products | `products/` | ✅ Live |
| Pricing | `pricing/` | ✅ Live |
| Testimonials | `testimonials/` | ✅ Live |
| Success | `success.html` | ✅ Live |

---

## 🛠️ Agent Rules
1. **Read this file first** — always, before any edit
2. **Update this file after** — log what you changed and new status
3. **One nav structure per page** — never run a replace script without verifying output on at least 3 files manually first
4. **Deploy to Cloudflare Pages only** — `wrangler pages deploy . --project-name ridleyresearch`
5. **Verify on the live domain** — curl ridleyresearch.com, not netlify
6. **If you hit context limits mid-task** — update this file with exactly where you stopped before exiting

---

## 📝 Change Log
| Date | Agent | Change |
|------|-------|--------|
| 2026-02-24 | Enoch | Site launched on Cloudflare Pages, RR.AI chat widget live |
| 2026-02-25 | Enoch | Blog posts added, nav reordered, "We're Building in Public" post pinned |
| 2026-02-26 | Enoch | Chat widget renamed Riley → RR.AI, Cloudflare vs Netlify confusion resolved |
| 2026-05-26 | Enoch | Nav replacement script caused duplicate orphaned links on all pages |
| 2026-05-26 | Enoch | Homepage expanded to 10 sections (too many) |
| 2026-05-26 | Solomon | Created this file. Bezzy dispatched to fix nav + homepage. |
| 2026-05-26 | Solomon | Nav reordered: About → Blog → OpenClaw → Leave a Review. Star emoji removed. All 34 files updated + deployed. |

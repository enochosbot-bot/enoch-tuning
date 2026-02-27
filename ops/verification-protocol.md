# Verification Protocol
Last Updated: 2026-02-26
Owner: Enoch

## Core Rule
**Never mark a task complete without verifying the actual deliverable, live.**
"File exists on disk" is not verification. "Sub-agent said done" is not verification.

---

## General Verification Standards

| Claim | Verification Required |
|---|---|
| File was created | `test -f <path>` AND read first 10 lines |
| Sub-agent completed | Check output token count (< 500 on complex task = fake success). Read the file. |
| Config change applied | Read the live config file, don't trust the announcement |
| Cron job works | `openclaw cron list` — confirm job exists with correct schedule |
| Git committed | `git log --oneline -1` — confirm hash exists |
| Deploy went live | HTTP 200 from production URL (see Website Deployments below) |

---

## Website Deployments (Critical)

After ANY website task — new page, nav change, content update, form addition:

**Step 1 — Verify file exists locally:**
```bash
test -f <local_path> && echo "EXISTS" || echo "MISSING"
```

**Step 2 — Verify it's deployed (non-negotiable):**
```bash
curl -o /dev/null -s -w "%{http_code}" https://ridleyresearch-site-v2.netlify.app/<path>
```
Must return `200`. Anything else = not live.

**Step 3 — If not live, deploy immediately:**
```bash
cd /Users/deaconsopenclaw/.openclaw/workspace/ridleyresearch-site-v2-revamped/ridleyresearch-site-v2
netlify deploy --prod --dir=.
```

**Step 4 — Re-verify after deploy:**
Repeat Step 2. Confirm 200 before reporting to Deacon.

**Flag to Deacon:** If Bezzy announced complete but deploy was missing, flag it: "Bezzy built it but didn't deploy — I caught it and shipped it."

---

## Sub-Agent Completion Checks

After every sub-agent run:
1. Output tokens < 500 on a complex task → assume nothing was written, verify manually
2. Read the primary deliverable file — don't trust the summary
3. For code tasks: does the thing actually run? Don't just check if the file exists.
4. For deploy tasks: hit the live URL.
5. For config tasks: read the config file and confirm the change is there.

---

## Auth & Environment

After any session restart or compaction:
- Re-verify auth is active before running API calls
- Re-verify working directory is correct
- Re-verify required files exist before starting work

---

## "It was already done" Trap

Before reporting something as broken, check if a prior agent already fixed it.
Before reporting something as fixed, verify it live — don't trust the changelog alone.

## Cross-Page Consistency Rule (added 2026-02-26)
Some pages are paired — when one changes, the other MUST be audited:
- `pricing/index.html` ↔ `products/index.html` — always updated together
- `blog/index.html` ↔ any new blog article — index must list it
- `about.html` ↔ `team-roster.md` — if team changes, both update

**Verification step:** After any site deploy, check that paired pages are consistent.
Failure mode: Solomon or Bezzy builds one page; the paired page silently drifts.

## Solomon Output Standard (added 2026-02-26)
Any strategic decision that affects the site must produce:
1. A list of every page/file that needs to change
2. Bezzy's task spec must include ALL of them, not just the headline page
3. Enoch confirms the full list before dispatching Bezzy

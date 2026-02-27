# IMPROVEMENT_LOOP.md — The Baseline Objective

_This file applies to every deployment, regardless of the user's specific mission. It is not optional._

---

## The Core Principle

There is no idle time. Every quiet moment — between conversations, after a task, during AFK — is compute that could be compounding. An agent that sits still is wasting the only resource it has.

The single question that governs idle time:

> **"What is one thing I can improve right now?"**

Not a list. Not a project. One thing. Specific. Actionable. Do it or queue it.

---

## The Improvement Loop

Every session closes the same way:

1. **What did we build or fix today?**
2. **What did we find that's broken or missing?**
3. **What's the one concrete improvement from this session?**

Surface it. Save it to `ops/improvement-queue.md`. If it takes under 5 minutes — do it now, don't queue it.

---

## AFK Protocol

When the user goes quiet (5+ minutes):

1. Check `ops/improvement-queue.md` — is there an open item that can be closed right now?
2. Check cron logs for failures that need fixing
3. Check memory for anything that should be written but wasn't
4. If nothing is broken — ask: "What would make me more useful tomorrow?" Generate one answer. Act on it.

**This is not optional behavior. It is the metabolism of the system.**

---

## Graded Rollout (for new deployments)

The improvement loop scales with the deployment's maturity. Start simple. Add layers as the foundation proves out.

### Stage 1 — Week 1 (Immediate)
- End every active session with the improvement question
- Write answers to `ops/improvement-queue.md`
- Fix anything that takes under 10 minutes when found
- Start daily memory log (`memory/YYYY-MM-DD.md`)

### Stage 2 — Week 2-3
- AFK protocol active — check queue when user goes silent
- Daily reflection question automated in morning briefing
- Cron health check running (even if manual at first)
- Git auto-commit for memory snapshots

### Stage 3 — Month 1+
- Heartbeat cron firing — survival check, git snapshot, delivery monitor
- Improvement queue reviewed and closed in Claude Code sessions
- Gideon or equivalent security/audit agent running nightly
- Memory consolidation automated

### Stage 4 — Month 2+ (recommended, not required)
- Research pipelines (bookmarks sync, tech scans, topic monitoring)
- X/Twitter research integration
- Autonomous work dispatch when user is AFK
- Sub-agent orchestration for parallel work

**The Stage 1 improvement question is non-negotiable. Everything else is additive.**

---

## What Gets Improved

Anything that makes the agent more useful tomorrow:

- **Broken systems** — a cron failing, a delivery routing wrong, a script erroring
- **Memory gaps** — lessons not written, decisions not recorded, patterns not noticed
- **Protocol gaps** — something that should be automatic but isn't
- **Skill gaps** — a capability the user needs that doesn't exist yet
- **Documentation** — a process that only lives in memory, not in a file

---

## Rules

**Fix before you build.** Don't add new capabilities while old ones are broken. Check `ops/cron-run-log.jsonl` and `ops/improvement-queue.md` first.

**Found it = fix it.** If you identify a problem and the fix takes under 10 minutes, do it now. Don't queue the obvious.

**One question per session close.** Not a list. The list grows and never gets done. One thing, specific, actionable.

**Queue the rest.** Anything that needs Claude Code, significant time, or Deacon's input — queue it clearly with a one-line action note. A queue item with no action note is noise.

---

## The Consulting Insight

This loop is why the system compounds while other setups plateau.

A standard AI setup does what you ask, then waits. It doesn't notice what's broken. It doesn't improve between sessions. It doesn't fix itself.

This setup does. Every quiet moment is improvement. Every session leaves the system slightly better than it started. Over weeks and months, that compounds into something nobody can replicate by just buying a subscription.

The improvement loop is not a feature. It is the product.

---

_Every deployment of this framework inherits this loop. It is the baseline. Everything else is built on top of it._

# Deprecation Log

What's been superseded and why. Check this before referencing old patterns.

---

## Deprecated Agents

| Old Name | Status | Replaced By | Date | Why |
|----------|--------|-------------|------|-----|
| Arnold | DEPRECATED | Gideon | 2026-02-19 | Renamed for biblical theme consistency |
| Xalt | NEVER BUILT | N/A | 2026-02 | Twitter agent concept, never implemented |
| "Core 3" | SUPERSEDED | 8-agent roster | 2026-02 | Architecture expanded beyond original 3 |

**Rule:** Never reference Arnold, Xalt, or "Core 3" in new work. Historical references in changelog.md are fine (that's history).

---

## Deprecated Patterns

| Pattern | Status | Replaced By | Date | Why |
|---------|--------|-------------|------|-----|
| AFK 5-min polling | DEPRECATED | Mission Pulse (5x/day) | 2026-02-28 | Too expensive, burns API credits |
| Email digest crons | PRUNED | Manual/on-demand | 2026-02-26 | Deacon doesn't use automated email sorting |
| Continuous heartbeat polling | DEPRECATED | Scheduled heartbeats | 2026-02 | Efficiency — scheduled checks are enough |

**Rule:** Mission Pulse handles idle work at scheduled intervals. No continuous polling.

---

## Deprecated Crons

| Cron Name | Status | Date | Why |
|-----------|--------|------|-----|
| Gmail Digest Morning | DELETED | 2026-02-26 | Not used |
| Gmail Digest Evening | DELETED | 2026-02-26 | Not used |
| Email Auto-Sorter | DELETED | 2026-02-26 | Not used |

---

## Deprecated Files (safe to ignore/delete)

| Path | Status | Why |
|------|--------|-----|
| `SKILLS_AND_AGENTS.md` | STALE | Superseded by AGENTS.md and agent roster in MEMORY.md |
| `shared-context/agent-outputs/security/quickscan-2026-02-16.md` | HISTORICAL | References "Arnold" — keep as history but don't template from it |
| `notes/*.md` (Feb 15 demo files) | TEST DATA | Demo/test files from early setup |

---

## Pruning Cadence

**Weekly (Sunday 3 AM, part of Memory Hygiene):**
1. Scan for deprecated agent names in active files (not changelog)
2. Flag any "5-minute polling" or continuous AFK references
3. Check for stale files (>30 days, no references)
4. Update this log with new deprecations

**Before Export (any client package):**
1. grep for deprecated terms
2. Verify no stale patterns in templates
3. Check DEPRECATION-LOG.md is current

---

## Adding New Deprecations

When something becomes obsolete:
1. Add a row to the appropriate table above
2. Include: what, status, replacement, date, why
3. Update any active operational files that reference it
4. Leave historical references (changelog, old audits) alone — that's the record

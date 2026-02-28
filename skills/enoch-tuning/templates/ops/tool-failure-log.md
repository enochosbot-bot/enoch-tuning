# Tool Failure Log

## Purpose
Track tools, APIs, and approaches that don't work. Prevents agents from wasting tokens retrying dead ends.

---

## Format

| Tool/Approach | Date | What Failed | Root Cause | Workaround |
|---|---|---|---|---|
| [Name] | [YYYY-MM-DD] | [What you tried] | [Why it failed] | [Alternative, or "none"] |

---

## Current Failures

| Tool/Approach | Date | What Failed | Root Cause | Workaround |
|---|---|---|---|---|
| _example_ | 2026-02-01 | ACME API auth | API deprecated | Use ACME v2 instead |
| _example_ | 2026-02-15 | Browser skill on headless | Needs display | Use playwright with xvfb |

---

## Rules

1. **Add immediately** — when something fails after real effort (not typos)
2. **Include root cause** — "it didn't work" isn't useful. Why?
3. **Include workaround** — even if it's "wait for upstream fix"
4. **Review monthly** — some failures get fixed upstream
5. **Agent-readable** — write for future context, not just yourself

---

## When to Log

Log a failure when:
- You spent >10 minutes on something that doesn't work
- An API returns persistent errors (not transient 500s)
- A tool is fundamentally incompatible with the setup
- An approach is theoretically possible but impractical

Don't log:
- Typos or syntax errors
- Transient network failures
- User error (that's a lesson, not a tool failure)
- Things that worked but you didn't like

---

## Integration

Agents should check this file before:
- Attempting to use a tool for the first time
- Debugging a persistent failure
- Recommending an approach to the human

If a known failure is relevant, mention it: "Note: [tool] has a known issue with [X] — see tool-failure-log.md"

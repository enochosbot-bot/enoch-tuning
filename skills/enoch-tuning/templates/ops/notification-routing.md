# Notification Routing
Last Updated: [DATE]

## Rule
Every workflow has exactly ONE notification channel. No cross-posting unless escalating.

---

## Channel Assignment

| Workflow | Primary Channel | Escalation |
|---|---|---|
| Content review | Scribe channel | Security/Ops (on KILL only) |
| Security audits | Security/Ops channel | DM to human |
| Agent dispatch | General / DM | Security/Ops (if stalled >60min) |
| Cron results | Ops channel | DM if error |
| Research delivery | Research channel | — |
| Build/deploy | DM or Ops | — |

---

## Anti-Patterns

- ❌ Posting routine approvals to multiple channels
- ❌ Cross-posting "FYI" to security for non-security items
- ❌ Every agent announcing completion everywhere
- ❌ Duplicating the same status to DM + topic

## Pattern

- ✅ One channel owns each workflow
- ✅ Only escalate on error/kill/timeout
- ✅ Human DM is the escalation surface, not a routine channel
- ✅ Agents post to their assigned channel only

---

## Escalation Triggers

Post to Security/Ops or DM only when:
1. Task killed (not just revised)
2. Agent stalled >60 minutes
3. Cron job failed
4. Security incident detected
5. Explicit human request

---

## Why This Matters

Without this rule:
- Channels fill with noise
- Important signals get buried
- Human ignores notifications because 90% are FYI
- Agents waste tokens on redundant messages

With this rule:
- If it's in Security/Ops, it needs attention
- If it's a DM, it's urgent or blocked
- Everything else stays in its lane

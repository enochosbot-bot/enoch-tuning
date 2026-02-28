# Data Management

## Principle
Every piece of data has one canonical location. Know where things live. Back up what matters.

---

## Data Locations

### Identity & Behavior
| What | Location | Backed Up |
|---|---|---|
| Agent identity | `SOUL.md`, `IDENTITY.md` | Git |
| Operating rules | `AGENTS.md` | Git |
| User profile | `USER.md` | Git |
| Mission statement | `MISSION.md` | Git |

### Memory
| What | Location | Backed Up |
|---|---|---|
| Long-term ops facts | `MEMORY.md` (workspace) | Git |
| Typed memory | `~/Documents/Brain/Personal Memories/[Agent]/` | Obsidian Sync / Drive |
| Daily logs | `~/Documents/Brain/Personal Memories/[Agent]/Daily Logs/` | Obsidian Sync / Drive |
| Vault index | `~/Documents/Brain/Personal Memories/[Agent]/VAULT_INDEX.md` | Obsidian Sync / Drive |

### Operational
| What | Location | Backed Up |
|---|---|---|
| Cron definitions | `ops/cron-definitions.json` | Git |
| In-flight tasks | `ops/in-flight.md` | Git |
| Production queue | `ops/production-queue.md` | Git |
| Dispatch routing | `ops/dispatch-routing.md` | Git |
| Verification protocol | `ops/verification-protocol.md` | Git |

### Shared Context
| What | Location | Backed Up |
|---|---|---|
| Draft content | `shared-context/drafts/` | Git (transient) |
| Review feedback | `shared-context/feedback/` | Git (transient) |
| Session checkpoints | `shared-context/checkpoints/` | Not backed up |
| Priorities | `shared-context/priorities.md` | Git |

### Research
| What | Location | Backed Up |
|---|---|---|
| Research output | `~/Documents/Brain/Research/[topic]/` | Obsidian Sync / Drive |
| Staging area | `workspace/research/` | Git (transient) |
| People notes | `~/Documents/Brain/Personal Memories/[Agent]/People/` | Obsidian Sync / Drive |

### Credentials (sensitive)
| What | Location | Backed Up |
|---|---|---|
| API keys | `~/.zshrc` or keychain | Manual only |
| OAuth tokens | `~/.openclaw/` or skill-specific | Never (re-auth) |
| OpenClaw config | `~/.openclaw/openclaw.json` | Manual only |

---

## Backup Strategy

### Automatic
1. **Git** — workspace committed after significant changes
2. **Obsidian Sync** — if configured, handles vault continuously
3. **Google Drive** — `OpenClaw-Backups/` folder, synced via cron

### Manual (do these)
- Export `openclaw.json` before major config changes
- Export cron definitions: `openclaw cron export > backup-cron.json`
- Snapshot API keys somewhere secure (1Password, encrypted note)

### Backup Cron (example)
```
# Every 6 hours — sync workspace to Drive
0 */6 * * * — Drive Backup
```

---

## Restore Procedures

### Lost workspace
```bash
git clone [repo] ~/.openclaw/workspace
# Re-run any setup scripts
# Re-auth OAuth flows (gog, X, YouTube)
```

### Lost Obsidian vault
- Restore from Obsidian Sync (if configured)
- Or restore from Drive backup
- Agent can function on MEMORY.md alone temporarily

### Lost cron definitions
```bash
openclaw cron import < backup-cron.json
# Or rebuild from ops/cron-registry.md (human-readable record)
```

### Lost API keys
- Re-generate from provider dashboards
- Update `~/.zshrc`
- Restart shell: `source ~/.zshrc`
- Restart gateway: `openclaw gateway restart`

---

## Sensitive Data Rules

1. **Never in plaintext memory:** phone numbers, SSNs, passwords, full API keys
2. **Redact before committing:** check git diff for sensitive strings
3. **Use [redacted] markers:** note that sensitive data exists, don't include it
4. **OAuth tokens:** re-auth is cheaper than secure storage

---

## The Canon Rule

> **Obsidian is the canon for memory. Workspace is the canon for operations.**

- If typed memory conflicts with MEMORY.md → Obsidian wins
- If ops docs conflict with cron-definitions.json → JSON wins
- If identity files conflict between sources → workspace wins

---

## Cleanup Schedule

| What | Frequency | Action |
|---|---|---|
| Git commit | After significant work | `git add -A && git commit` |
| Drive backup | Every 6 hours (cron) | Automatic |
| Obsidian prune | Weekly | Archive old daily logs |
| Staging cleanup | Weekly | Move research/ to Obsidian or delete |
| Checkpoint cleanup | Every 2 hours | Delete old completed checkpoints |

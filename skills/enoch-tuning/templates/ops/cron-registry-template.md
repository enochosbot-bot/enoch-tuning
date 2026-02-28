# Cron Registry

## Purpose
Human-readable record of all scheduled jobs. Source of truth is `cron-definitions.json` — this is the documentation layer.

---

## Active Jobs

| ID | Name | Schedule | Agent | Purpose |
|---|---|---|---|---|
| [uuid] | [Human name] | [cron expression] | [agent] | [What it does] |

---

## Schedule Reference

### Timing Patterns
| Pattern | Meaning |
|---|---|
| `0 * * * *` | Every hour on the hour |
| `*/5 * * * *` | Every 5 minutes |
| `0 8 * * *` | Daily at 8 AM |
| `0 3 * * 0` | Weekly Sunday at 3 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 9,12,15,18,21 * * *` | 5x daily at specific hours |

### Agent Assignment
- **main** — orchestration, briefs, human-facing
- **observer** — security, monitoring, maintenance
- **researcher** — data gathering, synthesis
- **basher** — QA, testing
- **coder** — builds, deploys (rare for cron)
- **scribe** — content scheduling (rare)

---

## Job Categories

### Daily Operations
| Name | Time | Agent | Purpose |
|---|---|---|---|
| Morning Brief | 8:00 AM | main | Daily summary to human |
| Daily Cost Report | 8:00 AM | observer | API spend tracking |
| Daily Quick Scan | 6:00 AM | observer | Security check |

### Continuous Monitoring
| Name | Interval | Agent | Purpose |
|---|---|---|---|
| Session Watchdog | Hourly | observer | Check for stuck sessions |
| Shorty Monitor | 5 min | main | Content pipeline check |

### Maintenance
| Name | Schedule | Agent | Purpose |
|---|---|---|---|
| Session Auto-Prune | Every 2 hours | observer | Clean old checkpoints |
| Nightly Maintenance | 3:00 AM | main | Cleanup, optimization |
| qmd Reindex | Every 4 hours | observer | Memory search index |

### Weekly
| Name | Day/Time | Agent | Purpose |
|---|---|---|---|
| Weekly Memory Hygiene | Sunday 3 AM | main | Archive, prune, consolidate |
| Weekly Full Audit | Sunday 8 AM | observer | Deep security scan |

---

## Adding a Job

```bash
openclaw cron add "<name>" "<schedule>" "<prompt>" --agent <agent>
```

Then update this file with the new entry.

---

## Removing a Job

```bash
openclaw cron rm <id>
```

Then remove from this file.

---

## Export/Import

```bash
# Backup
openclaw cron export > ops/cron-backup.json

# Restore
openclaw cron import < ops/cron-backup.json
```

---

## Troubleshooting

### Job not running
1. Check `openclaw cron list` for status
2. Look for `error` status — check logs
3. Verify agent is configured
4. Check timezone (all times in local TZ)

### Job running but failing
1. Check the job's prompt — is it clear?
2. Check agent boundaries — can this agent do this task?
3. Look at recent session logs for errors

### Too many jobs
- Consolidate related tasks into single jobs
- Use idle-time behavior instead of polling crons
- Delete jobs that aren't providing value

---

## Cost Awareness

Every cron job = tokens spent. Consider:
- **5-minute crons:** ~288 runs/day — make them cheap
- **Hourly crons:** 24 runs/day — can be more substantial
- **Daily crons:** 1 run/day — can be thorough

Use cheaper models (observer on Sonnet) for monitoring crons.
Reserve expensive models for jobs that need judgment.

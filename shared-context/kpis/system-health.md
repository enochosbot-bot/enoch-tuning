# System Health Dashboard
_Updated: 2026-02-27 15:02 CST_

## Snapshot
- **Gateway uptime:** PID `91784` • running `02:13:42` • started `Fri Feb 27 12:48:58 2026`
- **Active session count:** `32` sessions indexed across agent stores
- **Workspace disk usage:** `4.0G` (`/Users/deaconsopenclaw/.openclaw/workspace`)
- **Cron success rate (last 24h):** `66.7%` (12 pass / 6 fail; total considered: 18)
- **Latest session update seen:** `2026-02-27 15:02 CST`

## Agent Activity (last 24h)
_Proxy metric: sessions with `updatedAt` in the last 24h._

| Agent | Active Sessions (24h) |
|---|---:|
| basher | 3 |
| coder | 9 |
| creative | 3 |
| main | 6 |
| observer | 4 |
| researcher | 2 |
| scribe | 3 |
| solomon | 2 |

## Data Sources
- `openclaw gateway status` + `ps` (uptime)
- `~/.openclaw/agents/*/sessions/sessions.json` (session/activity)
- `ops/task-ledger.md` (`[cron]` entries in last 24h)
- `du -sh /Users/deaconsopenclaw/.openclaw/workspace` (workspace size)

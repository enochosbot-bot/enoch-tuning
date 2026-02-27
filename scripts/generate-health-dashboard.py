#!/usr/bin/env python3
import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACE = Path("/Users/deaconsopenclaw/.openclaw/workspace")
OPENCLAW_HOME = Path.home() / ".openclaw"
OUTPUT = WORKSPACE / "shared-context/kpis/system-health.md"
LEDGER = WORKSPACE / "ops/task-ledger.md"
SESSIONS_GLOB = OPENCLAW_HOME / "agents"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


def gateway_status():
    status = run(["openclaw", "gateway", "status"])
    m = re.search(r"Runtime: running \(pid (\d+),", status)
    pid = int(m.group(1)) if m else None
    if not pid:
        return {"pid": "unknown", "elapsed": "unknown", "started": "unknown"}

    elapsed = run(["ps", "-o", "etime=", "-p", str(pid)]).strip() or "unknown"
    started = run(["ps", "-o", "lstart=", "-p", str(pid)]).strip() or "unknown"
    return {"pid": pid, "elapsed": elapsed, "started": started}


def load_sessions():
    session_files = list(SESSIONS_GLOB.glob("*/sessions/sessions.json"))
    all_sessions = []
    per_agent_recent = defaultdict(int)
    cutoff_ms = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp() * 1000)

    for sf in session_files:
        agent = sf.parts[-3]
        try:
            data = json.loads(sf.read_text())
        except Exception:
            continue

        if isinstance(data, dict):
            items = data.items()
        elif isinstance(data, list):
            items = [(str(i), row) for i, row in enumerate(data)]
        else:
            items = []

        for key, row in items:
            if not isinstance(row, dict):
                continue
            updated = row.get("updatedAt")
            all_sessions.append((agent, key, updated))
            if isinstance(updated, (int, float)) and updated >= cutoff_ms:
                per_agent_recent[agent] += 1

    return all_sessions, per_agent_recent


def workspace_size_human() -> str:
    return run(["du", "-sh", str(WORKSPACE)]).split()[0]


def cron_success_24h():
    if not LEDGER.exists():
        return {"pass": 0, "fail": 0, "rate": "n/a", "total": 0}

    lines = LEDGER.read_text().splitlines()
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    pass_n = 0
    fail_n = 0

    for ln in lines:
        if "[cron]" not in ln:
            continue
        tm = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]", ln)
        if not tm:
            continue
        try:
            ts = datetime.strptime(tm.group(1), "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if ts < cutoff:
            continue

        if "[✅ done]" in ln:
            pass_n += 1
        elif "[❌ failed]" in ln or "[⏳ timeout]" in ln:
            fail_n += 1

    total = pass_n + fail_n
    rate = f"{(pass_n / total * 100):.1f}%" if total else "n/a"
    return {"pass": pass_n, "fail": fail_n, "rate": rate, "total": total}


def fmt_time(ms):
    if not isinstance(ms, (int, float)):
        return "unknown"
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")


def main():
    gw = gateway_status()
    sessions, agent_recent = load_sessions()
    cron = cron_success_24h()
    size = workspace_size_human()

    rows = []
    for agent in sorted(agent_recent):
        rows.append(f"| {agent} | {agent_recent[agent]} |")
    rows_md = "\n".join(rows) if rows else "| (none) | 0 |"

    active_count = len(sessions)
    newest = max((u for _, _, u in sessions if isinstance(u, (int, float))), default=None)

    md = f"""# System Health Dashboard
_Updated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}_

## Snapshot
- **Gateway uptime:** PID `{gw['pid']}` • running `{gw['elapsed']}` • started `{gw['started']}`
- **Active session count:** `{active_count}` sessions indexed across agent stores
- **Workspace disk usage:** `{size}` (`{WORKSPACE}`)
- **Cron success rate (last 24h):** `{cron['rate']}` ({cron['pass']} pass / {cron['fail']} fail; total considered: {cron['total']})
- **Latest session update seen:** `{fmt_time(newest)}`

## Agent Activity (last 24h)
_Proxy metric: sessions with `updatedAt` in the last 24h._

| Agent | Active Sessions (24h) |
|---|---:|
{rows_md}

## Data Sources
- `openclaw gateway status` + `ps` (uptime)
- `~/.openclaw/agents/*/sessions/sessions.json` (session/activity)
- `ops/task-ledger.md` (`[cron]` entries in last 24h)
- `du -sh {WORKSPACE}` (workspace size)
"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(md)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

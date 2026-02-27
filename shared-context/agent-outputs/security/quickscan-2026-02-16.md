# Arnold Quick Scan — 2026-02-16 06:00 CST

1) MEDIUM — New non-loopback listeners detected (drift from last audit)
- Evidence: `/usr/sbin/lsof -nP -iTCP -sTCP:LISTEN`
  - `Spotify (PID 47387) TCP *:49919 (LISTEN)`
  - `Spotify (PID 47387) TCP *:57621 (LISTEN)`
- Drift: Last full audit (2026-02-15) reported all listeners bound to loopback only.
- Risk: Service now reachable from LAN interfaces, increasing local network attack surface.

2) LOW — Tailscale still installed but control plane not connected (persistent drift)
- Evidence: `/opt/homebrew/bin/tailscale status` → `failed to connect to local Tailscale service; is Tailscale running?`
- Context: Tailscale app + system extension processes exist, but CLI health remains broken.
- Risk: Intended ngrok replacement path remains non-operational.

3) LOW — Partial visibility gap on host firewall packet filter state
- Evidence: `/sbin/pfctl -s info` → `/dev/pf: Permission denied`
- Impact: Could not verify current pf runtime state in this quick scan without elevated rights.
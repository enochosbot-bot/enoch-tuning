---
title: "OpenClaw Architecture Ideas"
tags: [openclaw, architecture, ideas]
category: Ideas
pinned: true
archived: false
created: 2026-02-15T10:25:00-06:00
modified: 2026-02-15T10:25:00-06:00
---

Think about separating the gateway into microservices:
- **Core router** — message routing and session management
- **Memory service** — handles all memory read/write
- **Skill executor** — sandboxed skill execution

This would make it easier to scale and test independently.

Also look into #websocket support for real-time updates.

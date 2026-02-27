---
title: "Tailscale Funnel over ngrok for tunneling"
date: 2026-02-15
category: decisions
priority: 🔴
tags: [networking, voice, infrastructure]
---
ngrok is fragile — dies on restart, gets new URLs. Tailscale Funnel gives a permanent stable URL. Nuke ngrok entirely once Tailscale is set up.

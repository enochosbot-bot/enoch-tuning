# Dispatch Routing
Last Updated: 2026-02-26
Owner: Enoch

## Rule
All coding, config, and build tasks → Bezzy (coder/Codex) via sessions_spawn.
Never attempt code changes from chat. Never override Bezzy's completed work.

---

## Task → Agent Routing

| Task Type | Agent | Notes |
|---|---|---|
| Code (new features, fixes, scripts) | Bezzy | Always |
| Website changes | Bezzy | Must include deploy + live URL check in brief |
| Config changes (openclaw.json, cron) | Bezzy | Never from chat |
| Gateway/model changes | Bezzy | Outage risk — never from chat |
| Security audits | Gideon | Nightly 3:30AM auto, or manual trigger |
| Research tasks | Berean | Web search, synthesis, daily briefs |
| Strategy questions | Solomon | Daily cron + on-demand |
| Content/writing | Ezra | Blog posts, social copy, docs |
| Image generation | Selah | Creative output |
| QA / testing | Basher | After Bezzy ships |
| Everything else | Enoch (main) | Handle directly |

---

## Bezzy Brief Requirements (mandatory)

Every Bezzy dispatch MUST include:

1. **Context** — relevant file paths, current state, what exists
2. **Explicit task list** — numbered, unambiguous
3. **Verification step** — exact commands to confirm it worked
4. **Deploy step (for site tasks)** — `netlify deploy --prod` + `curl` check for HTTP 200
5. **Changelog** — append to `ops/changelog.md`

### Site Task Mandatory Closing Block
Every website task brief must end with:
```
## Mandatory Final Steps
1. Run: netlify deploy --prod --dir=.
2. Verify live: curl -o /dev/null -s -w "%{http_code}" https://ridleyresearch-site-v2.netlify.app/<path>
3. Confirm 200 before marking done
4. Report the live URL back
```

---

## Mandatory Dispatch Protocol (ALL agents, every task)

### Before dispatching
1. Add a row to `ops/in-flight.md` → Active table (task name, agent, timestamp, expected window)
2. Include the Closing Block in every brief (see below)

### Closing Block (paste verbatim at end of every brief)
```
## Mandatory Close (do not skip)
When your work is fully done:
1. Update ops/in-flight.md — move your row from Active to Completed with result summary
2. Send a Telegram message to confirm completion:
   - channel: telegram
   - target: -1003772049875
   - threadId: "1"
   - message: "✅ [task name] — done. [1-sentence summary of what was shipped/produced]"
3. Do NOT mark done until both steps above are complete.
```

### After close
- Verify the Telegram ping arrived
- If agent went silent >60min: check sessions_history, then ping Deacon manually with status

---

---

## Enoch Oversight (after any Bezzy site task)

Before telling Deacon it's done:
1. Check the live URL returns 200
2. If not — deploy it, flag that Bezzy missed the step
3. Never report "live" based on local file existence alone

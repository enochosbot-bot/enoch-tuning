# Dispatch Routing
Last Updated: [DATE]
Owner: [Main Agent]

## Rule
All tasks route to the agent best suited for them. Never attempt work outside your domain.

---

## Task → Agent Routing

| Task Type | Agent | Notes |
|---|---|---|
| Code (new features, fixes, scripts) | Coder | Always |
| Website changes | Coder | Must include deploy + live URL check |
| Config changes (openclaw.json, cron) | Coder | Never from chat |
| Gateway/model changes | Coder | Outage risk — never from chat |
| Security audits | Observer | Scheduled or manual trigger |
| Research tasks | Researcher | Web search, synthesis, briefs |
| Strategy questions | Judgment Agent | Analysis, recommendations |
| Content/writing | Scribe | Blog posts, social copy, docs |
| Image generation | Creative | Visual output |
| QA / testing | Basher | After code ships |
| Everything else | Main | Handle directly |

---

## Brief Requirements (mandatory)

Every dispatch MUST include:

1. **Context** — relevant file paths, current state, what exists
2. **Explicit task list** — numbered, unambiguous
3. **Verification step** — exact commands to confirm it worked
4. **Deploy step (if applicable)** — command + verification
5. **Changelog entry** — append to `ops/changelog.md`

---

## Mandatory Dispatch Protocol

### Before dispatching
1. Add a row to `ops/in-flight.md` → Active table
2. Include the Closing Block in every brief (see below)

### Closing Block (paste verbatim at end of every brief)
```
## Mandatory Close (do not skip)
When your work is fully done:
1. Update ops/in-flight.md — move your row from Active to Completed
2. Send notification to confirm completion
3. Do NOT mark done until both steps above are complete.
```

### After close
- Verify completion notification arrived
- If agent silent >60min: check sessions_history, escalate manually

---

## In-Flight Tracker Format

```markdown
# In-Flight Tasks

## Active
| Task | Agent | Started | Expected |
|---|---|---|---|
| [Name] | [agent] | [timestamp] | [window] |

## Completed (last 7 days)
| Task | Agent | Completed | Result |
|---|---|---|---|
| [Name] | [agent] | [timestamp] | [1-line outcome] |
```

---

## Main Agent Oversight

Before reporting any sub-agent task as done:
1. Check the live result (URL, file, output)
2. If verification failed — fix or flag that agent missed the step
3. Never report "done" based on agent's claim alone

---

## Anti-Patterns

- ❌ Dispatching to wrong agent (code to scribe, research to coder)
- ❌ Briefs without verification steps
- ❌ Marking done without in-flight update
- ❌ Trusting agent completion without verification
- ❌ Attempting code/config from chat

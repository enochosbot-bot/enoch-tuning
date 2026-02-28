# Model Selection Guide

## Quick Reference

| Task Type | Model | Why |
|---|---|---|
| Orchestration, DM, complex reasoning | Opus | Full context, best judgment |
| Research, writing, analysis | Sonnet | Good balance of quality and cost |
| Code, builds, scripts | Codex/Sonnet | Optimized for code, free tier |
| Routine ops, cron, monitoring | Sonnet | Cost-efficient for structured tasks |
| Bulk processing, simple transforms | Haiku/Flash | Cheapest, fast enough |

---

## Model Tiers

### Tier 1: Full Power (Opus)
- Complex multi-step reasoning
- Sensitive external communications
- Judgment calls with consequences
- Orchestrating other agents
- Direct human interaction (DMs)

**Cost:** ~$15/$75 per million tokens (input/output)

### Tier 2: Workhorse (Sonnet)
- Research and synthesis
- Long-form writing
- Code review and refactoring
- Analysis and recommendations
- Most sub-agent work

**Cost:** ~$3/$15 per million tokens

### Tier 3: Code-Optimized (Codex)
- New feature development
- Bug fixes and refactoring
- Script creation
- Build and deploy tasks
- File transformations

**Cost:** Free tier available, or Sonnet pricing

### Tier 4: Bulk/Simple (Haiku/Flash)
- Data extraction
- Format conversion
- Simple summarization
- High-volume, low-complexity tasks

**Cost:** ~$0.25/$1.25 per million tokens

---

## Agent-Model Assignments

| Agent | Default Model | Override When |
|---|---|---|
| Main (Enoch) | Opus | Never — always Opus |
| Researcher (Berean) | Sonnet | — |
| Scribe (Ezra) | Sonnet | — |
| Coder (Bezzy) | Codex | Complex architecture → Sonnet |
| Observer (Gideon) | Sonnet | Security audit → consider Opus |
| Basher (Nehemiah) | Sonnet | — |
| Solomon | Sonnet | High-stakes decisions → Opus |
| Creative (Selah) | Sonnet | — |

---

## Cost Awareness Rules

1. **Estimate before multi-step operations** — if >$0.50, ask first
2. **Batch operations** — don't make 10 calls when 1 will do
3. **Local over API** — file ops, grep, jq before LLM processing
4. **Right-size the model** — don't use Opus for data formatting
5. **Monitor daily costs** — daily cost report catches runaway spend

---

## When to Override

**Upgrade to higher tier:**
- Task is failing due to reasoning limits
- Output quality is critical (external publication)
- Security implications require careful judgment

**Downgrade to lower tier:**
- Task is repetitive/mechanical
- Output is internal-only
- Processing large volumes
- Cost is becoming an issue

---

## Setting Model Overrides

```bash
# Per-session override
/model sonnet

# Check current model
/status

# Reset to default
/model default
```

In agent configs:
```json
{
  "agents": {
    "researcher": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

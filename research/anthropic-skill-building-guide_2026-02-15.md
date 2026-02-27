---
title: "Anthropic Official Guide to Building Skills for Claude"
date: 2026-02-15
category: research
priority: 🟡
tags: [claude, skills, anthropic, reference]
---

## Source
https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

## Key Concepts

### What's a Skill?
A folder containing:
- **SKILL.md** (required) — instructions in markdown with YAML frontmatter
- **scripts/** (optional) — executable code
- **references/** (optional) — docs loaded as needed
- **assets/** (optional) — templates, fonts, icons

### Progressive Disclosure (3 levels)
1. **YAML frontmatter** — always loaded in system prompt. Tells Claude when to use the skill.
2. **SKILL.md body** — loaded when Claude thinks the skill is relevant.
3. **Linked files** — Claude discovers only as needed.
This minimizes token usage while maintaining expertise.

### Three Skill Categories
1. **Document & Asset Creation** — consistent output (docs, designs, code, presentations)
2. **Workflow Automation** — multi-step processes with validation gates
3. **MCP Enhancement** — workflow guidance on top of MCP tool access

### File Structure Rules
- SKILL.md must be exactly `SKILL.md` (case-sensitive)
- Folder names: kebab-case only (`notion-project-setup`)
- No README.md inside skill folder
- No XML tags in frontmatter (security — appears in system prompt)
- No "claude" or "anthropic" in skill name (reserved)

### YAML Frontmatter (Critical)
```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```
Description MUST include: what it does + when to use it (trigger conditions). Under 1024 chars.

### Writing Good Skills
- **Be specific about triggers** — include phrases users actually say
- **Embed domain knowledge** — don't just call tools, teach Claude HOW to use them well
- **Quality checklists** — validate before finalizing output
- **Iterative refinement loops** — build in self-review

### Success Criteria
- Skill triggers on 90% of relevant queries
- Completes workflow in expected tool calls
- 0 failed API calls per workflow
- Users don't need to prompt about next steps
- Consistent results across sessions

### Testing Approach
- Run 10-20 test queries that should trigger the skill
- Same request 3-5 times for consistency
- Compare with/without skill for improvement
- Monitor tool call counts and token consumption

### Distribution
- GitHub repo with repo-level README (for humans)
- SKILL.md stays inside the skill folder (for Claude)
- Use skill-creator skill to scaffold new skills interactively

## Applicability to Us
- Our SOUL.md / AGENTS.md follow these principles already
- Telegram topic system prompts are essentially lightweight skills
- If we build custom skills for Spectrum or content pipeline, follow this structure
- The progressive disclosure pattern (frontmatter → body → linked files) is smart for token efficiency

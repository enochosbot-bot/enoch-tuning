# Anthropic Skill Building Guide — Key Takeaways

Source: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

## Skill Structure
```
skill-name/           # kebab-case, no spaces/caps/underscores
├── SKILL.md          # Required (exact case)
├── scripts/          # Optional executables
├── references/       # Optional docs (loaded on demand)
└── assets/           # Optional templates, fonts, icons
```
- NO README.md inside skill folder
- SKILL.md must have YAML frontmatter with `---` delimiters
- No XML angle brackets in frontmatter
- No "claude" or "anthropic" in skill names

## YAML Frontmatter
```yaml
---
name: kebab-case-name        # required, must match folder
description: What + When + Triggers  # required, <1024 chars
license: MIT                 # optional
metadata:                    # optional
  author: Name
  version: 1.0.0
---
```

### Description Formula
`[What it does] + [When to use it] + [Key capabilities]`
- Include specific trigger phrases users would say
- Mention relevant file types
- Bad: "Helps with projects" / Good: "Manages Linear workflows including sprint planning. Use when user mentions 'sprint', 'Linear tasks', 'project planning'"

## Progressive Disclosure (3 levels)
1. **YAML frontmatter** — always in system prompt, minimal
2. **SKILL.md body** — loaded when skill seems relevant
3. **Linked files** (references/) — loaded only when needed

## Three Skill Categories
1. **Document & Asset Creation** — consistent output (designs, docs, code)
2. **Workflow Automation** — multi-step processes with validation gates
3. **MCP Enhancement** — workflow guidance on top of tool access

## Key Patterns
1. **Sequential Workflow** — explicit step ordering, dependencies, validation at each stage, rollback on failure
2. **Multi-MCP Coordination** — clear phase separation, data passing between services, validate before next phase
3. **Iterative Refinement** — draft → quality check → refinement loop → finalization
4. **Context-Aware Tool Selection** — decision trees based on context, fallback options
5. **Domain-Specific Intelligence** — embed expertise, compliance before action, audit trails

## Testing Checklist
- Triggering tests (does it load when it should? not load when it shouldn't?)
- Functional tests (correct outputs, API calls succeed, edge cases)
- Performance comparison (with vs without skill)

## Best Practices
- Be specific and actionable in instructions
- Include error handling
- Use progressive disclosure (keep SKILL.md under 5,000 words)
- Code > language for critical validations (scripts are deterministic)
- Put critical instructions at the TOP
- Iterate on a single task first, then expand

## Troubleshooting
- **Under-triggering**: Add more trigger phrases to description
- **Over-triggering**: Add negative triggers, be more specific
- **Instructions not followed**: Too verbose, buried, or ambiguous — simplify and prioritize
- **Large context issues**: Move docs to references/, limit enabled skills

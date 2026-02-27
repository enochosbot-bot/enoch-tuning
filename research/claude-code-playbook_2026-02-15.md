# Claude Code Playbook — SWE Best Practices
_Source: CTO with 7 years at Amazon/Disney/Capital One, now building enterprise agents_
_Date: 2026-02-15_

## Core Principles

### 1. Think First, Type Second
- Plan mode (Shift+Tab twice) before every task
- 10/10 times, planned output beats unplanned
- Architecture before implementation, always
- Even small tasks benefit from thinking first

### 2. CLAUDE.md (Our AGENTS.md/SOUL.md Equivalent)
- First thing Claude reads every session — shapes all behavior
- **Keep it short** — ~150-200 instructions max (system prompt uses ~50)
- **Be specific to YOUR project** — not generic docs
- **Tell it WHY, not just what** — "strict mode because we had prod bugs from implicit any" > "use strict mode"
- **Update constantly** — # key auto-adds instructions; if you correct twice, it belongs in the file
- Bad = documentation for a new hire. Good = notes for yourself with amnesia.

### 3. Context Window Management
- **Quality degrades at 20-40% usage**, not 100%
- Compaction doesn't restore quality — model was already degraded
- **One conversation per feature/task** — don't bleed contexts
- **External memory** — write plans to files (SCRATCHPAD.md, plan.md) that persist across sessions
- **Copy-paste reset trick**: copy important stuff → /compact → /clear → paste back only what matters
- **Claude is stateless** — every conversation starts from nothing except what you explicitly give it

### 4. Prompting
- Specific > vague. Constraints > open-ended. Examples > descriptions.
- Tell it what NOT to do — Claude tends to overengineer
- Give context about WHY — "runs on every request" vs "prototype we'll throw away" changes approach
- **Bad input == bad output** — if output sucks, input sucked. Always.

### 5. Model Routing
- **Opus** = complex reasoning, planning, architectural decisions
- **Sonnet** = execution, boilerplate, refactoring, clear-path implementation
- Workflow: Opus plans → Sonnet implements (Shift+Tab to switch)

### 6. When Stuck
- Don't loop — if you've explained 3 times, more explaining won't help
- /clear and start fresh (counterintuitively better 9/10 times)
- Simplify the task — break into smaller pieces
- Show instead of tell — write a minimal example, let Claude pattern-match
- Reframe the problem — different angle can unlock progress

### 7. Build Systems, Not One-Shots
- `-p` flag = headless mode (scriptable, pipeable)
- Chain with bash, integrate into workflows
- Auto PR reviews, ticket responses, documentation updates
- Flywheel: mistake → review logs → improve CLAUDE.md → better next time
- This compounds over months

## Key Quotes
- "Bad CLAUDE.md looks like documentation for a new hire. Good CLAUDE.md looks like notes you'd leave yourself if you knew you'd have amnesia tomorrow."
- "Output is everything, but it only comes from input."
- "If you're only using Claude interactively, you're leaving value on the table."

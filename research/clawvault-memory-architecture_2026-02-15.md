# ClawVault Memory Architecture — Analysis
_Source: Versatly blog post / article_
_Date: 2026-02-15_

## Core Concept
Markdown files + YAML frontmatter + wiki-links = agent memory that's also an Obsidian vault. No cloud, no proprietary DB.

## Key Finding
Plain markdown files (74.0%) outperformed specialized memory tools (68.5%) on LoCoMo benchmark. LLMs already know how to work with files.

## Architecture

### Typed Memories
Every memory gets a type: decision, preference, relationship, commitment, lesson, project, handoff.
Folder structure mirrors types: `decisions/`, `people/`, `lessons/`, `projects/`, `commitments/`, `preferences/`, `handoffs/`

### YAML Frontmatter
```yaml
title: "Architecture Decision: Event-Driven Pipeline"
date: 2026-02-12
category: decisions
memoryType: decision
priority: 🔴
tags: [architecture, pipeline, backend]
```

### Wiki-Links / Knowledge Graph
`[[entity-name]]` links inside notes. `clawvault link --all` auto-detects entity mentions.
Graph is navigable — agent traverses links to find related decisions, people, commitments.

### Observational Memory (compression)
Priority-tagged observations from conversations:
- 🔴 Critical — decisions, commitments, blockers
- 🟡 Notable — insights, preferences, context
- 🟢 Background — routine updates, low-signal

Budget-aware context injection: load 🔴 first, fill with 🟡, then 🟢.
Compression via LLM (Gemini Flash) + regex-based priority enforcement after.

### Vault Index
Single file listing every note + one-line description. Agent scans index FIRST before deciding what to read. More efficient than embedding search for most queries.

## What's Worth Adopting
1. **Typed memory folders** — restructure memory/ into decisions/, people/, lessons/, etc.
2. **YAML frontmatter** — add metadata to memory files for structured queries
3. **Vault index** — single index file for quick lookup (complements QMD)
4. **Priority tagging** — 🔴🟡🟢 on memories for budget-aware loading

## What We Can Skip
- **Observational memory** — article itself notes they're "not convinced" they need it
- **Wiki-links** — nice but QMD semantic search already covers associative retrieval
- **ClawVault npm package** — we can implement the pattern ourselves without the dependency

## Install
```bash
npm install clawvault
```
GitHub: https://github.com/Versatly/clawvault
Docs: https://clawvault.dev

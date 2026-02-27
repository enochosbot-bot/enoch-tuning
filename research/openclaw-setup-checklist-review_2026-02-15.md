# OpenClaw Setup Checklist Review
**Date:** 2026-02-15
**Source:** cigar-tom's OpenClaw setup checklist (Telegram)

## Tier 1 — Install Immediately
- **Tirith** — terminal security, homograph/ANSI injection defense. `brew install sheeki03/tap/tirith` → ✅ Installed
- **QMD** — local semantic search over docs. BM25 + vector + reranking, all on-device. MCP server built in. → ✅ Installed

## Tier 2 — Crypto/Finance
- **BankrBot Skills** — drop-in OpenClaw skills for DeFi, Polymarket, token launches, onchain messaging. github.com/BankrBot/openclaw-skills
- **Dexter** — autonomous financial research agent. Live market data, self-validates analysis. github.com/virattt/dexter
- **Solana Dev Skill** — official Solana Foundation skill. Anchor, Pinocchio, testing, security. github.com/solana-foundation/solana-dev-skill
- **Allium AgentHub** — free API, 150+ chain data. Same infra as Phantom/Coinbase. agents.allium.so

## Tier 3 — Situational
- **exo** — local AI cluster across multiple Macs. RDMA over Thunderbolt 5. github.com/exo-explore/exo
- **Matrix Agents** — multi-agent coordination over self-hosted Matrix. github.com/zscole/matrix-agents
- **X Research Skill** — Twitter API research. github.com/rohunvora/x-research-skill → ✅ Installed
- **Schematron-3B** — HTML→JSON extraction model. huggingface.co/inference-net/Schematron-3B → API key saved, model not yet in endpoint
- **YouTube-to-Doc** — video→doc converter. github.com/Solomonkassa/Youtube-to-Doc → ✅ Installed

## Dead Links / Skip
- **last30days-skillModels** — 404, repo doesn't exist
- **Font Stealer** — decorative, low value
- **Qwen3-TTS** — needs GPU for local voice cloning

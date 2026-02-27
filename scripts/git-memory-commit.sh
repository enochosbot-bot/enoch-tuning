#!/usr/bin/env bash
# git-memory-commit.sh
# Auto-commits any changes in the workspace AND openclaw config repo to git
# with a timestamped message. Run via cron or manually after significant
# memory/file writes. Safe to run frequently — exits silently if nothing changed.

set -euo pipefail

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# ─────────────────────────────────────────────────────────────────────────────
# REPO 1 — workspace (~/.openclaw/workspace)
# ─────────────────────────────────────────────────────────────────────────────
WORKSPACE="/Users/deaconsopenclaw/.openclaw/workspace"

if [ -d "$WORKSPACE/.git" ]; then
  cd "$WORKSPACE"

  # Stage known safe paths only
  git add \
    memory/ \
    research/ \
    CONSTITUTION.md \
    SOUL.md \
    MEMORY.md \
    MISSION.md \
    AGENTS.md \
    ops/ \
    skills/ \
    shared-context/ \
    scripts/ \
    agents/ \
    skills-lock.json \
    .agents/ \
    2>/dev/null || true

  # Commit only if something is staged
  if ! git diff --staged --quiet; then
    CHANGED_FILES=$(git diff --staged --name-only | head -10 | tr '\n' ' ')
    git commit -m "auto: memory snapshot ${TIMESTAMP}

Files: ${CHANGED_FILES}
" --no-verify 2>/dev/null
    git push origin HEAD --no-verify 2>/dev/null || true
    echo "✓ [workspace] Committed and pushed at ${TIMESTAMP}"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# REPO 2 — openclaw config (~/.openclaw)
# ─────────────────────────────────────────────────────────────────────────────
OPENCLAW_DIR="/Users/deaconsopenclaw/.openclaw"

if [ -d "$OPENCLAW_DIR/.git" ]; then
  cd "$OPENCLAW_DIR"

  # Stage safe config files only — gitignore handles the exclusions
  git add \
    openclaw.json \
    exec-approvals.json \
    node.json \
    gateway-launcher.sh \
    cron/jobs.json \
    agents/ \
    scripts/ \
    shared/ \
    .gitignore \
    2>/dev/null || true

  # Commit only if something is staged
  if ! git diff --staged --quiet; then
    CHANGED_FILES=$(git diff --staged --name-only | head -10 | tr '\n' ' ')
    git commit -m "auto: openclaw config snapshot ${TIMESTAMP}

Files: ${CHANGED_FILES}
" --no-verify 2>/dev/null
    git push origin HEAD --no-verify 2>/dev/null || true
    echo "✓ [openclaw-config] Committed and pushed at ${TIMESTAMP}"
  fi
fi

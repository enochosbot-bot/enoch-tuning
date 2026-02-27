#!/usr/bin/env bash
# social-post-pipeline.sh — BL-005
#
# Cron-ready wrapper for the social post approval pipeline.
# Picks next unreviewed post from shared-context/drafts/ and
# sends it to Deacon via Telegram for approval.
#
# USAGE:
#   ./scripts/social-post-pipeline.sh [--dry-run] [--verbose]
#
# CRON EXAMPLE (run daily at 9am Central — adjust to server timezone):
#   0 9 * * * cd /Users/deaconsopenclaw/.openclaw/workspace && \
#     SOCIAL_APPROVAL_TARGET=@deacon \
#     ./scripts/social-post-pipeline.sh >> /tmp/social-pipeline.log 2>&1
#
# ENV VARS:
#   SOCIAL_APPROVAL_TARGET  — Telegram chat ID or @username (required unless --dry-run)
#   DRAFT_DIR               — Override draft directory (default: shared-context/drafts)
#   LOG_FILE                — Override log file path (default: scripts/social-pipeline-log.jsonl)

set -euo pipefail

# Resolve script dir so cron can call this from any working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Defaults (can be overridden by env)
DRAFT_DIR="${DRAFT_DIR:-${WORKSPACE_DIR}/shared-context/drafts}"
LOG_FILE="${LOG_FILE:-${SCRIPT_DIR}/social-pipeline-log.jsonl}"
TARGET="${SOCIAL_APPROVAL_TARGET:-}"

# Pass through --dry-run / --verbose if provided
EXTRA_ARGS=()
for arg in "$@"; do
  EXTRA_ARGS+=("$arg")
done

# Run the pipeline
exec python3 "${SCRIPT_DIR}/social-post-pipeline.py" \
  --draft-dir "${DRAFT_DIR}" \
  --log-file  "${LOG_FILE}" \
  ${TARGET:+--target "${TARGET}"} \
  "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}"

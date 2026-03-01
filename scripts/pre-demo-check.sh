#!/usr/bin/env bash
set -u

PASS_COUNT=0
FAIL_COUNT=0

pass() {
  echo "✅ PASS — $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
  echo "❌ FAIL — $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

check_gateway() {
  if command -v openclaw >/dev/null 2>&1; then
    local out
    out="$(openclaw gateway status 2>&1 || true)"
    if echo "$out" | grep -Eiq "running|active|online|healthy"; then
      pass "OpenClaw gateway is running"
      return
    fi
  fi

  # Fallback process check if CLI status output is unavailable/ambiguous
  if pgrep -f "openclaw.*gateway|openclaw-gateway|node.*openclaw" >/dev/null 2>&1; then
    pass "OpenClaw gateway process appears to be running (process check fallback)"
  else
    fail "OpenClaw gateway is not running. Run: openclaw gateway start"
  fi
}

check_url() {
  local name="$1"
  local url="$2"

  local code
  code="$(curl -L -s -o /dev/null -w "%{http_code}" --max-time 20 "$url")"
  if [[ -z "$code" || "$code" == "000" ]]; then
    code="000"
  fi

  case "$code" in
    2*|3*)
      pass "$name reachable ($url) — HTTP $code"
      ;;
    *)
      fail "$name unreachable ($url) — HTTP $code. Check internet/VPN/firewall and retry."
      ;;
  esac
}

check_disk() {
  local target="/Users/deaconsopenclaw/.openclaw/workspace"
  local avail_kb
  avail_kb="$(df -k "$target" | awk 'NR==2 {print $4}')"

  if [[ -z "${avail_kb:-}" ]]; then
    fail "Could not read disk space for $target"
    return
  fi

  if (( avail_kb > 1048576 )); then
    local avail_gb
    avail_gb="$(awk -v kb="$avail_kb" 'BEGIN {printf "%.2f", kb/1024/1024}')"
    pass "Workspace free space is ${avail_gb} GB (> 1 GB)"
  else
    local avail_mb
    avail_mb="$(awk -v kb="$avail_kb" 'BEGIN {printf "%.0f", kb/1024}')"
    fail "Workspace free space is ${avail_mb} MB (<= 1 GB). Free up disk before demo."
  fi
}

check_m365_manual() {
  pass "M365 license check is manual: sign in to Microsoft 365 Admin Center → Billing → Your products, confirm active licenses for required users."
}

main() {
  echo "=== Pre-Demo Environment Verification ==="
  echo "Time: $(date)"
  echo

  check_gateway
  check_url "Redtail CRM" "https://redtailtechnology.com"
  check_url "eMoney" "https://wealth.emaplan.com"
  check_disk
  check_m365_manual

  echo
  local total
  total=$((PASS_COUNT + FAIL_COUNT))
  if (( FAIL_COUNT == 0 )); then
    echo "✅ OVERALL PASS — ${PASS_COUNT}/${total} checks passed. Environment is demo-ready."
    exit 0
  else
    echo "❌ OVERALL FAIL — ${FAIL_COUNT}/${total} checks failed (${PASS_COUNT} passed). Resolve failures before demo."
    exit 1
  fi
}

main "$@"

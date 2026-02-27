#!/bin/bash
# enforce-env-secret-scrub.sh — Enforced env secret scrub guardrail
# Fails (exit 1) if plaintext secrets are found in shell rc/profile files,
# LaunchAgent plists, workspace config files, or rclone config.
# Part of the Secret Hygiene Lockdown (2026-02-26).
# Updated 2026-02-26: Added rclone.conf scan and case-insensitive INI/TOML coverage.

set -euo pipefail

VIOLATIONS=0
REPORT_LINES=()

HOME_DIR="/Users/deaconsopenclaw"

# Files to scan
SHELL_FILES=(
  "$HOME_DIR/.zshrc"
  "$HOME_DIR/.zprofile"
  "$HOME_DIR/.bashrc"
  "$HOME_DIR/.bash_profile"
)

PLIST_DIR="$HOME_DIR/Library/LaunchAgents"
CONFIG_DIR="$HOME_DIR/.openclaw"

# Denylist regex: catches export VAR=<literal_value> patterns for secret-like names
# Matches lines like: export SOME_KEY=actualvalue or <string>secretvalue</string> after a KEY/TOKEN key
DENYLIST_PATTERN='(API_KEY|TOKEN|SECRET|PASSWORD|BEARER)='

# Allowlist: patterns that are safe (Keychain lookups, empty values, placeholders, comments)
is_allowlisted() {
  local line="$1"
  # Lines that use security find-generic-password (Keychain lookup)
  [[ "$line" =~ security[[:space:]]find-generic-password ]] && return 0
  # Lines that are comments
  [[ "$line" =~ ^[[:space:]]*# ]] && return 0
  # Lines with __FROM_KEYCHAIN__ placeholder
  [[ "$line" =~ __FROM_KEYCHAIN__ ]] && return 0
  # Lines with empty value: export KEY= or export KEY=""
  [[ "$line" =~ =[[:space:]]*$ ]] && return 0
  [[ "$line" =~ =\"\"$ ]] && return 0
  [[ "$line" =~ =\'\'$ ]] && return 0
  # Lines that use $(  ) command substitution (dynamic lookup)
  [[ "$line" =~ =.*\$\( ]] && return 0
  return 1
}

scan_file() {
  local file="$1"
  local lineno=0
  [ -f "$file" ] || return 0
  while IFS= read -r line; do
    lineno=$((lineno + 1))
    # Check if line matches denylist
    if echo "$line" | grep -qE "$DENYLIST_PATTERN"; then
      # Check if it's allowlisted
      if ! is_allowlisted "$line"; then
        VIOLATIONS=$((VIOLATIONS + 1))
        REPORT_LINES+=("VIOLATION: $file:$lineno: $line")
      fi
    fi
  done < "$file"
}

scan_plist_for_secrets() {
  local file="$1"
  [ -f "$file" ] || return 0
  local in_env_block=0
  local prev_was_key=0
  local prev_key=""
  local lineno=0
  while IFS= read -r line; do
    lineno=$((lineno + 1))
    # Track EnvironmentVariables dict
    if echo "$line" | grep -q '<key>EnvironmentVariables</key>'; then
      in_env_block=1
      continue
    fi
    if [ $in_env_block -eq 1 ]; then
      # Check for secret-like keys followed by string values
      if echo "$line" | grep -qE '<key>.*(API_KEY|TOKEN|SECRET|PASSWORD|BEARER).*</key>'; then
        prev_was_key=1
        prev_key=$(echo "$line" | sed 's/.*<key>//;s/<\/key>.*//')
        continue
      fi
      if [ $prev_was_key -eq 1 ] && echo "$line" | grep -q '<string>'; then
        local val=$(echo "$line" | sed 's/.*<string>//;s/<\/string>.*//')
        if [ -n "$val" ] && [ "$val" != "__FROM_KEYCHAIN__" ] && [ "$val" != "" ]; then
          VIOLATIONS=$((VIOLATIONS + 1))
          REPORT_LINES+=("VIOLATION: $file:$lineno: plaintext value for $prev_key")
        fi
        prev_was_key=0
        continue
      fi
      prev_was_key=0
    fi
  done < "$file"
}

# --- Scan shell files ---
for f in "${SHELL_FILES[@]}"; do
  scan_file "$f"
done

# --- Scan LaunchAgent plists ---
if [ -d "$PLIST_DIR" ]; then
  for f in "$PLIST_DIR"/*.plist; do
    [ -f "$f" ] || continue
    scan_plist_for_secrets "$f"
  done
fi

# --- Scan gateway.env (should be empty/stub) ---
if [ -f "$CONFIG_DIR/gateway.env" ]; then
  scan_file "$CONFIG_DIR/gateway.env"
fi

# --- Scan workspace config files ---
for f in "$CONFIG_DIR"/*.json "$CONFIG_DIR"/*.yml "$CONFIG_DIR"/*.yaml "$CONFIG_DIR"/*.toml; do
  [ -f "$f" ] || continue
  scan_file "$f"
done

# --- Scan rclone config (INI-style: key = value with no export keyword) ---
# Denylist: case-insensitive matches for secret-like key names in INI format
# Safe: lines starting with # (comments) or values that are empty
scan_ini_file() {
  local file="$1"
  local lineno=0
  [ -f "$file" ] || return 0
  while IFS= read -r line; do
    lineno=$((lineno + 1))
    # Skip comments and blank lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    # Check for INI-style key = value with secret-like names (case insensitive)
    if echo "$line" | grep -qiE '^[[:space:]]*(access_key_id|secret_access_key|api_key|api_secret|token|password|bearer)[[:space:]]*=[[:space:]]*\S'; then
      # Flag it - no allowlist for INI secrets (rclone.conf should have no raw values)
      VIOLATIONS=$((VIOLATIONS + 1))
      REPORT_LINES+=("VIOLATION: $file:$lineno: $line")
    fi
  done < "$file"
}

RCLONE_CONF="$HOME_DIR/.config/rclone/rclone.conf"
scan_ini_file "$RCLONE_CONF"

# --- Scan other ~/.config secret-bearing files ---
HIMALAYA_CONF="$HOME_DIR/.config/himalaya/config.toml"
# Himalaya uses cmd-based auth — scan INI-style for any raw password = value lines
scan_ini_file "$HIMALAYA_CONF"

# --- Check plist permissions ---
PLIST_FILE="$HOME_DIR/Library/LaunchAgents/ai.openclaw.gateway.plist"
if [ -f "$PLIST_FILE" ]; then
  perms=$(stat -f '%OLp' "$PLIST_FILE")
  if [ "$perms" != "600" ]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT_LINES+=("VIOLATION: $PLIST_FILE: permissions are $perms (expected 600)")
  fi
fi

# --- Output ---
if [ $VIOLATIONS -gt 0 ]; then
  echo "SECRET SCRUB FAILED: $VIOLATIONS violation(s) found"
  for line in "${REPORT_LINES[@]}"; do
    echo "  $line"
  done
  exit 1
else
  echo "SECRET SCRUB PASSED: 0 violations found"
  exit 0
fi

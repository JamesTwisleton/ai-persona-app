#!/usr/bin/env bash
# setup-keys.sh — Interactively populate missing API keys in backend/.env

set -euo pipefail

ENV_FILE="$(dirname "$0")/backend/.env"
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
RESET='\033[0m'

open_browser() {
  local url="$1"
  if command -v open &>/dev/null; then
    open "$url"          # macOS
  elif command -v xdg-open &>/dev/null; then
    xdg-open "$url"      # Linux
  else
    echo -e "  ${YELLOW}Open manually:${RESET} $url"
  fi
}

# Read current value of a key from .env (returns empty string if missing/commented)
get_env_value() {
  local key="$1"
  grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d'=' -f2- || true
}

set_env_value() {
  local key="$1"
  local value="$2"

  if grep -qE "^#?\s*${key}=" "$ENV_FILE" 2>/dev/null; then
    # Replace existing line (commented or not)
    sed -i.bak "s|^#\?\s*${key}=.*|${key}=${value}|" "$ENV_FILE"
    rm -f "${ENV_FILE}.bak"
  else
    # Append
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

prompt_key() {
  local key="$1"
  local label="$2"
  local url="$3"
  local current
  current="$(get_env_value "$key")"

  if [[ -n "$current" ]]; then
    echo -e "${GREEN}✓${RESET} ${label} already set"
    return
  fi

  echo ""
  echo -e "${BOLD}${label}${RESET}"
  echo -e "  Opening ${CYAN}${url}${RESET}..."
  open_browser "$url"
  echo -n "  Paste your key: "
  read -r value
  if [[ -z "$value" ]]; then
    echo -e "  ${YELLOW}Skipped (left blank)${RESET}"
    return
  fi
  set_env_value "$key" "$value"
  echo -e "  ${GREEN}Saved.${RESET}"
}

# ============================================================

echo ""
echo -e "${BOLD}=== AI Focus Groups — API Key Setup ===${RESET}"
echo -e "Editing: ${CYAN}${ENV_FILE}${RESET}"
echo ""

if [[ ! -f "$ENV_FILE" ]]; then
  echo -e "${RED}Error:${RESET} $ENV_FILE not found. Copy .env.example first:"
  echo "  cp backend/.env.example backend/.env"
  exit 1
fi

# --- Anthropic ---
prompt_key \
  "ANTHROPIC_API_KEY" \
  "Anthropic API Key (Claude — OCEAN inference, mottos, conversations)" \
  "https://console.anthropic.com/settings/keys"

# --- OpenAI ---
prompt_key \
  "OPENAI_API_KEY" \
  "OpenAI API Key (DALL-E avatars + content moderation)" \
  "https://platform.openai.com/api-keys"

# Set OPENAI_API_KEY as DALLE_API_KEY and OPENAI_MODERATION_API_KEY too if not set
OPENAI_VAL="$(get_env_value "OPENAI_API_KEY")"
if [[ -n "$OPENAI_VAL" ]]; then
  [[ -z "$(get_env_value "DALLE_API_KEY")" ]] && set_env_value "DALLE_API_KEY" "$OPENAI_VAL"
  [[ -z "$(get_env_value "OPENAI_MODERATION_API_KEY")" ]] && set_env_value "OPENAI_MODERATION_API_KEY" "$OPENAI_VAL"
fi

# --- Google OAuth (in case it's missing) ---
prompt_key \
  "GOOGLE_CLIENT_ID" \
  "Google OAuth Client ID" \
  "https://console.cloud.google.com/apis/credentials"

prompt_key \
  "GOOGLE_CLIENT_SECRET" \
  "Google OAuth Client Secret" \
  "https://console.cloud.google.com/apis/credentials"

echo ""
echo -e "${BOLD}=== Done ===${RESET}"
echo ""
echo "To start the app:"
echo -e "  ${CYAN}docker-compose --profile frontend up${RESET}"
echo ""
echo "Then open: http://localhost:3000"
echo ""

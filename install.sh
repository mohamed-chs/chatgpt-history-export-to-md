#!/usr/bin/env bash
# Convoviz Installer for Linux/macOS
# https://github.com/mohamed-chs/chatgpt-history-export-to-md

set -euo pipefail

# Colors (disabled if not a terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    RED='' GREEN='' BLUE='' BOLD='' RESET=''
fi

info()    { echo -e "${BLUE}[INFO]${RESET} $1"; }
success() { echo -e "${GREEN}[OK]${RESET} $1"; }
error()   { echo -e "${RED}[ERROR]${RESET} $1" >&2; exit 1; }

# Check if a command exists
has_cmd() { command -v "$1" &>/dev/null; }

echo -e "\n${BOLD}Convoviz Installer${RESET}\n"

# Step 1: Install uv if missing
if has_cmd uv; then
    success "uv is already installed"
else
    info "Installing uv..."
    if has_cmd curl; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif has_cmd wget; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        error "curl or wget is required to install uv"
    fi
    
    # Source the updated PATH (uv installer adds to shell profile)
    export PATH="$HOME/.local/bin:$PATH"
    
    if has_cmd uv; then
        success "uv installed successfully"
    else
        error "uv installation failed. Please restart your terminal and try again."
    fi
fi

# Step 2: Install convoviz
info "Installing convoviz..."
uv tool install "convoviz[viz]"
success "convoviz installed successfully"

# Done
echo -e "\n${GREEN}${BOLD}Installation complete!${RESET}"
echo -e "\nTo start using convoviz, either:"
echo -e "  1. Restart your terminal, or"
echo -e "  2. Run: ${BOLD}source ~/.local/bin/env${RESET}"
echo -e "\nThen run ${BOLD}convoviz${RESET} to get started.\n"

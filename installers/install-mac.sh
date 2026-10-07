#!/usr/bin/env bash
# CodeGenZ installer (macOS / Linux)
#
#   curl -fsSL https://raw.githubusercontent.com/enderairstudio/CodeGenZ/main/installers/install-mac.sh | bash
#
# Clones the repo into ~/.codegenz, installs the Python compiler as a
# real `genz` command, and adds it to your PATH.

set -euo pipefail

REPO_URL="https://github.com/enderairstudio/CodeGenZ.git"
INSTALL_DIR="$HOME/.codegenz"

info()  { echo "==> $1"; }
fail()  { echo "error: $1" >&2; exit 1; }

command -v git >/dev/null 2>&1 || fail "git is required but not found. Install it and re-run."
command -v python3 >/dev/null 2>&1 || fail "python3 is required but not found. Install it and re-run."
command -v pip3 >/dev/null 2>&1 || fail "pip3 is required but not found (usually ships with python3)."

info "Installing CodeGenZ into $INSTALL_DIR"
rm -rf "$INSTALL_DIR"
git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" >/dev/null

info "Installing the genz CLI (pip --user)"
cd "$INSTALL_DIR/compiler-py"
if ! pip3 install --user -e . >/tmp/codegenz-pip.log 2>&1; then
  if grep -q "externally-managed-environment" /tmp/codegenz-pip.log; then
    # modern Homebrew/Debian Pythons refuse system-wide installs by
    # default (PEP 668); --user -e into our own prefix is safe to override
    pip3 install --user --break-system-packages -e . >/tmp/codegenz-pip.log 2>&1 \
      || fail "pip install failed, see /tmp/codegenz-pip.log"
  else
    fail "pip install failed, see /tmp/codegenz-pip.log"
  fi
fi

USER_BASE="$(python3 -m site --user-base)"
BIN_DIR="$USER_BASE/bin"

# figure out which rc file this shell actually reads
SHELL_NAME="$(basename "${SHELL:-bash}")"
case "$SHELL_NAME" in
  zsh)  RC_FILE="$HOME/.zshrc" ;;
  bash) RC_FILE="$HOME/.bashrc" ;;
  *)    RC_FILE="$HOME/.profile" ;;
esac

if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
  if ! grep -q "# codegenz" "$RC_FILE" 2>/dev/null; then
    { echo ""; echo "export PATH=\"$BIN_DIR:\$PATH\" # codegenz"; } >> "$RC_FILE"
    info "Added $BIN_DIR to PATH in $RC_FILE"
  fi
fi

echo ""
echo "CodeGenZ installed."
echo ""
echo "  Restart your terminal (or run: source $RC_FILE), then:"
echo "    genz build path/to/site.gz -o dist/"
echo ""
echo "  Examples live in: $INSTALL_DIR/examples"
echo "  Language reference: $INSTALL_DIR/docs/SYNTAX.md"

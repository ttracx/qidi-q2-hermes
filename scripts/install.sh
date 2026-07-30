#!/usr/bin/env bash
# Install Qidi Q2 tool into Hermes Agent
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
HERMES_DIR="${HERMES_HOME:-$HOME/.hermes/hermes-agent}"

echo "=== Qidi Q2 Hermes integration installer ==="
echo ""

# Find Hermes tools directory
TOOLS_DIR="$HERMES_DIR/tools"
if [ ! -d "$TOOLS_DIR" ]; then
    echo "ERROR: Cannot find Hermes tools directory at $TOOLS_DIR"
    echo "Make sure Hermes is installed (hermes --version)"
    exit 1
fi

echo "Hermes found at: $HERMES_DIR"

# Copy tool
echo "Installing tool..."
rm -rf "$TOOLS_DIR/qidi_q2"
cp -r "$REPO_DIR/tools/qidi_q2" "$TOOLS_DIR/qidi_q2"
echo "  Tool installed: $TOOLS_DIR/qidi_q2"

# Copy skill
SKILLS_DIR="${HERMES_SKILLS_HOME:-$HOME/.hermes/skills}"
mkdir -p "$SKILLS_DIR"
echo "Installing skill..."
rm -rf "$SKILLS_DIR/qidi-q2"
cp -r "$REPO_DIR/skills/qidi-q2" "$SKILLS_DIR/qidi-q2"
echo "  Skill installed: $SKILLS_DIR/qidi-q2"

# Test Python imports
echo ""
echo "Testing imports..."
python3 -c "
import sys
sys.path.insert(0, '$TOOLS_DIR')
from qidi_q2.client import MoonrakerClient
from qidi_q2.models import PrinterStatus
from qidi_q2 import status, printer, files, camera, system, monitor
print('  All imports OK')
"

if [ $? -ne 0 ]; then
    echo "ERROR: Python import test failed"
    exit 1
fi

# Test connection (optional)
HOST="${QIDI_Q2_HOST:-10.1.10.153}"
echo ""
echo "Testing connection to $HOST:7125..."
python3 -c "
from qidi_q2.client import MoonrakerClient
client = MoonrakerClient(host='$HOST')
if client.is_reachable():
    print('  ✓ Printer is ONLINE')
else:
    print('  ✗ Printer is OFFLINE (may need to power on)')
" 2>/dev/null || echo "  ⚠ Could not test connection"

echo ""
echo "=== Installation complete ==="
echo ""
echo "To enable the toolset in Hermes:"
echo "  hermes config set tools.enabled '[..., \"qidi_q2\"]'"
echo ""
echo "Or in an active session:"
echo "  /tools enable qidi_q2"
echo ""
echo "Quick test:"
echo "  hermes chat -q 'Check if my Qidi Q2 printer is online'"

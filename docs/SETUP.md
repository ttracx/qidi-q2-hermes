# Detailed Setup Guide

## Prerequisites

- Hermes Agent installed and configured (`hermes --version` shows a version)
- Qidi Q2 3D printer on the same network
- Printer's Moonraker API accessible (stock firmware exposes it on port 7125)
- Python 3.10+

## Step 1: Verify Moonraker is accessible

```bash
curl http://10.1.10.153:7125/server/info
```

Should return Moonraker server info JSON. If not:
- Check printer IP (may have DHCP'd a new one)
- Ensure printer is powered on
- Check network connectivity

## Step 2: Install the tool

### Option A: Copy into Hermes source (recommended)

```bash
cd ~/.hermes/hermes-agent
# Clone this repo
git clone https://github.com/ttracx/qidi-q2-hermes /tmp/qidi-q2-hermes
# Copy tool into Hermes tools directory
cp -r /tmp/qidi-q2-hermes/tools/qidi_q2 tools/
# Or use the installer script
bash /tmp/qidi-q2-hermes/scripts/install.sh
```

### Option B: Install as a Python package

```bash
pip install -e /tmp/qidi-q2-hermes
# Tool auto-registers via entry point
```

## Step 3: Register the toolset

Add `qidi_q2` to your enabled tools in `~/.hermes/config.yaml`:

```yaml
tools:
  enabled:
    - qidi_q2
```

Or enable dynamically in a session:
```
/tools enable qidi_q2
```

## Step 4: Configure the printer IP

### Method 1: Environment variable (recommended)

```bash
export QIDI_Q2_HOST="10.1.10.153"
```

Add to your shell profile for persistence.

### Method 2: Hermes config

```bash
hermes config set qidi_q2.host "10.1.10.153"
```

### Method 3: Default

If your printer is at the default IP `10.1.10.153`, no configuration needed.

## Step 5: Test the connection

```bash
hermes chat -q "Check if my Qidi Q2 printer is online"
```

Expected output:
```
Printer is ONLINE at 10.1.10.153:7125
```

## Step 6: Install the skill (for natural language)

```bash
# Copy skill into Hermes skills directory
cp -r /tmp/qidi-q2-hermes/skills/qidi-q2 ~/.hermes/skills/
# Or install via hermes CLI
hermes skills install /tmp/qidi-q2-hermes/skills/qidi-q2/SKILL.md --name qidi-q2
```

Now you can use natural language:
```
hermes chat -q "What's my printer status?"
hermes chat -q "Pause the print"
hermes chat -q "List G-code files"
```

## Step 7: Set up monitoring (optional)

### Print completion alerts

Create a cron job that checks every 5 minutes:

```bash
hermes cron create '*/5 * * * *' \
  --prompt 'Check Qidi Q2 alerts with qidi_q2_check_alerts. Report to user if any alerts found. Stay silent if none.' \
  --name qidi-alerts
```

### Temperature watchdog

```bash
hermes cron create '*/2 * * * *' \
  --prompt 'Check Qidi Q2 temperatures. Alert if hotend exceeds 300C or bed exceeds 120C. Stay silent if normal.' \
  --name qidi-temps
```

### Progress updates during print

```bash
hermes cron create '*/15 * * * *' \
  --prompt 'Check Qidi Q2 print progress. Report percentage and ETA if a print is active. Stay silent otherwise.' \
  --name qidi-progress
```

## Verifying Installation

Run the connection test:

```bash
python3 /tmp/qidi-q2-hermes/scripts/test_connection.py
```

Expected:
```
✓ Printer reachable at 10.1.10.153:7125
✓ Moonraker version: v0.9.x
✓ Klipper state: ready
✓ Hotend: 24.1°C / 0°C
✓ Bed: 24.3°C / 0°C
✓ No active print
All tests passed!
```

## Uninstalling

```bash
# Remove tool
rm -rf ~/.hermes/hermes-agent/tools/qidi_q2
# Remove skill
rm -rf ~/.hermes/skills/qidi-q2
# Remove from config.yaml tools.enabled list
```

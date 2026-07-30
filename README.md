# Hermes + Qidi Q2 3D Printer Integration

Full end-to-end integration between Hermes Agent and the Qidi Q2 3D printer. Control your printer via natural language — check status, start prints, monitor progress, capture timelapses, manage files, and receive proactive alerts.

Built on **Moonraker** (port 7125) + **Klipper** — the stock Qidi Q2 firmware exposes a complete Moonraker API that Hermes can call directly.

## Hardware

| Property | Value |
|----------|-------|
| Printer | Qidi Q2 (FLSUN OEM Board) |
| IP (default) | `10.1.10.153` |
| SSH | `linaro` / `linaro` (sudo NOPASSWD) |
| Moonraker API | `http://10.1.10.153:7125` |
| Klipper config | `/home/mks/qidi/qidi-k1/Klipper/` |
| OS | Armbian (linaro-alip) |

## Architecture

```
┌─────────────────────────────────────┐
│          Hermes Agent               │
│  ┌─────────┐  ┌──────────────────┐  │
│  │  Chat   │  │  qidi_q2 Tool   │  │
│  │  (You)  │  │  (Moonraker API) │  │
│  └─────────┘  └──────────────────┘  │
│         │              │            │
│    Gateway         Terminal        │
│  (Telegram/     (SSH to Qidi)     │
│   iMessage)                       │
└─────────────────────────────────────┘
         │
         ▼ HTTP :7125
┌─────────────────────────────────────┐
│         Qidi Q2 Printer             │
│  ┌──────────┐  ┌────────────────┐  │
│  │Moonraker │  │ Klipper (mks)  │  │
│  │  :7125   │◄─┤   firmware     │  │
│  └──────────┘  └────────────────┘  │
│         │                           │
│    ┌────▼────┐                      │
│    │ Toolhead│  Bed  Extruder      │
│    └─────────┘                      │
└─────────────────────────────────────┘
```

## Quick Start

### 1. Install the tool

```bash
# Clone this repo into your Hermes plugins
cd ~/.hermes/hermes-agent
git clone https://github.com/ttracx/qidi-q2-hermes.git /tmp/qidi-q2-hermes
cp -r /tmp/qidi-q2-hermes/tools/qidi_q2 tools/
```

### 2. Register the tool

Add to `~/.hermes/config.yaml`:

```yaml
tools:
  enabled:
    - qidi_q2
```

### 3. Install the skill

```bash
hermes skills install ttracx/qidi-q2-hermes/skills/qidi-q2/SKILL.md --name qidi-q2
```

### 4. Set the printer IP

```bash
hermes config set qidi_q2.host "10.1.10.153"
hermes config set qidi_q2.moonraker_port 7125
```

Or via environment variable:

```bash
export QIDI_Q2_HOST="10.1.10.153"
```

### 5. Use it

```
hermes chat -q "What's my Qidi Q2 printer status?"
hermes chat -q "Start printing benchy.gcode"
hermes chat -q "Show me the current print progress"
hermes chat -q "Pause the print"
hermes chat -q "Take a timelapse snapshot"
```

## Features

### Printer Status & Telemetry
- Full Klipper state machine status (ready / printing / paused / error / shutdown)
- Real-time temperature readings (hotend, bed, chamber)
- Fan speeds, print speed multiplier, flow rate
- Print duration, filament used, ETA
- Position tracking (X/Y/Z)

### Print Job Control
- Start / pause / resume / cancel prints
- Upload G-code files remotely
- Delete old G-code files
- List available print files
- Emergency stop (M112)

### File Management
- Upload G-code via Moonraker file API
- List files with metadata (size, estimated print time, layer count)
- Delete files remotely
- Download G-code files

### Camera / Timelapse
- Capture single snapshots
- Start/stop timelapse recording
- Download timelapse videos
- List available timelapses

### System Operations
- Reboot / shutdown printer board
- Restart Klipper firmware
- Restart Moonraker service
- SSH access for advanced diagnostics

### Proactive Monitoring (Cron)
- Scheduled print progress updates
- Print completion alerts
- Error/fault detection alerts
- Temperature anomaly warnings
- Filament runout detection (if sensor equipped)

## Repository Structure

```
qidi-q2-hermes/
├── tools/
│   └── qidi_q2/
│       ├── __init__.py          # Tool registration
│       ├── client.py            # Moonraker API client
│       ├── status.py            # Status & telemetry queries
│       ├── printer.py           # Print job control
│       ├── files.py             # G-code file management
│       ├── camera.py            # Camera & timelapse
│       ├── system.py            # System operations (reboot, restart)
│       ├── monitor.py           # Proactive monitoring helpers
│       └── models.py            # Data models / dataclasses
├── skills/
│   └── qidi-q2/
│       └── SKILL.md            # Hermes skill (auto-loads on print queries)
├── docs/
│   ├── SETUP.md                 # Detailed setup guide
│   ├── API.md                   # Moonraker API reference
│   ├── TROUBLESHOOTING.md       # Common issues & fixes
│   └── CRON.md                  # Monitoring cron job recipes
├── examples/
│   ├── status-check.py          # Standalone status check script
│   ├── print-monitor.py         # Full monitoring loop example
│   ├── upload-and-print.py      # Upload G-code and start print
│   └── cron-status.sh           # Shell script for cron status checks
└── scripts/
    ├── install.sh               # One-line installer
    └── test_connection.py       # Connection test utility
```

## Natural Language Commands

Once set up, these all work out of the box:

**Status:**
- "What's the printer doing?"
- "Is the print done yet?"
- "What temperature is the hotend?"
- "How much filament has been used?"

**Control:**
- "Pause the print"
- "Resume printing"
- "Cancel the current job"
- "Emergency stop the printer"
- "Set print speed to 150%"

**Files:**
- "List all G-code files on the printer"
- "Upload this G-code file and start printing"
- "Delete the old benchy.gcode"
- "How long will dragon.gcode take to print?"

**Camera:**
- "Take a photo of the print bed"
- "Start recording a timelapse"
- "Stop the timelapse and save it"

**Monitoring:**
- "Alert me when the print finishes"
- "Let me know if the printer errors"
- "Check the printer every 30 minutes"

## Safety

- Emergency stop (M112) requires explicit confirmation
- Delete operations require explicit confirmation
- Klipper restart requires explicit confirmation
- All temperatures clamped to printer limits
- Tool validates printer state before every action

## License

MIT - THOX.ai

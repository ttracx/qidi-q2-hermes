---
name: qidi-q2
description: Use when the user asks about their Qidi Q2 3D printer — status, control, monitoring, file management, camera, or troubleshooting.
version: 1.0.0
author: Hermes Agent + THOX.ai
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [3d-printing, qidi, q2, klipper, moonraker, iot]
    related_skills: [hermes-agent]
---

# Qidi Q2 3D Printer Skill

Use when the user asks about their Qidi Q2 3D printer — checking status, controlling prints, managing files, taking photos, or troubleshooting issues. This skill loads automatically when the user mentions their printer, prints, G-code, or 3D printing.

## Hardware Info

| Property | Value |
|----------|-------|
| Printer | Qidi Q2 |
| Board | FLSUN OEM (linaro-alip) |
| Default IP | `10.1.10.153` |
| SSH | `linaro` / `linaro` (sudo NOPASSWD) |
| Moonraker | Port 7125 |
| Klipper | `/home/mks/qidi/qidi-k1/Klipper/` |
| OS | Armbian Linux |

## Quick Reference

### Status Queries
- "What's the printer status?" → `qidi_q2_status`
- "What temp is the hotend?" → `qidi_q2_temperatures`
- "How's the print going?" → `qidi_q2_print_progress`
- "Is the printer online?" → `qidi_q2_online`

### Print Control
- "Start printing X" → `qidi_q2_print_start` with filename
- "Pause" → `qidi_q2_print_pause`
- "Resume" → `qidi_q2_print_resume`
- "Cancel" → `qidi_q2_print_cancel` (confirm first!)
- "E-stop" → `qidi_q2_emergency_stop` (confirm first!)

### Tuning
- "Speed up" → `qidi_q2_set_speed` (e.g. 150%)
- "More flow" → `qidi_q2_set_flow` (e.g. 105%)
- "Set hotend to X" → `qidi_q2_set_temperature` heater=hotend
- "Fan to X%" → `qidi_q2_set_fan`
- "Home" → `qidi_q2_home`

### Files
- "What files are on the printer?" → `qidi_q2_files_list`
- "Delete X" → `qidi_q2_delete_file` (confirm first!)
- "How big is X?" → `qidi_q2_file_info`
- "Filament for X?" → `qidi_q2_filament_estimate`
- "Upload and print" → `qidi_q2_upload_and_print`

### Camera
- "Take a photo" → `qidi_q2_snapshot`
- "Timelapses?" → `qidi_q2_timelapses`

### System
- "Restart Klipper" → `qidi_q2_restart_klipper` (confirm first!)
- "SSH: uptime" → `qidi_q2_ssh`
- "Moonraker version?" → `qidi_q2_system_info`

### Monitoring
- "Any alerts?" → `qidi_q2_check_alerts`

## Common Pitfalls

1. **Printer offline**: Check `qidi_q2_online` first. If offline, verify IP/network. The printer may have gotten a new DHCP address — check the router or run `nmap -sn 10.1.10.0/24`.

2. **Emergency stop**: After M112, Klipper MUST be restarted. Use `qidi_q2_restart_klipper`, wait ~10s, then home axes before printing again.

3. **Upload fails**: Large G-code files may time out. The client uses 3x timeout for uploads. If it still fails, copy via SCP and SSH instead.

4. **"File not found" on print_start**: The filename must match exactly (case-sensitive). Run `qidi_q2_files_list` first to see exact filenames.

5. **Print progress shows 0%**: The printer just started — the first layer hasn't completed yet. Progress updates as layers complete.

6. **Camera shows nothing**: The Qidi Q2 camera is an optional add-on. If not installed, camera tools will return errors.

7. **SSH not working**: Ensure `sshpass` is installed (`brew install sshpass` on macOS) or SSH keys are configured between the Mac and printer.

8. **Moonraker API returns empty objects**: When Klipper is in `startup` or `shutdown` state, object data may be empty. Wait for `ready` state or use `qidi_q2_restart_klipper`.

## Workflow: Check Print Status

1. `qidi_q2_online` — verify connectivity
2. `qidi_q2_status` — get full picture
3. If printing: `qidi_q2_print_progress` for ETA
4. If issue: `qidi_q2_check_alerts` for warnings

## Workflow: Start a Print

1. `qidi_q2_files_list` — find the file
2. `qidi_q2_filament_estimate` — check if enough filament
3. `qidi_q2_status` — verify printer is ready (not already printing)
4. `qidi_q2_print_start` — start the print
5. `qidi_q2_snapshot` — take a first-layer photo to verify adhesion

## Workflow: Monitor Until Done

1. `qidi_q2_print_progress` — check current state
2. Use cronjob with `qidi_q2_check_alerts` to get notified on completion
3. Or create a monitoring loop (see examples/print-monitor.py)

## Cron Monitoring Recipes

### Print completion alert
```
cronjob(action='create', schedule='5m', prompt='Check Qidi Q2 printer alerts using qidi_q2_check_alerts. If there is a completion or error alert, tell the user immediately. If empty, do nothing.')
```

### Status check every 30 min during print
```
cronjob(action='create', schedule='30m', prompt='Check the Qidi Q2 print progress with qidi_q2_print_progress. Report the progress percentage, ETA, and any issues. Only report if a print is active.')
```

### Temperature watchdog (every 2 min)
```
cronjob(action='create', schedule='2m', prompt='Check Qidi Q2 temperatures with qidi_q2_temperatures. Alert if hotend exceeds 300C or bed exceeds 120C. Stay silent if normal.')
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QIDI_Q2_HOST` | `10.1.10.153` | Printer IP address |
| `QIDI_Q2_PORT` | `7125` | Moonraker API port |

## Integration with Hermes Config

Add to `~/.hermes/config.yaml`:

```yaml
tools:
  enabled:
    - qidi_q2
```

Or enable dynamically:

```python
# In a Hermes session
/tools enable qidi_q2
```

## SSH Access Pattern

The printer runs `sshd` on port 22. Default credentials: `linaro` / `linaro`.

For advanced operations (firmware updates, config changes):

```bash
# From terminal
ssh linaro@10.1.10.153 "sudo systemctl status klipper"

# Or via the tool
qidi_q2_ssh(command="sudo systemctl status klipper")
```

Klipper config directory: `/home/mks/qidi/qidi-k1/Klipper/`

# Troubleshooting

## Printer Offline / Cannot Connect

### Symptom
`Printer is OFFLINE` or `Cannot reach printer at 10.1.10.153:7125`

### Diagnosis
1. Check if printer is powered on (touch screen responsive?)
2. Check network: `ping 10.1.10.153`
3. Check if printer got a new IP: `nmap -sn 10.1.10.0/24` or check your router's DHCP table
4. Check if Moonraker is running on the printer: SSH in and run `systemctl status moonraker`

### Fix
- If new IP: update `QIDI_Q2_HOST` or `~/.hermes/config.yaml`
- If Moonraker crashed: `sudo systemctl restart moonraker` (SSH in)
- If whole system hung: power cycle the printer

## Printer Stuck in "shutdown" State

### Symptom
Status shows `SHUTDOWN`, can't start prints.

### Cause
Klipper encountered an error and shut down for safety (e.g. M112 emergency stop, thermal runaway protection).

### Fix
1. SSH in: `sh linaro@10.1.10.153` (password: `linaro`)
2. Check Klipper log: `tail -50 /tmp/klippy.log`
3. Identify and fix the root cause
4. Restart: `qidi_q2_restart_klipper`
5. Home axes: `qidi_q2_home`
6. Resume printing

## Print Starts But Immediately Cancels

### Symptom
`print_start` returns success but status immediately shows `cancelled`.

### Possible Causes
- File is corrupted or incompatible
- Printer needs homing first (some slicers require G28)
- Bed mesh not loaded

### Fix
1. Home the printer: `qidi_q2_home`
2. Check if file exists: `qidi_q2_files_list`
3. Verify the file was sliced for Qidi Q2 (not another printer)
4. Try uploading the file again

## Emergency Stop (M112) Executed

### Symptom
All motors stopped, no heating.

### Recovery
1. `qidi_q2_restart_klipper` — restart firmware
2. Wait ~10 seconds
3. `qidi_q2_home` — home all axes
4. Resume or start a new print

**IMPORTANT**: After E-stop, ALWAYS home before printing again.

## Upload Fails / Times Out

### Symptom
`Upload failed` or timeout during file upload.

### Diagnosis
Large G-code files (50MB+) may time out.

### Fix
1. Use SCP instead:
```bash
scp local_file.gcode linaro@10.1.10.153:/home/mks/gcode_files/
```
2. Or upload via the Qidi slicer's built-in network upload

## Temperatures Show 0°C

### Symptom
Hotend/bed temperatures show 0.0°C.

### Cause
Klipper is in `startup` or `shutdown` state and hasn't initialized thermistors yet.

### Fix
1. Wait for printer to reach `ready` state
2. If stuck: `qidi_q2_restart_klipper`

## Print Progress Shows 0% / Unknown ETA

### Symptom
Progress stays at 0%, ETA shows "unknown".

### Cause
Print just started — no layers completed yet.

### Fix
Wait a few minutes. Progress updates as layers complete.

## Camera Tools Return Errors

### Symptom
`snapshot` fails or returns empty data.

### Cause
Qidi Q2 camera is an optional accessory. Not all units have one.

### Fix
Check if camera is connected: SSH in and run `lsusb | grep -i camera` or `v4l2-ctl --list-devices`.
If no camera installed, camera tools won't work.

## SSH Connection Refused

### Symptom
`qidi_q2_ssh` returns connection errors.

### Diagnosis
1. Check SSH is running: `nmap 10.1.10.153 -p 22`
2. Check credentials (default: `linaro` / `linaro`)
3. Check network firewall

### Fix
- The printer's SSH server may restart on reboot. Try connecting manually first: `ssh linaro@10.1.10.153`
- If password changed, you need physical access or the Qidi app to reset

## Moonraker API Returns "Invalid JSON"

### Symptom
Tools returning `Invalid JSON response` errors.

### Cause
Moonraker version mismatch or corrupt response.

### Fix
1. Check Moonraker version: `qidi_q2_system_info`
2. Restart Moonraker: `qidi_q2_restart_moonraker`
3. Wait 10 seconds, then retry

## G-code File Not Found After Upload

### Symptom
`print_start` fails with "File not found" after upload.

### Cause
Moonraker may rename the file or place it in a subdirectory.

### Fix
1. `qidi_q2_files_list` — check exact filename
2. Use the exact filename (including path if in subdirectory) for `print_start`

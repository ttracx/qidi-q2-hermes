# Cron Monitoring Recipes

Schedule printer monitoring tasks using Hermes cron jobs. All these recipes use the `qidi_q2_check_alerts` tool which returns empty string when everything is fine (silent watchdog pattern).

## Print Completion Alert

Get notified within 5 minutes when a print finishes:

```
cronjob(
    action='create',
    name='qidi-print-complete',
    schedule='5m',
    prompt='Check the Qidi Q2 printer status using qidi_q2_check_alerts. If there is any alert (especially print completion, errors, or warnings), tell the user immediately with details. If the tool returns an empty string, do nothing — stay completely silent, just return HEARTBEAT_OK. Do not send a message if there are no alerts.',
    no_agent=True,
    script='qidi-q2-check-alerts.sh'
)
```

## Temperature Watchdog

Alert immediately if temperatures go critical:

```
cronjob(
    action='create',
    name='qidi-temp-watchdog',
    schedule='2m',
    prompt='Check Qidi Q2 temperatures with qidi_q2_check_alerts. If hotend exceeds 280°C while not printing, or bed exceeds 110°C, alert immediately. If print is active and temperatures are normal, stay silent. Any tool-returned alert should be forwarded to the user.'
)
```

## Print Progress Updates

Get progress updates every 15 minutes while printing:

```
cronjob(
    action='create',
    name='qidi-progress',
    schedule='15m',
    prompt='Check Qidi Q2 print progress with qidi_q2_print_progress. If a print is actively printing, report the current percentage, layer, elapsed time, and ETA. If no print is active (printer is ready/idle), stay silent. Only report when a print is actually running.'
)
```

## Daily Printer Health Check

Check printer health every morning:

```
cronjob(
    action='create',
    name='qidi-daily-health',
    schedule='0 8 * * *',
    prompt='Check the Qidi Q2 printer: is it online? Are there any errors? Check the temperatures. If everything is normal, report briefly "Printer OK, ready". If there are any issues, report them in detail.'
)
```

## Silent Pattern

The key to cron monitoring is the **silent-on-healthy** pattern:

1. `qidi_q2_check_alerts` returns empty string `""` when everything is normal
2. Use `no_agent=True` with a script that only prints when there's an alert
3. The cron job only delivers a message when stdout is non-empty
4. This prevents notification spam

### Script for silent monitoring

Create `~/.hermes/scripts/qidi-q2-alerts.sh`:

```bash
#!/bin/bash
# Silent alert check — only prints when there's something to report
python3 -c "
from tools.qidi_q2.client import MoonrakerClient
from tools.qidi_q2.monitor import check_alerts
result = check_alerts(MoonrakerClient())
if result:
    print(result)
"
```

## Managing Cron Jobs

```bash
# List all jobs
hermes cron list

# Pause monitoring (e.g. printer offline for maintenance)
hermes cron pause qidi-print-complete
hermes cron pause qidi-temp-watchdog

# Resume
hermes cron resume qidi-print-complete
hermes cron resume qidi-temp-watchdog

# Remove all Qidi jobs
hermes cron remove qidi-print-complete
hermes cron remove qidi-temp-watchdog
hermes cron remove qidi-progress
hermes cron remove qidi-daily-health
```

## Delivery Targets

By default, cron output goes to local logs. For notification delivery:

- **Telegram**: Add `deliver='telegram'` to the cronjob
- **iMessage**: Add `deliver='imessage'` (requires Photon setup)
- **Email**: Add `deliver='email'`

Example with delivery:
```
cronjob(
    action='create',
    name='qidi-urgent',
    schedule='2m',
    prompt='Check Qidi Q2 alerts. Report immediately if any error, completion, or overheat condition.',
    deliver='telegram'
)
```

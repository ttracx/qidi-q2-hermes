"""Proactive monitoring helpers for cron jobs."""

from __future__ import annotations

import json
import time
from typing import Optional

from .client import MoonrakerClient, MoonrakerError
from .models import PrinterStatus, parse_printer_status
from .status import get_status, get_print_progress


def monitor_print(
    interval: int = 60,
    max_wait: int = 14400,  # 4 hours
    on_complete: Optional[callable] = None,
    on_error: Optional[callable] = None,
    on_progress: Optional[callable] = None,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Monitor a print until completion, calling callbacks on state changes.

    Args:
        interval: Seconds between status checks.
        max_wait: Maximum seconds to monitor.
        on_complete: Called when print finishes (state=complete).
        on_error: Called on error state.
        on_progress: Called on each progress update.
        client: MoonrakerClient instance.

    Returns:
        Final status message.
    """
    client = client or MoonrakerClient()
    start = time.time()
    last_state = None

    while time.time() - start < max_wait:
        try:
            info = client.get_printer_info()
            state = info.get("state", "unknown")

            if state != last_state:
                if state == "complete" and on_complete:
                    on_complete()
                elif state == "error" and on_error:
                    on_error()
                last_state = state

            if state == "printing":
                objects = client.get_objects(["print_stats", "virtual_sdcard"])
                status = parse_printer_status({
                    "printer_info": info,
                    "objects": objects.get("status", {}),
                })
                if status.print_job and on_progress:
                    on_progress(status.print_job)

            if state in ("complete", "cancelled", "error"):
                return f"Print {state}"

        except MoonrakerError as e:
            return f"Lost connection to printer: {e}"

        time.sleep(interval)

    return f"Monitoring timeout after {max_wait}s"


def check_alerts(client: Optional[MoonrakerClient] = None) -> str:
    """Check for alert conditions. Returns empty string if all OK (silent watchdog).

    Alerts on:
    - Printer in error/shutdown state
    - Print complete
    - High temperature anomalies
    - Connection failure
    """
    client = client or MoonrakerClient()

    try:
        info = client.get_printer_info()
        state = info.get("state")

        if state == "error":
            return f"⚠️ PRINTER ERROR: {info.get('state_message', 'Unknown error')}"

        if state == "shutdown":
            return "⚠️ PRINTER SHUTDOWN: Klipper needs restart (FIRMWARE_RESTART)"

        # Check if print just completed
        if state == "ready":
            try:
                objects = client.get_objects(["print_stats"])
                stats = objects.get("status", {}).get("print_stats", {})
                if stats.get("state") == "complete":
                    filename = stats.get("filename", "unknown")
                    duration = stats.get("total_duration", 0)
                    h = int(duration // 3600)
                    m = int((duration % 3600) // 60)
                    return f"✅ Print complete: {filename} ({h}h {m:02d}m)"
            except MoonrakerError:
                pass

        # Check temperature anomalies
        try:
            objects = client.get_objects(["extruder", "heater_bed"])
            status = parse_printer_status({
                "printer_info": {},
                "objects": objects.get("status", {}),
            })

            if status.extruder and status.extruder.current > 300:
                return f"⚠️ HOTEND OVERHEAT: {status.extruder.current:.0f}°C (target: {status.extruder.target:.0f}°C)"

            if status.heater_bed and status.heater_bed.current > 120:
                return f"⚠️ BED OVERHEAT: {status.heater_bed.current:.0f}°C (target: {status.heater_bed.target:.0f}°C)"

        except MoonrakerError:
            pass

    except MoonrakerError as e:
        return f"⚠️ PRINTER OFFLINE: Cannot reach {client.host}:{client.port}"

    return ""  # Silent — no alerts

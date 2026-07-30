"""Printer status and telemetry queries."""

from __future__ import annotations

import json
from typing import Optional

from .client import MoonrakerClient, MoonrakerError
from .models import PrinterStatus, parse_printer_status


def get_status(client: Optional[MoonrakerClient] = None) -> str:
    """Get full printer status as human-readable text."""
    client = client or MoonrakerClient()

    try:
        info = client.get_printer_info()
        objects = client.get_objects([
            "extruder", "heater_bed", "fan", "heater_fan extruder_fan",
            "gcode_move", "print_stats", "virtual_sdcard", "toolhead",
            "motion_report", "temperature_sensor chamber",
        ])
        status = parse_printer_status({
            "printer_info": info,
            "objects": objects.get("status", {}),
        })
    except MoonrakerError as e:
        return json.dumps({
            "success": False,
            "error": str(e),
        })

    lines = []
    lines.append(f"Printer: {status.hostname or 'Qidi Q2'}")
    lines.append(f"Klipper: {status.klipper_version}")
    lines.append(f"State: {status.state.upper()}")
    if status.state_message:
        lines.append(f"Message: {status.state_message}")

    lines.append("")

    # Temperatures
    if status.extruder:
        t = status.extruder
        heat = " (heating)" if t.is_heating else " (at target)" if t.is_at_target else ""
        lines.append(f"Hotend:  {t}{heat} (power: {int(t.power * 100)}%)")
    if status.heater_bed:
        t = status.heater_bed
        heat = " (heating)" if t.is_heating else " (at target)" if t.is_at_target else ""
        lines.append(f"Bed:     {t}{heat} (power: {int(t.power * 100)}%)")
    if status.chamber:
        lines.append(f"Chamber: {status.chamber.current:.1f}°C")

    # Fans
    if status.fan:
        lines.append(f"Part fan: {status.fan.percent}%")
    if status.heater_fan:
        lines.append(f"Hotend fan: {status.heater_fan.percent}%")

    # Speed/flow
    if status.speed_factor != 1.0 or status.extrude_factor != 1.0:
        lines.append(f"Speed: {int(status.speed_factor * 100)}%  Flow: {int(status.extrude_factor * 100)}%")

    # Position
    if status.position:
        p = status.position
        lines.append(f"Position: X{p.x:.1f} Y{p.y:.1f} Z{p.z:.1f}")

    # Print job
    if status.print_job and status.print_job.is_active:
        job = status.print_job
        lines.append("")
        lines.append(f"Print: {job.filename}")
        lines.append(f"State: {job.state} — {job.percent}%")
        lines.append(f"Elapsed: {job.elapsed_str}  ETA: {job.eta_str}")
        if job.total_layers > 0:
            lines.append(f"Layer: {job.current_layer}/{job.total_layers}")
        if job.filament_used_mm > 0:
            lines.append(f"Filament: {job.filament_used_mm / 1000:.1f}m used")
    elif status.print_job and status.print_job.is_finished:
        job = status.print_job
        lines.append(f"Last print: {job.filename} — {job.state}")
        lines.append(f"Duration: {job.elapsed_str}")

    return "\n".join(lines)


def get_temperatures(client: Optional[MoonrakerClient] = None) -> str:
    """Get just temperature readings."""
    client = client or MoonrakerClient()
    try:
        objects = client.get_objects([
            "extruder", "heater_bed", "temperature_sensor chamber",
        ])
        status = parse_printer_status({
            "printer_info": client.get_printer_info(),
            "objects": objects.get("status", {}),
        })

        parts = []
        if status.extruder:
            parts.append(f"Hotend: {status.extruder}")
        if status.heater_bed:
            parts.append(f"Bed: {status.heater_bed}")
        if status.chamber:
            parts.append(f"Chamber: {status.chamber.current:.1f}°C")
        return " | ".join(parts) if parts else "No temperature data available"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def is_printing(client: Optional[MoonrakerClient] = None) -> bool:
    """Check if printer is currently printing."""
    client = client or MoonrakerClient()
    try:
        info = client.get_printer_info()
        return info.get("state") == "printing"
    except MoonrakerError:
        return False


def get_print_progress(client: Optional[MoonrakerClient] = None) -> str:
    """Get current print progress details."""
    client = client or MoonrakerClient()
    try:
        objects = client.get_objects(["print_stats", "virtual_sdcard"])
        status = parse_printer_status({
            "printer_info": {},
            "objects": objects.get("status", {}),
        })
        if not status.print_job:
            return "No active print job"

        job = status.print_job
        if not job.is_active:
            return f"Printer is {job.state}"

        lines = [
            f"File: {job.filename}",
            f"State: {job.state}",
            f"Progress: {job.percent}%",
            f"Elapsed: {job.elapsed_str}",
            f"Remaining: {job.eta_str}",
        ]
        if job.total_layers > 0:
            lines.append(f"Layer: {job.current_layer}/{job.total_layers}")
        if job.filament_used_mm > 0:
            lines.append(f"Filament used: {job.filament_used_mm / 1000:.1f}m")
        if job.message:
            lines.append(f"Message: {job.message}")
        return "\n".join(lines)
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def check_printer_online(client: Optional[MoonrakerClient] = None) -> str:
    """Check if the printer is reachable."""
    client = client or MoonrakerClient()
    if client.is_reachable():
        return f"Printer is ONLINE at {client.host}:{client.port}"
    return f"Printer is OFFLINE at {client.host}:{client.port}"

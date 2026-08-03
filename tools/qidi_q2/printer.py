"""Print job control operations."""

from __future__ import annotations

import json
import os
from typing import Optional

from .client import MoonrakerClient, MoonrakerError
from .models import parse_file_list


def start_print(
    filename: Optional[str] = None,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Start a print job.

    Args:
        filename: G-code file to print. If None, prints the currently loaded file.
        client: MoonrakerClient instance.
    """
    client = client or MoonrakerClient()
    try:
        if filename:
            # Verify file exists first
            files = client.list_files()
            gcodes = parse_file_list(files if isinstance(files, list) else [])
            if not any(f.filename == filename for f in gcodes):
                return json.dumps({
                    "success": False,
                    "error": f"File '{filename}' not found on printer. Use files_list to see available files.",
                })
            result = client.print_start(filename)
            return f"Started printing: {filename}"
        else:
            result = client.print_start()
            return "Started printing (current file)"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def pause_print(client: Optional[MoonrakerClient] = None) -> str:
    """Pause the current print job."""
    client = client or MoonrakerClient()
    try:
        client.print_pause()
        return "Print paused"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def resume_print(client: Optional[MoonrakerClient] = None) -> str:
    """Resume a paused print job."""
    client = client or MoonrakerClient()
    try:
        client.print_resume()
        return "Print resumed"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def cancel_print(client: Optional[MoonrakerClient] = None) -> str:
    """Cancel the current print job (cannot be undone)."""
    client = client or MoonrakerClient()
    try:
        client.print_cancel()
        return "Print cancelled"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def emergency_stop(client: Optional[MoonrakerClient] = None) -> str:
    """Emergency stop the printer (M112).

    WARNING: This halts all motors and heaters immediately.
    Requires Klipper firmware restart to recover.
    """
    client = client or MoonrakerClient()
    try:
        client.emergency_stop()
        return (
            "EMERGENCY STOP executed. All motors and heaters halted. "
            "Klipper firmware restart required before further printing. "
            "Use qidi_q2_restart_klipper to recover."
        )
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def upload_and_print(
    filepath: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Upload a G-code file and immediately start printing it.

    Args:
        filepath: Local path to the G-code file.
        client: MoonrakerClient instance.
    """
    client = client or MoonrakerClient()

    if not os.path.exists(filepath):
        return json.dumps({
            "success": False,
            "error": f"File not found: {filepath}",
        })

    filename = os.path.basename(filepath)

    try:
        # Upload
        result = client.upload_file(filepath)
        uploaded = result.get("item", {}).get("path", filename)

        # Start print
        client.print_start(uploaded)
        return f"Uploaded {filename} and started printing"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def set_print_speed(
    percent: int,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Set print speed override percentage (M220).

    Args:
        percent: Speed percentage (50-200 typical range).
    """
    client = client or MoonrakerClient()
    if not 50 <= percent <= 200:
        return json.dumps({
            "success": False,
            "error": "Print speed must be between 50% and 200%.",
        })
    try:
        client.gcode(f"M220 S{percent}")
        return f"Print speed set to {percent}%"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def set_flow_rate(
    percent: int,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Set extrusion flow rate percentage (M221).

    Args:
        percent: Flow percentage (90-110 typical range).
    """
    client = client or MoonrakerClient()
    if not 90 <= percent <= 110:
        return json.dumps({
            "success": False,
            "error": "Flow rate must be between 90% and 110%.",
        })
    try:
        client.gcode(f"M221 S{percent}")
        return f"Flow rate set to {percent}%"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def set_temperature(
    heater: str,
    temperature: int,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Set heater target temperature.

    Args:
        heater: 'hotend' or 'bed'.
        temperature: Target temperature in °C.
    """
    client = client or MoonrakerClient()
    normalized_heater = heater.lower()
    limits = {"hotend": 300, "extruder": 300, "bed": 120}
    if normalized_heater not in limits:
        return json.dumps({
            "success": False,
            "error": f"Unknown heater: {heater}. Use 'hotend' or 'bed'.",
        })
    if not 0 <= temperature <= limits[normalized_heater]:
        return json.dumps({
            "success": False,
            "error": (
                f"{normalized_heater} temperature must be between 0°C and "
                f"{limits[normalized_heater]}°C."
            ),
        })
    try:
        if normalized_heater in ("hotend", "extruder"):
            client.gcode(f"M104 S{temperature}")
            return f"Hotend target set to {temperature}°C"
        elif normalized_heater == "bed":
            client.gcode(f"M140 S{temperature}")
            return f"Bed target set to {temperature}°C"
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown heater: {heater}. Use 'hotend' or 'bed'.",
            })
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def set_fan_speed(
    percent: int,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Set part cooling fan speed (M106).

    Args:
        percent: Fan speed 0-100%.
    """
    client = client or MoonrakerClient()
    if not 0 <= percent <= 100:
        return json.dumps({
            "success": False,
            "error": "Fan speed must be between 0% and 100%.",
        })
    try:
        speed = int(percent * 255 / 100)  # Convert % to PWM value
        client.gcode(f"M106 S{speed}")
        return f"Part fan set to {percent}%"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def home_axes(
    axes: str = "XYZ",
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Home printer axes (G28).

    Args:
        axes: 'XYZ' to home all, or specific axes like 'X', 'Y', 'Z', 'XY'.
    """
    client = client or MoonrakerClient()
    normalized_axes = axes.upper()
    if normalized_axes not in {"X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"}:
        return json.dumps({
            "success": False,
            "error": "Axes must be a non-repeating combination of X, Y, and Z.",
        })
    try:
        if normalized_axes == "XYZ":
            client.gcode("G28")
            return "Homing all axes (XYZ)"
        else:
            client.gcode(f"G28 {normalized_axes}")
            return f"Homing {normalized_axes}"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def move_axis(
    axis: str,
    distance: float,
    speed: int = 3000,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Move an axis by relative distance (G91 + G1 + G90).

    Args:
        axis: 'X', 'Y', 'Z', or 'E' (extruder).
        distance: Distance in mm (negative for reverse).
        speed: Feedrate in mm/min.
    """
    client = client or MoonrakerClient()
    try:
        client.gcode(f"G91\nG1 {axis.upper()}{distance} F{speed}\nG90")
        return f"Moved {axis.upper()} by {distance}mm at {speed}mm/min"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def run_gcode(
    script: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Execute arbitrary G-code commands.

    Args:
        script: G-code commands (one per line).
    """
    client = client or MoonrakerClient()
    try:
        client.gcode(script)
        return f"Executed G-code:\n{script}"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})

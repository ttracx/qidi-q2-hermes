"""Qidi Q2 printer tool registration for Hermes Agent.

Registers all qidi_q2_* tools with the Hermes tool registry.
Auto-discovered by Hermes via tools/*.py scan.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from .client import MoonrakerClient, MoonrakerError
from . import status, printer, files, camera, system, monitor


def _check_qidi_q2() -> bool:
    """Check if Qidi Q2 host is configured."""
    host = os.getenv("QIDI_Q2_HOST", MoonrakerClient.DEFAULT_HOST)
    return bool(host)


def _get_client() -> MoonrakerClient:
    return MoonrakerClient()


# -- Status Tools --

def qidi_q2_status(task_id: str = None) -> str:
    """Get full printer status: state, temperatures, print progress, position."""
    return status.get_status(_get_client())


def qidi_q2_temperatures(task_id: str = None) -> str:
    """Get current temperature readings for hotend, bed, and chamber."""
    return status.get_temperatures(_get_client())


def qidi_q2_print_progress(task_id: str = None) -> str:
    """Get detailed progress of the current print job."""
    return status.get_print_progress(_get_client())


def qidi_q2_online(task_id: str = None) -> str:
    """Check if the Qidi Q2 printer is reachable."""
    return status.check_printer_online(_get_client())


# -- Print Control Tools --

def qidi_q2_print_start(filename: str = "", task_id: str = None) -> str:
    """Start printing a G-code file. If no filename, prints currently loaded file."""
    return printer.start_print(filename or None, _get_client())


def qidi_q2_print_pause(task_id: str = None) -> str:
    """Pause the current print job."""
    return printer.pause_print(_get_client())


def qidi_q2_print_resume(task_id: str = None) -> str:
    """Resume a paused print job."""
    return printer.resume_print(_get_client())


def qidi_q2_print_cancel(task_id: str = None) -> str:
    """Cancel the current print job. Cannot be undone."""
    return printer.cancel_print(_get_client())


def qidi_q2_emergency_stop(task_id: str = None) -> str:
    """Emergency stop the printer (M112). Halts all motors and heaters immediately. Requires firmware restart."""
    return printer.emergency_stop(_get_client())


# -- Tuning Tools --

def qidi_q2_set_speed(percent: int, task_id: str = None) -> str:
    """Set print speed override (M220). Range: 50-200%."""
    return printer.set_print_speed(percent, _get_client())


def qidi_q2_set_flow(percent: int, task_id: str = None) -> str:
    """Set extrusion flow rate (M221). Range: 90-110%."""
    return printer.set_flow_rate(percent, _get_client())


def qidi_q2_set_temperature(heater: str, temperature: int, task_id: str = None) -> str:
    """Set heater target temperature. Heater: 'hotend' or 'bed'."""
    return printer.set_temperature(heater, temperature, _get_client())


def qidi_q2_set_fan(percent: int, task_id: str = None) -> str:
    """Set part cooling fan speed (M106). Range: 0-100%."""
    return printer.set_fan_speed(percent, _get_client())


def qidi_q2_home(axes: str = "XYZ", task_id: str = None) -> str:
    """Home printer axes (G28). Axes: 'XYZ', 'X', 'Y', 'Z', 'XY'."""
    return printer.home_axes(axes, _get_client())


def qidi_q2_move(axis: str, distance: float, speed: int = 3000, task_id: str = None) -> str:
    """Move an axis by relative distance. Use caution — no bounds checking."""
    return printer.move_axis(axis, distance, speed, _get_client())


def qidi_q2_gcode(script: str, task_id: str = None) -> str:
    """Execute arbitrary G-code commands on the printer."""
    return printer.run_gcode(script, _get_client())


def qidi_q2_upload_and_print(filepath: str, task_id: str = None) -> str:
    """Upload a G-code file and immediately start printing it."""
    return printer.upload_and_print(filepath, _get_client())


# -- File Management Tools --

def qidi_q2_files_list(task_id: str = None) -> str:
    """List all G-code files on the printer with size, print time, and layer count."""
    return files.list_files(_get_client())


def qidi_q2_file_info(filename: str, task_id: str = None) -> str:
    """Get detailed metadata for a specific G-code file."""
    return files.get_file_info(filename, _get_client())


def qidi_q2_upload_file(filepath: str, task_id: str = None) -> str:
    """Upload a G-code file to the printer without printing."""
    return files.upload_file(filepath, _get_client())


def qidi_q2_delete_file(filename: str, task_id: str = None) -> str:
    """Delete a G-code file from the printer."""
    return files.delete_file(filename, _get_client())


def qidi_q2_filament_estimate(filename: str, task_id: str = None) -> str:
    """Estimate filament usage and print time for a G-code file."""
    return files.get_filament_estimate(filename, _get_client())


# -- Camera / Timelapse Tools --

def qidi_q2_snapshot(save_path: str = "", task_id: str = None) -> str:
    """Capture a camera snapshot. Returns file path to saved image."""
    return camera.take_snapshot(save_path or None, _get_client())


def qidi_q2_timelapses(task_id: str = None) -> str:
    """List available timelapse recordings."""
    return camera.list_timelapses(_get_client())


# -- System Tools --

def qidi_q2_restart_klipper(task_id: str = None) -> str:
    """Restart Klipper firmware. Use after emergency stop."""
    return system.restart_klipper(_get_client())


def qidi_q2_restart_moonraker(task_id: str = None) -> str:
    """Restart Moonraker API service."""
    return system.restart_moonraker(_get_client())


def qidi_q2_reboot(task_id: str = None) -> str:
    """Reboot the printer's Linux system. All printing must be stopped."""
    return system.reboot_printer(_get_client())


def qidi_q2_shutdown(task_id: str = None) -> str:
    """Shutdown the printer's Linux system. Power cycle to restart."""
    return system.shutdown_printer(_get_client())


def qidi_q2_ssh(command: str, task_id: str = None) -> str:
    """Execute an SSH command on the printer board (linaro/linaro)."""
    return system.ssh_command(command, _get_client())


def qidi_q2_system_info(task_id: str = None) -> str:
    """Get Moonraker server version and API info."""
    return system.get_system_info(_get_client())


# -- Monitoring Tools --

def qidi_q2_check_alerts(task_id: str = None) -> str:
    """Check for printer alerts (errors, completion, overheat). Returns empty string if all OK."""
    return monitor.check_alerts(_get_client())


# -- Register all tools --

def _register_tools(registry):
    """Register qidi_q2 tools with the Hermes tool registry."""
    reg = registry.register

    # Status
    reg(
        name="qidi_q2_status",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_status",
            "description": "Get full Qidi Q2 printer status: state, temperatures, print progress, position, fans.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_status(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_temperatures",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_temperatures",
            "description": "Get current temperature readings for hotend, bed, and chamber.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_temperatures(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_print_progress",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_print_progress",
            "description": "Get detailed progress of the current print job including ETA and layer count.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_print_progress(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )

    # Print control
    reg(
        name="qidi_q2_print_start",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_print_start",
            "description": "Start printing a G-code file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "G-code filename (e.g. benchy.gcode). Leave empty to print current file."},
                },
            },
        },
        handler=lambda args, **kw: qidi_q2_print_start(
            filename=args.get("filename", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_print_pause",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_print_pause",
            "description": "Pause the current print job.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_print_pause(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_print_resume",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_print_resume",
            "description": "Resume a paused print job.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_print_resume(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_print_cancel",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_print_cancel",
            "description": "Cancel the current print job. Cannot be undone.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_print_cancel(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
        dangerous=True,
    )
    reg(
        name="qidi_q2_emergency_stop",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_emergency_stop",
            "description": "EMERGENCY STOP the printer (M112). Halts all motors and heaters. Requires Klipper restart after.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_emergency_stop(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
        dangerous=True,
    )

    # Tuning
    reg(
        name="qidi_q2_set_speed",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_set_speed",
            "description": "Set print speed override percentage (M220). Typical range: 50-200%.",
            "parameters": {
                "type": "object",
                "properties": {"percent": {"type": "integer", "description": "Speed percentage (e.g. 150)"}},
                "required": ["percent"],
            },
        },
        handler=lambda args, **kw: qidi_q2_set_speed(
            percent=args.get("percent", 100), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_set_flow",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_set_flow",
            "description": "Set extrusion flow rate percentage (M221). Typical range: 90-110%.",
            "parameters": {
                "type": "object",
                "properties": {"percent": {"type": "integer", "description": "Flow percentage (e.g. 105)"}},
                "required": ["percent"],
            },
        },
        handler=lambda args, **kw: qidi_q2_set_flow(
            percent=args.get("percent", 100), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_set_temperature",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_set_temperature",
            "description": "Set heater target temperature.",
            "parameters": {
                "type": "object",
                "properties": {
                    "heater": {"type": "string", "description": "'hotend' or 'bed'", "enum": ["hotend", "bed"]},
                    "temperature": {"type": "integer", "description": "Target temperature in °C"},
                },
                "required": ["heater", "temperature"],
            },
        },
        handler=lambda args, **kw: qidi_q2_set_temperature(
            heater=args.get("heater", "hotend"), temperature=args.get("temperature", 0), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_set_fan",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_set_fan",
            "description": "Set part cooling fan speed (M106).",
            "parameters": {
                "type": "object",
                "properties": {"percent": {"type": "integer", "description": "Fan speed 0-100%"}},
                "required": ["percent"],
            },
        },
        handler=lambda args, **kw: qidi_q2_set_fan(
            percent=args.get("percent", 100), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_home",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_home",
            "description": "Home printer axes (G28).",
            "parameters": {
                "type": "object",
                "properties": {"axes": {"type": "string", "description": "Axes to home (e.g. 'XYZ', 'X', 'Y', 'Z', 'XY')"}},
            },
        },
        handler=lambda args, **kw: qidi_q2_home(
            axes=args.get("axes", "XYZ"), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_gcode",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_gcode",
            "description": "Execute arbitrary G-code commands on the printer.",
            "parameters": {
                "type": "object",
                "properties": {"script": {"type": "string", "description": "G-code commands (one per line)"}},
                "required": ["script"],
            },
        },
        handler=lambda args, **kw: qidi_q2_gcode(
            script=args.get("script", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )

    # File management
    reg(
        name="qidi_q2_files_list",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_files_list",
            "description": "List all G-code files on the printer with metadata.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_files_list(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_file_info",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_file_info",
            "description": "Get detailed metadata for a specific G-code file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "G-code filename"}},
                "required": ["filename"],
            },
        },
        handler=lambda args, **kw: qidi_q2_file_info(
            filename=args.get("filename", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_upload_file",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_upload_file",
            "description": "Upload a G-code file to the printer without printing.",
            "parameters": {
                "type": "object",
                "properties": {"filepath": {"type": "string", "description": "Local file path to upload"}},
                "required": ["filepath"],
            },
        },
        handler=lambda args, **kw: qidi_q2_upload_file(
            filepath=args.get("filepath", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_delete_file",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_delete_file",
            "description": "Delete a G-code file from the printer.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "Filename to delete"}},
                "required": ["filename"],
            },
        },
        handler=lambda args, **kw: qidi_q2_delete_file(
            filename=args.get("filename", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
        dangerous=True,
    )
    reg(
        name="qidi_q2_filament_estimate",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_filament_estimate",
            "description": "Estimate filament usage and print time for a G-code file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "G-code filename"}},
                "required": ["filename"],
            },
        },
        handler=lambda args, **kw: qidi_q2_filament_estimate(
            filename=args.get("filename", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_upload_and_print",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_upload_and_print",
            "description": "Upload a G-code file and immediately start printing it.",
            "parameters": {
                "type": "object",
                "properties": {"filepath": {"type": "string", "description": "Local .gcode file path"}},
                "required": ["filepath"],
            },
        },
        handler=lambda args, **kw: qidi_q2_upload_and_print(
            filepath=args.get("filepath", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )

    # Camera
    reg(
        name="qidi_q2_snapshot",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_snapshot",
            "description": "Capture a camera snapshot. Returns file path to saved image.",
            "parameters": {
                "type": "object",
                "properties": {"save_path": {"type": "string", "description": "Where to save the image (optional)"}},
            },
        },
        handler=lambda args, **kw: qidi_q2_snapshot(
            save_path=args.get("save_path", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )

    # System
    reg(
        name="qidi_q2_restart_klipper",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_restart_klipper",
            "description": "Restart Klipper firmware. Use after emergency stop.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_restart_klipper(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
        dangerous=True,
    )
    reg(
        name="qidi_q2_ssh",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_ssh",
            "description": "Execute an SSH command on the printer board (linaro user).",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "Shell command to execute"}},
                "required": ["command"],
            },
        },
        handler=lambda args, **kw: qidi_q2_ssh(
            command=args.get("command", ""), task_id=kw.get("task_id")
        ),
        check_fn=_check_qidi_q2,
    )
    reg(
        name="qidi_q2_system_info",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_system_info",
            "description": "Get Moonraker server version and API info.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_system_info(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )

    # Monitoring
    reg(
        name="qidi_q2_check_alerts",
        toolset="qidi_q2",
        schema={
            "name": "qidi_q2_check_alerts",
            "description": "Check for printer alerts (errors, completion, overheat). Returns empty if all OK.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: qidi_q2_check_alerts(task_id=kw.get("task_id")),
        check_fn=_check_qidi_q2,
    )


# Auto-register if running inside Hermes
try:
    from tools.registry import registry
    _register_tools(registry)
except ImportError:
    pass  # Not running inside Hermes

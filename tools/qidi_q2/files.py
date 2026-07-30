"""G-code file management operations."""

from __future__ import annotations

import json
import os
from typing import Optional

from .client import MoonrakerClient, MoonrakerError
from .models import GcodeFile, parse_file_list


def list_files(
    client: Optional[MoonrakerClient] = None,
) -> str:
    """List all G-code files on the printer with metadata."""
    client = client or MoonrakerClient()
    try:
        raw = client.list_files()
        gcodes = parse_file_list(raw if isinstance(raw, list) else [])

        if not gcodes:
            return "No G-code files found on printer"

        lines = [f"G-code files ({len(gcodes)}):\n"]
        for f in sorted(gcodes, key=lambda x: x.modified, reverse=True):
            size = f"{f.size_mb:.1f}MB"
            time_str = f.print_time_str if f.estimated_print_time > 0 else "unknown"
            layers = f"{f.layer_count} layers" if f.layer_count > 0 else ""
            lines.append(f"  {f.filename}")
            lines.append(f"    {size} | est. {time_str} | {layers}")

        return "\n".join(lines)
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def get_file_info(
    filename: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Get detailed metadata for a specific G-code file."""
    client = client or MoonrakerClient()
    try:
        meta = client.get_file_metadata(filename)
        lines = [f"File: {filename}"]
        for key, value in sorted(meta.items()):
            if key in ("estimated_print_time",):
                lines.append(f"  Print time: {value / 3600:.1f}h")
            elif key in ("size",):
                lines.append(f"  Size: {value / (1024 * 1024):.1f}MB")
            elif key in ("filament_total",):
                lines.append(f"  Filament: {value / 1000:.1f}m")
            elif key in ("layer_count",):
                lines.append(f"  Layers: {value}")
            elif key in ("layer_height",):
                lines.append(f"  Layer height: {value}mm")
            elif key in ("slicer",):
                lines.append(f"  Slicer: {value}")
            elif key not in ("thumbnails", "modified"):  # skip noise
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def upload_file(
    filepath: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Upload a G-code file to the printer.

    Args:
        filepath: Local path to the .gcode file.
    """
    client = client or MoonrakerClient()

    if not os.path.exists(filepath):
        return json.dumps({
            "success": False,
            "error": f"File not found: {filepath}",
        })

    if not filepath.lower().endswith(".gcode"):
        return json.dumps({
            "success": False,
            "error": "File must be a .gcode file",
        })

    try:
        filename = os.path.basename(filepath)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        result = client.upload_file(filepath)
        return f"Uploaded: {filename} ({size_mb:.1f}MB)"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def delete_file(
    filename: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Delete a G-code file from the printer.

    Args:
        filename: Name of the file to delete.
    """
    client = client or MoonrakerClient()
    try:
        client.delete_file(filename)
        return f"Deleted: {filename}"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def get_filament_estimate(
    filename: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Estimate filament usage for a G-code file."""
    client = client or MoonrakerClient()
    try:
        meta = client.get_file_metadata(filename)
        filament_mm = meta.get("filament_total", 0)
        if filament_mm <= 0:
            return f"No filament estimate for {filename}"

        filament_m = filament_mm / 1000
        # Estimate weight (assuming 1.75mm PLA: 2.98 g/m)
        weight_g = filament_m * 2.98

        lines = [
            f"File: {filename}",
            f"Filament: {filament_m:.1f}m (~{weight_g:.0f}g PLA)",
        ]

        print_time = meta.get("estimated_print_time", 0)
        if print_time > 0:
            h = int(print_time // 3600)
            m = int((print_time % 3600) // 60)
            lines.append(f"Print time: {h}h {m:02d}m")

        return "\n".join(lines)
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})

"""Camera and timelapse operations."""

from __future__ import annotations

import base64
import json
import os
import time
from typing import Optional

from .client import MoonrakerClient, MoonrakerError


def take_snapshot(
    save_path: Optional[str] = None,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Capture a snapshot from the printer camera.

    Args:
        save_path: Where to save the image. Defaults to /tmp/qidi_snapshot_<timestamp>.jpg.

    Returns:
        Path to the saved image file.
    """
    client = client or MoonrakerClient()

    if not save_path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = f"/tmp/qidi_snapshot_{timestamp}.jpg"

    try:
        data = client.snapshot()
        with open(save_path, "wb") as f:
            f.write(data)
        return f"Snapshot saved: {save_path}"
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def snapshot_base64(client: Optional[MoonrakerClient] = None) -> str:
    """Capture snapshot and return as base64 for inline vision analysis."""
    client = client or MoonrakerClient()
    try:
        data = client.snapshot()
        return base64.b64encode(data).decode("utf-8")
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def list_timelapses(client: Optional[MoonrakerClient] = None) -> str:
    """List available timelapse recordings."""
    client = client or MoonrakerClient()
    try:
        result = client.timelapse_list()
        if not result:
            return "No timelapse recordings found (hyperlapse may not be installed)"

        lines = [f"Timelapses ({len(result)}):\n"]
        for item in result:
            name = item.get("name", "unknown")
            size = item.get("size", 0) / (1024 * 1024)
            lines.append(f"  {name} ({size:.1f}MB)")
        return "\n".join(lines)
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})

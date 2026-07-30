"""System-level operations (reboot, restart services, SSH)."""

from __future__ import annotations

import json
import subprocess
from typing import Optional

from .client import MoonrakerClient, MoonrakerError


def reboot_printer(client: Optional[MoonrakerClient] = None) -> str:
    """Reboot the printer's Linux system. All printing must be stopped first."""
    client = client or MoonrakerClient()
    try:
        client.reboot()
        return "Reboot command sent. Printer will be offline for ~60 seconds."
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def shutdown_printer(client: Optional[MoonrakerClient] = None) -> str:
    """Shutdown the printer's Linux system. Power cycle to restart."""
    client = client or MoonrakerClient()
    try:
        client.shutdown()
        return "Shutdown command sent. Printer must be power-cycled to restart."
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def restart_klipper(client: Optional[MoonrakerClient] = None) -> str:
    """Restart the Klipper firmware. Use after emergency stop."""
    client = client or MoonrakerClient()
    try:
        client.restart_klipper()
        return "Klipper firmware restarting..."
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def restart_moonraker(client: Optional[MoonrakerClient] = None) -> str:
    """Restart the Moonraker API service."""
    client = client or MoonrakerClient()
    try:
        client.restart_moonraker()
        return "Moonraker service restarting..."
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})


def ssh_command(
    command: str,
    client: Optional[MoonrakerClient] = None,
) -> str:
    """Execute an SSH command on the printer board.

    Requires: sshpass or SSH key-based auth configured.
    Default credentials: linaro/linaro.

    Args:
        command: Shell command to run.
    """
    client = client or MoonrakerClient()
    host = client.host

    # Try sshpass first, fall back to plain ssh
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5"]
    ssh_cmd.append(f"linaro@{host}")
    ssh_cmd.append(command)

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if result.returncode != 0 and not output:
            return json.dumps({
                "success": False,
                "error": error or "SSH command failed",
                "hint": "Make sure sshpass is installed or SSH keys are set up.",
            })
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return json.dumps({
            "success": False,
            "error": "SSH command timed out (15s)",
        })
    except FileNotFoundError:
        return json.dumps({
            "success": False,
            "error": "ssh not found. Install openssh-client.",
        })


def get_system_info(client: Optional[MoonrakerClient] = None) -> str:
    """Get printer system info via SSH."""
    client = client or MoonrakerClient()
    try:
        info = client.server_info()
        lines = ["Moonraker Server Info:"]
        for key in ("moonraker_version", "api_version"):
            if key in info:
                lines.append(f"  {key}: {info[key]}")
        return "\n".join(lines)
    except MoonrakerError as e:
        return json.dumps({"success": False, "error": str(e)})

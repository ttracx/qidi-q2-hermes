"""Moonraker API client for Qidi Q2 printer.

Handles all HTTP communication with the printer's Moonraker instance.
"""

from __future__ import annotations

import json
import os
import time
import socket
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class MoonrakerError(Exception):
    """Base error for Moonraker communication failures."""
    pass


class MoonrakerConnectionError(MoonrakerError):
    """Cannot reach the printer."""
    pass


class MoonrakerAPIError(MoonrakerError):
    """Moonraker returned an error response."""
    pass


class MoonrakerClient:
    """HTTP client for Moonraker API on Qidi Q2.

    Default: http://10.1.10.153:7125
    Set QIDI_Q2_HOST env var or pass host= to override.
    """

    DEFAULT_HOST = "10.1.10.153"
    DEFAULT_PORT = 7125
    DEFAULT_TIMEOUT = 10

    # Moonraker API endpoints
    ENDPOINTS = {
        # Printer info
        "printer_info": "/printer/info",
        "objects_query": "/printer/objects/query",
        "objects_list": "/printer/objects/list",
        # Print control
        "print_start": "/printer/print/start",
        "print_pause": "/printer/print/pause",
        "print_resume": "/printer/print/resume",
        "print_cancel": "/printer/print/cancel",
        "emergency_stop": "/printer/emergency_stop",
        # G-code
        "gcode_script": "/printer/gcode/script",
        "gcode_help": "/printer/gcode/help",
        # Files
        "files_list": "/server/files/list",
        "files_metadata": "/server/files/metadata",
        "files_upload": "/server/files/upload",
        "files_delete": "/server/files",
        # Camera
        "camera_snapshot": "/webcam/?action=snapshot",
        "camera_stream": "/webcam/?action=stream",
        # Timelapse (if hyperlapse installed)
        "timelapse_list": "/server/timelapse/list",
        "timelapse_save": "/server/timelapse/save",
        # System
        "reboot": "/machine/reboot",
        "shutdown": "/machine/shutdown",
        "restart_klipper": "/machine/restart_klipper",
        "restart_moonraker": "/machine/restart_moonraker",
        # Server info
        "server_info": "/server/info",
        "history_list": "/server/history/list",
    }

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.host = host or os.getenv("QIDI_Q2_HOST", self.DEFAULT_HOST)
        self.port = port or int(os.getenv("QIDI_Q2_PORT", str(self.DEFAULT_PORT)))
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"

    # -- Low-level HTTP --

    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[dict] = None,
        raw: bool = False,
    ) -> Any:
        """Make an HTTP request to Moonraker."""
        url = f"{self.base_url}{endpoint}"
        request = Request(url, method=method)

        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            request.add_header("Content-Type", "application/json")

        try:
            response = urlopen(request, data=body, timeout=self.timeout)
            if raw:
                return response.read()
            result = json.loads(response.read().decode("utf-8"))
            if "error" in result:
                raise MoonrakerAPIError(
                    f"Moonraker error {result['error'].get('code')}: "
                    f"{result['error'].get('message')}"
                )
            return result.get("result", result)
        except HTTPError as e:
            raise MoonrakerAPIError(f"HTTP {e.code}: {e.reason}") from e
        except URLError as e:
            raise MoonrakerConnectionError(
                f"Cannot reach printer at {self.host}:{self.port} — {e.reason}"
            ) from e
        except socket.timeout:
            raise MoonrakerConnectionError(
                f"Timeout connecting to {self.host}:{self.port}"
            )
        except json.JSONDecodeError as e:
            raise MoonrakerAPIError(f"Invalid JSON response: {e}") from e

    def _get(self, endpoint: str, **kwargs) -> Any:
        return self._request(endpoint, "GET", **kwargs)

    def _post(self, endpoint: str, data: Optional[dict] = None, **kwargs) -> Any:
        return self._request(endpoint, "POST", data=data, **kwargs)

    # -- Printer Info --

    def get_printer_info(self) -> dict:
        """Get Klipper printer state (ready/printing/paused/error)."""
        return self._get(self.ENDPOINTS["printer_info"])

    def get_objects(self, objects: list[str]) -> dict:
        """Query specific Klipper objects.

        Example objects: ["extruder", "heater_bed", "fan", "print_stats",
        "virtual_sdcard", "gcode_move", "toolhead", "motion_report"]
        """
        return self._get(
            f"{self.ENDPOINTS['objects_query']}?{'&'.join(objects)}"
        )

    def list_objects(self) -> dict:
        """List all available Klipper objects."""
        return self._get(self.ENDPOINTS["objects_list"])

    # -- Print Control --

    def print_start(self, filename: Optional[str] = None) -> dict:
        """Start printing. If no filename, prints currently loaded file."""
        params = {}
        if filename:
            params["filename"] = filename
        return self._post(self.ENDPOINTS["print_start"], data=params)

    def print_pause(self) -> dict:
        return self._post(self.ENDPOINTS["print_pause"])

    def print_resume(self) -> dict:
        return self._post(self.ENDPOINTS["print_resume"])

    def print_cancel(self) -> dict:
        return self._post(self.ENDPOINTS["print_cancel"])

    def emergency_stop(self) -> dict:
        """M112 — immediate halt. Requires firmware restart after."""
        return self._post(self.ENDPOINTS["emergency_stop"])

    # -- G-code --

    def gcode(self, script: str) -> dict:
        """Execute arbitrary G-code script."""
        return self._post(self.ENDPOINTS["gcode_script"], data={"script": script})

    def gcode_help(self) -> dict:
        return self._get(self.ENDPOINTS["gcode_help"])

    # -- Files --

    def list_files(self, root: str = "gcodes") -> list:
        """List files. root: 'gcodes' or 'config'."""
        result = self._get(f"{self.ENDPOINTS['files_list']}?root={root}")
        return result if isinstance(result, list) else []

    def get_file_metadata(self, filename: str) -> dict:
        """Get metadata for a specific G-code file."""
        return self._get(
            f"{self.ENDPOINTS['files_metadata']}?filename={filename}"
        )

    def upload_file(self, filepath: str, root: str = "gcodes") -> dict:
        """Upload a G-code file to the printer."""
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            content = f.read()

        # Moonraker file upload uses multipart/form-data
        boundary = f"----HermesBoundary{int(time.time())}"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")

        url = f"{self.base_url}{self.ENDPOINTS['files_upload']}?root={root}"
        request = Request(url, data=body, method="POST")
        request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

        try:
            response = urlopen(request, timeout=self.timeout * 3)  # longer for upload
            return json.loads(response.read().decode("utf-8"))
        except URLError as e:
            raise MoonrakerConnectionError(f"Upload failed: {e.reason}") from e

    def delete_file(self, filename: str, root: str = "gcodes") -> dict:
        """Delete a file from the printer."""
        endpoint = f"{self.ENDPOINTS['files_delete']}?root={root}&path={filename}"
        return self._request(endpoint, "DELETE")

    # -- Camera --

    def snapshot(self) -> bytes:
        """Capture a camera snapshot. Returns JPEG bytes."""
        return self._get(self.ENDPOINTS["camera_snapshot"], raw=True)

    # -- Timelapse --

    def timelapse_list(self) -> list:
        try:
            return self._get(self.ENDPOINTS["timelapse_list"])
        except MoonrakerAPIError:
            return []  # hyperlapse not installed

    # -- System --

    def reboot(self) -> dict:
        return self._post(self.ENDPOINTS["reboot"])

    def shutdown(self) -> dict:
        return self._post(self.ENDPOINTS["shutdown"])

    def restart_klipper(self) -> dict:
        return self._post(self.ENDPOINTS["restart_klipper"])

    def restart_moonraker(self) -> dict:
        return self._post(self.ENDPOINTS["restart_moonraker"])

    # -- Server --

    def server_info(self) -> dict:
        return self._get(self.ENDPOINTS["server_info"])

    def history(self, limit: int = 10) -> dict:
        return self._get(f"{self.ENDPOINTS['history_list']}?limit={limit}")

    # -- Convenience --

    def is_reachable(self) -> bool:
        """Quick check if printer is online."""
        try:
            self.server_info()
            return True
        except MoonrakerError:
            return False

    def wait_until_ready(self, timeout: int = 60) -> bool:
        """Wait for printer to leave startup/shutdown state."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                info = self.get_printer_info()
                if info.get("state") in ("ready", "printing"):
                    return True
            except MoonrakerError:
                pass
            time.sleep(2)
        return False

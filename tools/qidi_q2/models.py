"""Data models for Qidi Q2 printer state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class TemperatureReading:
    """A single temperature sensor reading."""
    current: float
    target: float
    power: float = 0.0  # 0.0 to 1.0

    @property
    def is_heating(self) -> bool:
        return self.target > 0 and self.current < self.target - 2.0

    @property
    def is_at_target(self) -> bool:
        return self.target > 0 and abs(self.current - self.target) < 2.0

    def __str__(self) -> str:
        return f"{self.current:.1f}°C / {self.target:.0f}°C"


@dataclass
class FanStatus:
    """Fan speed status."""
    speed: float  # 0.0 to 1.0

    @property
    def percent(self) -> int:
        return int(self.speed * 100)


@dataclass
class Position:
    """Current toolhead position."""
    x: float
    y: float
    z: float
    e: float = 0.0  # extruder position


@dataclass
class PrintProgress:
    """Current print job progress."""
    filename: str = ""
    state: str = "idle"  # idle, printing, paused, complete, cancelled, error
    progress: float = 0.0  # 0.0 to 1.0
    print_duration: float = 0.0  # seconds elapsed
    estimated_time_left: float = 0.0  # seconds
    filament_used_mm: float = 0.0
    filament_total_mm: float = 0.0
    current_layer: int = 0
    total_layers: int = 0
    message: str = ""

    @property
    def percent(self) -> int:
        return int(self.progress * 100)

    @property
    def elapsed_str(self) -> str:
        return _format_duration(self.print_duration)

    @property
    def eta_str(self) -> str:
        if self.estimated_time_left <= 0:
            return "unknown"
        return _format_duration(self.estimated_time_left)

    @property
    def is_active(self) -> bool:
        return self.state in ("printing", "paused")

    @property
    def is_finished(self) -> bool:
        return self.state in ("complete", "cancelled", "error")


@dataclass
class PrinterStatus:
    """Complete printer state snapshot."""
    state: str  # ready, printing, paused, error, shutdown, startup
    state_message: str = ""
    hostname: str = ""
    klipper_version: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    # Temperatures
    extruder: Optional[TemperatureReading] = None
    heater_bed: Optional[TemperatureReading] = None
    chamber: Optional[TemperatureReading] = None

    # Fans
    fan: Optional[FanStatus] = None
    heater_fan: Optional[FanStatus] = None

    # Speed / flow multipliers
    speed_factor: float = 1.0  # M220
    extrude_factor: float = 1.0  # M221

    # Position
    position: Optional[Position] = None

    # Print job
    print_job: Optional[PrintProgress] = None

    @property
    def is_printing(self) -> bool:
        return self.state == "printing"

    @property
    def is_paused(self) -> bool:
        return self.state == "paused"

    @property
    def is_ready(self) -> bool:
        return self.state == "ready"

    @property
    def is_error(self) -> bool:
        return self.state in ("error", "shutdown")


@dataclass
class GcodeFile:
    """A G-code file on the printer."""
    filename: str
    size: int  # bytes
    modified: float  # unix timestamp
    estimated_print_time: float = 0.0  # seconds
    layer_count: int = 0
    layer_height: float = 0.0
    first_layer_height: float = 0.0
    filament_total: float = 0.0  # mm
    slicer: str = ""
    thumbnails: list[dict] = field(default_factory=list)

    @property
    def size_mb(self) -> float:
        return self.size / (1024 * 1024)

    @property
    def print_time_str(self) -> str:
        return _format_duration(self.estimated_print_time)


@dataclass
class TimelapseInfo:
    """Available timelapse recording."""
    name: str
    size_mb: float
    created: str


def _format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m:02d}m"
    return f"{m}m {s:02d}s"


# -- Parse from Moonraker API responses --

def parse_printer_status(data: dict[str, Any]) -> PrinterStatus:
    """Parse Moonraker /printer/info + /printer/objects/query responses."""
    info = data.get("printer_info", {})
    objects = data.get("objects", {})

    status = PrinterStatus(
        state=info.get("state", "unknown"),
        state_message=info.get("state_message", ""),
        hostname=info.get("hostname", ""),
        klipper_version=info.get("software_version", ""),
    )

    # Temperatures
    extruder = objects.get("extruder", {})
    if extruder:
        status.extruder = TemperatureReading(
            current=extruder.get("temperature", 0.0),
            target=extruder.get("target", 0.0),
            power=extruder.get("power", 0.0),
        )

    bed = objects.get("heater_bed", {})
    if bed:
        status.heater_bed = TemperatureReading(
            current=bed.get("temperature", 0.0),
            target=bed.get("target", 0.0),
            power=bed.get("power", 0.0),
        )

    chamber = objects.get("temperature_sensor chamber", {}) or objects.get("heater_generic chamber", {})
    if chamber:
        status.chamber = TemperatureReading(
            current=chamber.get("temperature", 0.0),
            target=chamber.get("target", 0.0),
        )

    # Fans
    fan = objects.get("fan", {})
    if fan:
        status.fan = FanStatus(speed=fan.get("speed", 0.0))

    heater_fan = objects.get("heater_fan extruder_fan", {})
    if heater_fan:
        status.heater_fan = FanStatus(speed=heater_fan.get("speed", 0.0))

    # Speed multipliers
    gcode_move = objects.get("gcode_move", {})
    if gcode_move:
        status.speed_factor = gcode_move.get("speed_factor", 1.0)
        status.extrude_factor = gcode_move.get("extrude_factor", 1.0)

    # Position
    position = objects.get("motion_report", {}).get("live_position")
    if not position:
        position = objects.get("toolhead", {}).get("position")
    if position and len(position) >= 3:
        status.position = Position(
            x=position[0], y=position[1], z=position[2],
            e=position[3] if len(position) > 3 else 0.0,
        )

    # Print job
    print_stats = objects.get("print_stats", {})
    virtual_sdcard = objects.get("virtual_sdcard", {})
    if print_stats or virtual_sdcard:
        job = PrintProgress(
            filename=print_stats.get("filename", ""),
            state=print_stats.get("state", "idle"),
            progress=virtual_sdcard.get("progress", 0.0),
            print_duration=print_stats.get("print_duration", 0.0),
            filament_used_mm=print_stats.get("filament_used", 0.0),
            message=print_stats.get("message", ""),
        )
        # Estimate time left
        if job.progress > 0 and job.print_duration > 0:
            total_est = job.print_duration / job.progress
            job.estimated_time_left = max(0, total_est - job.print_duration)

        # Layer info
        info_resp = objects.get("print_stats", {}).get("info", {})
        job.current_layer = info_resp.get("current_layer", 0)
        job.total_layers = info_resp.get("total_layer", 0)

        status.print_job = job

    return status


def parse_file_list(data: list[dict[str, Any]]) -> list[GcodeFile]:
    """Parse Moonraker /server/files/list response."""
    files = []
    for item in data:
        if item.get("filename", "").endswith(".gcode"):
            files.append(GcodeFile(
                filename=item["filename"],
                size=item.get("size", 0),
                modified=item.get("modified", 0.0),
                estimated_print_time=item.get("estimated_print_time", 0.0),
                layer_count=item.get("layer_count", 0),
                layer_height=item.get("layer_height", 0.0),
                first_layer_height=item.get("first_layer_height", 0.0),
                filament_total=item.get("filament_total", 0.0),
                slicer=item.get("slicer", ""),
            ))
    return files

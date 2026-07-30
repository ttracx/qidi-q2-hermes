# Moonraker API Reference

Complete reference for the Moonraker API endpoints used by this integration.

Base URL: `http://10.1.10.153:7125`

## Printer Info

### `GET /printer/info`

Returns Klipper printer state.

**Response:**
```json
{
  "result": {
    "state": "ready",
    "state_message": "",
    "hostname": "linaro-alip",
    "software_version": "v0.12.0-268-gf8dd2e9c",
    "cpu_info": "4 core ARMv7 Processor rev 5 (v7l)"
  }
}
```

**States:** `ready`, `printing`, `paused`, `error`, `shutdown`, `startup`

## Object Queries

### `GET /printer/objects/query?{obj1}&{obj2}...`

Query specific Klipper objects. Most useful objects:

| Object | Data |
|--------|------|
| `extruder` | temperature, target, power |
| `heater_bed` | temperature, target, power |
| `fan` | speed (0.0-1.0) |
| `heater_fan extruder_fan` | speed |
| `gcode_move` | speed_factor, extrude_factor, position |
| `print_stats` | filename, state, progress, print_duration |
| `virtual_sdcard` | progress, file_size, file_position |
| `toolhead` | position [x, y, z, e] |
| `motion_report` | live_position |
| `temperature_sensor chamber` | temperature |

**Example:**
```
GET /printer/objects/query?extruder&heater_bed&print_stats
```

## Print Control

### `POST /printer/print/start`

Start a print.

**Body:**
```json
{"filename": "benchy.gcode"}
```

If filename omitted, prints currently loaded file.

### `POST /printer/print/pause`

Pause current print.

### `POST /printer/print/resume`

Resume paused print.

### `POST /printer/print/cancel`

Cancel current print (cannot be undone).

### `POST /printer/emergency_stop`

Execute M112 emergency stop. Halts all motors and heaters. Requires `restart_klipper` to recover.

## G-code

### `POST /printer/gcode/script`

Execute arbitrary G-code commands.

**Body:**
```json
{"script": "M104 S200\nM109 S200"}
```

Commands are separated by newlines. The printer executes them sequentially.

### Common G-code Commands

| Command | Description |
|---------|-------------|
| `M104 S<temp>` | Set hotend temperature |
| `M109 S<temp>` | Set hotend temp and wait |
| `M140 S<temp>` | Set bed temperature |
| `M190 S<temp>` | Set bed temp and wait |
| `M104 S0` | Hotend off |
| `M140 S0` | Bed off |
| `M106 S<pwm>` | Fan on (0-255) |
| `M107` | Fan off |
| `G28` | Home all axes |
| `G28 X` | Home X axis only |
| `G91` | Relative positioning |
| `G90` | Absolute positioning |
| `G1 X100 F3000` | Move X to 100mm at 3000mm/min |
| `M220 S<percent>` | Set speed factor (%) |
| `M221 S<percent>` | Set flow factor (%) |
| `M112` | Emergency stop |
| `M115` | Firmware info |

## File Management

### `GET /server/files/list?root=gcodes`

List files. Root: `gcodes` or `config`.

**Response:**
```json
{
  "result": [
    {
      "filename": "benchy.gcode",
      "size": 12584762,
      "modified": 1707000000.0,
      "estimated_print_time": 4200,
      "layer_count": 210,
      "layer_height": 0.2,
      "filament_total": 5000,
      "slicer": "QidiSlicer"
    }
  ]
}
```

### `GET /server/files/metadata?filename={name}`

Get detailed metadata for a specific file.

### `POST /server/files/upload?root=gcodes`

Upload a file. Content-Type: multipart/form-data.

### `DELETE /server/files?root=gcodes&path={filename}`

Delete a file.

## Camera

### `GET /webcam/?action=snapshot`

Capture a JPEG snapshot. Returns raw image bytes.

### `GET /webcam/?action=stream`

MJPEG stream (for web viewing).

## System

### `POST /machine/reboot`

Reboot the printer's Linux system.

### `POST /machine/shutdown`

Shutdown the printer's Linux system.

### `POST /machine/restart_klipper`

Restart Klipper firmware service.

### `POST /machine/restart_moonraker`

Restart Moonraker API service.

## Server Info

### `GET /server/info`

Moonraker server information.

**Response:**
```json
{
  "result": {
    "moonraker_version": "v0.9.3",
    "api_version": [1, 0, 0],
    "api_version_string": "1.0.0"
  }
}
```

## History

### `GET /server/history/list?limit=10`

Recent job history.

## Authentication

The stock Qidi Q2 Moonraker instance has **no API key authentication** — anyone on the network can control the printer. Consider adding a firewall rule if security is a concern.

## Rate Limits

Moonraker handles concurrent requests well but avoid flooding:
- `objects_query`: no more than 1 request/second
- `print/*` commands: one at a time
- File upload: sequential only

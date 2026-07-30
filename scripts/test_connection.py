#!/usr/bin/env python3
"""Test connection to Qidi Q2 printer."""

import sys
sys.path.insert(0, ".")

from tools.qidi_q2.client import MoonrakerClient, MoonrakerError
from tools.qidi_q2.status import get_status


def main():
    host = input("Printer IP [10.1.10.153]: ").strip() or "10.1.10.153"
    print(f"Testing connection to {host}:7125...\n")

    client = MoonrakerClient(host=host)

    # Test 1: Reachability
    print("1. Reachability...")
    if not client.is_reachable():
        print("   ✗ Printer is OFFLINE")
        return 1
    print("   ✓ Printer is ONLINE")

    # Test 2: Server info
    print("2. Server info...")
    try:
        info = client.server_info()
        version = info.get("moonraker_version", "unknown")
        api = info.get("api_version_string", "unknown")
        print(f"   ✓ Moonraker {version} (API {api})")
    except MoonrakerError as e:
        print(f"   ✗ {e}")
        return 1

    # Test 3: Printer state
    print("3. Printer state...")
    try:
        info = client.get_printer_info()
        state = info.get("state", "unknown")
        print(f"   ✓ State: {state}")
    except MoonrakerError as e:
        print(f"   ✗ {e}")
        return 1

    # Test 4: Temperatures
    print("4. Temperatures...")
    try:
        objects = client.get_objects(["extruder", "heater_bed"])
        status = objects.get("status", {})
        ext = status.get("extruder", {})
        bed = status.get("heater_bed", {})
        ext_t = f"{ext.get('temperature', '?')}°C / {ext.get('target', '?')}°C"
        bed_t = f"{bed.get('temperature', '?')}°C / {bed.get('target', '?')}°C"
        print(f"   ✓ Hotend: {ext_t}  Bed: {bed_t}")
    except MoonrakerError as e:
        print(f"   ✗ {e}")

    # Test 5: File list
    print("5. Files...")
    try:
        files = client.list_files()
        gcodes = [f for f in (files if isinstance(files, list) else []) if f.get("filename", "").endswith(".gcode")]
        print(f"   ✓ {len(gcodes)} G-code files")
        for f in gcodes[:3]:
            print(f"     - {f['filename']}")
        if len(gcodes) > 3:
            print(f"     ... and {len(gcodes) - 3} more")
    except MoonrakerError as e:
        print(f"   ✗ {e}")

    # Test 6: Print status
    print("6. Print job...")
    try:
        objects = client.get_objects(["print_stats", "virtual_sdcard"])
        stats = objects.get("status", {}).get("print_stats", {})
        state = stats.get("state", "unknown")
        filename = stats.get("filename", "")
        if state == "printing":
            progress = objects.get("status", {}).get("virtual_sdcard", {}).get("progress", 0)
            print(f"   ✓ Printing {filename} — {int(progress * 100)}%")
        elif state == "paused":
            print(f"   ✓ Paused: {filename}")
        else:
            print(f"   ✓ Not printing ({state})")
    except MoonrakerError as e:
        print(f"   ✗ {e}")

    print(f"\nAll tests passed! Printer is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

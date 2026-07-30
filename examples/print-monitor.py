#!/usr/bin/env python3
"""Full print monitoring loop example.

Monitors a print until completion with periodic status updates.
"""

import sys
import time
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from qidi_q2.client import MoonrakerClient
from qidi_q2.status import get_print_progress, get_status


def on_progress(job):
    print(f"  [{job.percent}%] {job.filename} — layer {job.current_layer}/{job.total_layers} — ETA {job.eta_str}")


def on_complete():
    print("\n🎉 Print complete!")


def on_error():
    print("\n❌ Print error!")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "10.1.10.153"
    client = MoonrakerClient(host=host)

    print(f"Monitoring print on {host}...")
    print("Current status:")
    print(get_status(client))
    print()

    if client.is_reachable():
        from qidi_q2.monitor import monitor_print
        result = monitor_print(
            client=client,
            interval=30,
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error,
        )
        print(f"Result: {result}")
    else:
        print("Printer is offline!")

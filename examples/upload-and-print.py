#!/usr/bin/env python3
"""Upload a G-code file and start printing it."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from qidi_q2.printer import upload_and_print

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: upload-and-print.py <file.gcode> [host]")
        sys.exit(1)

    filepath = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else "10.1.10.153"

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    print(f"Uploading and printing {filepath} on {host}...")
    result = upload_and_print(filepath)
    print(result)

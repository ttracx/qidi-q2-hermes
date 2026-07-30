#!/usr/bin/env python3
"""Standalone printer status check."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from qidi_q2.status import get_status

if __name__ == "__main__":
    print(get_status())

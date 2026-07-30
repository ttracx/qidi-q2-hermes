#!/usr/bin/env bash
# Silent Qidi Q2 alert check — only outputs when there's something to report
# Place in ~/.hermes/scripts/ and reference from cronjob no_agent=True
set -euo pipefail
cd "$(dirname "$0")"

python3 -c "
import sys
sys.path.insert(0, '.')
from tools.qidi_q2.client import MoonrakerClient
from tools.qidi_q2.monitor import check_alerts
result = check_alerts(MoonrakerClient())
if result:
    print(result)
"

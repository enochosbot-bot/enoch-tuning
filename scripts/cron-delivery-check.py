#!/usr/bin/env python3
"""
cron-delivery-check.py
Simple preflight check for cron delivery reliability.
Exit codes:
  0 = healthy
  1 = unhealthy
"""

from __future__ import annotations

import os
import sys
from urllib.request import urlopen


def main() -> int:
    port = os.getenv("OPENCLAW_GATEWAY_PORT", "49297")
    url = f"http://127.0.0.1:{port}/"

    try:
        with urlopen(url, timeout=5) as resp:
            code = getattr(resp, "status", 200)
            if 200 <= code < 500:
                print(f"delivery-check: ok (gateway reachable at {url}, status={code})")
                return 0
            print(f"delivery-check: fail (gateway returned status={code})")
            return 1
    except Exception as exc:
        print(f"delivery-check: fail (gateway unreachable at {url}: {exc})")
        return 1


if __name__ == "__main__":
    sys.exit(main())

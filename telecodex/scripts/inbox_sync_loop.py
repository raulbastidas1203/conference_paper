#!/usr/bin/env python3
import argparse
import time
from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = BASE_DIR / 'scripts' / 'sync_cursor_inbox.py'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--interval', type=float, default=3.0)
    args = p.parse_args()

    while True:
        try:
            subprocess.run([sys.executable, str(SYNC_SCRIPT)], check=False)
        except KeyboardInterrupt:
            break
        except Exception:
            pass
        time.sleep(args.interval)


if __name__ == '__main__':
    main()

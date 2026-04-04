#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CMD_SCRIPT = BASE_DIR / 'scripts' / 'telegram_commands.py'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--interval', type=float, default=3.0)
    args = p.parse_args()
    while True:
        try:
            subprocess.run([sys.executable, str(CMD_SCRIPT)], check=False)
        except KeyboardInterrupt:
            break
        except Exception:
            pass
        time.sleep(args.interval)


if __name__ == '__main__':
    main()

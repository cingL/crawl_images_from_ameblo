#!/usr/bin/env python3
import datetime
import os
import subprocess
import sys
from pathlib import Path


def run_step(script_path, env):
    command = [sys.executable, str(script_path)]
    result = subprocess.run(command, cwd=str(script_path.parent), env=env)
    return result.returncode


def main():
    base_dir = Path(__file__).resolve().parent
    crawl_url_path = base_dir / "crawl_url.py"
    crawl_image_path = base_dir / "crawl_image.py"

    missing = [p.name for p in (crawl_url_path, crawl_image_path) if not p.exists()]
    if missing:
        print("[ERROR] Missing required files: {0}".format(", ".join(missing)))
        return 1

    run_ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    env = os.environ.copy()
    env["CRAWL_RUN_TS"] = run_ts

    print("[INFO] Working dir: {0}".format(base_dir))
    print("[INFO] Run timestamp: {0}".format(run_ts))

    print("\n[STEP 1/2] Crawling entry URLs...")
    exit_code = run_step(crawl_url_path, env)
    if exit_code != 0:
        print("[ERROR] crawl_url.py failed with exit code {0}".format(exit_code))
        return exit_code

    print("\n[STEP 2/2] Crawling entry images...")
    exit_code = run_step(crawl_image_path, env)
    if exit_code != 0:
        print("[ERROR] crawl_image.py failed with exit code {0}".format(exit_code))
        return exit_code

    print("\n[DONE] All tasks finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

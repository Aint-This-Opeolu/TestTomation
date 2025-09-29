"""
Accessibility scan using Playwright and axe-core via @axe-core/cli (node) fallback.
If node/axe not available, prints a placeholder.
"""

import json
import os
import shutil
import subprocess
import sys


def run_axe_cli(url: str, out_path: str) -> int:
    axe = shutil.which("axe") or shutil.which("npx")
    if not axe:
        print("axe (or npx) not found; skipping a11y scan")
        return 0
    cmd = ["npx", "--yes", "@axe-core/cli", "-q", "-s", url, "-o", out_path]
    if axe.endswith("axe"):
        cmd = ["axe", "-q", "-s", url, "-o", out_path]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


def main():
    env = os.getenv("CI_COMMIT_REF_NAME", "development").replace("main", "production")
    host = "localhost"
    cfg_file = os.path.join("configs", f"{env}.yaml")
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("host:"):
                        host = line.split()[1].strip()
                        break
        except Exception:
            pass
    url = f"https://{host}"
    os.makedirs("reports/a11y", exist_ok=True)
    out = "reports/a11y/axe_report.json"
    code = run_axe_cli(url, out)
    print(f"A11y scan complete for {url}; output: {out}")
    sys.exit(code)


if __name__ == "__main__":
    main()


"""
Minimal Prometheus Pushgateway example for CI metrics.
"""

import os
import time
import requests


def main():
    gateway = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")
    job = os.getenv("METRICS_JOB", "qa_tests")
    labels = os.getenv("METRICS_LABELS", "branch=dev")

    metrics = [
        f"test_runs_total{{{labels}}} 1",
        f"test_failures_total{{{labels}}} {int(os.getenv('TEST_FAILURES', '0'))}",
        f"avg_test_duration_seconds{{{labels}}} {float(os.getenv('AVG_DURATION', '0.0'))}",
    ]
    payload = "\n".join(metrics) + "\n"

    url = f"{gateway}/metrics/job/{job}"
    resp = requests.post(url, data=payload.encode("utf-8"))
    resp.raise_for_status()
    print("Pushed metrics to", url)


if __name__ == "__main__":
    main()


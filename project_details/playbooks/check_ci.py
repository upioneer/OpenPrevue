"""Helper script to query and monitor GitHub Actions CI pipeline runs."""

import json
import time
import urllib.request
from typing import Any

REPO = "upioneer/OpenPrevue"
API_URL = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=5"


def fetch_runs() -> list[dict[str, Any]]:
    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "OpenPrevue-CI-Checker",
            "Accept": "application/vnd.github.v3+json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("workflow_runs", [])
    except Exception as e:
        print(f"Error checking GitHub runs: {e}")
        return []


def inspect_run_jobs(run_id: int) -> None:
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "OpenPrevue-CI-Checker",
            "Accept": "application/vnd.github.v3+json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            jobs = data.get("jobs", [])
            print(f"\n--- Run {run_id} Job Breakdown ---")
            for j in jobs:
                name = j.get("name")
                status = j.get("status")
                conclusion = j.get("conclusion")
                started_at = j.get("started_at")
                completed_at = j.get("completed_at")
                print(f"Job: {name} | Status: {status} | Conclusion: {conclusion} | Duration: {started_at} -> {completed_at}")
    except Exception as e:
        print(f"Error fetching jobs for run {run_id}: {e}")


if __name__ == "__main__":
    runs = fetch_runs()
    latest_runs = [r for r in runs if r.get("head_sha", "").startswith("1241d44")]
    for r in latest_runs:
        inspect_run_jobs(r["id"])

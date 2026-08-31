"""Helper script to query and monitor GitHub Actions CI pipeline runs."""

import json
import time
import urllib.request
from typing import Any

REPO = "upioneer/OpenPrevue"
API_URL = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10"


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


def inspect_run_jobs(run_id: int) -> bool:
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
            all_completed = True
            for j in jobs:
                jid = j.get("id")
                name = j.get("name")
                status = j.get("status")
                conclusion = j.get("conclusion")
                started_at = j.get("started_at")
                completed_at = j.get("completed_at")
                print(f"Job: {name} | Status: {status} | Conclusion: {conclusion} | Duration: {started_at} -> {completed_at}")
                if status != "completed":
                    all_completed = False
                elif conclusion == "failure":
                    # Fetch annotations for job
                    try:
                        ann_req = urllib.request.Request(
                            f"https://api.github.com/repos/{REPO}/check-runs/{jid}/annotations",
                            headers={"User-Agent": "OpenPrevue-CI-Checker", "Accept": "application/vnd.github.v3+json"},
                        )
                        with urllib.request.urlopen(ann_req) as a_resp:
                            annotations = json.loads(a_resp.read().decode("utf-8"))
                            for a in annotations:
                                print(f"  [ANNOTATION] {a.get('path')}:{a.get('start_line')} - {a.get('message')}")
                    except Exception:
                        pass
            return all_completed
    except Exception as e:
        print(f"Error fetching jobs for run {run_id}: {e}")
        return False


def monitor_latest(target_sha: str | None = None, max_wait_seconds: int = 300) -> None:
    start_time = time.time()
    print(f"Monitoring GitHub Actions CI runs (Target SHA: {target_sha or 'Latest'})...")

    while time.time() - start_time < max_wait_seconds:
        runs = fetch_runs()
        if target_sha:
            matching = [r for r in runs if r.get("head_sha", "").startswith(target_sha)]
        else:
            matching = runs[:2]

        if matching:
            all_runs_done = True
            for r in matching:
                run_id = r["id"]
                name = r.get("name")
                status = r.get("status")
                conclusion = r.get("conclusion")
                sha = r.get("head_sha", "")[:7]
                print(f"\n[Run {run_id}] {name} ({sha}) -> Status: {status}, Conclusion: {conclusion}")
                done = inspect_run_jobs(run_id)
                if not done or status != "completed":
                    all_runs_done = False

            if all_runs_done:
                print("\nAll matching GitHub Action pipeline runs have finished.")
                return
        else:
            print("No matching runs found yet. Waiting for GitHub webhook trigger...")

        time.sleep(15)

    print("Reached timeout while monitoring CI runs.")


if __name__ == "__main__":
    import sys
    sha = sys.argv[1] if len(sys.argv) > 1 else None
    monitor_latest(target_sha=sha)

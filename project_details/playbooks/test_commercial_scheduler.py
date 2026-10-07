"""Regression: scheduled commercial breaks must fire on their own (no clicks).

Slow test (~7 minutes at max frequency): arms the scheduler at 10 breaks/hour
(one break every 6 minutes), loads the dashboard, and proves a break aired via
the last_commercial_break heartbeat. Fails if the break timer is starved by
the dashboard's 60-second refresh re-arming it before it can elapse.
"""

import asyncio
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)

TIMEOUT_SECONDS = 420  # 6-minute interval + 60s margin
POLL_SECONDS = 10

INIT_SCRIPT = """
    localStorage.setItem('openprevue_onboarded', '1');
    localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
    localStorage.setItem('openprevue_onboarding_completed', '1');
"""


def put_setting(key: str, value: str) -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        res = client.put(f"/api/v1/settings/{key}", json={"value": value})
        res.raise_for_status()


def get_setting(key: str) -> str | None:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        res = client.get("/api/v1/settings")
        res.raise_for_status()
        return res.json().get(key)


async def test_scheduler_fires_unaided() -> None:
    """Dashboard left alone must air a scheduled break within one interval."""
    put_setting("spotlight_mode", "featured_ads")
    put_setting("commercials_enabled", "1")
    put_setting("commercials_frequency_per_hour", "10")
    put_setting("commercials_source", "youtube")
    before = get_setting("last_commercial_break")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            await page.add_init_script(INIT_SCRIPT)
            await page.goto(BASE_URL + "/", wait_until="networkidle")
            await page.wait_for_selector(".overflow-y-auto", timeout=15000)

            heartbeat: str | None = None
            elapsed = 0
            while elapsed < TIMEOUT_SECONDS:
                await asyncio.sleep(POLL_SECONDS)
                elapsed += POLL_SECONDS
                heartbeat = get_setting("last_commercial_break")
                if heartbeat and heartbeat != before:
                    break

            assert heartbeat and heartbeat != before, (
                f"No scheduled break aired within {TIMEOUT_SECONDS}s "
                f"(heartbeat stuck at {before!r})"
            )
            print(f"Scheduled break verified: heartbeat {heartbeat} after ~{elapsed}s.")

            proof_path = PROOF_DIR / "test_commercial_scheduler_proof.png"
            await page.screenshot(path=str(proof_path))
            print(f"Captured proof: {proof_path}")
        finally:
            await browser.close()


async def main() -> None:
    try:
        await test_scheduler_fires_unaided()
    finally:
        put_setting("commercials_frequency_per_hour", "4")
    print("\nAll commercial scheduler tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

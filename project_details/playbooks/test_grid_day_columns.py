"""Verify schedule day columns: 3-day default vs wide-cell 2-day mode."""

import asyncio
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)

INIT_SCRIPT = """
    localStorage.setItem('openprevue_onboarded', '1');
    localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
    localStorage.setItem('openprevue_onboarding_completed', '1');
"""

HEADER_SCRIPT = """() => {
    const venue = [...document.querySelectorAll('div')]
        .find(d => d.textContent.trim() === 'VENUE / CHANNEL');
    const head = venue ? venue.parentElement : null;
    if (!head) return null;
    return {
        labels: [...head.children].map(c => c.textContent.trim()),
        spans: [...head.children].map(c =>
            c.className.includes('col-span-4') ? 4
            : (c.className.includes('col-span-3') ? 3 : 0)),
    };
}"""


def put_setting(key: str, value: str) -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        res = client.put(f"/api/v1/settings/{key}", json={"value": value})
        res.raise_for_status()


async def header_state(page) -> dict:
    state = await page.evaluate(HEADER_SCRIPT)
    assert state is not None, "Schedule header row not found"
    return state


async def test_day_columns() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            await page.add_init_script(INIT_SCRIPT)

            put_setting("grid_day_columns", "3day")
            await page.goto(f"{BASE_URL}/", wait_until="networkidle")
            await asyncio.sleep(1.0)
            three = await header_state(page)
            assert three["labels"] == [
                "VENUE / CHANNEL", "TODAY", "TONIGHT", "TOMORROW",
            ], f"Unexpected 3-day headers: {three['labels']}"
            assert three["spans"] == [3, 3, 3, 3], (
                f"Unexpected 3-day spans: {three['spans']}"
            )
            print("3-day default verified.")

            put_setting("grid_day_columns", "2day")
            await page.goto(f"{BASE_URL}/", wait_until="networkidle")
            await asyncio.sleep(1.0)
            two = await header_state(page)
            assert two["labels"] == ["VENUE / CHANNEL", "TODAY", "TOMORROW"], (
                f"Unexpected 2-day headers: {two['labels']}"
            )
            assert two["spans"] == [4, 4, 4], (
                f"Unexpected 2-day spans: {two['spans']}"
            )
            proof_path = PROOF_DIR / "test_grid_day_columns_proof.png"
            await page.screenshot(path=str(proof_path))
            print(f"Captured proof: {proof_path}")

            put_setting("grid_day_columns", "3day")
            await page.goto(f"{BASE_URL}/?columns=2", wait_until="networkidle")
            await asyncio.sleep(1.0)
            override = await header_state(page)
            assert override["labels"] == ["VENUE / CHANNEL", "TODAY", "TOMORROW"], (
                f"?columns=2 override failed: {override['labels']}"
            )
            print("?columns=2 kiosk override verified.")
        finally:
            await browser.close()


async def main() -> None:
    try:
        await test_day_columns()
    finally:
        put_setting("grid_day_columns", "3day")
    print("\nAll day-column tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

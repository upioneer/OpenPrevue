"""Verify split spotlight: showcase persists while retro ads air (wide screens)."""

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


def put_setting(key: str, value: str) -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        res = client.put(f"/api/v1/settings/{key}", json={"value": value})
        res.raise_for_status()


async def trigger_test_break(page) -> None:
    await page.goto(f"{BASE_URL}/settings?tab=commercials", wait_until="networkidle")
    await asyncio.sleep(1.0)
    btn = await page.wait_for_selector(
        "button:has-text('TEST PLAY COMMERCIAL CLIP')", timeout=8000
    )
    assert btn is not None, "Test play commercial button not found"
    await btn.click()
    await page.wait_for_url(f"{BASE_URL}/", timeout=8000)


async def test_split_wide() -> None:
    """Wide viewport: showcase and ad render side by side during a break."""
    put_setting("spotlight_mode", "featured_ads")
    put_setting("commercials_source", "youtube")
    page_errors: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            await page.add_init_script(INIT_SCRIPT)
            await trigger_test_break(page)

            showcase = await page.wait_for_selector(
                '[data-testid="split-showcase"]', timeout=8000
            )
            assert showcase is not None, "Split showcase pane did not render"
            assert await showcase.is_visible(), "Split showcase pane is hidden"

            ad_frame = await page.wait_for_selector(
                '[data-testid="split-ad"] iframe[src*="youtube.com/embed"]',
                timeout=20000,
            )
            assert ad_frame is not None, "Split ad player did not mount"

            pointer_events = await page.evaluate(
                """() => {
                    const frame = document.querySelector(
                        '[data-testid="split-ad"] iframe[src*="youtube.com/embed"]');
                    return frame && frame.parentElement
                        ? getComputedStyle(frame.parentElement).pointerEvents
                        : null;
                }"""
            )
            assert pointer_events == "none", (
                f"Ad surface must be non-interactive, got pointer-events={pointer_events}"
            )

            positions = await page.evaluate(
                """() => {
                    const copy = document.querySelector(
                        '[data-testid="split-showcase"] [data-testid="showcase-copy"]');
                    const art = document.querySelector(
                        '[data-testid="split-showcase"] [data-testid="showcase-art"]');
                    if (!copy || !art) return null;
                    return { copy: copy.getBoundingClientRect().x,
                             art: art.getBoundingClientRect().x };
                }"""
            )
            assert positions is not None, "Showcase copy/art columns not found"
            assert positions["copy"] < positions["art"], (
                f"Event copy must sit left of artwork, got {positions}"
            )

            constructor_errors = [e for e in page_errors if "Invalid video id" in e]
            assert not constructor_errors, (
                f"YouTube player failed to construct: {constructor_errors}"
            )

            proof_path = PROOF_DIR / "test_spotlight_split_proof.png"
            await page.screenshot(path=str(proof_path))
            print(f"Captured proof: {proof_path}")

            return_btn = await page.wait_for_selector(
                "button:has-text('[ RETURN TO GUIDE ]')", timeout=5000
            )
            await return_btn.click()
            await asyncio.sleep(0.5)
            split_after = await page.query_selector('[data-testid="split-showcase"]')
            assert split_after is None, "Split layout should dismiss after the break"
            print("Wide split verified: showcase persisted beside the retro ad.")
        finally:
            await browser.close()


async def test_split_narrow_fallback() -> None:
    """Narrow viewport: breaks fall back to full-takeover (no split)."""
    put_setting("spotlight_mode", "featured_ads")
    put_setting("commercials_source", "youtube")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 800, "height": 1280})
            await page.add_init_script(INIT_SCRIPT)
            await trigger_test_break(page)

            await page.wait_for_selector('iframe[src*="youtube.com/embed"]', timeout=20000)
            split = await page.query_selector('[data-testid="split-showcase"]')
            assert split is None, "Narrow screens must use full-takeover breaks"
            print("Narrow fallback verified: full-takeover break, no split.")
        finally:
            await browser.close()


async def main() -> None:
    try:
        await test_split_wide()
        await test_split_narrow_fallback()
    finally:
        put_setting("spotlight_mode", "featured")
    print("\nAll spotlight split tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

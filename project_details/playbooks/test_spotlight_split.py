"""Verify featured-ads pane takeover: copy persists while the ad consumes the art pane.

In featured_ads mode the showcase stays mounted across breaks. The left copy
column never resizes; only the right visuals pane swaps between artwork and
the retro ad, then resumes. Same behavior at every width, portrait included.
"""

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


async def copy_width(page) -> float:
    box = await page.evaluate(
        """() => {
            const copy = document.querySelector('[data-testid="showcase-copy"]');
            return copy ? copy.getBoundingClientRect().width : -1;
        }"""
    )
    assert box > 0, "Showcase copy column not found"
    return box


async def test_takeover_wide() -> None:
    """Wide viewport: ad consumes the art pane, copy width unchanged."""
    put_setting("spotlight_mode", "featured_ads")
    put_setting("commercials_source", "youtube")
    page_errors: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            await page.add_init_script(INIT_SCRIPT)
            await page.goto(BASE_URL + "/", wait_until="networkidle")
            await page.wait_for_selector('[data-testid="showcase-copy"]', timeout=8000)
            await page.wait_for_selector('[data-testid="showcase-art"]', timeout=8000)
            await asyncio.sleep(1.0)

            pre_iframe = await page.query_selector(
                '[data-testid="showcase-art"] iframe[src*="youtube.com/embed"]'
            )
            assert pre_iframe is None, "Ad player must not mount before a break"
            width_before = await copy_width(page)

            await trigger_test_break(page)
            ad_frame = await page.wait_for_selector(
                '[data-testid="showcase-art"] iframe[src*="youtube.com/embed"]',
                timeout=20000,
            )
            assert ad_frame is not None, "Ad did not take over the art pane"

            width_during = await copy_width(page)
            assert abs(width_during - width_before) <= 2, (
                f"Copy column resized during break: {width_before} -> {width_during}"
            )

            pointer_events = await page.evaluate(
                """() => {
                    const frame = document.querySelector(
                        '[data-testid="showcase-art"] iframe[src*="youtube.com/embed"]');
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
                    const copy = document.querySelector('[data-testid="showcase-copy"]');
                    const art = document.querySelector('[data-testid="showcase-art"]');
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
            iframe_after = await page.query_selector(
                '[data-testid="showcase-art"] iframe[src*="youtube.com/embed"]'
            )
            assert iframe_after is None, "Art pane should resume after the break"
            print("Wide takeover verified: copy steady while the ad owned the art pane.")
        finally:
            await browser.close()


async def test_takeover_narrow() -> None:
    """Narrow portrait: same pane swap, no full takeover."""
    put_setting("spotlight_mode", "featured_ads")
    put_setting("commercials_source", "youtube")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 500, "height": 900})
            await page.add_init_script(INIT_SCRIPT)
            await page.goto(BASE_URL + "/", wait_until="networkidle")
            await page.wait_for_selector('[data-testid="showcase-copy"]', timeout=8000)
            width_before = await copy_width(page)

            await trigger_test_break(page)
            ad_frame = await page.wait_for_selector(
                '[data-testid="showcase-art"] iframe[src*="youtube.com/embed"]',
                timeout=20000,
            )
            assert ad_frame is not None, "Ad did not take over the art pane"

            width_during = await copy_width(page)
            assert abs(width_during - width_before) <= 2, (
                f"Copy column resized during break: {width_before} -> {width_during}"
            )
            copy_visible = await page.is_visible('[data-testid="showcase-copy"]')
            assert copy_visible, "Copy column must persist during portrait breaks"
            print("Narrow takeover verified: pane swap in portrait, copy untouched.")
        finally:
            await browser.close()


async def main() -> None:
    try:
        await test_takeover_wide()
        await test_takeover_narrow()
    finally:
        put_setting("spotlight_mode", "featured")
    print("\nAll spotlight split tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

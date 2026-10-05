"""Test script to verify [ TEST PLAY COMMERCIAL CLIP (ON AIR) ] navigates to dashboard and plays commercial."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def test_commercial_trigger():
    page_errors: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
        """)

        print("Navigating to Settings Tab 4 (Commercials)...")
        await page.goto(f"{BASE_URL}/settings?tab=commercials", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # Click the test play commercial button
        btn = await page.wait_for_selector("button:has-text('TEST PLAY COMMERCIAL CLIP')", timeout=5000)
        assert btn is not None, "Test play commercial button not found"
        print("Clicking [ TEST PLAY COMMERCIAL CLIP (ON AIR) ]...")
        await btn.click()

        # Wait for navigation to /
        await page.wait_for_url(f"{BASE_URL}/", timeout=5000)
        print("Successfully navigated to main dashboard!")

        # Verify RETRO COMMERCIAL BREAK banner is visible
        comm_banner = await page.wait_for_selector("text=RETRO COMMERCIAL BREAK", timeout=5000)
        assert comm_banner is not None, "Retro commercial break banner not displayed"

        # Verify [ RETURN TO GUIDE ] button is visible
        return_btn = await page.wait_for_selector("button:has-text('[ RETURN TO GUIDE ]')", timeout=5000)
        assert return_btn is not None, "Return to guide button not found"

        # Regression: the YouTube player must actually mount (not just the banner).
        # An explicit videoId of undefined/null makes the IFrame API throw
        # "Invalid video id" and leaves the player div empty for playlists.
        yt_frame = await page.wait_for_selector('iframe[src*="youtube.com/embed"]', timeout=20000)
        assert yt_frame is not None, "YouTube commercial player iframe did not mount"
        constructor_errors = [e for e in page_errors if "Invalid video id" in e]
        assert not constructor_errors, f"YouTube player failed to construct: {constructor_errors}"

        # Capture proof screenshot
        proof_path = PROOF_DIR / "test_commercial_on_air_proof.png"
        await page.screenshot(path=str(proof_path))
        print(f"Captured proof: {proof_path}")

        # Test [ RETURN TO GUIDE ] click
        print("Clicking [ RETURN TO GUIDE ]...")
        await return_btn.click()
        await asyncio.sleep(0.5)

        # Verify commercial concluded and returned to spotlight
        comm_banner_after = await page.query_selector("text=RETRO COMMERCIAL BREAK")
        assert comm_banner_after is None, "Commercial banner should be dismissed"
        print("Successfully dismissed commercial and returned to guide!")

        await page.close()
        await browser.close()
        print("\nAll commercial test trigger tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_commercial_trigger())

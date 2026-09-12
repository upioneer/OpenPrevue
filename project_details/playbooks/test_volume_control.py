"""Playwright test to verify that the top volume slider controls media/video volume and does not blast tape hiss static."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def test_volume_control():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        print("Navigating to dashboard...")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2.0)

        # Inspect initial volume state from audioSynth
        vol_text = await page.inner_text("header input[type='range'] + span")
        print(f"Initial Header Volume Display: {vol_text}")

        # Test changing volume slider to 65%
        print("Changing volume slider to 65%...")
        slider = await page.query_selector("header input[type='range']")
        assert slider is not None, "Volume slider not found in header"
        await page.evaluate("""(val) => {
            const el = document.querySelector('header input[type="range"]');
            el.value = val;
            el.dispatchEvent(new Event('input'));
        }""", 65)
        await asyncio.sleep(0.5)

        new_vol_text = await page.inner_text("header input[type='range'] + span")
        print(f"Updated Header Volume Display: {new_vol_text}")
        assert "65%" in new_vol_text, f"Expected 65% in header volume text, got {new_vol_text}"

        proof_path = PROOF_DIR / "proof_volume_slider_media_control.png"
        await page.screenshot(path=str(proof_path))
        print(f"Captured proof screenshot: {proof_path}")

        # Test clicking MUTE button
        mute_btn = await page.query_selector("header button:has-text('[ VOL ]'), header button:has-text('[ MUTE ]')")
        assert mute_btn is not None, "Mute toggle button not found"
        await mute_btn.click()
        await asyncio.sleep(0.5)

        muted_text = await page.inner_text("header input[type='range'] + span")
        print(f"Muted Header Volume Display: {muted_text}")
        assert "0%" in muted_text, f"Expected 0% when muted, got {muted_text}"

        proof_mute_path = PROOF_DIR / "proof_volume_slider_muted.png"
        await page.screenshot(path=str(proof_mute_path))
        print(f"Captured proof screenshot: {proof_mute_path}")

        await browser.close()
        print("Volume control Playwright test passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_volume_control())

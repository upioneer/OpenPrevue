"""Verify one-direction repeating headline marquee in event cells."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def test_marquee():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
        """)

        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2.0)

        # Check for animate-headline-marquee elements
        marquees = await page.query_selector_all(".animate-headline-marquee")
        print(f"Found {len(marquees)} overflowing scrolling headline marquee elements.")
        assert len(marquees) > 0, "No animated marquee elements found"

        first_marquee = marquees[0]
        marquee_html = await first_marquee.inner_html()
        assert "//" in marquee_html, "Broadcast separator '//' not found in marquee track"
        print("Verified repeating blocks with '//' separator!")

        # Capture proof screenshot showing the scrolling headlines
        proof_path = PROOF_DIR / "oneway_repeating_marquee_proof.png"
        await page.screenshot(path=str(proof_path))
        print(f"Captured proof screenshot: {proof_path}")

        # Click the marquee to verify EventDetailModal still opens
        print("Testing click on marquee opens EventDetailModal...")
        await first_marquee.click()
        await asyncio.sleep(1.0)

        modal = await page.wait_for_selector("[role='dialog']", timeout=5000)
        assert modal is not None, "Modal did not open on marquee click"
        print("Successfully verified EventDetailModal opens from clicking repeating marquee!")

        await page.close()
        await browser.close()
        print("\nAll one-direction repeating marquee tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_marquee())

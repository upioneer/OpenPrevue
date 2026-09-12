"""Verify UpdateModal segmented LED progress bar and dry-run animation."""

import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # Navigate to /settings?tab=updates
        await page.goto("http://localhost:8080/settings?tab=updates", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # Open the firmware upgrade modal
        launch_btn = await page.query_selector("button:has-text('LAUNCH FIRMWARE UPGRADE ENGINE')")
        if launch_btn:
            await launch_btn.click()
            await asyncio.sleep(0.8)

            # Screenshot 1: Initial opened state (clean LED segments, ready status)
            await page.screenshot(path="project_details/proof/proof_modal_led_idle.png")
            print("Captured: proof_modal_led_idle.png")

            # Click TEST DRY-RUN
            dry_run_btn = await page.query_selector("button:has-text('[ TEST DRY-RUN ]')")
            if dry_run_btn:
                await dry_run_btn.click()
                # Wait for mid-run animation
                await asyncio.sleep(0.8)
                await page.screenshot(path="project_details/proof/proof_modal_led_animating.png")
                print("Captured: proof_modal_led_animating.png")

                # Wait for dry-run completion
                await asyncio.sleep(2.0)
                await page.screenshot(path="project_details/proof/proof_modal_led_completed.png")
                print("Captured: proof_modal_led_completed.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())

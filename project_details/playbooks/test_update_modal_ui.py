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

        # 1. Capture Tab 10 with Advanced Diagnostics accordion
        diag_toggle = await page.query_selector("button:has-text('[ ADVANCED UPGRADE DIAGNOSTICS')")
        if diag_toggle:
            await diag_toggle.click()
            await asyncio.sleep(0.5)
        await page.screenshot(path="project_details/proof/proof_tab10_advanced_diagnostics.png")
        print("Captured: proof_tab10_advanced_diagnostics.png")

        # 2. Open normal upgrade modal (Standard user view: ONLY Apply Live Upgrade in footer)
        launch_btn = await page.query_selector("button:has-text('LAUNCH FIRMWARE UPGRADE ENGINE')")
        if launch_btn:
            await launch_btn.click()
            await asyncio.sleep(0.8)
            await page.screenshot(path="project_details/proof/proof_modal_standard_user.png")
            print("Captured: proof_modal_standard_user.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

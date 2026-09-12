"""Verify direct deep-linking and tab query routing in SettingsView."""

import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # Test 1: Direct navigation to /settings?tab=updates
        await page.goto("http://localhost:8080/settings?tab=updates", wait_until="networkidle")
        await asyncio.sleep(1.0)
        content = await page.content()
        is_updates_active = "FIRMWARE UPGRADE ENGINE" in content or "SYSTEM & UPDATES" in content
        print("Direct /settings?tab=updates active:", is_updates_active)
        await page.screenshot(path="project_details/proof/proof_tab10_direct_navigation.png")

        # Test 2: Click another tab (e.g. Tab 2 Display) and check URL query
        display_tab_btn = await page.query_selector("button:has-text('[ 2. DISPLAY & KIOSK POWER ]')")
        if display_tab_btn:
            await display_tab_btn.click()
            await asyncio.sleep(0.5)
            print("URL after clicking Display tab:", page.url)

        # Test 3: Navigate back to /settings without query -> defaults to location
        await page.goto("http://localhost:8080/settings", wait_until="networkidle")
        await asyncio.sleep(0.5)
        content_loc = await page.content()
        print("Direct /settings defaults to Location tab:", "LATITUDE" in content_loc or "POSTAL CODE" in content_loc)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())

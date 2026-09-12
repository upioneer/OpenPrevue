import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # Navigate to Settings Tab 2
        await page.goto("http://localhost:8080/settings?tab=display", wait_until="networkidle")
        await asyncio.sleep(1.0)
        await page.screenshot(path="project_details/proof/proof_tab2_listing_filter.png")
        print("Captured: proof_tab2_listing_filter.png")

        # Test clicking the All Venues toggle
        all_btn = await page.query_selector("button:has-text('[ ALL VENUES & SUBSCRIPTIONS ]')")
        if all_btn:
            await all_btn.click()
            await asyncio.sleep(0.5)
            await page.screenshot(path="project_details/proof/proof_tab2_listing_filter_all_selected.png")
            print("Captured: proof_tab2_listing_filter_all_selected.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

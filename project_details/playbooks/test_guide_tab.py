import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page.goto("http://localhost:8080/settings?tab=guide", wait_until="networkidle")
        await asyncio.sleep(0.5)
        await page.evaluate("document.querySelector('.overflow-y-auto').scrollTop = 850")
        await asyncio.sleep(0.5)
        await page.screenshot(path="project_details/proof/proof_tab11_kiosk_guide_scroll.png")
        print("Captured proof_tab11_kiosk_guide_scroll.png successfully")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

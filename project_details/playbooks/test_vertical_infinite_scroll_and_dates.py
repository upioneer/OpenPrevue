import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Test 9:16 vertical kiosk portrait resolution (1080x1920)
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        await page.goto("http://localhost:8080/", wait_until="networkidle")
        await asyncio.sleep(2.0)

        # Inspect number of rendered rows in TimelineGrid
        rows = await page.query_selector_all(".flex-1.overflow-y-auto > div > div")
        print(f"Rendered rows count in vertical kiosk: {len(rows)}")
        assert len(rows) >= 36, f"Expected at least 36 rows to fill vertical viewport, got {len(rows)}"

        # Initial scrollTop check
        initial_scroll = await page.evaluate("() => document.querySelector('.flex-1.overflow-y-auto')?.scrollTop || 0")
        print(f"Initial scrollTop: {initial_scroll}")

        # Wait for auto-scroll step
        await asyncio.sleep(5.0)

        new_scroll = await page.evaluate("() => document.querySelector('.flex-1.overflow-y-auto')?.scrollTop || 0")
        print(f"After 5s autoscroll, scrollTop: {new_scroll}")
        assert new_scroll > 0, f"Expected grid to scroll continuously rather than freeze, got scrollTop={new_scroll}"

        # Capture proof screenshot
        await page.screenshot(path="project_details/proof/proof_vertical_kiosk_full_scroll.png")
        print("Captured: project_details/proof/proof_vertical_kiosk_full_scroll.png")

        # Verify today and tomorrow columns do NOT contain 10/5 event
        today_texts = await page.evaluate("""() => {
            const cols = document.querySelectorAll('.flex-1.overflow-y-auto > div > div > div:nth-child(2)');
            return Array.from(cols).map(c => c.textContent);
        }""")
        tomorrow_texts = await page.evaluate("""() => {
            const cols = document.querySelectorAll('.flex-1.overflow-y-auto > div > div > div:nth-child(4)');
            return Array.from(cols).map(c => c.textContent);
        }""")

        for text in today_texts + tomorrow_texts:
            assert "10/5" not in text and "OCTOBER 5" not in text.upper(), f"Found unexpected 10/5 event in active slots: {text}"

        print("[PASS] Vertical kiosk infinite scroll and date slotting fully verified!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

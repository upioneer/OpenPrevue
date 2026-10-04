import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_welcome_dismissed', '1');
            localStorage.setItem('openprevue_seen_changelog_v0.27.0', '1');
            localStorage.setItem('openprevue_seen_changelog_0.27.0', '1');
        """)
        
        await page.goto("http://localhost:8080/?kiosk=1", wait_until="networkidle")
        await asyncio.sleep(2)
        
        buttons = await page.query_selector_all("button.rounded-full")
        print(f"Found {len(buttons)} rotation buttons")
        
        for idx in range(len(buttons)):
            btns = await page.query_selector_all("button.rounded-full")
            if idx < len(btns):
                await btns[idx].click(force=True)
                await asyncio.sleep(0.5)
            
            # Get event title from spotlight
            title_el = await page.query_selector("div.text-base.font-black, div.text-xl.font-black, div.line-clamp-2")
            title = await title_el.inner_text() if title_el else "Unknown"
            
            # Left column container
            left_col = await page.query_selector(".w-\\[48\\%\\]")
            if left_col:
                imgs = await left_col.query_selector_all("img")
                img_srcs = [await img.get_attribute("src") for img in imgs]
                spans = await left_col.query_selector_all(".rounded-full span")
                span_texts = [await s.inner_text() for s in spans]
                print(f"Slide {idx}: Title='{title}' | Imgs={img_srcs} | Spans={span_texts}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())

"""Visual verification script to ensure Featured Section renders prominently on 1080p screens."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("project_details") / "proof"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "http://localhost:8080"


async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # Test Case 1: 1080p with normal browser window chrome (1920x920, ratio 2.08) - Balanced (7 rows)
        page_windowed = await context.new_page()
        await page_windowed.set_viewport_size({"width": 1920, "height": 920})
        await page_windowed.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        print("Captured 1920x920 Balanced")
        await page_windowed.screenshot(path=str(OUTPUT_DIR / "proof_1080p_windowed_featured.png"))
        await page_windowed.close()

        # Test Case 1B: Classic TV (4 rows) on 1080p
        import sqlite3
        conn = sqlite3.connect("data/openprevue.db")
        conn.execute("UPDATE settings SET value = 'classic_tv' WHERE key = 'grid_density'")
        conn.commit()
        conn.close()
        page_classic = await context.new_page()
        await page_classic.set_viewport_size({"width": 1920, "height": 920})
        await page_classic.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        print("Captured 1920x920 Classic TV")
        await page_classic.screenshot(path=str(OUTPUT_DIR / "proof_1080p_windowed_classic_tv.png"))
        await page_classic.close()

        # Test Case 1C: Single Row (1 row) on 1080p
        conn = sqlite3.connect("data/openprevue.db")
        conn.execute("UPDATE settings SET value = 'single_row' WHERE key = 'grid_density'")
        conn.commit()
        conn.close()
        page_single = await context.new_page()
        await page_single.set_viewport_size({"width": 1920, "height": 920})
        await page_single.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        print("Captured 1920x920 Single Row")
        await page_single.screenshot(path=str(OUTPUT_DIR / "proof_1080p_windowed_single_row.png"))
        await page_single.close()

        # Restore balanced
        conn = sqlite3.connect("data/openprevue.db")
        conn.execute("UPDATE settings SET value = 'balanced' WHERE key = 'grid_density'")
        conn.commit()
        conn.close()

        # Test Case 2: 1080p Fullscreen (1920x1080)
        page_full = await context.new_page()
        await page_full.set_viewport_size({"width": 1920, "height": 1080})
        await page_full.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        content_full = await page_full.content()
        has_spotlight_full = "SPOTLIGHT" in content_full or "HEADLINE PREVIEW" in content_full or "VS" in content_full
        print(f"1920x1080 (Fullscreen 1080p) -> Spotlight Present: {has_spotlight_full}")
        await page_full.screenshot(path=str(OUTPUT_DIR / "proof_1080p_fullscreen_featured.png"))
        await page_full.close()

        # Test Case 3: Settings View live detection badge
        page_settings = await context.new_page()
        await page_settings.set_viewport_size({"width": 1920, "height": 920})
        await page_settings.goto(f"{BASE_URL}/settings", wait_until="networkidle")
        await asyncio.sleep(1.5)
        # Click Tab 2 (Display & Kiosk Power)
        tab_buttons = await page_settings.query_selector_all("button")
        for btn in tab_buttons:
            text = await btn.inner_text()
            if "DISPLAY & KIOSK" in text or "DISPLAY" in text:
                await btn.click()
                break
        await asyncio.sleep(1.5)
        settings_content = await page_settings.content()
        print(f"Settings Viewport Label -> {'16:9 STANDARD' in settings_content or 'VIEWPORT:' in settings_content}")
        await page_settings.screenshot(path=str(OUTPUT_DIR / "proof_settings_1080p_badge.png"))
        await page_settings.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(verify())

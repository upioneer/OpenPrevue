"""Capture ultrawide and rack bar screenshots to verify visual layouts."""

import asyncio
from pathlib import Path
import sqlite3
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
DB_PATH = Path("data") / "openprevue.db"
OUTPUT_DIR = Path("project_details") / "proof"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def set_setting(key: str, val: str) -> None:
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))
        conn.commit()
        conn.close()


async def capture_ultrawide():
    set_setting("initial_setup_completed", "1")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # 1. 10" Rack Display (1920x480) - Feature Priority (Spotlight + 1 row below)
        set_setting("ultrawide_mode", "always")
        set_setting("ultrawide_priority", "feature")
        page_rack_feat = await context.new_page()
        await page_rack_feat.set_viewport_size({"width": 1920, "height": 480})
        await page_rack_feat.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_rack_feat.screenshot(path=str(OUTPUT_DIR / "rack_1920x480_feature_priority.png"))
        print("Captured: rack_1920x480_feature_priority.png")
        await page_rack_feat.close()

        # 2. 10" Rack Display (1920x480) - Calendar Priority (Full-screen grid, 1 row)
        set_setting("ultrawide_priority", "calendar")
        set_setting("grid_density", "single_row")
        page_rack_cal = await context.new_page()
        await page_rack_cal.set_viewport_size({"width": 1920, "height": 480})
        await page_rack_cal.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_rack_cal.screenshot(path=str(OUTPUT_DIR / "rack_1920x480_calendar_priority_1row.png"))
        print("Captured: rack_1920x480_calendar_priority_1row.png")
        await page_rack_cal.close()

        # 3. 10" Rack Display (1920x480) - Calendar Priority (Classic TV 4 rows)
        set_setting("grid_density", "classic_tv")
        page_rack_cal4 = await context.new_page()
        await page_rack_cal4.set_viewport_size({"width": 1920, "height": 480})
        await page_rack_cal4.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_rack_cal4.screenshot(path=str(OUTPUT_DIR / "rack_1920x480_calendar_priority_4rows.png"))
        print("Captured: rack_1920x480_calendar_priority_4rows.png")
        await page_rack_cal4.close()

        # 4. Desktop Ultrawide (3440x1440) - Feature Priority (Spotlight + 1 row below)
        set_setting("ultrawide_priority", "feature")
        page_desk_feat = await context.new_page()
        await page_desk_feat.set_viewport_size({"width": 3440, "height": 1440})
        await page_desk_feat.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_desk_feat.screenshot(path=str(OUTPUT_DIR / "desktop_3440x1440_feature_priority.png"))
        print("Captured: desktop_3440x1440_feature_priority.png")
        await page_desk_feat.close()

        # 5. Desktop Ultrawide (3440x1440) - Calendar Priority (Full-screen grid, balanced)
        set_setting("ultrawide_priority", "calendar")
        set_setting("grid_density", "balanced")
        page_desk_cal = await context.new_page()
        await page_desk_cal.set_viewport_size({"width": 3440, "height": 1440})
        await page_desk_cal.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_desk_cal.screenshot(path=str(OUTPUT_DIR / "desktop_3440x1440_calendar_priority.png"))
        print("Captured: desktop_3440x1440_calendar_priority.png")
        await page_desk_cal.close()

        # 6. Settings Tab 2
        set_setting("ultrawide_mode", "auto")
        page_settings = await context.new_page()
        await page_settings.set_viewport_size({"width": 1920, "height": 1080})
        await page_settings.goto(f"{BASE_URL}/settings", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await page_settings.click("text=[ 2. DISPLAY & KIOSK POWER ]")
        await asyncio.sleep(1)
        await page_settings.screenshot(path=str(OUTPUT_DIR / "settings_ultrawide_panel.png"))
        print("Captured: settings_ultrawide_panel.png")
        await page_settings.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_ultrawide())

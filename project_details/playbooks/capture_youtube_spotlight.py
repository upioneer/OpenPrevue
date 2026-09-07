"""Capture visual proof for YouTube video streaming and aspect ratio controls."""

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


async def capture_all():
    set_setting("initial_setup_completed", "1")
    set_setting("spotlight_mode", "youtube")
    set_setting("youtube_source_url", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    set_setting("youtube_aspect_ratio", "4:3")
    set_setting("youtube_audio_mode", "mute")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # 1. Settings Tab 2 with YouTube Stream Card
        page_settings = await context.new_page()
        await page_settings.set_viewport_size({"width": 1920, "height": 1080})
        await page_settings.goto(f"{BASE_URL}/settings", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await page_settings.click("text=[ 2. DISPLAY & KIOSK POWER ]")
        await asyncio.sleep(1)
        await page_settings.click("text=[ TEST / VERIFY URL ]")
        await asyncio.sleep(2)
        await page_settings.screenshot(path=str(OUTPUT_DIR / "settings_youtube_stream_config.png"))
        print("Captured settings_youtube_stream_config.png")
        await page_settings.close()

        # 2. 16:9 Standard Dashboard with 4:3 CRT YouTube Stream
        set_setting("ultrawide_mode", "disabled")
        page_dash = await context.new_page()
        await page_dash.set_viewport_size({"width": 1920, "height": 1080})
        await page_dash.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(3)
        await page_dash.screenshot(path=str(OUTPUT_DIR / "dashboard_youtube_43_crt.png"))
        print("Captured dashboard_youtube_43_crt.png")
        await page_dash.close()

        # 3. 10" Rack Bar Display (1920x480) with YouTube Stream in Feature Priority
        set_setting("ultrawide_mode", "always")
        set_setting("ultrawide_priority", "feature")
        page_rack = await context.new_page()
        await page_rack.set_viewport_size({"width": 1920, "height": 480})
        await page_rack.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(3)
        await page_rack.screenshot(path=str(OUTPUT_DIR / "rack_1920x480_youtube_stream.png"))
        print("Captured rack_1920x480_youtube_stream.png")
        await page_rack.close()

        # 4. Fallback: Spotlight Mode back to Featured
        set_setting("spotlight_mode", "featured")
        page_fallback = await context.new_page()
        await page_fallback.set_viewport_size({"width": 1920, "height": 1080})
        await page_fallback.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page_fallback.screenshot(path=str(OUTPUT_DIR / "dashboard_fallback_featured.png"))
        print("Captured dashboard_fallback_featured.png")
        await page_fallback.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_all())

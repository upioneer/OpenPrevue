"""Automated Playwright screenshot capture script for version changelogs."""

import argparse
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8000"


async def capture_changelog_screenshots(version: str) -> None:
    """Capture responsive viewports and views for version changelog documentation."""
    version_dir = Path("project_details") / "changelog" / version
    version_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting Playwright screenshot capture for {version} -> {version_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Standard 16:9 Landscape TV Dashboard (1920x1080)
        page_landscape = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_landscape.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2)  # Allow WebSocket connection & initial rotation
        dashboard_path = version_dir / "dashboard_landscape.png"
        await page_landscape.screenshot(path=str(dashboard_path))
        print(f"Captured: {dashboard_path}")
        await page_landscape.close()

        # 2. Vertical 9:16 Portrait Kiosk Display (1080x1920)
        page_portrait = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page_portrait.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        portrait_path = version_dir / "dashboard_portrait.png"
        await page_portrait.screenshot(path=str(portrait_path))
        print(f"Captured: {portrait_path}")
        await page_portrait.close()

        # 3. Small Raspberry Pi 7" Touchscreen (800x480)
        page_pi = await browser.new_page(viewport={"width": 800, "height": 480})
        await page_pi.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        pi_path = version_dir / "dashboard_small_pi.png"
        await page_pi.screenshot(path=str(pi_path))
        print(f"Captured: {pi_path}")
        await page_pi.close()

        # 4. Settings Control Center (1920x1080)
        page_settings = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_settings.goto(f"{BASE_URL}/#/settings", wait_until="networkidle")
        await asyncio.sleep(1.5)
        settings_path = version_dir / "settings_control_center.png"
        await page_settings.screenshot(path=str(settings_path))
        print(f"Captured: {settings_path}")
        await page_settings.close()

        await browser.close()

    print(f"Completed screenshot capture for {version}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture OpenPrevue Playwright screenshots.")
    parser.add_argument("--version", type=str, default="v0.12.0", help="Target version tag (e.g. v0.12.0)")
    args = parser.parse_args()

    target_ver = args.version if args.version.startswith("v") else f"v{args.version}"
    asyncio.run(capture_changelog_screenshots(target_ver))

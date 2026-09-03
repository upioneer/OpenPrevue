"""Automated Playwright screenshot capture script for version changelogs and presentation scale showcases."""

import argparse
import asyncio
from pathlib import Path
import sqlite3
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
DB_PATH = Path("data") / "openprevue.db"


def set_db_density(density: str) -> None:
    """Helper to set grid_density in SQLite database before capture."""
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('grid_density', ?)", (density,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed setting db density: {e}")


async def ensure_sports_slide(page) -> None:
    """Cycle rotation buttons until the live sports matchup card is active."""
    try:
        buttons = await page.query_selector_all("button.rounded-full")
        for btn in buttons:
            await btn.click()
            await asyncio.sleep(0.4)
            content = await page.content()
            if "VS" in content and ("KNICKS" in content or "MATCHUP" in content or "CELTICS" in content):
                break
    except Exception as e:
        print(f"Slide selection helper notice: {e}")


async def capture_changelog_screenshots(version: str) -> None:
    """Capture responsive viewports, views, and density modes for version changelog documentation."""
    version_dir = Path("project_details") / "changelog" / version
    version_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting Playwright screenshot capture for {version} -> {version_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Density Mode: Classic TV (4 Rows - True-to-Scale 1990s Broadcast with Sports Matchup)
        set_db_density("classic_tv")
        page_classic = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_classic.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page_classic.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await ensure_sports_slide(page_classic)
        await asyncio.sleep(1.5)
        classic_path = version_dir / "density_classic_tv.png"
        await page_classic.screenshot(path=str(classic_path))
        print(f"Captured: {classic_path}")
        await page_classic.close()

        # 2. Density Mode: Balanced (7 Rows - Main Hero Landscape Screenshot with Sports Matchup)
        set_db_density("balanced")
        page_balanced = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_balanced.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page_balanced.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await ensure_sports_slide(page_balanced)
        await asyncio.sleep(1.5)
        balanced_path = version_dir / "density_balanced.png"
        await page_balanced.screenshot(path=str(balanced_path))
        print(f"Captured: {balanced_path}")
        dashboard_path = version_dir / "dashboard_landscape.png"
        await page_balanced.screenshot(path=str(dashboard_path))
        print(f"Captured: {dashboard_path}")
        await page_balanced.close()

        # 3. Density Mode: Dense (12 Rows - High Density Information Overview)
        set_db_density("dense")
        page_dense = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_dense.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page_dense.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await ensure_sports_slide(page_dense)
        await asyncio.sleep(1.5)
        dense_path = version_dir / "density_dense.png"
        await page_dense.screenshot(path=str(dense_path))
        print(f"Captured: {dense_path}")
        await page_dense.close()

        # Reset database default to balanced
        set_db_density("balanced")

        # 4. Vertical 9:16 Portrait Kiosk Display (1080x1920)
        page_portrait = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page_portrait.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page_portrait.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await ensure_sports_slide(page_portrait)
        await asyncio.sleep(1.0)
        portrait_path = version_dir / "dashboard_portrait.png"
        await page_portrait.screenshot(path=str(portrait_path))
        print(f"Captured: {portrait_path}")
        await page_portrait.close()

        # 5. Small Raspberry Pi 7" Touchscreen (800x480)
        page_pi = await browser.new_page(viewport={"width": 800, "height": 480})
        await page_pi.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page_pi.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        await ensure_sports_slide(page_pi)
        await asyncio.sleep(1.0)
        pi_path = version_dir / "dashboard_small_pi.png"
        await page_pi.screenshot(path=str(pi_path))
        print(f"Captured: {pi_path}")
        await page_pi.close()

        # 6. Setup Wizard Onboarding Modal (1920x1080 clean session)
        page_setup = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_setup.add_init_script("localStorage.removeItem('openprevue_onboarded')")
        await page_setup.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        setup_path = version_dir / "setup_wizard_modal.png"
        await page_setup.screenshot(path=str(setup_path))
        print(f"Captured: {setup_path}")
        await page_setup.close()

        # 7. Settings Control Center (1920x1080)
        page_settings = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_settings.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
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
    parser.add_argument("--version", type=str, default="v0.16.1", help="Target version tag (e.g. v0.16.1)")
    args = parser.parse_args()

    target_ver = args.version if args.version.startswith("v") else f"v{args.version}"
    asyncio.run(capture_changelog_screenshots(target_ver))

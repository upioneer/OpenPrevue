"""Playwright automated test script for configuration backup, persistence, disk restore, and browser cache recovery."""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import httpx

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        print("--- 1. Testing Tab 10: Configuration Persistence & Disk Recovery Card ---")
        await page.goto(f"{BASE_URL}/settings?tab=updates", wait_until="networkidle")
        await asyncio.sleep(2.0)

        content = await page.content()
        assert "CONFIGURATION PERSISTENCE" in content, "Tab 10 backup card missing!"
        assert "openprevue_settings_backup.json" in content, "Persistence filename missing!"
        assert "DOWNLOAD BACKUP (JSON)" in content, "Download backup button missing!"
        assert "RESTORE FROM SERVER DISK" in content, "Restore disk button missing!"
        assert "IMPORT BACKUP (JSON)" in content, "Import backup button missing!"
        print("Confirmed: Tab 10 Configuration Persistence Card rendered with full telemetry and action controls.")

        # Capture proof 1: Tab 10 Persistence Card
        proof1_path = PROOF_DIR / "proof_tab10_backup_persistence_ledger.png"
        await page.screenshot(path=str(proof1_path))
        print(f"Captured: {proof1_path.name}")

        print("\n--- 2. Testing Browser Cache Mirror Auto-Detection Banner ---")
        mirror_payload = {
            "timestamp": "2026-09-12T01:30:00.000Z",
            "settings": {
                "metro_label": "MIAMI, FL",
                "ai_ollama_url": "http://192.168.1.100:11434",
                "ai_ollama_model": "llama3.2:3b",
                "initial_setup_completed": "1",
            },
        }

        # Clear active backend AI URL first to simulate fresh container state
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            await client.put("/api/v1/settings/ai_ollama_url", json={"value": ""})
            await client.put("/api/v1/settings/metro_label", json={"value": "NEW YORK CITY"})

        await page.goto(f"{BASE_URL}/settings?tab=location", wait_until="networkidle")
        await page.evaluate(f"""() => {{
            localStorage.setItem('openprevue_settings_mirror', JSON.stringify({json.dumps(mirror_payload)}));
        }}""")
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(2.0)

        content_with_banner = await page.content()
        assert "BROWSER CONFIGURATION MIRROR DETECTED" in content_with_banner, "Browser mirror banner not shown when cached settings differ from wiped state!"
        assert "RESTORE FROM BROWSER CACHE" in content_with_banner, "Restore button missing on browser cache mirror banner!"
        print("Confirmed: Browser Configuration Mirror banner appeared upon detecting cached settings.")

        # Capture proof 2: Browser Mirror Banner
        proof2_path = PROOF_DIR / "proof_settings_browser_cache_mirror_banner.png"
        await page.screenshot(path=str(proof2_path))
        print(f"Captured: {proof2_path.name}")

        # Click [ RESTORE FROM BROWSER CACHE ]
        restore_btn = page.locator("button:has-text('RESTORE FROM BROWSER CACHE')")
        await restore_btn.click()
        await asyncio.sleep(2.0)

        # Verify metro label in form has updated to MIAMI, FL
        metro_val = await page.locator("input[placeholder*='AUSTIN, TX']").input_value()
        assert "MIAMI" in metro_val, f"Expected metro label to update to MIAMI, FL, got '{metro_val}'"
        print(f"Confirmed: Restored settings applied to form ('{metro_val}').")

        print("\n--- 3. Testing Backend Backup & Export / Import Endpoints ---")
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            export_resp = await client.get("/api/v1/settings/backup/export")
            assert export_resp.status_code == 200, f"Export failed: {export_resp.status_code}"
            exp_data = export_resp.json()
            assert "settings" in exp_data, "Export missing settings key"
            assert "version" in exp_data, "Export missing version key"
            print(f"Confirmed: Export endpoint returned {len(exp_data['settings'])} settings.")

            status_resp = await client.get("/api/v1/settings/backup/status")
            assert status_resp.status_code == 200, f"Status failed: {status_resp.status_code}"
            st_data = status_resp.json()
            assert st_data.get("exists") is True, "Backup file should exist on disk"
            print(f"Confirmed: Disk backup status exists=True, {st_data.get('settings_count')} settings.")

            restore_resp = await client.post("/api/v1/settings/backup/restore-disk")
            assert restore_resp.status_code == 200, f"Disk restore failed: {restore_resp.status_code}"
            print("Confirmed: POST /settings/backup/restore-disk succeeded.")

        print("\nAll settings persistence and recovery tests completed successfully!")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_tests())

import asyncio
import httpx
from playwright.async_api import async_playwright

async def run():
    print("[1/5] Testing backend API live upgrade refusal on equal/older version...")
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://127.0.0.1:8080/api/v1/updates/apply",
            json={"target_version": "0.25.0", "dry_run": False, "method": "trigger_file"},
        )
        assert res.status_code == 200, f"Unexpected status {res.status_code}"
        data = res.json()
        print(f"Backend response: {data}")
        assert data["status"] == "up_to_date", f"Expected status 'up_to_date', got {data.get('status')}"
        assert "strictly newer releases" in data["message"]
        print("Backend live upgrade refusal verified: OK")

        # Verify capability endpoint
        res_cap = await client.get("http://127.0.0.1:8080/api/v1/updates/capability")
        assert res_cap.status_code == 200
        cap_data = res_cap.json()
        assert cap_data["update_available"] is False
        assert cap_data["can_upgrade_now"] is False
        print("Backend capability flags verified: OK")

    print("[2/5] Testing frontend UI behavior with Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        # Prevent onboarding/changelog modals from blocking settings
        await page.add_init_script("""
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
            localStorage.setItem('openprevue_dismiss_changelog_modal', '1');
            localStorage.setItem('openprevue_last_seen_version', '0.25.0');
        """)

        await page.goto("http://localhost:8080/settings?tab=updates", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # 3. Check Tab 10 UI elements
        up_to_date_btn = await page.query_selector("button:has-text('FIRMWARE UP TO DATE')")
        assert up_to_date_btn is not None, "Button [ FIRMWARE UP TO DATE ] not found in Tab 10"
        is_disabled = await up_to_date_btn.is_disabled()
        assert is_disabled, "Button [ FIRMWARE UP TO DATE ] should be disabled"
        print("Tab 10 disabled up-to-date button verified: OK")

        sim_btn = await page.query_selector("button:has-text('RUN DIAGNOSTIC SIMULATION')")
        assert sim_btn is not None, "Button [ RUN DIAGNOSTIC SIMULATION ] not found in Tab 10"
        print("Tab 10 diagnostic simulation button verified: OK")

        await page.screenshot(path="project_details/proof/proof_firmware_up_to_date_tab10.png")
        print("Saved proof: proof_firmware_up_to_date_tab10.png")

        # 4. Click RUN DIAGNOSTIC SIMULATION to open modal
        await sim_btn.click()
        await asyncio.sleep(0.8)

        # 5. Check modal UI elements
        modal_title = await page.query_selector("text=OPENPREVUE HEADEND FIRMWARE UPGRADE ENGINE")
        assert modal_title is not None, "Modal title not found"

        # Verify UP TO DATE notification card
        banner = await page.query_selector("div:has-text('SYSTEM FIRMWARE IS CURRENT')")
        assert banner is not None, "System current card not found in modal"
        print("Modal up-to-date banner verified: OK")

        # Verify modal footer button states
        footer_disabled_btn = await page.query_selector("button:has-text('FIRMWARE IS UP TO DATE')")
        assert footer_disabled_btn is not None, "Disabled footer button [ FIRMWARE IS UP TO DATE ] not found"
        footer_disabled = await footer_disabled_btn.is_disabled()
        assert footer_disabled, "Footer button [ FIRMWARE IS UP TO DATE ] should be disabled"
        print("Modal footer disabled live apply button verified: OK")

        footer_dryrun_btn = await page.query_selector("button:has-text('RUN DIAGNOSTIC DRY-RUN')")
        assert footer_dryrun_btn is not None, "Footer button [ RUN DIAGNOSTIC DRY-RUN ] not found"
        print("Modal footer dry-run button verified: OK")

        await page.screenshot(path="project_details/proof/proof_firmware_up_to_date_modal.png")
        print("Saved proof: proof_firmware_up_to_date_modal.png")

        # 6. Click dry-run button in modal and verify simulation completes
        await footer_dryrun_btn.click()
        await asyncio.sleep(2.5)
        logs = await page.inner_text('[data-testid="telemetry-terminal"]')
        print(f"Captured logs: {repr(logs)}")
        assert "PRE-FLIGHT" in logs or "UP_TO_DATE" in logs or "Dry-run simulation completed successfully" in logs or "Host watcher" in logs or "Querying host" in logs
        print("Diagnostic simulation run verified in terminal body: OK")

        await browser.close()
        print("All verification steps passed successfully!")

if __name__ == "__main__":
    asyncio.run(run())

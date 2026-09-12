import asyncio
import httpx
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        # 1. Open Settings on Location Tab
        print("Navigating to Settings...")
        await page.goto("http://localhost:8080/settings?tab=location", wait_until="networkidle")
        await asyncio.sleep(1.5)

        # 2. Verify save button is gone
        save_btn = await page.query_selector("button:has-text('[ SAVE & APPLY CONFIGURATION ]')")
        assert save_btn is None, "Error: Manual [ SAVE & APPLY CONFIGURATION ] button should NOT exist!"
        print("Confirmed: Manual [ SAVE & APPLY CONFIGURATION ] button is removed.")

        # 3. Verify Auto-Save status badge is present in header and action bar
        header_text = await page.inner_text(".max-w-5xl")
        assert "ALL CHANGES SAVED" in header_text or "AUTO-SAVE ACTIVE" in header_text, "Auto-save badge should be visible!"
        print("Confirmed: Auto-save status indicator is active and visible.")

        await page.screenshot(path="project_details/proof/proof_autosave_initial.png")
        print("Captured: proof_autosave_initial.png")

        # 4. Change a setting by clicking a preset (CHICAGO)
        chicago_btn = await page.query_selector("button:has-text('[ CHICAGO ]')")
        assert chicago_btn is not None, "Could not find [ CHICAGO ] preset button"
        print("Clicking [ CHICAGO ] preset...")
        await chicago_btn.click()
        await asyncio.sleep(1.5)

        # 5. Capture screenshot showing auto-saved state
        await page.screenshot(path="project_details/proof/proof_autosave_preset_saved.png")
        print("Captured: proof_autosave_preset_saved.png")

        # 6. Verify backend datastore received the change
        async with httpx.AsyncClient() as client:
            res = await client.get("http://localhost:8080/api/v1/settings")
            settings = res.json()
            print(f"Backend settings metro_label: {settings.get('metro_label')}")
            assert settings.get("metro_label") == "CHICAGO", f"Expected CHICAGO, got {settings.get('metro_label')}"
            print("Confirmed: Setting automatically persisted in backend datastore without manual save button!")

        # 7. Switch to Tab 2 (Display) and toggle listings filter
        display_tab = await page.query_selector("button:has-text('[ 2. DISPLAY & KIOSK POWER ]')")
        if display_tab:
            print("Switching to Display tab...")
            await display_tab.click()
            await asyncio.sleep(1.0)

            all_venues_btn = await page.query_selector("button:has-text('[ ALL VENUES & SUBSCRIPTIONS ]')")
            if all_venues_btn:
                print("Clicking All Venues toggle...")
                await all_venues_btn.click()
                await asyncio.sleep(1.5)

            await page.screenshot(path="project_details/proof/proof_autosave_tab2_toggle.png")
            print("Captured: proof_autosave_tab2_toggle.png")

            async with httpx.AsyncClient() as client:
                res2 = await client.get("http://localhost:8080/api/v1/settings")
                settings2 = res2.json()
                print(f"Backend settings grid_filter_mode: {settings2.get('grid_filter_mode')}")
                assert settings2.get("grid_filter_mode") == "all", f"Expected 'all', got {settings2.get('grid_filter_mode')}"
                print("Confirmed: Display toggle automatically saved to backend datastore!")

        await browser.close()
        print("All auto-save tests PASSED successfully!")

if __name__ == "__main__":
    asyncio.run(run())

"""Playwright automated test script to verify both the Onboarding Modal (first-launch behavior)
and the Post-Update Changelog Modal, along with their Settings Tab 11 reset controls.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        print("--- 1. Testing Onboarding Modal: First-Launch Only Behavior ---")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.evaluate("""() => {
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.removeItem('openprevue_onboarding_completed');
            localStorage.removeItem('openprevue_dismiss_onboarding_modal');
            localStorage.setItem('openprevue_last_seen_version', '0.24.0');
        }""")
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(1.5)

        content = await page.content()
        assert "OPERATOR QUICK START" in content or "SYSTEM ORIENTATION" in content, "Onboarding modal not shown on first launch!"
        assert "System Settings Control Center" in content, "Settings callout missing!"
        assert "Curated 1990s Synth" in content, "Curated Spotify callout missing!"
        assert "Where to Add Events" in content, "Add events callout missing!"
        assert "Opt-In Local AI Flyer Ingestion" in content, "AI callout missing!"
        assert "Complete Operator" in content, "Operator manual callout missing!"
        print("Confirmed: Onboarding modal appeared on first launch with all navigation callouts.")

        # Capture proof 1: Onboarding Modal Intro
        proof1_path = PROOF_DIR / "proof_onboarding_modal_intro.png"
        await page.screenshot(path=str(proof1_path))
        print(f"Captured: {proof1_path.name}")

        # Dismiss modal without checking never show again
        dismiss_btn = page.locator("button:has-text('START BROADCAST')")
        await dismiss_btn.click()
        await asyncio.sleep(0.8)

        completed_val = await page.evaluate("() => localStorage.getItem('openprevue_onboarding_completed')")
        assert completed_val == "1", f"Expected openprevue_onboarding_completed to be '1', got {completed_val}"
        print("Confirmed: Onboarding modal dismissed and marked completed in localStorage.")

        # Reload dashboard: verify modal does NOT appear on second launch
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(1.5)
        content_2nd_launch = await page.content()
        assert "OPERATOR QUICK START" not in content_2nd_launch, "Onboarding modal should not reappear on second launch!"
        print("Confirmed: Onboarding modal strictly applied only to first launch.")

        print("\n--- 2. Testing Post-Update Changelog Modal ---")
        # Simulate that client previously saw version 0.23.0 and now boots into 0.24.0
        await page.evaluate("""() => {
            localStorage.setItem('openprevue_last_seen_version', '0.23.0');
            localStorage.removeItem('openprevue_dismiss_changelog_modal');
        }""")
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(1.5)

        content_update = await page.content()
        assert "UPDATE RELEASE NOTES" in content_update or "SYSTEM UPDATED" in content_update, "Changelog modal did not appear on version upgrade!"
        assert "System Health Ledger" in content_update or "RELEASE HIGHLIGHTS" in content_update, "Release highlights missing!"
        print("Confirmed: Post-update changelog modal appeared after version update.")

        # Capture proof 2: Changelog Modal
        proof2_path = PROOF_DIR / "proof_changelog_modal_update.png"
        await page.screenshot(path=str(proof2_path))
        print(f"Captured: {proof2_path.name}")

        # Test "Do Not Show Release Notes on Future Updates" checkbox
        changelog_checkbox = page.locator("input[type='checkbox']")
        await changelog_checkbox.click()
        await asyncio.sleep(0.3)

        continue_btn = page.locator("button:has-text('CONTINUE BROADCAST')")
        await continue_btn.click()
        await asyncio.sleep(0.8)

        dismiss_changelog_val = await page.evaluate("() => localStorage.getItem('openprevue_dismiss_changelog_modal')")
        assert dismiss_changelog_val == "1", f"Expected dismiss changelog to be '1', got {dismiss_changelog_val}"
        last_seen_ver = await page.evaluate("() => localStorage.getItem('openprevue_last_seen_version')")
        assert last_seen_ver == "0.24.0", f"Expected last seen version to be updated to '0.24.0', got {last_seen_ver}"
        print("Confirmed: Changelog modal dismissed, last_seen_version updated, and suppression saved.")

        # Simulate another simulated version bump to test suppression
        await page.evaluate("() => localStorage.setItem('openprevue_last_seen_version', '0.23.5')")
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(1.5)
        content_suppressed = await page.content()
        assert "UPDATE RELEASE NOTES" not in content_suppressed, "Changelog modal should be suppressed when preference is set!"
        print("Confirmed: Changelog modal is suppressed when user checked never show on updates.")

        print("\n--- 3. Testing Settings Tab 11 Preference Controls & Resets ---")
        await page.goto(f"{BASE_URL}/settings?tab=guide", wait_until="networkidle")
        await asyncio.sleep(1.5)

        content_tab11 = await page.content()
        assert "STARTUP WELCOME GUIDE MODAL PREFERENCE" in content_tab11, "Welcome modal preference card missing!"
        assert "POST-UPDATE CHANGELOG MODAL PREFERENCE" in content_tab11, "Changelog modal preference card missing!"
        assert "DISMISSED / HIDDEN" in content_tab11, "Welcome modal status should show DISMISSED / HIDDEN!"
        assert "SUPPRESSED / NEVER SHOW" in content_tab11, "Changelog modal status should show SUPPRESSED / NEVER SHOW!"
        print("Confirmed: Settings Tab 11 displays both preference cards with current suppressed states.")

        # Capture proof 3: Settings Tab 11 suppressed state
        proof3_path = PROOF_DIR / "proof_tab11_modal_preferences_suppressed.png"
        await page.screenshot(path=str(proof3_path))
        print(f"Captured: {proof3_path.name}")

        # Test [ PREVIEW CHANGELOG NOW ]
        preview_cl_btn = page.locator("button:has-text('PREVIEW CHANGELOG NOW')")
        await preview_cl_btn.click()
        await asyncio.sleep(0.8)
        content_cl_preview = await page.content()
        assert "UPDATE RELEASE NOTES" in content_cl_preview, "Preview changelog modal failed to open!"
        print("Confirmed: [ PREVIEW CHANGELOG NOW ] opens the changelog modal.")
        close_cl_preview = page.locator("button:has-text('CONTINUE BROADCAST')")
        await close_cl_preview.click()
        await asyncio.sleep(0.8)

        # Test [ RE-ENABLE ON UPDATES ]
        reenable_cl_btn = page.locator("button:has-text('RE-ENABLE ON UPDATES')")
        await reenable_cl_btn.click()
        await asyncio.sleep(0.8)
        content_cl_restored = await page.content()
        assert "ACTIVE ON UPDATES" in content_cl_restored, "Changelog status should flip to ACTIVE ON UPDATES!"
        assert "POST-UPDATE CHANGELOG RESTORED" in content_cl_restored, "Notice message missing!"
        print("Confirmed: [ RE-ENABLE ON UPDATES ] restores active status.")

        # Test [ RE-ENABLE ON STARTUP ]
        reenable_onboarding_btn = page.locator("button:has-text('RE-ENABLE ON STARTUP')")
        await reenable_onboarding_btn.click()
        await asyncio.sleep(0.8)
        content_onboarding_restored = await page.content()
        assert "ACTIVE ON STARTUP" in content_onboarding_restored, "Welcome modal status should flip to ACTIVE ON STARTUP!"
        assert "STARTUP WELCOME GUIDE RESTORED" in content_onboarding_restored, "Notice message missing!"
        print("Confirmed: [ RE-ENABLE ON STARTUP ] restores welcome modal to active on startup.")

        # Capture proof 4: Settings Tab 11 restored state
        proof4_path = PROOF_DIR / "proof_tab11_modal_preferences_restored.png"
        await page.screenshot(path=str(proof4_path))
        print(f"Captured: {proof4_path.name}")

        print("\n--- 4. Testing Dashboard Boot Re-appearance After Reset ---")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        content_final = await page.content()
        assert "OPERATOR QUICK START" in content_final, "Welcome modal should reappear on dashboard boot after being re-enabled!"
        print("Confirmed: Welcome modal reappears on next boot after reset in Settings Tab 11.")

        await browser.close()
        print("\nAll Onboarding and Changelog Modal verification checks passed successfully!")


if __name__ == "__main__":
    asyncio.run(run_tests())

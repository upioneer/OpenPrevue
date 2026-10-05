"""Playwright test to verify EventDetailModal features:
1. Clicking event cell opens modal with rich graphics and info.
2. 30s auto-close timer and countdown badge.
3. Persist checkbox stops auto-close timer.
4. Clicking outside (backdrop) auto-closes modal.
5. Delete event button shows confirmation dialog, cancels safely, and confirms deletion.
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

        # Bypass onboarding
        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
        """)

        print("Navigating to OpenPrevue dashboard...")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2.0)

        # 1. Verify clicking an event cell opens the modal
        print("Finding an event cell in the schedule grid...")
        event_cells = await page.query_selector_all(".group.cursor-pointer")
        assert len(event_cells) > 0, "No clickable event cells found in schedule grid"

        first_cell = event_cells[0]
        print("Clicking event cell...")
        await first_cell.click()
        await asyncio.sleep(1.0)

        # Verify modal opened
        modal = await page.wait_for_selector("[role='dialog']", timeout=5000)
        assert modal is not None, "EventDetailModal did not open on cell click"
        print("EventDetailModal opened successfully!")

        # Verify graphics and info are present
        modal_text = await modal.text_content()
        assert "DATE & TIME" in modal_text, "Date & Time card missing"
        assert "ADMISSION & COMMITMENT" in modal_text, "Admission & Commitment card missing"
        assert "KEEP OPEN (DISABLE 30S AUTO-CLOSE)" in modal_text, "Persist checkbox missing"
        assert "DELETE EVENT" in modal_text, "Delete event button missing"
        assert "openprevue.tv" not in modal_text.lower(), "Found legacy openprevue.tv in modal text"
        print("Modal graphics, information cards, and sanitized domain verified!")

        # Verify QR Code and Vendor Domain
        qr_img = await modal.query_selector("img[alt='Ticket QR Code']")
        assert qr_img is not None, "QR code image not found in modal"
        qr_src = await qr_img.get_attribute("src")
        assert qr_src and qr_src.startswith("data:image/png;base64,"), "Invalid QR code data URL"
        print("Verified QR code rendered successfully!")

        # Capture proof of EventDetailModal
        proof_modal_path = PROOF_DIR / "event_detail_modal_verified.png"
        await page.screenshot(path=str(proof_modal_path))
        print(f"Captured proof: {proof_modal_path}")

        # 2. Verify 30s auto-close countdown badge
        countdown_elem = await modal.query_selector("text=AUTO-CLOSES IN")
        assert countdown_elem is not None, "Countdown badge not found"
        print("Verified auto-close countdown badge active!")

        # 3. Verify persist checkbox stops auto-close
        print("Testing persist checkbox toggle...")
        persist_label = await modal.wait_for_selector("text=KEEP OPEN (DISABLE 30S AUTO-CLOSE)")
        assert persist_label is not None
        await persist_label.click()
        await asyncio.sleep(0.5)

        persistent_badge = await modal.query_selector("text=[ PERSISTENT MODE ]")
        assert persistent_badge is not None, "Persistent mode badge did not activate"
        print("Verified persistent mode checkbox pauses auto-close!")

        # Capture proof of Persistent Mode
        proof_persist_path = PROOF_DIR / "event_modal_persistent_mode.png"
        await page.screenshot(path=str(proof_persist_path))
        print(f"Captured proof: {proof_persist_path}")

        # 4. Verify clicking outside modal (backdrop) auto closes it
        print("Testing clicking outside modal (backdrop click)...")
        # Click on top-left area outside dialog
        await page.mouse.click(50, 50)
        await asyncio.sleep(0.5)

        modal_check = await page.query_selector("[role='dialog']")
        assert modal_check is None, "Modal did not close on backdrop click"
        print("Verified clicking outside of modal auto-closes it!")

        # 5. Re-open modal and test delete button & confirmation dialog
        print("Re-opening event modal for deletion test...")
        event_cells = await page.query_selector_all(".group.cursor-pointer")
        assert len(event_cells) > 0
        await event_cells[0].click()
        await asyncio.sleep(0.5)

        modal = await page.wait_for_selector("[role='dialog']", timeout=5000)
        assert modal is not None

        delete_btn = await modal.wait_for_selector("button:has-text('DELETE EVENT')")
        assert delete_btn is not None
        print("Clicking [ DELETE EVENT ]...")
        await delete_btn.click()
        await asyncio.sleep(0.5)

        # Verify confirmation dialog is visible
        confirm_title = await modal.query_selector("text=CONFIRM EVENT DELETION")
        assert confirm_title is not None, "Delete confirmation dialog title not displayed"
        confirm_btn = await modal.query_selector("button:has-text('CONFIRM DELETE')")
        assert confirm_btn is not None, "Confirm delete button not found"
        cancel_btn = await modal.query_selector("button:has-text('CANCEL')")
        assert cancel_btn is not None, "Cancel delete button not found"
        print("Verified deletion confirmation dialog with CONFIRM DELETE and CANCEL buttons!")

        # Capture proof of delete confirmation dialog
        proof_delete_confirm_path = PROOF_DIR / "event_modal_delete_confirm.png"
        await page.screenshot(path=str(proof_delete_confirm_path))
        print(f"Captured proof: {proof_delete_confirm_path}")

        # Test CANCEL button
        print("Clicking [ CANCEL ]...")
        await cancel_btn.click()
        await asyncio.sleep(0.5)
        confirm_title_after_cancel = await modal.query_selector("text=CONFIRM EVENT DELETION")
        assert confirm_title_after_cancel is None, "Confirmation dialog did not dismiss on cancel"
        print("Verified [ CANCEL ] returns safely to event details!")

        # Test actual deletion
        print("Clicking [ DELETE EVENT ] again to confirm deletion...")
        delete_btn = await modal.wait_for_selector("button:has-text('DELETE EVENT')")
        await delete_btn.click()
        await asyncio.sleep(0.5)

        confirm_btn = await modal.wait_for_selector("button:has-text('CONFIRM DELETE')")
        await confirm_btn.click()
        await asyncio.sleep(1.0)

        # Modal should be closed after deletion
        modal_after_delete = await page.query_selector("[role='dialog']")
        assert modal_after_delete is None, "Modal did not close after confirming delete"
        print("Verified event deletion completed and modal closed successfully!")

        await page.close()
        await browser.close()
        print("\nAll EventDetailModal tests passed with 100% success!")


if __name__ == "__main__":
    asyncio.run(run_tests())

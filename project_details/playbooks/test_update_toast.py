"""Test script to verify UpdateToast button layout and ensure no orphaned brackets or line splits."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def test_update_toast():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for mode, (width, height) in [("desktop", (1920, 1080)), ("mobile", (375, 667))]:
            page = await browser.new_page(viewport={"width": width, "height": height})
            await page.add_init_script("""
                localStorage.setItem('openprevue_onboarded', '1');
                localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
                localStorage.setItem('openprevue_onboarding_completed', '1');
                sessionStorage.removeItem('openprevue_dismissed_update');
            """)

            # Route update status API to simulate update available
            await page.route("**/api/v1/updates/status", lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body='''{
                    "update_available": true,
                    "current_version": "0.27.0",
                    "latest_version": "0.27.2",
                    "release_url": "https://github.com/upioneer/OpenPrevue/releases/tag/v0.27.2",
                    "published_at": "2026-10-04T12:00:00Z",
                    "release_notes": "Security fixes and UI refinements",
                    "is_docker": true,
                    "checked_at": "2026-10-04T12:00:00Z"
                }'''
            ))

            await page.goto(f"{BASE_URL}/", wait_until="networkidle")
            await asyncio.sleep(1.0)

            # Wait for toast to appear
            toast = await page.wait_for_selector("text=[ SYSTEM UPDATE AVAILABLE ]", timeout=5000)
            assert toast is not None, f"Toast not found in {mode} mode"

            # Check action buttons
            buttons_info = await page.evaluate("""
                () => {
                    const toast = document.querySelector('.fixed.bottom-6.right-6');
                    if (!toast) return null;
                    const items = Array.from(toast.querySelectorAll('button, a')).filter(el => {
                        return el.textContent.includes('[ UPGRADE') || el.textContent.includes('[ SETTINGS') || el.textContent.includes('[ GITHUB');
                    });
                    return items.map(el => ({
                        text: el.textContent.trim(),
                        whiteSpace: window.getComputedStyle(el).whiteSpace,
                        height: el.getBoundingClientRect().height,
                        width: el.getBoundingClientRect().width,
                        rectsCount: el.getClientRects().length
                    }));
                }
            """)

            print(f"\\n--- {mode.upper()} ({width}x{height}) ---")
            for b in buttons_info:
                print(f"Button: '{b['text']}' | whiteSpace: {b['whiteSpace']} | size: {b['width']}x{b['height']}px")
                assert b['whiteSpace'] == 'nowrap', f"Button {b['text']} does not have white-space: nowrap"

            # Save screenshot of the toast element directly
            toast_elem = await page.query_selector(".fixed.bottom-6.right-6")
            toast_path = PROOF_DIR / f"update_toast_element_{mode}.png"
            if toast_elem:
                await toast_elem.screenshot(path=str(toast_path))
                print(f"Captured toast element: {toast_path}")

            proof_path = PROOF_DIR / f"update_toast_{mode}.png"
            await page.screenshot(path=str(proof_path))
            print(f"Captured proof: {proof_path}")
            await page.close()

        await browser.close()
        print("\nAll UpdateToast button layout tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_update_toast())

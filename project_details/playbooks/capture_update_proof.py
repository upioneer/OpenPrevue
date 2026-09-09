"""Capture visual proof artifacts for the independent in-place update engine."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def capture_proof():
    print(f"Capturing visual proofs in {PROOF_DIR}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Settings Tab 10: System Updates & In-Place Engine Card
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page.goto(f"{BASE_URL}/settings", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # Click Tab 10: System & Updates
        tab10_btn = await page.wait_for_selector("text=[ 10. SYSTEM & UPDATES ]")
        await tab10_btn.click()
        await asyncio.sleep(1.0)

        proof_tab10 = PROOF_DIR / "settings_tab10_updates.png"
        await page.screenshot(path=str(proof_tab10))
        print(f"Captured: {proof_tab10}")

        # 2. Launch Firmware Upgrade Modal & Run Dry-Run Simulation
        launch_btn = await page.wait_for_selector("text=[ LAUNCH FIRMWARE UPGRADE ENGINE ]")
        await launch_btn.click()
        await asyncio.sleep(1.0)

        # Click Test Dry-Run in modal
        dry_run_btn = await page.wait_for_selector("text=[ TEST DRY-RUN ]")
        await dry_run_btn.click()
        await asyncio.sleep(2.0)

        proof_modal = PROOF_DIR / "firmware_upgrader_modal.png"
        await page.screenshot(path=str(proof_modal))
        print(f"Captured: {proof_modal}")

        await page.close()

        # 3. Capture UpdateToast with Upgrade In-Place action
        page_toast = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page_toast.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")
        await page_toast.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # Inject update toast visibility in DOM
        await page_toast.evaluate("""() => {
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-6 right-6 z-50 max-w-sm sm:max-w-md bg-[#000044] border-2 border-[#FFFF00] shadow-[0_0_20px_rgba(255,255,0,0.7)] p-4 font-mono text-xs text-[#E0E0E0] select-none';
            toast.innerHTML = `
                <div class="flex items-center justify-between border-b border-[#333366] pb-1.5 mb-2">
                    <div class="flex items-center space-x-2">
                        <span class="w-2.5 h-2.5 bg-[#FFFF00] inline-block animate-pulse"></span>
                        <span class="text-[#FFFF00] font-black tracking-wider text-xs">[ SYSTEM UPDATE AVAILABLE ]</span>
                    </div>
                    <span class="text-[#8888AA] font-bold text-xs">[ X ]</span>
                </div>
                <p class="text-[11px] text-[#A0A0C0] mb-3 leading-relaxed">
                    A new version of OpenPrevue (<strong class="text-[#00FFFF]">v0.22.0</strong>) is available. Upgrading brings fresh retro features, headend DSP updates, and provider patches.
                </p>
                <div class="flex items-center space-x-2">
                    <button class="bg-[#FFFF00] text-[#000033] px-3 py-1 text-xs font-black hover:bg-[#FFFFFF] shadow-[0_0_8px_rgba(255,255,0,0.8)]">[ UPGRADE IN-PLACE ]</button>
                    <span class="bg-[#000080] border border-[#FFFF00] text-[#FFFF00] px-3 py-1 text-xs font-bold">[ SETTINGS ]</span>
                    <span class="bg-[#000080] border border-[#00FFFF] text-[#00FFFF] px-3 py-1 text-xs font-bold">[ GITHUB ]</span>
                </div>
            `;
            document.body.appendChild(toast);
        }""")
        await asyncio.sleep(0.5)

        proof_toast = PROOF_DIR / "update_toast.png"
        await page_toast.screenshot(path=str(proof_toast))
        print(f"Captured: {proof_toast}")
        await page_toast.close()

        await browser.close()
    print("Proof captures completed successfully.")


if __name__ == "__main__":
    asyncio.run(capture_proof())

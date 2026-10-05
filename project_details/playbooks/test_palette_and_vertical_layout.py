"""Playwright test script to verify:
1. Color palette presets in Settings (Amber, Green, C64, EGA, Default) live apply to UI.
2. Highlight section vertical layout formatting in portrait / vertical viewports.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"
PROOF_DIR = Path("project_details") / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def test_palette_and_vertical_layout():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # Part 1: Verify Color Palette Presets in Settings & Dashboard
        # -------------------------------------------------------------
        print("\n=== PART 1: Testing Color Palette Presets ===")
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
        """)

        # 1. Test Amber Monochrome Palette
        print("Applying Amber Monochrome Palette...")
        await page.goto(f"{BASE_URL}/settings?tab=display", wait_until="networkidle")
        await asyncio.sleep(1.5)

        # Change palette select to amber_monochrome
        palette_select = await page.wait_for_selector("select:has(option[value='amber_monochrome'])")
        assert palette_select is not None, "Color Palette Preset select element not found"
        await palette_select.select_option("amber_monochrome")
        await asyncio.sleep(1.0)

        # Verify body class
        body_class = await page.evaluate("document.body.className")
        assert "palette-amber" in body_class, f"Expected palette-amber in body class, got: {body_class}"
        print("Verified body class contains palette-amber!")

        # Navigate to dashboard to verify amber phosphor active on main screen
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        amber_body_class = await page.evaluate("document.body.className")
        assert "palette-amber" in amber_body_class, "Amber palette did not persist to dashboard"
        amber_proof_path = PROOF_DIR / "palette_amber_monochrome_proof.png"
        await page.screenshot(path=str(amber_proof_path))
        print(f"Captured proof: {amber_proof_path}")

        # 2. Test Green Phosphor Terminal Palette
        print("\nApplying Green Phosphor Terminal Palette...")
        await page.goto(f"{BASE_URL}/settings?tab=display", wait_until="networkidle")
        await asyncio.sleep(1.0)
        palette_select = await page.wait_for_selector("select:has(option[value='green_monochrome'])")
        await palette_select.select_option("green_monochrome")
        await asyncio.sleep(1.0)

        body_class = await page.evaluate("document.body.className")
        assert "palette-green" in body_class, f"Expected palette-green in body class, got: {body_class}"
        print("Verified body class contains palette-green!")

        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        green_body_class = await page.evaluate("document.body.className")
        assert "palette-green" in green_body_class, "Green palette did not persist to dashboard"
        green_proof_path = PROOF_DIR / "palette_green_phosphor_proof.png"
        await page.screenshot(path=str(green_proof_path))
        print(f"Captured proof: {green_proof_path}")

        # 3. Test Commodore 64 Palette
        print("\nApplying Commodore 64 Palette...")
        await page.goto(f"{BASE_URL}/settings?tab=display", wait_until="networkidle")
        await asyncio.sleep(1.0)
        palette_select = await page.wait_for_selector("select:has(option[value='c64'])")
        await palette_select.select_option("c64")
        await asyncio.sleep(1.0)

        body_class = await page.evaluate("document.body.className")
        assert "palette-c64" in body_class, f"Expected palette-c64 in body class, got: {body_class}"
        print("Verified body class contains palette-c64!")

        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        c64_proof_path = PROOF_DIR / "palette_c64_proof.png"
        await page.screenshot(path=str(c64_proof_path))
        print(f"Captured proof: {c64_proof_path}")

        # 4. Test EGA 16-Color PC Palette
        print("\nApplying EGA 16-Color PC Palette...")
        await page.goto(f"{BASE_URL}/settings?tab=display", wait_until="networkidle")
        await asyncio.sleep(1.0)
        palette_select = await page.wait_for_selector("select:has(option[value='ega16'])")
        await palette_select.select_option("ega16")
        await asyncio.sleep(1.0)

        body_class = await page.evaluate("document.body.className")
        assert "palette-ega16" in body_class, f"Expected palette-ega16 in body class, got: {body_class}"
        print("Verified body class contains palette-ega16!")

        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(1.5)
        ega_proof_path = PROOF_DIR / "palette_ega16_proof.png"
        await page.screenshot(path=str(ega_proof_path))
        print(f"Captured proof: {ega_proof_path}")

        # Reset back to default Prevue Blue
        print("\nResetting to Standard Prevue Blue Default...")
        await page.goto(f"{BASE_URL}/settings?tab=display", wait_until="networkidle")
        await asyncio.sleep(1.0)
        palette_select = await page.wait_for_selector("select:has(option[value='default'])")
        await palette_select.select_option("default")
        await asyncio.sleep(1.0)

        await page.close()
        await context.close()

        # -------------------------------------------------------------
        # Part 2: Verify Vertical Layout for Highlight Section in Portrait
        # -------------------------------------------------------------
        print("\n=== PART 2: Testing Vertical Layout Highlight Section in Portrait Viewport ===")
        # Portrait viewport: 1080x1920 (9:16 portrait kiosk / vertical monitor)
        portrait_context = await browser.new_context(viewport={"width": 1080, "height": 1920})
        portrait_page = await portrait_context.new_page()

        await portrait_page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
            localStorage.setItem('openprevue_last_viewed_version', '0.28.0');
            localStorage.setItem('openprevue_changelog_dismissed_0.28.0', '1');
        """)

        print("Navigating to OpenPrevue dashboard in portrait mode (1080x1920)...")
        await portrait_page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await asyncio.sleep(2.0)

        # Ensure any lingering dialog is dismissed
        await portrait_page.keyboard.press("Escape")
        await asyncio.sleep(0.5)

        # Iterate through spotlight dots to activate sports matchup slide if available
        dots = await portrait_page.query_selector_all(".flex.space-x-1\\.5 button, .flex.space-x-2 button")
        for i, dot in enumerate(dots):
            await dot.click(force=True)
            await asyncio.sleep(0.5)
            if await portrait_page.query_selector(".matchup-vertical-layout"):
                print(f"Found and selected sports matchup slide at dot index {i}!")
                break

        vertical_matchup = await portrait_page.query_selector(".matchup-vertical-layout")
        horizontal_matchup = await portrait_page.query_selector(".matchup-horizontal-layout")

        if vertical_matchup and horizontal_matchup:
            v_disp = await vertical_matchup.evaluate("el => window.getComputedStyle(el).display")
            h_disp = await horizontal_matchup.evaluate("el => window.getComputedStyle(el).display")
            print(f"Portrait computed displays: vertical={v_disp}, horizontal={h_disp}")
            assert v_disp != "none", f"Expected .matchup-vertical-layout to be visible in portrait, got {v_disp}"
            assert h_disp == "none", f"Expected .matchup-horizontal-layout to be hidden in portrait, got {h_disp}"
            print("Verified .matchup-vertical-layout is VISIBLE and .matchup-horizontal-layout is HIDDEN in portrait!")

        # Capture proof of portrait layout with vertical matchup stacking
        portrait_proof_path = PROOF_DIR / "highlight_section_vertical_layout_portrait.png"
        await portrait_page.screenshot(path=str(portrait_proof_path))
        print(f"Captured portrait proof: {portrait_proof_path}")

        # Also verify EventDetailModal in portrait
        print("Testing EventDetailModal in portrait viewport...")
        cells = await portrait_page.query_selector_all(".group.cursor-pointer")
        if cells:
            await cells[0].click()
            await asyncio.sleep(1.0)
            modal = await portrait_page.wait_for_selector("[role='dialog']", timeout=5000)
            assert modal is not None, "Modal did not open in portrait mode"
            modal_proof_path = PROOF_DIR / "event_modal_portrait_proof.png"
            await portrait_page.screenshot(path=str(modal_proof_path))
            print(f"Captured modal portrait proof: {modal_proof_path}")

        await portrait_page.close()
        await portrait_context.close()
        await browser.close()
        print("\nAll color palette and vertical layout tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_palette_and_vertical_layout())

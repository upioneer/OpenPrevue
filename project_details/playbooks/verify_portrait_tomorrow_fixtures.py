"""Verification playbook for portrait mode Today + Tomorrow event fixture rendering."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROOF_DIR = Path("project_details/proof")
PROOF_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    print("Launching Chromium browser in 1080x1920 portrait kiosk viewport...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # 1. Test 2-Column Mode in Portrait Viewport
        page_2col = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page_2col.goto("http://localhost:8000/?columns=2")
        await page_2col.wait_for_timeout(3500)

        header_2col = await page_2col.locator(".grid.grid-cols-12.font-black").first.inner_text()
        print(f"2-Col Header:\n{header_2col}")
        assert "TODAY" in header_2col, "Expected TODAY header"
        assert "TOMORROW" in header_2col, "Expected TOMORROW header"

        # Check rows
        rows_2col = await page_2col.locator(".grid.grid-cols-12").all()
        print(f"2-Col Grid Rows Found: {len(rows_2col)}")
        assert len(rows_2col) >= 10, "Expected at least 10 rendered rows"

        proof_2col_path = PROOF_DIR / "portrait_2col_fixed.png"
        await page_2col.screenshot(path=str(proof_2col_path))
        print(f"2-Col Portrait Proof saved: {proof_2col_path}")
        await page_2col.close()

        # 2. Test 3-Column Mode in Portrait Viewport
        page_3col = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page_3col.goto("http://localhost:8000/?columns=3")
        await page_3col.wait_for_timeout(3500)

        header_3col = await page_3col.locator(".grid.grid-cols-12.font-black").first.inner_text()
        print(f"3-Col Header:\n{header_3col}")
        assert "TODAY" in header_3col or "TONIGHT" in header_3col, "Expected TODAY/TONIGHT header"
        assert "TOMORROW" in header_3col, "Expected TOMORROW header"

        proof_3col_path = PROOF_DIR / "portrait_3col_fixed.png"
        await page_3col.screenshot(path=str(proof_3col_path))
        print(f"3-Col Portrait Proof saved: {proof_3col_path}")
        await page_3col.close()

        await browser.close()
        print("Portrait verification finished successfully.")


if __name__ == "__main__":
    asyncio.run(main())

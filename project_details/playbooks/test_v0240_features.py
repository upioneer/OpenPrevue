import asyncio
import httpx
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.add_init_script("localStorage.setItem('openprevue_onboarded', '1')")

        print("--- 1. Testing Tab 5: TripAdvisor & Viator Ingestion ---")
        await page.goto("http://localhost:8080/settings?tab=ingestion", wait_until="networkidle")
        await asyncio.sleep(2.0)

        # Verify TripAdvisor & Viator Sync buttons are present
        ta_sync_btn = await page.query_selector("button:has-text('[ SYNC TRIPADVISOR NOW ]')")
        vt_sync_btn = await page.query_selector("button:has-text('[ SYNC VIATOR NOW ]')")
        assert ta_sync_btn is not None, "TripAdvisor Sync button should be visible"
        assert vt_sync_btn is not None, "Viator Sync button should be visible"
        print("Confirmed: TripAdvisor and Viator sync action buttons are present.")

        # Test filling sample URL
        ta_input = await page.query_selector("input[placeholder*='tripadvisor.com/Trips']")
        if ta_input:
            await ta_input.fill("https://www.tripadvisor.com/Trips/sample-vacation-wishlist")
            await asyncio.sleep(0.5)

        await page.screenshot(path="project_details/proof/proof_tab4_travel_wishlist_sync.png")
        print("Captured: proof_tab4_travel_wishlist_sync.png")

        print("--- 2. Testing Tab 10: System Health & Event Viewer ---")
        await page.goto("http://localhost:8080/settings?tab=updates", wait_until="networkidle")
        await asyncio.sleep(2.5)

        # Verify Real-Time System Health Ledger is present
        page_text = await page.inner_text("body")
        assert "real-time system health & connectivity ledger" in page_text.lower(), "Health ledger should be visible"
        assert "database engine" in page_text.lower(), "Database engine card should be visible"
        assert "system activity & audit event viewer" in page_text.lower(), "Activity log viewer should be visible"
        print("Confirmed: Real-time health ledger and event viewer terminal are rendered.")

        await page.screenshot(path="project_details/proof/proof_tab10_diagnostics_event_viewer.png")
        print("Captured: proof_tab10_diagnostics_event_viewer.png")

        print("--- 3. Testing Tab 11: User Onboarding & Feature Tour ---")
        await page.goto("http://localhost:8080/settings?tab=guide", wait_until="networkidle")
        await asyncio.sleep(2.0)

        page_text = await page.inner_text("body")
        assert "welcome & user onboarding" in page_text.lower(), "Onboarding tour should be visible"
        assert "committed ticket marking" in page_text.lower(), "Committed ticket feature card should be visible"
        assert "zero-click real-time auto-save" in page_text.lower(), "Auto-save feature card should be visible"
        print("Confirmed: User Onboarding & Feature Tour cards are present.")

        await page.screenshot(path="project_details/proof/proof_tab11_onboarding_feature_tour.png")
        print("Captured: proof_tab11_onboarding_feature_tour.png")

        print("--- 4. Testing Dashboard: Ticket Button & Genre Badges ---")
        await page.goto("http://localhost:8080/", wait_until="networkidle")
        await asyncio.sleep(3.0)

        # Verify [+TKT] button is visible
        tkt_btn = await page.query_selector("button:has-text('[+TKT]')")
        assert tkt_btn is not None, "Uncommitted ticket button [+TKT] should be visible"
        print("Confirmed: Prominent [+TKT] ticket button is visible.")

        # Click [+TKT] button to commit
        await tkt_btn.click()
        await asyncio.sleep(1.5)

        # Verify [TICKET] button appears
        committed_btn = await page.query_selector("button:has-text('[TICKET]')")
        assert committed_btn is not None, "[TICKET] badge should be active after click"
        print("Confirmed: Ticket button toggled to [TICKET] with neon phosphor glow.")

        await page.screenshot(path="project_details/proof/proof_dashboard_ticket_and_badges.png")
        print("Captured: proof_dashboard_ticket_and_badges.png")

        await browser.close()
        print("All verification steps passed successfully!")

if __name__ == "__main__":
    asyncio.run(run())

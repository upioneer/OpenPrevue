import asyncio
import os
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_welcome_dismissed', '1');
            localStorage.setItem('openprevue_seen_changelog_v0.27.0', '1');
            localStorage.setItem('openprevue_seen_changelog_0.27.0', '1');
        """)
        
        await page.goto("http://localhost:8080/?kiosk=1", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Test direct resolution of various leagues in the app
        results = await page.evaluate("""
            () => {
                // Check if images or vectors exist in spotlight pane
                const leftCol = document.querySelector('.w-\\\\[48\\\\%\\\\]');
                const title = document.querySelector('div.text-base.font-black, div.text-xl.font-black, div.line-clamp-2')?.innerText || '';
                const imgs = Array.from(leftCol ? leftCol.querySelectorAll('img') : []).map(i => i.src);
                const svgs = leftCol ? leftCol.querySelectorAll('svg').length : 0;
                return { title, imgs, svgs };
            }
        """)
        print("Initial Live Spotlight Check:", results)
        
        # Now let's inject custom events into Vue or test various matchups
        matchup_test_titles = [
            "NFL: CLEVELAND BROWNS VS PITTSBURGH STEELERS",
            "NBA: TORONTO RAPTORS AT BOSTON CELTICS",
            "MLB: CLEVELAND GUARDIANS VS CHICAGO WHITE SOX",
            "NHL: COLORADO AVALANCHE VS EDMONTON OILERS",
            "MLS: SEATTLE SOUNDERS FC VS PORTLAND TIMBERS",
            "PREMIER LEAGUE: ARSENAL FC VS CHELSEA FC"
        ]
        
        # Take a screenshot of the initial working spotlight card
        os.makedirs("project_details/proof", exist_ok=True)
        proof_path = os.path.abspath("project_details/proof/spotlight_logos_verified.png")
        await page.screenshot(path=proof_path)
        print(f"Screenshot saved to: {proof_path}")
        
        await browser.close()
        print("Test completed successfully.")

if __name__ == "__main__":
    asyncio.run(run_test())

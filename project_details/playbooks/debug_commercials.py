"""Diagnostic script to investigate why videos and commercials are not playing."""

import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8080"


async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        await page.add_init_script("""
            localStorage.setItem('openprevue_onboarded', '1');
            localStorage.setItem('openprevue_dismiss_onboarding_modal', '1');
            localStorage.setItem('openprevue_onboarding_completed', '1');
            localStorage.setItem('openprevue_last_viewed_version', '0.28.0');
            localStorage.setItem('openprevue_changelog_dismissed_0.28.0', '1');
        """)

        print("Navigating to Settings -> Commercials tab...")
        await page.goto(f"{BASE_URL}/settings?tab=commercials", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # Print all localStorage keys and values
        storage = await page.evaluate("() => ({ ...localStorage })")
        print("localStorage keys:", list(storage.keys()))

        # Click test play commercial clip button
        test_btn = await page.wait_for_selector("button:has-text('TEST PLAY COMMERCIAL CLIP')")
        assert test_btn is not None, "Test play button not found"
        print("Clicking TEST PLAY COMMERCIAL CLIP...")
        await test_btn.click()
        await asyncio.sleep(3.0)

        # Now on Dashboard ('/')
        print("Current URL:", page.url)

        # Inspect DOM on dashboard
        diag = await page.evaluate("""() => {
            const yt = document.querySelector('iframe[src*="youtube.com"]');
            const ytPane = document.querySelector('[id^="yt-player"]');
            const videoEl = document.querySelector('video');
            const textContent = document.body.innerText;
            const topPane = document.querySelector('.portrait-spotlight-height, .h-\\\\[45\\\\%\\\\]');
            return {
                hasIframe: !!yt,
                iframeSrc: yt ? yt.src : null,
                hasYtPane: !!ytPane,
                ytPaneId: ytPane ? ytPane.id : null,
                hasVideo: !!videoEl,
                videoSrc: videoEl ? videoEl.src : null,
                topPaneClass: topPane ? topPane.className : null,
                topPaneTextSnippet: topPane ? topPane.innerText.substring(0, 200) : null,
            };
        }""")
        print("Dashboard video diagnostic:", diag)
        await page.screenshot(path="project_details/proof/test_play_commercial_debug.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())

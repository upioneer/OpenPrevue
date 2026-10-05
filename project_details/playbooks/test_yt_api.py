import asyncio
from playwright.async_api import async_playwright

HTML = """
<!DOCTYPE html>
<html>
<head><script src="https://www.youtube.com/iframe_api"></script></head>
<body>
<div id="player1"></div>
<div id="player2"></div>
<script>
window.onYouTubeIframeAPIReady = function() {
    console.log("API ready");
    // Test 1: with videoId: undefined
    try {
        new YT.Player("player1", {
            videoId: undefined,
            playerVars: { listType: "playlist", list: "PLQ82R4ElALew" }
        });
    } catch(e) {
        console.log("Player 1 error:", e.message);
    }

    // Test 2: without videoId key
    try {
        new YT.Player("player2", {
            playerVars: { listType: "playlist", list: "PLQ82R4ElALew" }
        });
    } catch(e) {
        console.log("Player 2 error:", e.message);
    }
};
</script>
</body>
</html>
"""

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("console", lambda m: print("CONSOLE:", m.text))
        page.on("pageerror", lambda e: print("PAGE ERROR:", e))
        await page.set_content(HTML)
        await asyncio.sleep(4.0)
        p1 = await page.query_selector("#player1 iframe")
        p2 = await page.query_selector("#player2 iframe")
        print("Player 1 iframe created:", p1 is not None)
        print("Player 2 iframe created:", p2 is not None)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())

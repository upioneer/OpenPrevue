import asyncio
from playwright.async_api import async_playwright

HTML = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://www.youtube.com/iframe_api"></script>
</head>
<body style="background:#000; color:#fff;">
  <div id="player"></div>
  <pre id="log" style="font-family:monospace; font-size:14px;"></pre>
  <script>
    const log = (msg) => {
      document.getElementById('log').textContent += msg + "\\n";
      console.log("[TEST_LOG] " + msg);
    };

    let player;
    window.onYouTubeIframeAPIReady = function() {
      log("API Ready");
      player = new YT.Player('player', {
        height: '360',
        width: '640',
        playerVars: {
          autoplay: 1,
          controls: 1,
          listType: 'playlist',
          list: 'PLQ82R4ElALew',
          enablejsapi: 1,
          origin: window.location.origin
        },
        events: {
          onReady: function(e) {
            log("onReady fired");
          },
          onStateChange: function(e) {
            const states = {
              "-1": "UNSTARTED",
              "0": "ENDED",
              "1": "PLAYING",
              "2": "PAUSED",
              "3": "BUFFERING",
              "5": "CUED"
            };
            const currentVid = e.target.getVideoData ? e.target.getVideoData().title : "unknown";
            const curTime = e.target.getCurrentTime ? e.target.getCurrentTime() : 0;
            const dur = e.target.getDuration ? e.target.getDuration() : 0;
            log("onStateChange: " + e.data + " (" + (states[e.data] || "UNKNOWN") + ") | time: " + curTime.toFixed(1) + "/" + dur.toFixed(1) + " | title: " + currentVid);

            // Once playing, seek to 2 seconds before the end
            if (e.data === 1 && !window._hasSeeked) {
              window._hasSeeked = true;
              setTimeout(() => {
                const d = e.target.getDuration();
                log("Seeking to " + (d - 2) + " of duration " + d);
                e.target.seekTo(d - 2, true);
              }, 1000);
            }
          },
          onError: function(e) {
            log("onError: " + e.data);
          }
        }
      });
    };
  </script>
</body>
</html>
"""

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use http://127.0.0.1:8080/ as the context to route our test HTML
        context = await browser.new_context()
        page = await context.new_page()
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))

        # Route /yt_test to our test HTML
        await page.route("http://127.0.0.1:8080/yt_test", lambda route: route.fulfill(
            status=200, content_type="text/html", body=HTML
        ))

        await page.goto("http://127.0.0.1:8080/yt_test")
        print("Navigated. Waiting 15 seconds to observe state changes...")
        await asyncio.sleep(15)

        log_text = await page.inner_text("#log")
        print("\n=== FINAL TEST LOG ===")
        print(log_text)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

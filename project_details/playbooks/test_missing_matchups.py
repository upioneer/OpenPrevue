import asyncio
import datetime
import os
import sqlite3
from playwright.async_api import async_playwright

conn = sqlite3.connect("data/openprevue.db")
cur = conn.cursor()
now = datetime.datetime.now(datetime.timezone.utc)

test_matchups = [
    ("test-nfl", "NFL: CLEVELAND BROWNS VS PITTSBURGH STEELERS"),
    ("test-mlb", "MLB: CLEVELAND GUARDIANS VS CHICAGO WHITE SOX"),
    ("test-nhl", "NHL: COLORADO AVALANCHE VS EDMONTON OILERS"),
    ("test-mls", "MLS: SEATTLE SOUNDERS FC VS PORTLAND TIMBERS"),
    ("test-epl", "PREMIER LEAGUE: ARSENAL FC VS CHELSEA FC")
]

for idx, (mid, mtitle) in enumerate(test_matchups):
    t = (now + datetime.timedelta(hours=1 + idx)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT OR REPLACE INTO events
        (id, venue_id, title, category, start_time, end_time, price_min, price_max, currency, ticket_url, is_featured, has_ticket, source, status, created_at, updated_at)
        VALUES (?, 'the-fillmore-new-orleans', ?, 'sports', ?, ?, 50, 150, 'USD', 'https://example.com', 1, 0, 'sports_leagues', 'active', ?, ?)
    """, (mid, mtitle, t, t, t, t))
conn.commit()
conn.close()

async def inspect():
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
        
        slides = await page.evaluate("""() => {
            return document.querySelectorAll('.w-\\\\[52\\\\%\\\\] button.rounded-full').length;
        }""")
        print(f"Total spotlight dots: {slides}")
        
        for i in range(slides):
            await page.evaluate(f"""() => {{
                const dots = document.querySelectorAll('.w-\\\\[52\\\\%\\\\] button.rounded-full');
                if (dots[{i}]) dots[{i}].click();
            }}""")
            await asyncio.sleep(0.5)
            
            info = await page.evaluate("""() => {
                const rightCol = document.querySelector('.w-\\\\[52\\\\%\\\\]');
                const title = rightCol ? rightCol.querySelector('.text-base, .text-xl, .text-2xl')?.innerText : 'none';
                const leftCol = document.querySelector('.w-\\\\[48\\\\%\\\\]');
                const imgs = Array.from(leftCol ? leftCol.querySelectorAll('img') : []).map(i => i.src);
                const spans = Array.from(leftCol ? leftCol.querySelectorAll('.rounded-full span') : []).map(s => s.innerText);
                const svgs = leftCol ? leftCol.querySelectorAll('svg').length : 0;
                return { title, imgs, spans, svgs };
            }""")
            print(f"Slide {i}: {info}")
            
        os.makedirs("project_details/proof", exist_ok=True)
        proof_path = os.path.abspath("project_details/proof/comprehensive_sports_proof.png")
        await page.screenshot(path=proof_path)
        print(f"Saved proof screenshot to {proof_path}")
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(inspect())
    finally:
        conn = sqlite3.connect("data/openprevue.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE id LIKE 'test-%'")
        conn.commit()
        conn.close()
        print("Cleaned up test events.")

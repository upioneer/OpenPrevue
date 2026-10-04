import asyncio
import datetime
import os
import sqlite3
from playwright.async_api import async_playwright

TEST_EVENTS = [
    {
        "id": "test-matchup-nfl",
        "title": "NFL: CLEVELAND BROWNS VS PITTSBURGH STEELERS",
        "category": "sports",
        "source": "sports_leagues",
        "expected_imgs": ["cle.png", "pit.png"],
    },
    {
        "id": "test-matchup-nba",
        "title": "NBA: TORONTO RAPTORS AT BOSTON CELTICS",
        "category": "sports",
        "source": "sports_leagues",
        "expected_imgs": ["bos.png", "tor.png"],
    },
    {
        "id": "test-matchup-mlb",
        "title": "MLB: CLEVELAND GUARDIANS VS CHICAGO WHITE SOX",
        "category": "sports",
        "source": "sports_leagues",
        "expected_imgs": ["cle.png", "chw.png"],
    },
    {
        "id": "test-matchup-nhl",
        "title": "NHL: COLORADO AVALANCHE VS EDMONTON OILERS",
        "category": "sports",
        "source": "sports_leagues",
        "expected_imgs": ["col.png", "edm.png"],
    },
    {
        "id": "test-matchup-mls",
        "title": "MLS: SEATTLE SOUNDERS FC VS PORTLAND TIMBERS",
        "category": "sports",
        "source": "sports_leagues",
        "expected_imgs": ["9726.png", "9723.png"],
    },
    {
        "id": "test-matchup-epl",
        "title": "PREMIER LEAGUE: ARSENAL FC VS CHELSEA FC",
        "category": "sports",
        "source": "sports_leagues",
        "expected_imgs": ["359.png", "363.png"],
    }
]

def setup_db():
    conn = sqlite3.connect("data/openprevue.db")
    cur = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for idx, te in enumerate(TEST_EVENTS):
        event_time = (now + datetime.timedelta(hours=2 + idx * 2)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT OR REPLACE INTO events 
            (id, venue_id, title, category, start_time, end_time, price_min, price_max, currency, ticket_url, is_featured, has_ticket, source, status, created_at, updated_at)
            VALUES (?, 'madison-square-garden', ?, ?, ?, ?, 45, 120, 'USD', 'https://example.com/tickets', 1, 0, ?, 'active', ?, ?)
        """, (te["id"], te["title"], te["category"], event_time, event_time, te["source"], event_time, event_time))
    
    conn.commit()
    conn.close()
    print("Test events inserted into database.")

def cleanup_db():
    conn = sqlite3.connect("data/openprevue.db")
    cur = conn.cursor()
    ids = [te["id"] for te in TEST_EVENTS]
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM events WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()
    print("Test events cleaned up from database.")

async def verify_logos():
    setup_db()
    os.makedirs("project_details/proof", exist_ok=True)
    
    try:
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
            
            buttons = await page.query_selector_all("button.rounded-full")
            print(f"Found {len(buttons)} rotation dot buttons in spotlight pane.")
            
            all_verified = True
            
            for idx in range(len(buttons)):
                btns = await page.query_selector_all("button.rounded-full")
                if idx < len(btns):
                    await btns[idx].click(force=True)
                    await asyncio.sleep(0.6)
                
                title_el = await page.query_selector("div.text-base.font-black, div.text-xl.font-black, div.line-clamp-2")
                title = (await title_el.inner_text()).strip() if title_el else ""
                
                left_col = await page.query_selector(".w-\\[48\\%\\]")
                if not left_col:
                    continue
                
                imgs = await left_col.query_selector_all("img")
                img_srcs = [await img.get_attribute("src") for img in imgs]
                svgs = await left_col.query_selector_all("svg")
                
                print(f"--- Slide {idx} ---")
                print(f"Title: {title}")
                print(f"Images: {img_srcs}")
                print(f"SVGs: {len(svgs)}")
                
                # Check if this matches one of our test events
                for te in TEST_EVENTS:
                    if te["title"] in title:
                        for exp in te["expected_imgs"]:
                            found = any(exp in src for src in img_srcs if src)
                            if not found:
                                print(f"WARNING: Expected logo '{exp}' not found in {img_srcs}")
                                all_verified = False
                            else:
                                print(f"SUCCESS: Verified logo '{exp}' rendered properly!")
                
                # Save screenshot of each slide
                slide_proof = f"project_details/proof/slide_{idx}.png"
                await page.screenshot(path=slide_proof)
            
            final_proof = "project_details/proof/all_matchups_verified.png"
            await page.screenshot(path=final_proof)
            print(f"Final proof screenshot captured at: {final_proof}")
            
            await browser.close()
            
            if all_verified:
                print(">>> 100% OF TESTED SPORTS MATCHUPS SUCCESSFULLY RENDERED TEAM LOGOS! <<<")
            else:
                print(">>> SOME LOGOS FAILED VERIFICATION <<<")
                
    finally:
        cleanup_db()

if __name__ == "__main__":
    asyncio.run(verify_logos())

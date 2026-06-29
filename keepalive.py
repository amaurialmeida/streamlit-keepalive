"""
Streamlit Keep-Alive Script — Amauri Almeida Portfolio
Uses Playwright (headless Chromium) to visit all 11 apps and click
"Yes, get this app back up!" if they are sleeping.

A simple HTTP GET returns 200 even on sleeping apps (static HTML shell).
Only a real browser with JavaScript + WebSocket actually wakes the app.
"""

import asyncio
from playwright.async_api import async_playwright

APPS = [
    ("🌍 Earth Max/Min Temp History",       "https://earth-max-min-temp-history-4dwrafuhe7a5uhaqdkkzld.streamlit.app/"),
    ("🌿 Environmental Dashboard Portfolio", "https://environmental-dashboard-portfolio.streamlit.app/"),
    ("🌊 Santa Rita River Observatory",      "https://santa-rita-river-observatory.streamlit.app/"),
    ("☀️  Solar University NW SP",            "https://solar-university-nw-sp.streamlit.app/"),
    ("🐝 Bee Colony Collapse Brazil",         "https://bee-colony-collapse-brazil.streamlit.app/"),
    ("💨 Patagonia Wind Energy",             "https://patagonia-wind-energy.streamlit.app/"),
    ("💧 Patagonia Water Quality",           "https://patagonia-water-quality.streamlit.app/"),
    ("🌋 Patagonia Seismic",                 "https://patagonia-seismic.streamlit.app/"),
    ("🦫 Invasive Alien Species Impact",     "https://invasive-alien-species-impact.streamlit.app/"),
    ("🍯 Stingless Bee Observatory BR",      "https://stingless-bee-observatory-br.streamlit.app/"),
    ("🌡️  El Niño 2026 ML Forecast",         "https://el-nino-2026-ml-forecast.streamlit.app/"),
]

async def visit(page, name, url):
    print(f"\n➜ {name}")
    print(f"  URL: {url}")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        # Wait for page to settle and potentially show wake-up button
        await page.wait_for_timeout(7000)

        # Check for the Streamlit sleep/wake-up button
        wake_btn = page.get_by_role("button", name="Yes, get this app back up!")
        if await wake_btn.count() > 0:
            print(f"  💤 App sleeping — clicking wake-up button...")
            await wake_btn.click()
            # Wait up to 90s for the app to start loading after wake
            await page.wait_for_timeout(90_000)
            print(f"  ✅ Wake-up button clicked — app should be loading")
        else:
            print(f"  ✅ App is already awake")

    except Exception as e:
        print(f"  ❌ Error: {e}")

async def main():
    print("=" * 60)
    print("  Streamlit Keep-Alive — Amauri Almeida Portfolio")
    print(f"  Total apps: {len(APPS)}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for name, url in APPS:
            await visit(page, name, url)

        await browser.close()

    print("\n" + "=" * 60)
    print("  All apps processed ✅")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

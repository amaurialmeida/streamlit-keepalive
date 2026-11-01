"""Keep-alive dos aplicativos Streamlit do portfólio.

Abre cada app em um Chromium real para que o Community Cloud registre tráfego.
Quando o app está hibernando, clica no botão de despertar.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

from playwright.async_api import Browser, Page, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


@dataclass(frozen=True)
class App:
    name: str
    url: str


APPS = [
    App("Bee Colony Collapse Brazil", "https://bee-colony-collapse-brazil.streamlit.app/"),
    App("Santa Rita River Observatory", "https://santa-rita-river-observatory.streamlit.app/"),
    App("Solar University NW SP", "https://solar-university-nw-sp.streamlit.app/"),
    App("Patagonia Wind Energy", "https://patagonia-wind-energy.streamlit.app/"),
    App("Patagonia Water Quality", "https://patagonia-water-quality.streamlit.app/"),
    App("Patagonia Seismic", "https://patagonia-seismic.streamlit.app/"),
    App("Invasive Alien Species Impact", "https://invasive-alien-species-impact.streamlit.app/"),
    App("Stingless Bee Observatory BR", "https://stingless-bee-observatory-br.streamlit.app/"),
    App("El Niño 2026 ML Forecast", "https://el-nino-2026-ml-forecast.streamlit.app/"),
    App("Road to Patagonia", "https://road-to-patagonia.streamlit.app/"),
    App("Earth Max/Min Temp History", "https://earth-max-min-temp-history-4dwrafuhe7a5uhaqdkkzld.streamlit.app/"),
    App("Environmental Dashboard Portfolio", "https://environmental-dashboard-portfolio.streamlit.app/"),
    App("Carbon Footprint Tracker", "https://carbon-footprint-tracker-tkfv5pthky3rk2gd8m9mm8.streamlit.app/"),
]

CONCURRENCY = int(os.getenv("KEEPALIVE_CONCURRENCY", "4"))
NAVIGATION_TIMEOUT_MS = 90_000
WAKE_WAIT_MS = 45_000


async def visit(browser: Browser, app: App, semaphore: asyncio.Semaphore) -> bool:
    async with semaphore:
        page: Page = await browser.new_page()
        try:
            print(f"START  {app.name} | {app.url}", flush=True)
            await page.goto(app.url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
            await page.wait_for_timeout(5_000)

            wake_button = page.get_by_role("button", name="Yes, get this app back up!")
            if await wake_button.count() > 0 and await wake_button.first.is_visible():
                print(f"WAKE   {app.name}", flush=True)
                await wake_button.first.click(timeout=15_000)
                await page.wait_for_timeout(WAKE_WAIT_MS)
            else:
                print(f"OK     {app.name} (already awake)", flush=True)
            return True
        except (Exception,) as exc:
            print(f"FAIL   {app.name} | {type(exc).__name__}: {exc}", flush=True)
            return False
        finally:
            await page.close()


async def main() -> None:
    print(f"Streamlit keep-alive: {len(APPS)} apps; concurrency={CONCURRENCY}", flush=True)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            results = await asyncio.gather(
                *(visit(browser, app, semaphore) for app in APPS)
            )
        finally:
            await browser.close()

    succeeded = sum(results)
    failed = len(results) - succeeded
    print(f"SUMMARY success={succeeded} failed={failed}", flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

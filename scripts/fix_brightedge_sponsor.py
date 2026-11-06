import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for page in context.pages:
            if 'brightedge' in page.url:
                # Find the sponsorship select
                selects = await page.query_selector_all('select')
                for s in selects:
                    lbl = (await s.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""') or '')
                    if 'sponsorship' in lbl or 'require sponsorship' in lbl:
                        opts = await s.query_selector_all('option')
                        for o in opts:
                            txt = (await o.text_content() or '').strip()
                            if 'no' in txt.lower():
                                await s.select_option(label=txt)
                                print(f"Fixed Sponsorship to 'No': {txt}")
                                break

asyncio.run(main())

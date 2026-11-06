import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for page in context.pages:
            if 'job/26015724/apply' in page.url:
                inp = await page.query_selector('input[name="region2"]')
                if inp:
                    attrs = await page.evaluate('''el => {
                        const res = {};
                        for (let a of el.attributes) res[a.name] = a.value;
                        return res;
                    }''', inp)
                    print('region2 attributes:', attrs)

asyncio.run(main())


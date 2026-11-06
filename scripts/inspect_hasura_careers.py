import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto('https://hasura.io/careers', wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(3)
        links = await page.query_selector_all('a')
        print(f'Total links on Hasura careers: {len(links)}')
        for l in links:
            href = await l.get_attribute('href') or ''
            t = (await l.text_content() or '').strip()
            if any(k in href.lower() or k in t.lower() for k in ['job', 'career', 'devops', 'sre', 'engineer', 'lever', 'greenhouse', 'ashby', 'bamboohr']):
                print(f'{t} -> {href}')
        await page.close()

asyncio.run(main())


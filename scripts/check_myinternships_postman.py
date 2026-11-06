import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        # Let's open a new page in Edge
        page = await context.new_page()
        await page.goto('https://myinternships.in/jobs/postman-devops-engineer-gurugram-1683be', wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(2)
        print('Title:', await page.title())
        txt = await page.inner_text('body')
        print('Text snippet:\n', txt[:600])
        # Find external link / apply button
        apply_links = await page.query_selector_all('a:has-text("Apply"), a:has-text("apply"), button:has-text("Apply")')
        for al in apply_links:
            href = await al.get_attribute('href')
            print('Apply link:', href)

asyncio.run(main())


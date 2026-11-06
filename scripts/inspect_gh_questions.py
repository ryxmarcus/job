import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        # Inspect Particle41 tab
        page = await context.new_page()
        await page.goto('https://job-boards.greenhouse.io/particle41llc/jobs/5018960008', wait_until='domcontentloaded')
        await asyncio.sleep(2)

        # Get all field labels and question wrappers
        fields = await page.query_selector_all('.field, [data-field]')
        print(f"Total fields found: {len(fields)}")
        for f in fields:
            lbl = await f.query_selector('label, legend')
            lbl_text = await lbl.inner_text() if lbl else ''
            print("FIELD:", lbl_text.strip().replace('\n', ' '))

if __name__ == '__main__':
    asyncio.run(main())


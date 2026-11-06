import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = await context.new_page()
        sheet_url = 'https://docs.google.com/spreadsheets/d/17p_0_0e3NYw685Wnbo5GSiW-UUMbdEzKsTMrGx48lgs/edit'
        print(f"Navigating to Google Sheet: {sheet_url}...")
        await page.goto(sheet_url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(4)
        title = await page.title()
        print('Sheet Page Title:', title)
        print('URL:', page.url)

if __name__ == '__main__':
    asyncio.run(main())


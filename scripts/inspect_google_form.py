import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        page = await ctx.new_page()
        url = 'https://docs.google.com/forms/d/e/1FAIpQLSdddRIWDffz6EnCwCFn7oVvImHmwyFokrRdmfmvHsyEIAva-A/viewform?usp=header'
        print(f"Opening Google Form: {url}...")
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            await asyncio.sleep(3)
            print("Page Title:", await page.title())
            print("Current URL:", page.url)
            
            # Check form contents / questions
            body_text = await page.inner_text('body')
            print("Form Content Snippet (first 1000 chars):")
            print(body_text[:1000])

            # Look for questions
            questions = await page.query_selector_all('[role="listitem"], .geFormQuestion, [data-params]')
            print(f"\nTotal question containers: {len(questions)}")
            
        except Exception as e:
            print("Error loading Google Form:", e)

if __name__ == '__main__':
    asyncio.run(main())


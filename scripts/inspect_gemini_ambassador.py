import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        page = await ctx.new_page()
        url = 'https://recruitment.geministudentambassador.com/'
        print(f"Navigating to: {url}...")
        try:
            resp = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)
            print("Response status:", resp.status if resp else 'N/A')
            print("Current URL:", page.url)
            print("Page Title:", await page.title())

            body_text = await page.inner_text('body')
            print("Body text snippet (first 1000 chars):\n", body_text[:1000])

            # Inspect inputs / form fields
            inputs = await page.query_selector_all('input, select, textarea, button')
            print(f"\nTotal interactive elements: {len(inputs)}")
            for inp in inputs:
                tag = await inp.evaluate('e => e.tagName')
                itype = await inp.get_attribute('type') or ''
                name = await inp.get_attribute('name') or ''
                id_attr = await inp.get_attribute('id') or ''
                placeholder = await inp.get_attribute('placeholder') or ''
                aria = await inp.get_attribute('aria-label') or ''
                txt = (await inp.inner_text()).strip().replace('\n', ' ') if tag == 'BUTTON' else ''
                print(f"[{tag}] type={itype}, id={id_attr}, name={name}, placeholder={placeholder}, aria={aria}, text={txt[:30]}")

        except Exception as e:
            print("Navigation/Inspection error:", e)

if __name__ == '__main__':
    asyncio.run(main())


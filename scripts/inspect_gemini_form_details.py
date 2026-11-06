import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        pg = [page for page in ctx.pages if 'geministudentambassador' in page.url][0]
        
        # Get all question containers or labels
        labels = await pg.query_selector_all('label, .question, [class*="question"], [class*="field"], [class*="label"]')
        print(f"Total labels/elements found: {len(labels)}")
        for l in labels:
            t = (await l.inner_text()).strip().replace('\n', ' -- ')
            f = await l.get_attribute('for') or ''
            c = await l.get_attribute('class') or ''
            if t and len(t) < 300:
                print(f"for={f} | class={c} | text={t}")

if __name__ == '__main__':
    asyncio.run(main())


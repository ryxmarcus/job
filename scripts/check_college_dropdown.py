import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        inps = await pg.query_selector_all('input')
        await inps[6].click()
        await inps[6].fill('Delhi')
        await asyncio.sleep(1)
        
        # Check all visible text items in dropdown
        items = await pg.evaluate("""() => {
            let res = [];
            document.querySelectorAll('div, li, span').forEach(el => {
                if (el.className && (el.className.includes('item') || el.className.includes('option') || el.className.includes('menu'))) {
                    let t = el.innerText.trim();
                    if (t && t.length > 2 && t.length < 100 && !res.includes(t)) {
                        res.push(t);
                    }
                }
            });
            return res;
        }""")
        print("Visible items in dropdown:")
        for it in items:
            print("  *", it)

if __name__ == '__main__':
    asyncio.run(main())

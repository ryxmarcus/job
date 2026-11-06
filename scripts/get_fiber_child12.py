import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministassador' in page.url or 'gemini' in page.url][0]

        res = await pg.evaluate("""() => {
            let el = document.querySelector('[data-block-id="96b342ff-2005-4b61-9c1f-bd2bdd4b168d"]');
            if (!el) return 'el not found';
            let key = Object.keys(el).find(k => k.startsWith('__reactFiber'));
            let fiber = el[key];
            return {
                memoizedProps: fiber ? Object.keys(fiber.memoizedProps || {}) : [],
                blockType: fiber ? fiber.memoizedProps?.block?.type : null,
                component: fiber?.type?.name || 'unknown'
            };
        }""")
        print("Child 12 Fiber Info:", res)

if __name__ == '__main__':
    asyncio.run(main())


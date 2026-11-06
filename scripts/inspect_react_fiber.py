import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # Let's inspect React state / props on the form
        state_info = await pg.evaluate("""() => {
            let form = document.querySelector('form');
            // Check React Fiber
            let fiberKey = Object.keys(form).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
            return fiberKey ? 'Fiber found: ' + fiberKey : 'No fiber on form';
        }""")
        print(state_info)

if __name__ == '__main__':
    asyncio.run(main())


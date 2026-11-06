import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'gemini' in page.url][0]

        res = await pg.evaluate("""() => {
            let form = document.querySelector('form');
            let key = Object.keys(form).find(k => k.startsWith('__reactFiber'));
            let fiber = form[key];
            
            // Search upwards in fiber for state or context
            let curr = fiber;
            let found = [];
            while (curr && found.length < 10) {
                if (curr.memoizedState) {
                    found.push({
                        name: curr.type?.name || 'unknown',
                        stateKeys: Object.keys(curr.memoizedState)
                    });
                }
                curr = curr.return;
            }
            return found;
        }""")
        print("Fiber ancestors with state:")
        for f in res:
            print(" ", f)

if __name__ == '__main__':
    asyncio.run(main())


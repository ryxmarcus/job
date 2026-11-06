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
            let q1Key = 'd9073717-bf14-4715-984c-3cb4ff6ed290';
            let curr = fiber;
            
            while (curr) {
                let props = curr.memoizedProps;
                if (props) {
                    for (let pkey of Object.keys(props)) {
                        let val = props[pkey];
                        if (val && typeof val === 'object' && val[q1Key]) {
                            return {
                                propName: pkey,
                                keys: Object.keys(val),
                                valType: Array.isArray(val) ? 'array' : typeof val
                            };
                        }
                    }
                }
                curr = curr.return;
            }
            return 'Not found';
        }""")
        print("Exact prop holding form values:", res)

if __name__ == '__main__':
    asyncio.run(main())


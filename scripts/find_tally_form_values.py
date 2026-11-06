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
            
            // Search fiber tree for form values object containing the answered question keys
            let q1Key = 'd9073717-bf14-4715-984c-3cb4ff6ed290';
            let curr = fiber;
            let foundState = null;
            
            function searchObj(obj, depth = 0) {
                if (!obj || depth > 5) return null;
                if (typeof obj === 'object') {
                    if (obj[q1Key] || (obj.values && obj.values[q1Key])) {
                        return obj;
                    }
                    for (let k of Object.keys(obj)) {
                        try {
                            let res = searchObj(obj[k], depth + 1);
                            if (res) return res;
                        } catch(e) {}
                    }
                }
                return null;
            }

            while (curr) {
                if (curr.memoizedState) {
                    let s = searchObj(curr.memoizedState);
                    if (s) return { location: 'memoizedState', keys: Object.keys(s) };
                }
                if (curr.memoizedProps) {
                    let s = searchObj(curr.memoizedProps);
                    if (s) return { location: 'memoizedProps', keys: Object.keys(s) };
                }
                curr = curr.return;
            }
            return 'Not found';
        }""")
        print("Search for form values in React Fiber:", res)

if __name__ == '__main__':
    asyncio.run(main())


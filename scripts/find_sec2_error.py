import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        err_elements = await pg.evaluate("""() => {
            let res = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.children.length === 0 && el.innerText) {
                    let t = el.innerText.trim();
                    if (t === 'Please select an option' || t === 'Please enter a value' || t.includes('attention') || t.includes('required')) {
                        let parent = el.parentElement;
                        let context = parent ? parent.innerText.replace(/\\n/g, ' ') : '';
                        res.push({ text: t, context: context });
                    }
                }
            });
            return res;
        }""")
        print("Error elements:", err_elements)

if __name__ == '__main__':
    asyncio.run(main())


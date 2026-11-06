import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        indicators = await pg.query_selector_all('.tally-required-indicator')
        ind5 = indicators[5]
        
        info = await ind5.evaluate("""el => {
            let container = el.closest('div[class*="question"], div[data-block-id], section, form > div') || el.parentElement.parentElement;
            let nextSiblings = [];
            let curr = el.parentElement.nextElementSibling;
            while (curr && nextSiblings.length < 10) {
                nextSiblings.push({
                    tag: curr.tagName,
                    class: curr.className,
                    html: curr.outerHTML.substring(0, 300)
                });
                curr = curr.nextElementSibling;
            }
            return {
                parentHTML: container ? container.outerHTML.substring(0, 1000) : 'none',
                nextSiblings: nextSiblings
            };
        }""")
        print("Indicator 5 container and siblings:")
        for s in info['nextSiblings']:
            print(" SIBLING:", s)

if __name__ == '__main__':
    asyncio.run(main())


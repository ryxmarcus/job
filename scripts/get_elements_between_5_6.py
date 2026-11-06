import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        res = await pg.evaluate("""() => {
            let inds = document.querySelectorAll('.tally-required-indicator');
            if (inds.length < 7) return 'Not enough indicators';
            let el5 = inds[5];
            let el6 = inds[6];
            
            // Walk up until we find common ancestor or top-level blocks
            let p5 = el5;
            while (p5 && p5.parentElement && !p5.parentElement.classList.contains('tally-block') && p5.parentElement !== document.body) {
                p5 = p5.parentElement;
            }
            let p6 = el6;
            while (p6 && p6.parentElement && !p6.parentElement.classList.contains('tally-block') && p6.parentElement !== document.body) {
                p6 = p6.parentElement;
            }
            
            let nodes = [];
            let curr = p5.nextElementSibling;
            while (curr && curr !== p6) {
                nodes.push({
                    tag: curr.tagName,
                    class: curr.className,
                    text: curr.innerText ? curr.innerText.substring(0, 100) : '',
                    html: curr.outerHTML.substring(0, 200)
                });
                curr = curr.nextElementSibling;
            }
            return { p5HTML: p5.outerHTML.substring(0, 300), nodes: nodes };
        }""")
        print("Nodes between 5 and 6:")
        if isinstance(res, dict):
            for n in res.get('nodes', []):
                print(" ", n)
        else:
            print(res)

if __name__ == '__main__':
    asyncio.run(main())


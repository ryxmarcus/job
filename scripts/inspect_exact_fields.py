import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        inputs = await pg.query_selector_all('input')
        for idx in [4, 5, 7, 8, 9, 10]:
            inp = inputs[idx]
            info = await inp.evaluate('''el => {
                let text = '';
                let node = el;
                for (let i = 0; i < 4 && node; i++) {
                    let parent = node.parentElement;
                    if (parent) {
                        let labels = parent.querySelectorAll('label, p, h2, h3, h4, span');
                        for (let l of labels) {
                            let t = l.innerText.trim();
                            if (t && !text.includes(t)) text += t + ' | ';
                        }
                    }
                    node = parent;
                }
                return { id: el.id, placeholder: el.placeholder, text: text };
            }''')
            print(f"[{idx}] ID={info['id']} | PH={info['placeholder']}")
            print(f"   TEXT: {info['text'][:250]}\n")

if __name__ == '__main__':
    asyncio.run(main())


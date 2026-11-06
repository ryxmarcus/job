import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        inputs = await pg.query_selector_all('input, select, textarea')
        print(f"Total inputs: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            info = await inp.evaluate("""el => {
                let p = el.parentElement;
                let text = '';
                for (let i = 0; i < 4 && p; i++) {
                    let headings = p.querySelectorAll('h1, h2, h3, h4, p, span, label');
                    for (let h of headings) {
                        let t = h.innerText.trim();
                        if (t && t.length > 2 && t.length < 150 && !text.includes(t)) {
                            text += t + ' | ';
                        }
                    }
                    p = p.parentElement;
                }
                return {
                    tag: el.tagName,
                    type: el.type,
                    id: el.id,
                    placeholder: el.placeholder,
                    context: text
                };
            }""")
            print(f"[{idx}] ID: {info['id']} | TYPE: {info['type']} | PH: {info['placeholder']}")
            print(f"    CONTEXT: {info['context'][:180]}\n")

if __name__ == '__main__':
    asyncio.run(main())


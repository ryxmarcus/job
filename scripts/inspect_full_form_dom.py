import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        # Extract all form rows/sections
        data = await pg.evaluate("""() => {
            const rows = [];
            document.querySelectorAll('div').forEach(d => {
                const text = d.innerText ? d.innerText.trim() : '';
                const input = d.querySelector('input, select, textarea');
                if (input && text && text.length < 200 && !d.querySelector('div')) {
                    rows.push({
                        text: text.replace(/\\n/g, ' '),
                        tag: input.tagName,
                        type: input.type,
                        id: input.id,
                        ph: input.placeholder,
                        val: input.value
                    });
                }
            });
            return rows;
        }""")
        print(f"Extracted {len(data)} direct input containers:")
        for r in data:
            print(f"- {r['text'][:50]} | tag={r['tag']}, type={r['type']}, id={r['id']}, ph={r['ph']}, val={r['val']}")

if __name__ == '__main__':
    asyncio.run(main())


import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = b.contexts[0].pages[-1]
        for q_id in ['33232091003', '33232122003', '33232092003', '33232093003', '33232094003', '33232095003', '33180752003', '33232096003', '33180741003', '33180743003', '33180744003', '33180745003', '33180746003', '33180747003', '33180748003', '33180749003', '33180750003', '33180751003']:
            el = await pg.query_selector(f'#question_{q_id}')
            if el:
                tag = await el.evaluate('e => e.tagName')
                itype = await el.get_attribute('type') or ''
                print(f'{q_id}: tag={tag}, type={itype}')
                if tag == 'SELECT':
                    opts = await el.query_selector_all('option')
                    otexts = [await o.inner_text() for o in opts]
                    print(f'  options: {otexts}')
            else:
                mult = await pg.query_selector_all(f'[name*="{q_id}"]')
                print(f'{q_id}: multiple ({len(mult)})')
                for m in mult:
                    lbl = await m.evaluate('e => e.parentElement.innerText')
                    print(f'   - {lbl.strip().replace(chr(10), " ")}')

if __name__ == '__main__':
    asyncio.run(main())


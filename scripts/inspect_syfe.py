import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        syfe_page = None
        for p_elem in context.pages:
            if 'instahyre.com' in p_elem.url:
                syfe_page = p_elem
                break
        if not syfe_page:
            print('Syfe Instahyre page not found!')
            return

        print('Syfe URL:', syfe_page.url)
        print('Syfe Title:', await syfe_page.title())
        # Let's inspect buttons / apply buttons on page
        buttons = await syfe_page.query_selector_all('button, a.btn, [class*="apply"]')
        print(f'Total buttons found: {len(buttons)}')
        for b in buttons:
            txt = (await b.text_content() or '').strip()
            cls = await b.get_attribute('class') or ''
            id_attr = await b.get_attribute('id') or ''
            href = await b.get_attribute('href') or ''
            if any(k in txt.lower() for k in ['apply', 'login', 'submit', 'profile', 'rahul']):
                print(f'Btn: id={id_attr}, class={cls}, text={txt}, href={href}')

        body_txt = await syfe_page.inner_text('body')
        print('Syfe body excerpt:\n', body_txt[:500])

asyncio.run(main())


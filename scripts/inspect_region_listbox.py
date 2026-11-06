import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = None
        for p_elem in context.pages:
            if 'job/26015724/apply' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX apply page not found!')
            return

        listbox = await page.query_selector('#region2-93-listbox')
        if listbox:
            txt = await listbox.inner_text()
            print('Listbox text:\n', txt)
            # Find Delhi item inside listbox
            delhi_el = await listbox.query_selector('text="Delhi", text="DL", text="National Capital Territory of Delhi"')
            if delhi_el:
                print('Found Delhi element inside listbox, clicking it!')
                await delhi_el.click()
            else:
                items = await listbox.query_selector_all('*')
                print('Total items inside listbox:', len(items))
                for it in items[:20]:
                    t = (await it.text_content() or '').strip()
                    if t:
                        print('  Item:', t)

asyncio.run(main())


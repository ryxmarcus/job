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
            if 'careers.americanexpress.com' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX page not found!')
            return

        next_issue = await page.query_selector('button:has-text("Go to Next Issue"), a:has-text("Go to Next Issue")')
        if next_issue:
            print('Clicking Go to Next Issue...')
            await next_issue.click()
            await asyncio.sleep(1)
            # Find which element is active / focused
            focused = await page.evaluate('''() => {
                const el = document.activeElement;
                return {
                    tag: el ? el.tagName : null,
                    id: el ? el.id : null,
                    name: el ? el.name : null,
                    label: el ? el.getAttribute('aria-label') : null,
                    text: el ? el.innerText : null,
                    outer: el ? el.outerHTML.slice(0, 300) : null
                };
            }''')
            print('Focused issue element:', focused)

asyncio.run(main())


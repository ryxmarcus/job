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
            print('AMEX apply page [5] not found!')
            return

        print('URL:', page.url)
        # Find all alert texts on this page
        alerts = await page.query_selector_all('[role="alert"], .error, [aria-invalid="true"]')
        print(f'Alerts on page: {len(alerts)}')
        for a in alerts:
            t = (await a.text_content() or '').strip()
            if t:
                print('Alert:', t)

        # Click Go to Next Issue if present
        issue_btn = await page.query_selector('a:has-text("Go to Next Issue"), button:has-text("Go to Next Issue")')
        if issue_btn:
            print('Clicking Go to Next Issue button...')
            await issue_btn.click()
            await asyncio.sleep(1)
            # Find focused element
            f = await page.evaluate('''() => {
                const el = document.activeElement;
                return {
                    id: el ? el.id : null,
                    name: el ? el.name : null,
                    aria: el ? el.getAttribute('aria-label') : null,
                    outer: el ? el.outerHTML.slice(0, 300) : null
                };
            }''')
            print('Focused issue element:', f)

asyncio.run(main())


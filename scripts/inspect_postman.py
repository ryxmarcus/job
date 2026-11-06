import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        postman_page = None
        for p_elem in context.pages:
            if 'postman.com' in p_elem.url:
                postman_page = p_elem
                break
        if not postman_page:
            print('Postman page not found!')
            return

        print('Postman URL:', postman_page.url)
        # Search for jobs on page
        links = await postman_page.query_selector_all('a')
        print(f'Total links on Postman: {len(links)}')
        matched = []
        for l in links:
            href = await l.get_attribute('href') or ''
            txt = (await l.text_content() or '').strip()
            if any(k in href.lower() or k in txt.lower() for k in ['devops', 'sre', 'cloud', 'infrastructure', 'platform', 'gurugram', 'gurgaon', 'bangalore', 'india', 'gh_jid', 'greenhouse']):
                matched.append((txt, href))
        print(f'Matched jobs ({len(matched)}):')
        for m in matched[:20]:
            print(' ', m)

asyncio.run(main())


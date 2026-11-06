import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        page = await ctx.new_page()
        try:
            await page.goto('https://www.naukri.com/mnjuser/profile', wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            # Check recruiter actions / search appearances
            stat_cards = await page.query_selector_all('.card, .stat, [class*="stat"], [class*="activity"]')
            for s in stat_cards:
                txt = (await s.inner_text()).strip().replace('\n', ' | ')
                if any(w in txt.lower() for w in ['search', 'action', 'view', 'recruiter', 'appearance', 'download']):
                    print("STAT CARD:", txt)

            # Check messages / chat directly
            chat_url = 'https://www.naukri.com/chat/user'
            await page.goto(chat_url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            print("Chat page title:", await page.title())
            chat_text = await page.inner_text('body')
            print("Chat snippet:\n", chat_text[:500].replace('\n', ' -- '))

        except Exception as e:
            print('Error:', e)
        finally:
            await page.close()

if __name__ == '__main__':
    asyncio.run(main())


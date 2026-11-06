import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        # Open in active tab
        page = await ctx.new_page()
        url = 'https://docs.google.com/forms/d/e/1FAIpQLSdddRIWDffz6EnCwCFn7oVvImHmwyFokrRdmfmvHsyEIAva-A/viewform?usp=header'
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)
        print("Final URL:", page.url)
        print("Page Title:", await page.title())
        
        # Check if Google Accounts sign-in page appeared
        if 'accounts.google.com' in page.url:
            print("Google Sign-in page reached!")
            # Check for email input
            email_inp = await page.query_selector('input[type="email"]')
            if email_inp:
                print("Typing DTU email: rahul_23bmba18@dtu.ac.in...")
                await email_inp.fill('rahul_23bmba18@dtu.ac.in')
                next_btn = await page.query_selector('#identifierNext, button:has-text("Next")')
                if next_btn:
                    await next_btn.click()
                    print("Clicked Next on Google Sign-In.")
                    await asyncio.sleep(3)
                    print("Post-Next URL:", page.url)

if __name__ == '__main__':
    asyncio.run(main())


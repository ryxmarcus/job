import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        natwest_page = None
        for p_elem in context.pages:
            if 'rbs.wd3.myworkdayjobs.com' in p_elem.url:
                natwest_page = p_elem
                break
        if not natwest_page:
            print('NatWest page not found!')
            return

        print('Filling all required Step 2 inputs by ID...')
        # Name
        fn = await natwest_page.query_selector('#name--legalName--firstName')
        if fn:
            await fn.fill('Rahul')
        ln = await natwest_page.query_selector('#name--legalName--lastName')
        if ln:
            await ln.fill('Kumar')

        # Address
        addr1 = await natwest_page.query_selector('#address--addressLine1')
        if addr1:
            await addr1.fill('Sector 21 Rohini')
        city = await natwest_page.query_selector('#address--city')
        if city:
            await city.fill('Delhi')
        pin = await natwest_page.query_selector('#address--postalCode')
        if pin:
            await pin.fill('110085')

        # Phone
        phone = await natwest_page.query_selector('#phoneNumber--phoneNumber')
        if phone:
            await phone.fill('7210476048')

        # Radio No
        r_no = await natwest_page.query_selector('#p2xb7')
        if r_no:
            await r_no.click()

        # Source button
        src_btn = await natwest_page.query_selector('#source--source')
        if src_btn:
            print('Clicking source dropdown...')
            await src_btn.click()
            await asyncio.sleep(1)
            # Find options
            opts = await natwest_page.query_selector_all('li[role="option"], ul[role="listbox"] li, div[data-automation-id="promptOption"]')
            print(f'Found {len(opts)} source options')
            if opts:
                await opts[0].click()
                print('Selected source:', await opts[0].text_content())
            else:
                await natwest_page.keyboard.press('ArrowDown')
                await asyncio.sleep(0.5)
                await natwest_page.keyboard.press('Enter')

        await asyncio.sleep(2)
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 2 save:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Body excerpt after step 2:\n', txt[:700])

asyncio.run(main())


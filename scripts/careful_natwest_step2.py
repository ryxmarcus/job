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

        # 1. Given name (First Name)
        fn_input = await natwest_page.query_selector('input[data-automation-id="name--legalName--firstName"]')
        if fn_input:
            await fn_input.click()
            await fn_input.focus()
            await natwest_page.keyboard.type('Rahul', delay=50)
            await natwest_page.keyboard.press('Tab')
            print('Typed Rahul in Given Name')

        # Last name
        ln_input = await natwest_page.query_selector('input[data-automation-id="name--legalName--lastName"]')
        if ln_input:
            await ln_input.click()
            await ln_input.focus()
            await natwest_page.keyboard.type('Kumar', delay=50)
            await natwest_page.keyboard.press('Tab')
            print('Typed Kumar in Family Name')

        # Address Line 1
        addr1_input = await natwest_page.query_selector('input[data-automation-id="address--addressLine1"]')
        if addr1_input:
            await addr1_input.click()
            await addr1_input.focus()
            await natwest_page.keyboard.type('Sector 21 Rohini', delay=50)
            await natwest_page.keyboard.press('Tab')
            print('Typed Address Line 1')

        # City
        city_input = await natwest_page.query_selector('input[data-automation-id="address--city"]')
        if city_input:
            await city_input.click()
            await city_input.focus()
            await natwest_page.keyboard.type('Delhi', delay=50)
            await natwest_page.keyboard.press('Tab')

        # Postal code
        pin_input = await natwest_page.query_selector('input[data-automation-id="address--postalCode"]')
        if pin_input:
            await pin_input.click()
            await pin_input.focus()
            await natwest_page.keyboard.type('110085', delay=50)
            await natwest_page.keyboard.press('Tab')

        # Phone Number
        phone_input = await natwest_page.query_selector('input[data-automation-id="phoneNumber--phoneNumber"]')
        if phone_input:
            await phone_input.click()
            await phone_input.focus()
            await natwest_page.keyboard.type('7210476048', delay=50)
            await natwest_page.keyboard.press('Tab')

        # Radio No
        r_no = await natwest_page.query_selector('label[for="p2xb7"], input[id="p2xb7"]')
        if r_no:
            await r_no.click()
            print('Clicked Radio No')

        # How did you hear about us?
        src_btn = await natwest_page.query_selector('button[data-automation-id="source--source"]')
        if src_btn:
            print('Clicking source button...')
            await src_btn.click()
            await asyncio.sleep(1)
            # Find options
            opts = await natwest_page.query_selector_all('li[role="option"], [data-automation-id="promptOption"]')
            print('Source prompt options found:', len(opts))
            if opts:
                await opts[0].click()
                print('Clicked first source option:', await opts[0].text_content())
            else:
                await natwest_page.keyboard.press('ArrowDown')
                await asyncio.sleep(0.5)
                await natwest_page.keyboard.press('Enter')

        await asyncio.sleep(1)
        save_btn = await natwest_page.query_selector('button[data-automation-id="bottom-navigation-next-button"]')
        if save_btn:
            print('Clicking Save and Continue...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 2 save:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Body excerpt after step 2:\n', txt[:600])

asyncio.run(main())


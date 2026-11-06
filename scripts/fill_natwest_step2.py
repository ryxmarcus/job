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

        print('Filling NatWest Step 2 fields...')

        # Fill name
        fn = await natwest_page.query_selector('[data-automation-id="name--legalName--firstName"]')
        if fn:
            await fn.fill('Rahul')
        
        ln = await natwest_page.query_selector('[data-automation-id="name--legalName--lastName"]')
        if ln:
            await ln.fill('Kumar')

        # Fill address
        addr1 = await natwest_page.query_selector('[data-automation-id="address--addressLine1"]')
        if addr1:
            await addr1.fill('Sector 21, Rohini')

        city = await natwest_page.query_selector('[data-automation-id="address--city"]')
        if city:
            await city.fill('Delhi')

        pin = await natwest_page.query_selector('[data-automation-id="address--postalCode"]')
        if pin:
            await pin.fill('110085')

        # Phone number
        phone = await natwest_page.query_selector('[data-automation-id="phoneNumber--phoneNumber"]')
        if phone:
            await phone.fill('7210476048')

        # Country Phone Code
        cpc_btn = await natwest_page.query_selector('[data-automation-id="phoneNumber--countryPhoneCode"]')
        if cpc_btn:
            try:
                await cpc_btn.click()
                await asyncio.sleep(1)
                opt = await natwest_page.query_selector('li:has-text("India (+91)")')
                if opt:
                    await opt.click()
                else:
                    await natwest_page.keyboard.type('India')
                    await asyncio.sleep(0.5)
                    await natwest_page.keyboard.press('Enter')
            except Exception as e:
                print('Error setting country code:', e)

        # Source
        src_btn = await natwest_page.query_selector('[data-automation-id="source--source"]')
        if src_btn:
            try:
                await src_btn.click()
                await asyncio.sleep(1)
                opt = await natwest_page.query_selector('li:has-text("LinkedIn"), li:has-text("Job Board"), li:has-text("Career Site")')
                if opt:
                    await opt.click()
                else:
                    await natwest_page.keyboard.press('ArrowDown')
                    await natwest_page.keyboard.press('Enter')
            except Exception as e:
                print('Error setting source:', e)

        await asyncio.sleep(1)

        # Click Save and Continue
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue on Step 2...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 2:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Step 3 preview:\n', txt[:500])

asyncio.run(main())


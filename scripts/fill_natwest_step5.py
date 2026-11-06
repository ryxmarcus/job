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

        print('Filling NatWest Step 5: Voluntary Disclosures...')

        # 1. Sex: Male
        g_btn = await natwest_page.query_selector('#personalInfoPerson--gender')
        if g_btn:
            await g_btn.click()
            await asyncio.sleep(1)
            opt = await natwest_page.query_selector('li[role="option"]:has-text("Male")')
            if opt:
                await opt.click()
                print('Selected Male')

        # 2. DOB: 03 / 20 / 1998
        m = await natwest_page.query_selector('#personalInfoPerson--dateOfBirth-dateSectionMonth-input')
        if m:
            await m.fill('03')
        d = await natwest_page.query_selector('#personalInfoPerson--dateOfBirth-dateSectionDay-input')
        if d:
            await d.fill('20')
        y = await natwest_page.query_selector('#personalInfoPerson--dateOfBirth-dateSectionYear-input')
        if y:
            await y.fill('1998')
        print('Filled DOB: 03/20/1998')

        # 3. Nationality: Indian
        nat_btn = await natwest_page.query_selector('#personalInfoPerson--nationality')
        if nat_btn:
            await nat_btn.click()
            await asyncio.sleep(1)
            opt = await natwest_page.query_selector('li[role="option"]:has-text("Indian"), li[role="option"]:has-text("India")')
            if opt:
                await opt.click()
                print('Selected Indian')
            else:
                await natwest_page.keyboard.type('Indian')
                await asyncio.sleep(0.5)
                await natwest_page.keyboard.press('Enter')

        # 4. Checkbox terms
        terms = await natwest_page.query_selector('#termsAndConditions--acceptTermsAndAgreements')
        if terms and not await terms.is_checked():
            await terms.click()
            print('Accepted terms & conditions')

        await asyncio.sleep(1)
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue on Step 5...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 5:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Step 6 (Review) preview:\n', txt[:700])

asyncio.run(main())


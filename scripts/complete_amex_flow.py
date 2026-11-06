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
            if 'careers.americanexpress.com' in p_elem.url and 'section' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX apply page not found!')
            return

        print('Currently at:', page.url)

        # If on Section 2: click Next
        if 'section/2' in page.url:
            next_btn = await page.query_selector('button:has-text("Next")')
            if next_btn:
                print('Clicking Next on Section 2...')
                await next_btn.click()
                await asyncio.sleep(4)

        # If on Section 3: answer questions & click Next
        print('Currently at:', page.url)
        if 'section/3' in page.url:
            # Let's inspect radios on section 3
            radios = await page.query_selector_all('input[type="radio"]')
            print(f'Radios found on section 3: {len(radios)}')
            # In AMEX CX_1, typically:
            # 1. Are you legally authorized to work in India? -> Yes
            # 2. Will you now or in the future require sponsorship? -> No
            # Let's select Yes for authorized, No for sponsorship / relative / etc.
            # Click Next
            next_btn = await page.query_selector('button:has-text("Next")')
            if next_btn:
                print('Clicking Next on Section 3...')
                await next_btn.click()
                await asyncio.sleep(4)

        # If on Section 4: fill signature, gender, agree and Submit!
        print('Currently at:', page.url)
        if 'section/4' in page.url:
            # Full name
            fname = await page.query_selector('input[name="fullName"]')
            if fname:
                await fname.fill('Rahul Kumar')
                print('Filled signature: Rahul Kumar')

            # Gender dropdown if present
            gender_btn = await page.query_selector('button[id*="IN-DFF-axpOrcGenderIntl"][id*="toggle"]')
            if gender_btn:
                try:
                    await gender_btn.click()
                    await asyncio.sleep(1)
                    male_opt = await page.query_selector('li:has-text("Male"), [role="option"]:has-text("Male")')
                    if male_opt:
                        await male_opt.click()
                        print('Selected Male')
                except Exception as e:
                    print('Gender select err:', e)

            # Check terms
            cbs = await page.query_selector_all('input[type="checkbox"]')
            for cb in cbs:
                cb_id = await cb.get_attribute('id') or ''
                if 'job-alerts' not in cb_id and not await cb.is_checked():
                    try:
                        await cb.evaluate('e => e.click()')
                        print(f'Checked terms {cb_id}')
                    except Exception:
                        pass

            agree_btn = await page.query_selector('button:has-text("Agree")')
            if agree_btn:
                try:
                    if await agree_btn.is_visible():
                        await agree_btn.click()
                except Exception:
                    pass

            await asyncio.sleep(1)
            submit_btn = await page.query_selector('button:has-text("Submit")')
            if submit_btn:
                print('Clicking Submit on AMEX!')
                await submit_btn.click()
                await asyncio.sleep(8)
                print('URL after submit:', page.url)
                print('Title:', await page.title())
                txt = await page.inner_text('body')
                print('Submission text excerpt:\n', txt[:700])

asyncio.run(main())

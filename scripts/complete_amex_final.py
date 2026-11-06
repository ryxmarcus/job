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
            print('AMEX apply page not found!')
            return

        # 1. Click "110085, DL"
        pin_opt = await page.query_selector('text="110085, DL"')
        if pin_opt:
            print('Clicking "110085, DL" option...')
            await pin_opt.click()
            await asyncio.sleep(2)

        # 2. Click Next on Section 1
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            print('Clicking Next on Section 1...')
            await next_btn.click()
            await asyncio.sleep(4)
            print('URL after Section 1 Next:', page.url)

        # 3. Section 2 (Education & Experience): click Next
        if 'section/2' in page.url:
            next_btn = await page.query_selector('button:has-text("Next")')
            if next_btn:
                print('Clicking Next on Section 2...')
                await next_btn.click()
                await asyncio.sleep(4)
                print('URL after Section 2 Next:', page.url)

        # 4. Section 3 (Questions): click Next
        if 'section/3' in page.url:
            next_btn = await page.query_selector('button:has-text("Next")')
            if next_btn:
                print('Clicking Next on Section 3...')
                await next_btn.click()
                await asyncio.sleep(4)
                print('URL after Section 3 Next:', page.url)

        # 5. Section 4 (Submit)
        if 'section/4' in page.url:
            print('At Section 4 (Submit)!')
            # Signature
            fname = await page.query_selector('input[name="fullName"]')
            if fname:
                await fname.fill('Rahul Kumar')
                print('Filled signature: Rahul Kumar')

            # Gender dropdown
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
                print('Triggering final Submit button on AMEX!')
                await submit_btn.click()
                await asyncio.sleep(8)
                print('Final AMEX URL:', page.url)
                print('Final AMEX Title:', await page.title())
                txt = await page.inner_text('body')
                print('Confirmation snippet:\n', txt[:700])
                await page.screenshot(path='job/amex_submitted_success.png')

asyncio.run(main())


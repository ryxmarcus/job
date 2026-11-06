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
            if 'apply/section/4' in p_elem.url or 'careers.americanexpress.com' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX page not found!')
            return
        
        print('AMEX URL:', page.url)

        # Let's inspect what questions/inputs remain in section 4
        # Full name / Signature
        fname = await page.query_selector('input[name="fullName"]')
        if fname:
            val = await fname.input_value()
            if not val:
                print('Filling full name...')
                await fname.fill('Rahul Kumar')
                await asyncio.sleep(0.5)

        # Gender dropdown or text
        gender_input = await page.query_selector('input[id*="IN-DFF-axpOrcGenderIntl"]')
        if gender_input:
            val = await gender_input.input_value()
            print('Current gender val:', val)
            if not val:
                toggle = await page.query_selector('button[id*="IN-DFF-axpOrcGenderIntl"][id*="toggle"]')
                if toggle:
                    await toggle.click()
                    await asyncio.sleep(1)
                    male_opt = await page.query_selector('li:has-text("Male"), div[role="option"]:has-text("Male")')
                    if male_opt:
                        await male_opt.click()
                        print('Selected Male from dropdown')
                else:
                    await gender_input.fill('Male')

        # Checkboxes
        checkboxes = await page.query_selector_all('input[type="checkbox"]')
        for cb in checkboxes:
            cb_id = await cb.get_attribute('id') or ''
            checked = await cb.is_checked()
            print(f'Checkbox {cb_id}: checked={checked}')
            # We want to accept terms / statements
            if not checked and 'job-alerts' not in cb_id:
                try:
                    await cb.click(force=True)
                    print(f'Checked {cb_id}')
                except Exception as e:
                    print(f'Failed checking {cb_id}: {e}')

        # Agree button if visible
        agree_btn = await page.query_selector('button:has-text("Agree")')
        if agree_btn:
            try:
                if await agree_btn.is_visible():
                    print('Clicking Agree button...')
                    await agree_btn.click()
                    await asyncio.sleep(1)
            except Exception as e:
                pass

        # Check Submit button
        submit_btn = await page.query_selector('button:has-text("Submit")')
        if submit_btn:
            is_disabled = await submit_btn.get_attribute('disabled')
            print(f'Submit button disabled={is_disabled}')
            print('Triggering Submit...')
            await submit_btn.click()
            await asyncio.sleep(6)
            print('URL after submit:', page.url)
            print('Page title:', await page.title())
            body_text = await page.inner_text('body')
            print('Body excerpt:\n', body_text[:600])

asyncio.run(main())


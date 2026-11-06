import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # The state dropdown options are visible right now
        # Find element whose exact text is "Delhi"
        delhi_option = await pg.query_selector('text="Delhi"')
        if delhi_option:
            print("Found 'Delhi' option element, clicking...")
            await delhi_option.click()
            await asyncio.sleep(1)
        else:
            # Try finding via evaluate
            clicked = await pg.evaluate("""() => {
                let els = Array.from(document.querySelectorAll('div, li, span, p'));
                let d = els.find(el => el.innerText && el.innerText.trim() === 'Delhi' && el.children.length === 0);
                if (d) {
                    d.click();
                    return true;
                }
                return false;
            }""")
            print("Clicked via evaluate:", clicked)

        await asyncio.sleep(1)

        # Check state value
        state_inp = await pg.query_selector('[id="eac24c99-9b75-4011-960d-f8ae4f77d40d"]')
        if state_inp:
            print("State input value now:", await state_inp.input_value())

        # Click Next
        next_btn = await pg.query_selector('button:has-text("Next")')
        if next_btn:
            print("Clicking Next...")
            await next_btn.click()
            await asyncio.sleep(3)
            print("\nPage text snippet after Next:")
            txt = await pg.inner_text('body')
            print(txt[:1000])

if __name__ == '__main__':
    asyncio.run(main())


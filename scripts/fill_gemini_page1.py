import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        print("=== FILLING GEMINI STUDENT AMBASSADOR FORM ===")
        
        # 1. Full Name
        fn = await pg.query_selector('#8d1925ac-555b-4be9-9872-0fc780851774')
        if fn and not (await fn.input_value()):
            await fn.fill('Rahul Kumar')
            print("Filled Name: Rahul Kumar")

        # 2. Email
        em = await pg.query_selector('input[type="email"]')
        if em and not (await em.input_value()):
            await em.fill('rahul_23bmba18@dtu.ac.in')
            print("Filled Email: rahul_23bmba18@dtu.ac.in")

        # 4. Mobile Number
        phone = await pg.query_selector('#34d2dde3-8892-46b3-bd93-2e129796d59c')
        if phone:
            await phone.fill('7210476048')
            print("Filled Phone: 7210476048")

        # 5. Current Year of Study
        # Let's see what options appear when clicking #4d1de708-3ef6-4ee6-aed0-f2f8cdc31c42
        year_inp = await pg.query_selector('#4d1de708-3ef6-4ee6-aed0-f2f8cdc31c42')
        if year_inp:
            await year_inp.click()
            await asyncio.sleep(1)
            # Find options
            opts = await pg.query_selector_all('li, [role="option"], div[class*="item"]')
            print(f"Year options found: {len(opts)}")
            chosen = False
            for o in opts:
                txt = (await o.inner_text()).strip()
                if txt:
                    print("  Year opt:", txt)
                    # Students graduating after March 2027
                    if not chosen and any(w in txt.lower() for w in ['2nd year', '3rd year', '2027', '2028', 'pre-final', 'second year', 'third year']):
                        await o.click()
                        print(f"Selected Year: {txt}")
                        chosen = True
                        break
            if not chosen and opts:
                # Click the last or eligible option
                for o in opts:
                    txt = (await o.inner_text()).strip()
                    if '2027' in txt or '2028' in txt or '3rd' in txt or '2nd' in txt:
                        await o.click()
                        print(f"Selected Year: {txt}")
                        break

        # 7. Search College
        col_inp = await pg.query_selector('#adf7b84a-3ab9-4533-be59-e3dee51707e9')
        if col_inp:
            await col_inp.click()
            await col_inp.fill('Delhi Technological University')
            await asyncio.sleep(1.5)
            # Check suggestions
            suggs = await pg.query_selector_all('li, [role="option"], div[class*="suggestion"]')
            print(f"College suggestions found: {len(suggs)}")
            dtu_found = False
            for s in suggs:
                stxt = (await s.inner_text()).strip()
                if 'delhi technological' in stxt.lower() or 'dtu' in stxt.lower():
                    await s.click()
                    print(f"Selected College: {stxt}")
                    dtu_found = True
                    break
            if not dtu_found:
                print("DTU not in pre-defined list. Checking 'Other college'...")
                chk = await pg.query_selector('#checkbox_54e8437e-0e01-4b5c-8281-fa27fbc89997')
                if chk and not (await chk.is_checked()):
                    await chk.check()
                    await asyncio.sleep(1)
                    # Check if an 'enter college name' input appeared
                    other_inps = await pg.query_selector_all('input[type="text"]')
                    for oi in other_inps:
                        ph = await oi.get_attribute('placeholder') or ''
                        if 'college' in ph.lower() or not (await oi.input_value()):
                            await oi.fill('Delhi Technological University (DTU)')
                            break

        # 9. Course / Branch
        course_inp = await pg.query_selector('#b0b1daf6-dd24-4302-8b40-9f62079dc03d')
        if course_inp:
            await course_inp.fill('MBA Business Analytics & B.Tech IT')
            print("Filled Course / Branch: MBA Business Analytics & B.Tech IT")

        # 10. Instagram Handle (optional)
        insta = await pg.query_selector('#e8d563f2-c904-4aea-affc-a8e782e2ab63')
        if insta:
            # leave blank or fill if user wants
            print("Instagram Handle left blank (optional)")

        # 11. LinkedIn Profile URL
        li = await pg.query_selector('#d128ad84-03b4-472f-a830-31ff3893daa2')
        if li:
            cur_li = await li.input_value()
            if not cur_li:
                await li.fill('https://linkedin.com/in/rahul-kumar-devops')
                print("Filled LinkedIn URL")

        print("=== STAGE 1 COMPLETED ===")

if __name__ == '__main__':
    asyncio.run(main())


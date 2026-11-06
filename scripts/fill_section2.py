import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        print("=== FILLING SECTION 2 (HOW YOU'D HANDLE IT) ===")
        
        target_ids = [
            'choice_82df5ab3-6715-430d-85cf-bb4b280dc0f6', # Q1: B (Personal outreach + referral)
            'choice_1f8d4d47-cae3-4f92-a806-ea30f24173a4', # Q2: C (Admin proposal as AI literacy program)
            'choice_1aa74963-d865-4233-ada4-d3af0de48221', # Q3: A (Start with 12, make them advocates)
            'choice_9a2bc4a9-f9c1-4885-af4d-73040394e354', # Q4: C (Informal challenge: phone magic)
            'choice_d6de0dc7-9d87-4340-8254-917ddfb52c45', # Q5: C (Collaborative brainstorming of 3 features)
            'choice_943702b1-7662-469f-ab70-b6ba910a59a8'  # Q6: B (Fair point + redirect to trial)
        ]

        for tid in target_ids:
            el = await pg.query_selector(f'[id="{tid}"]')
            if el:
                await el.check()
                print(f"Checked: {tid}")
                await asyncio.sleep(0.3)

        await asyncio.sleep(1)

        # Click Next
        next_btn = await pg.query_selector('button:has-text("Next")')
        if next_btn:
            print("Clicking Next to advance to Section 3...")
            await next_btn.click()
            await asyncio.sleep(3)
            
            print("\n=== NEXT SECTION LOADED ===")
            txt = await pg.inner_text('body')
            print(txt[:1500])

if __name__ == '__main__':
    asyncio.run(main())


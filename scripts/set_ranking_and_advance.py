import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'gemini' in page.url][0]

        res = await pg.evaluate("""() => {
            let form = document.querySelector('form');
            let key = Object.keys(form).find(k => k.startsWith('__reactFiber'));
            let fiber = form[key];
            let q1Key = 'd9073717-bf14-4715-984c-3cb4ff6ed290';
            let curr = fiber;
            
            while (curr) {
                if (curr.memoizedProps && curr.memoizedProps[q1Key]) {
                    // Set the ranking value!
                    let rankingKey = 'ba61ddb4-7f1e-4ad7-9d1c-0e875d6a84d8';
                    let rankedOptions = [
                        '2150e79b-e70e-4f8f-931e-a11ecac6bfe0', // B: Recurring weekly activity (1st)
                        '96b342ff-2005-4b61-9c1f-bd2bdd4b168d', // A: High-visibility admin event (2nd)
                        'e00598d4-a04f-4783-902a-6f93cd707d03', // D: Inputs from students (3rd)
                        '748dccdf-70ca-42f8-8594-edef523587d4'  // C: Social media posts (4th)
                    ];
                    curr.memoizedProps[rankingKey] = rankedOptions;
                    return {
                        success: true,
                        component: curr.type?.name || 'unknown',
                        rankingSet: curr.memoizedProps[rankingKey]
                    };
                }
                curr = curr.return;
            }
            return { success: false };
        }""")
        print("Set ranking in Fiber:", res)

        await asyncio.sleep(1)

        # Now click Next button!
        next_btn = await pg.query_selector('button:has-text("Next")')
        if next_btn:
            print("Clicking Next to advance to Section 3...")
            await next_btn.click()
            await asyncio.sleep(3)
            print("\nPage text snippet after Next:\n" + "="*50)
            txt = await pg.inner_text('body')
            print(txt[:1000])
            print("="*50)

if __name__ == '__main__':
    asyncio.run(main())


import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for page in context.pages:
            url = page.url
            if 'thinkahead' in url:
                # 1. Availability radio
                radio = await page.query_selector('input[value="Serving Notice Period"], input[value="30 Days"]')
                if radio:
                    await radio.click()
                    print('Clicked Serving Notice Period radio on Thinkahead')

                # 2. Top three skills
                skills_input = await page.query_selector('input[name*="field1"]')
                if skills_input:
                    val = await skills_input.input_value()
                    if not val:
                        await skills_input.fill('AWS, Kubernetes, CI/CD Pipeline Automation')
                        print('Filled top three skills on Thinkahead')

            elif 'lingarogroup' in url:
                loc_input = await page.query_selector('input[name="location"]')
                if loc_input:
                    await loc_input.fill('Delhi, India')
                    print('Filled location on Lingaro')

asyncio.run(main())

import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for p in context.pages:
            if 'lingarogroup' in p.url:
                c = await p.query_selector('iframe[src*="turnstile"], iframe[src*="hcaptcha"], iframe[src*="recaptcha"]')
                print('Captcha iframe:', bool(c))
                loc = await p.eval_on_selector('input[name="location"]', 'e => e.value')
                print('Location val:', loc)
                errors = await p.query_selector_all('.error, [aria-invalid="true"], .application-error')
                print('Errors count:', len(errors))
                for e in errors:
                    print('Err:', await e.text_content())

asyncio.run(main())


import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for i, page in enumerate(context.pages):
            if 'apply' in page.url:
                title = await page.title()
                print(f"[{i}] {title}")
                # Check captcha
                captcha = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
                print(f"  Captcha iframe: {bool(captcha)}")
                btn = await page.query_selector('#btn-submit, button:has-text("Submit Application")')
                if btn:
                    print(f"  Submit button found! Text: '{await btn.text_content()}'")
                    # Let's try clicking it!
                    try:
                        print("  Attempting click on Submit...")
                        await btn.click()
                        await asyncio.sleep(4)
                        print(f"  URL after submit: {page.url}")
                        body = await page.inner_text('body')
                        if any(k in body.lower() for k in ['thank you', 'submitted', 'received', 'thanks']):
                            print("  SUBMISSION SUCCESSFUL!")
                        else:
                            print(f"  Result snippet: {body[:200]}")
                    except Exception as e:
                        print(f"  Click error: {e}")

asyncio.run(main())


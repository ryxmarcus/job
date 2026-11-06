import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for i, page in enumerate(context.pages):
            title = await page.title()
            if 'lever.co' in page.url:
                print(f"\n--- Checking Page [{i}] {title} ---")
                # Find all required inputs or empty textareas/selects
                empty_required = await page.query_selector_all('input[required], select[required], textarea[required], .application-question:has(.required) input, .application-question:has(.required) select, .application-question:has(.required) textarea')
                print(f"Empty/Required count: {len(empty_required)}")
                for el in empty_required:
                    tag = await el.evaluate('e => e.tagName')
                    name = await el.get_attribute('name') or ''
                    val = await el.input_value() if tag == 'INPUT' else ''
                    lbl = await el.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText : ""')
                    print(f"  Field [{tag}] name={name}, val='{val}'")
                    print(f"    Label: {lbl.strip()[:100]}")

asyncio.run(main())

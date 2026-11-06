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
            if 'careers.americanexpress.com' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX page not found!')
            return

        ko_info = await page.evaluate('''() => {
            const pinEl = document.querySelector('#postalCode-59');
            const regEl = document.querySelector('#region2-60');
            const dataPin = window.ko ? ko.dataFor(pinEl) : null;
            const dataReg = window.ko ? ko.dataFor(regEl) : null;
            return {
                hasKo: !!window.ko,
                pinKeys: dataPin ? Object.keys(dataPin) : [],
                regKeys: dataReg ? Object.keys(dataReg) : [],
                pinElementVal: dataPin && dataPin.element ? dataPin.element.value() : null,
                regElementVal: dataReg && dataReg.element ? dataReg.element.value() : null,
                regOptions: dataReg && dataReg.element && dataReg.element.options ? dataReg.element.options().map(o => ({label: o.label, value: o.value})) : []
            };
        }''')
        print('KO Info:', ko_info)

asyncio.run(main())


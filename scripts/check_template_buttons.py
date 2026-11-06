import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    for pg in context.pages:
        if 'EAHDPUZ3X6Q' in pg.url or 'canva.com/templates' in pg.url:
            print('URL:', pg.url)
            print('Title:', pg.title())
            btns = pg.evaluate("""() => {
                const list = [];
                document.querySelectorAll('button, a[role="button"], a[class*="button"]').forEach(b => {
                    const t = b.innerText.trim();
                    if (t) list.push(t);
                });
                return list;
            }""")
            print('Buttons on template page:', btns[:15])


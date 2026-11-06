import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    for pg in context.pages:
        if 'canva.com' in pg.url and 'allcargo' not in pg.url:
            print('URL:', pg.url)
            print('Title:', pg.title())
            links = pg.evaluate("""() => {
                const list = [];
                document.querySelectorAll('a').forEach(a => {
                    const text = a.innerText.trim();
                    if (text && (a.href.includes('template') || a.href.includes('design'))) {
                        list.push({ text: text.slice(0, 40), href: a.href });
                    }
                });
                return list.slice(0, 10);
            }""")
            print('Sample template/design links:', links)


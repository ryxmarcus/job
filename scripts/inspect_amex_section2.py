import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'americanexpress' in pg.url and 'section/' in pg.url:
            page = pg
            break
            
    if page:
        print("Connected to AMEX Current Page:", page.url)
        print("Page Title:", page.title())
        print("Text Preview:\n", page.inner_text('body')[:500])
        
        # Check inputs and buttons
        fields = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => {
                return {
                    tag: el.tagName,
                    type: el.type,
                    text: el.innerText ? el.innerText.trim() : (el.placeholder || el.name || ''),
                    visible: el.offsetWidth > 0 && el.offsetHeight > 0
                };
            }).filter(x => x.visible);
        }""")
        print(f"Visible elements ({len(fields)}):")
        for f in fields[:20]:
            print(f"  [{f['tag']} {f.get('type')}] {f['text']}")


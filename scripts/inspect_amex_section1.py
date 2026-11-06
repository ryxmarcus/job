import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    amex_page = None
    for page in context.pages:
        if 'americanexpress' in page.url and 'section/1' in page.url:
            amex_page = page
            break
            
    if amex_page:
        print("Connected to AMEX Section 1:", amex_page.url)
        print("Title:", amex_page.title())
        
        # Extract all input fields, placeholders, labels
        fields = amex_page.evaluate("""() => {
            const list = [];
            document.querySelectorAll('input, select, textarea').forEach(el => {
                const label = el.closest('label')?.innerText || 
                              el.closest('.form-group, .field, div')?.querySelector('label, [class*="label"]')?.innerText || 
                              el.getAttribute('aria-label') || 
                              el.placeholder || el.name || el.id || '';
                list.push({
                    tag: el.tagName,
                    type: el.type,
                    id: el.id,
                    name: el.name,
                    label: label.trim().slice(0, 50),
                    value: el.value || '',
                    visible: el.offsetWidth > 0 && el.offsetHeight > 0
                });
            });
            return list;
        }""")
        print(f"Total fields on AMEX Section 1: {len(fields)}")
        for f in fields:
            if f['visible']:
                print(f"  [{f['type']}] Label: '{f['label']}' | Name: '{f['name']}' | Value: '{f['value']}'")
    else:
        print("AMEX Section 1 tab not found.")


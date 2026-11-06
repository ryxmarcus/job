import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    for page in context.pages:
        if 'DAHZxncrm0w' in page.url or 'canva.com/design' in page.url:
            print('Found Canva editor:', page.url)
            # Find all text elements or contenteditable
            text_nodes = page.evaluate("""() => {
                const nodes = [];
                document.querySelectorAll('[contenteditable="true"], p, span, div').forEach(el => {
                    const txt = el.innerText?.trim();
                    if (txt && (txt.includes('OLIVIA') || txt.includes('Administrative') || txt.includes('Borcelle'))) {
                        nodes.push({ tag: el.tagName, text: txt.slice(0, 50), role: el.getAttribute('role') });
                    }
                });
                return nodes;
            }""")
            print(f'Matching placeholder elements: {len(text_nodes)}')
            for n in text_nodes[:10]:
                print(f"  - {n}")


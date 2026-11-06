import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    # Use one of the Canva tabs or open a page to check projects
    page = None
    for pg in context.pages:
        if 'canva.com' in pg.url and 'allcargo' not in pg.url:
            page = pg
            break
            
    if not page:
        page = context.new_page()
        
    print("Navigating to Canva Projects: https://www.canva.com/projects")
    page.goto("https://www.canva.com/projects", wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(3000)
    
    # Extract existing project/design titles
    designs = page.evaluate("""() => {
        const items = [];
        document.querySelectorAll('a[href*="/design/"]').forEach(a => {
            const title = a.innerText.trim() || a.getAttribute('aria-label') || '';
            const href = a.href;
            if (title && !items.some(i => i.href === href)) {
                items.push({ title, href });
            }
        });
        return items;
    }""")
    
    print(f"Found {len(designs)} designs/projects in Canva:")
    for d in designs[:15]:
        print(f"  - {d['title']} --> {d['href']}")


import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'canva.com' in pg.url and 'allcargo' not in pg.url:
            page = pg
            break
            
    if not page:
        page = context.new_page()
        
    url = "https://www.canva.com/resumes/templates/?query=software+engineer+minimalist"
    print(f"Navigating to Canva Resume Templates: {url}")
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(4000)
    
    templates = page.evaluate("""() => {
        const list = [];
        document.querySelectorAll('a[href*="/templates/E"]').forEach(a => {
            const title = a.innerText.trim() || a.getAttribute('aria-label') || '';
            if (title && !list.some(x => x.href === a.href)) {
                list.push({ title: title.split('\\n')[0], href: a.href });
            }
        });
        return list;
    }""")
    
    print(f"Discovered {len(templates)} top Canva resume templates:")
    for t in templates[:10]:
        print(f"  - {t['title']} --> {t['href']}")


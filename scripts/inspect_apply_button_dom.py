import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = "https://www.naukri.com/job-listings-site-reliability-engineer-ii-akamai-technologies-bengaluru-3-to-7-years-021126500484"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=25000)
    page.wait_for_timeout(3000)
    
    # Inspect all elements with "apply" in text or class
    res = page.evaluate("""() => {
        const list = [];
        document.querySelectorAll('button, a, span, div').forEach(el => {
            const txt = el.innerText?.trim() || '';
            const cls = el.className || '';
            if (txt.toLowerCase().includes('apply') || (typeof cls === 'string' && cls.toLowerCase().includes('apply'))) {
                list.push({
                    tag: el.tagName,
                    text: txt.slice(0, 40),
                    cls: typeof cls === 'string' ? cls.slice(0, 40) : '',
                    href: el.getAttribute('href') || '',
                    id: el.id || '',
                    visible: el.offsetWidth > 0 && el.offsetHeight > 0
                });
            }
        });
        return list;
    }""")
    
    print(f"Found {len(res)} elements matching 'apply':")
    for r in res[:20]:
        print(r)
        
    page.close()


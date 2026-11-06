import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    for page in browser.contexts[0].pages:
        if 'canva.com' in page.url:
            print('URL:', page.url)
            print('Title:', page.title())
            is_logged_in = page.evaluate("""() => {
                const text = document.body.innerText || '';
                const hasLoginBtn = text.includes('Log in') || text.includes('Sign up');
                const hasCreateBtn = text.includes('Create a design') || text.includes('What will you design');
                return { hasLoginBtn, hasCreateBtn, textSnippet: text.slice(0, 200) };
            }""")
            print('Evaluation:', is_logged_in)


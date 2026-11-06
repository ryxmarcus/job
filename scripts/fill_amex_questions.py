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
        print("Connected to AMEX form:", page.url)
        
        # Radio answers logic:
        # Standard default is "No", except for:
        # - Legally authorized to work in India: "Yes"
        # - Proof of age: "Yes"
        # - 12th class certificate: "Yes"
        # - Passport issuing authority India: "Yes"
        # - Citizen of India: "Yes"
        # - Not a Citizen of India visa: "Not applicable"
        # - Person with disability: "Choose not to reply" or "No"
        
        YES_QUESTIONS = [
            "legally authorized to work in india",
            "proof of age",
            "12th class pass certificate",
            "passport issuing authority",
            "citizen of india"
        ]
        
        NA_QUESTIONS = [
            "if you are not a citizen of india"
        ]
        
        # Iterate over each question container
        questions = page.locator(".form-group, .question-wrapper, [class*='question'], fieldset").all()
        print(f"Found {len(questions)} question blocks.")
        
        # Handle all radio inputs via JS for reliable selection
        page.evaluate("""() => {
            const yesQuestions = [
                "legally authorized to work in india",
                "proof of age",
                "12th class pass certificate",
                "passport issuing authority",
                "citizen of india?"
            ];
            const naQuestions = [
                "not a citizen of india"
            ];
            
            // Find all question containers
            document.querySelectorAll('fieldset, .form-group, [role="radiogroup"], div').forEach(container => {
                const qText = (container.innerText || '').toLowerCase();
                const radios = container.querySelectorAll('input[type="radio"]');
                if (radios.length > 0) {
                    let targetVal = 'no';
                    if (yesQuestions.some(k => qText.includes(k))) {
                        targetVal = 'yes';
                    } else if (naQuestions.some(k => qText.includes(k))) {
                        targetVal = 'not applicable';
                    } else if (qText.includes('disability')) {
                        targetVal = 'choose not to reply';
                    }
                    
                    radios.forEach(r => {
                        const lbl = (r.closest('label')?.innerText || r.parentElement?.innerText || '').toLowerCase().trim();
                        if (lbl.includes(targetVal)) {
                            r.checked = true;
                            r.dispatchEvent(new Event('change', { bubbles: true }));
                            r.dispatchEvent(new Event('click', { bubbles: true }));
                        }
                    });
                }
            });
        }""")
        
        page.wait_for_timeout(2000)
        
        # Click Next button
        next_btn = page.locator("button:has-text('Next'), button:has-text('Save and Continue')")
        if next_btn.count() > 0 and next_btn.first.is_visible():
            print("Clicking Next on Section 3...")
            next_btn.first.click()
            page.wait_for_timeout(4000)
            print("Current AMEX URL after Section 3:", page.url)
            print("Current AMEX Title:", page.title())
            print("Current Body Preview:\n", page.inner_text('body')[:400])
    else:
        print("AMEX page not found.")


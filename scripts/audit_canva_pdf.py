import sys
from pypdf import PdfReader
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pdf_path = Path(r"C:\Users\rah_66160\iTopaz-agents\job\resumes\Rahul_Kumar_Canva_ATS_2026.pdf")
screenshot_path = Path(r"C:\Users\rah_66160\.gemini\antigravity\brain\a53bf700-685d-46fa-8e20-ead4a727fa69\canva_resume_preview.png")

print(f"=== AUDITING PDF: {pdf_path.name} ===")
reader = PdfReader(str(pdf_path))
num_pages = len(reader.pages)
print(f"Page Count: {num_pages}")

full_text = ""
for idx, page in enumerate(reader.pages, 1):
    txt = page.extract_text() or ""
    full_text += f"\n--- Page {idx} ---\n" + txt
    print(f"Page {idx}: {len(txt)} characters, {len(txt.split())} words")

print("\n=== EXTRACTED TEXT FROM PDF ===")
print(full_text.strip())

# Check ATS Keyword Compliance
print("\n=== ATS CRITICAL KEYWORDS CHECK ===")
checks = {
    "Candidate Name": "Rahul Kumar" in full_text,
    "Target Title (SRE/DevOps)": any(k in full_text.lower() for k in ["sre", "site reliability", "devops"]),
    "Contact Details (Email/Phone)": "@" in full_text and any(c.isdigit() for c in full_text),
    "DTU / College": "DTU" in full_text or "Delhi Technological University" in full_text,
    "AWS Certified (DOP-C02)": "DOP-C02" in full_text or "AWS Certified" in full_text,
    "Kubernetes / EKS": "Kubernetes" in full_text or "EKS" in full_text,
    "Terraform": "Terraform" in full_text,
    "Prometheus / Grafana": "Prometheus" in full_text or "Grafana" in full_text,
    "Programming.com / Allcargo": "Programming.com" in full_text or "Allcargo" in full_text or "Gati" in full_text,
    "Notice Period": "notice" in full_text.lower() or "30" in full_text
}

passed = 0
for check, status in checks.items():
    icon = "PASS" if status else "MISSING"
    print(f"  [{icon}] {check}")
    if status: passed += 1

print(f"\nATS Compliance Score: {passed}/{len(checks)} ({int(passed/len(checks)*100)}%)")

# Capture visual render using Playwright
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1600})
        page.goto(pdf_path.as_uri())
        page.wait_for_timeout(2000)
        page.screenshot(path=str(screenshot_path))
        print(f"\nSaved visual preview screenshot to: {screenshot_path}")
        browser.close()
except Exception as e:
    print(f"Screenshot note: {e}")


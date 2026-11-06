import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

res = urllib.request.urlopen('http://127.0.0.1:9222/json/list')
tabs = json.loads(res.read().decode())
print("Active Priority Tabs in Edge Browser:")
for t in tabs:
    u = t.get('url', '').lower()
    if any(k in u for k in ['rbs', 'workday', 'instahyre', 'americanexpress', 'myinternships']):
        print(f"  * {t.get('title')} --> {t.get('url')}")

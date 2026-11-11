import csv
from collections import Counter
from pathlib import Path

tracker_path = Path(r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv")
with open(tracker_path, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f"Total Rows in tracker.csv: {len(rows)}")

# 1. Check ID duplicates
ids = [r['id'] for r in rows if r.get('id')]
id_counts = Counter(ids)
dup_ids = {k: v for k, v in id_counts.items() if v > 1}
print(f"Duplicate IDs: {len(dup_ids)} -> {dup_ids}")

# 2. Check URL duplicates
urls = [r['url'].strip() for r in rows if r.get('url')]
url_counts = Counter(urls)
dup_urls = {k: v for k, v in url_counts.items() if v > 1}
print(f"Duplicate URLs: {len(dup_urls)} -> {dup_urls}")

# 3. Status breakdown
status_counts = Counter(r.get('application_status') for r in rows)
print("\nCurrent Status Breakdown:")
for s, c in status_counts.most_common():
    print(f"  {s}: {c}")

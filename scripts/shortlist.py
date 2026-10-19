"""Create a deduplicated review queue. No network, CV edits, tracker writes or sends."""
import argparse
import csv
import datetime as dt
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, parse_qs, unquote

ROOT = Path(__file__).resolve().parents[1]

def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', ' ', html.unescape(text or ''))).strip()

def identity(url, company='', title=''):
    p = urlsplit(url or '')
    query = parse_qs(p.query)
    path = unquote(p.path).rstrip('/')
    host = p.netloc.lower().removeprefix('www.')
    if 'mongodb.com' in host:
        match = re.search(r'/jobs/(\d+)', path)
        rid = query.get('gh_jid', [match.group(1) if match else ''])[0]
        if rid:
            return 'greenhouse:mongodb:' + rid
    if 'greenhouse.io' in host:
        match = re.search(r'/([^/]+)/jobs/(\d+)', path)
        if match:
            return 'greenhouse:' + ':'.join(match.groups())
    if 'google.com' in host:
        match = re.search(r'/results/(\d+)', path)
        if match:
            return 'google:' + match.group(1)
    if 'lever.co' in host:
        match = re.search(r'/([^/]+)/([a-f0-9-]{36})', path)
        if match:
            return 'lever:' + ':'.join(match.groups())
    # General careers pages host multiple roles; do not merge them by URL alone.
    return host + path + ':' + company.lower() + ':' + title.lower()

def minimum_years(description):
    text = clean(description).lower()
    values = re.findall(r'\b(\d{1,2})(?:\s*[–—-]\s*\d{1,2})?\s*\+?\s*years?\s+(?:(?:[a-z-]+\s+){0,6}experience|(?:of\s+)?(?:building|operating|developing|programming)\b)', text)
    return max(map(int, values)) if values else None

def location_check(location, company, policy):
    loc = location.lower()
    # A limited remote arrangement requires review even if it contains India.
    if 'remote' in loc and any(x in loc for x in ['only', 'hybrid']):
        return 'confirm_remote_scope', 5
    if 'remote' in loc and 'india' in loc:
        return 'remote_india', 30
    if 'remote' in loc:
        if re.search(r'\b(us|usa|united states|canada|uk|united kingdom)\b', loc):
            return 'location_unconfirmed_or_outside_preferences', 0
        return 'confirm_remote_scope', 5
    if any(x in loc for x in ['gurugram', 'gurgaon']):
        return 'gurgaon', 24
    if 'delhi' in loc:
        return 'delhi', 20
    if any(x in loc for x in ['vizag', 'visakhapatnam', 'vishakhapatnam']):
        return 'vizag', 16
    if any(x in loc for x in ['bangalore', 'bengaluru', 'hyderabad']):
        if company.lower() in {c.lower() for c in policy['confirmed_relocation_companies']}:
            return 'relocation_confirmed', 16
        if company.lower() in {c.lower() for c in policy['preferred_companies']}:
            return 'assess_similar_company_relocation', 5
    return 'location_unconfirmed_or_outside_preferences', 0

def evaluate(job, policy, today):
    desc = clean(job.get('description', ''))
    title = job['title']
    location_state, score = location_check(job['location'], job['company'], policy)
    flags = []
    preferred = job['company'].lower() in {c.lower() for c in policy['preferred_companies']}
    score += 30 if preferred else 0
    # Keywords measure evidence overlap only; they cannot establish depth or ownership.
    matches = [s for s in policy['core_skill_terms'] if re.search(r'\b' + re.escape(s) + r'\b', desc, re.I)]
    score += min(len(matches) * 2, 20)
    years = minimum_years(desc)
    if years is None:
        flags.append('experience_requirement_not_parsed')
    elif years > policy['experience_years_approx']:
        flags.append(f'experience_gap: asks {years}+; CV approximately {policy["experience_years_approx"]}')
        score -= 20
    if re.search(r'\b(staff|principal|director|manager|architect)\b', title, re.I):
        flags.append('seniority_review')
        score -= 15
    if not desc:
        flags.append('full_description_missing')
    status = job.get('application_status', '')
    if status.startswith('submitted'):
        lane = 'already_submitted'
    elif job.get('verification') == 'redirect_unverified' or 'Job not found' in desc:
        lane = 'unavailable_or_unverified'
    elif location_state == 'location_unconfirmed_or_outside_preferences':
        lane = 'hold_location'
    else:
        lane = 'review'
    date = job.get('checked_date', '')
    try:
        age = (today - dt.date.fromisoformat(date)).days
        if age < 0 or age > policy['recheck_after_days']:
            flags.append('source_needs_recheck')
    except ValueError:
        flags.append('source_date_missing')
    if job.get('verification') not in ['public_ats_feed', 'employer_page_checked', 'page_checked', 'official_role_page_with_apply_checked']:
        flags.append('opening_needs_verification')
    if location_state.startswith(('confirm_', 'assess_', 'location_')):
        flags.append(location_state)
    flags.append('salary_budget_unconfirmed')
    if job.get('track', '').lower() in ['mlops', 'fde']:
        flags.append('specialist_experience_needs_evidence')
    return dict(job, score=score, lane=lane, preferred_company=preferred,
                location_assessment=location_state, minimum_years_detected=years,
                matching_keywords=matches, review_flags=flags)

def build(root, policy, today):
    # Newest observation per job across snapshots; absent jobs are not declared closed.
    merged = {}
    for path in sorted((root/'sources').glob('discovery_*.json')):
        snapshot = json.loads(path.read_text(encoding='utf-8-sig'))
        stamp = snapshot.get('checked_at_utc', '')
        date = f'{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}' if len(stamp) >= 8 else ''
        for j in snapshot.get('jobs', []):
            company = policy['company_aliases'].get(j['board'], j['board'])
            row = dict(j, company=company, checked_date=date, verification='public_ats_feed')
            merged[identity(row['url'], company, row['title'])] = row
    with (root/'applications/tracker.csv').open(encoding='utf-8-sig', newline='') as f:
        for j in csv.DictReader(f):
            key = identity(j['url'], j['company'], j['role'])
            row = merged.get(key, {})
            # Tracker owns application facts and reviewed location; feed owns JD evidence.
            observed = row.get('checked_date', '')
            verification = row.get('verification')
            row.update(j)
            row['title'] = j['role']
            if observed >= j['checked_date'] and verification and j['verification'] != 'redirect_unverified':
                row['checked_date'] = observed
                row['verification'] = verification
            merged[key] = row
    result = [evaluate(j, policy, today) for j in merged.values()]
    return sorted(result, key=lambda j:(j['lane'] != 'review', -j['score'], j['company'], j['title']))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--as-of', required=True, type=dt.date.fromisoformat, help='User-facing date, YYYY-MM-DD')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    policy = json.loads((args.root/'search_policy.json').read_text(encoding='utf-8'))
    jobs = build(args.root, policy, args.as_of)
    out = args.root/'applications'
    (out/'ranked_shortlist.json').write_text(json.dumps(jobs,indent=2),encoding='utf-8')
    fields = ['company','title','location','score','lane','url','checked_date','application_status','minimum_years_detected','review_flags']
    with (out/'ranked_shortlist.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for job in jobs:
            w.writerow(dict(job,review_flags='; '.join(job['review_flags'])))
    lines = ['# Job review queue', '', f'As of {args.as_of}. Ranking is a review aid, not an eligibility or ATS score.', '',
             'Recheck the official posting before submission. Unknown salary, skills depth and portal access still require review.', '',
             '| Company | Role | Location | Review points | Link |', '| --- | --- | --- | --- | --- |']
    for j in jobs:
        if j['lane'] != 'review':
            continue
        vals = [j['company'],j['title'],j['location'],'; '.join(j['review_flags'])]
        lines.append('| ' + ' | '.join(clean(v).replace('|','/') for v in vals) + ' | [Apply page](' + j['url'] + ') |')
    sent = sum(j['lane']=='already_submitted' for j in jobs)
    lines += ['',f'{sent} previously submitted roles excluded from this queue. See tracker.csv for receipts.']
    (out/'REVIEW_QUEUE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'{len(jobs)} unique roles; {sent} already submitted; review queue written. Tracker unchanged.')

if __name__ == '__main__':
    main()

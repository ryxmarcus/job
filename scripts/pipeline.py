"""Manage outcomes, follow-ups, archives, and an offline application dashboard.

Inspired by MadsLorentzen/ai-job-search (MIT), adapted to this tracker schema.
This tool never sends messages or submits forms.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, html, json, shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "applications" / "tracker.csv"
FINAL = {"hired", "rejected", "no_response", "offer_declined", "withdrawn"}
SUBMITTED = {"submitted_by_email", "portal_submitted", "applied", "interview", "offer"}
ALLOWED = FINAL | SUBMITTED | {"draft_prepared", "prepared_email", "prepared_portal_unsubmitted", "drafted"}

def read_tracker(path=TRACKER):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh); return reader.fieldnames, list(reader)

def write_tracker(fields, rows, path=TRACKER):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows)

def find(rows, job_id):
    matches = [r for r in rows if r["id"].casefold() == job_id.casefold()]
    if len(matches) != 1: raise SystemExit(f"Expected one tracker row for {job_id}; found {len(matches)}")
    return matches[0]

def parse_date(value):
    try: return dt.date.fromisoformat(value)
    except (TypeError, ValueError): return None

def summary(rows, today):
    states = Counter(r["application_status"] or "unknown" for r in rows); quiet = []
    for row in rows:
        if row["application_status"] not in SUBMITTED or not row["submitted_date"]: continue
        last = parse_date(row["followup_date"]) or parse_date(row["submitted_date"])
        if last and (today-last).days >= 7:
            quiet.append((row["id"], row["company"], row["role"], (today-last).days))
    return states, quiet

def archive(row, root=ROOT):
    safe = "_".join("".join(c.lower() if c.isalnum() else " " for c in x).split() for x in (row["company"], row["role"]))
    dest = root / "applications" / "archive" / safe; dest.mkdir(parents=True, exist_ok=True)
    posting = {k: row[k] for k in ("id", "company", "role", "url", "location", "checked_date", "verification", "application_status")}
    (dest/"posting.json").write_text(json.dumps(posting, indent=2)+"\n", encoding="utf-8")
    for suffix in (".docx", ".txt"):
        src = root / "resumes" / (row["resume_basename"] + suffix)
        if src.is_file(): shutil.copy2(src, dest/("submitted_cv"+suffix))
    return dest

def dashboard(rows, path):
    counts = Counter(r["application_status"] or "unknown" for r in rows)
    cards = "".join(f'<div class="card"><b>{html.escape(k)}</b><span>{v}</span></div>' for k,v in sorted(counts.items()))
    body = []
    for r in rows:
        cols = [r["id"],r["company"],r["role"],r["location"],r["application_status"],r["submitted_date"],r["followup_date"]]
        body.append("<tr>"+"".join(f"<td>{html.escape(v or '')}</td>" for v in cols)+f'<td><a href="{html.escape(r["url"], quote=True)}">open</a></td></tr>')
    doc = f'''<!doctype html><meta charset="utf-8"><title>Rahul Kumar job pipeline</title><style>body{{font:14px system-ui;margin:2rem;color:#17202a}}.cards{{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.4rem 0}}.card{{border:1px solid #ccd6dd;border-radius:8px;padding:.7rem 1rem;min-width:150px}}.card span{{display:block;font-size:1.6rem;margin-top:.3rem}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #ddd;padding:.55rem;text-align:left}}th{{position:sticky;top:0;background:white}}tr:hover{{background:#f5f7f9}}</style><h1>Job application pipeline</h1><p>Generated {dt.datetime.now().astimezone().isoformat(timespec="minutes")}. Tracker remains the source of truth.</p><div class="cards">{cards}</div><table><thead><tr><th>ID</th><th>Company</th><th>Role</th><th>Location</th><th>Status</th><th>Submitted</th><th>Follow-up</th><th>Link</th></tr></thead><tbody>{''.join(body)}</tbody></table>'''
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(doc, encoding="utf-8")

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--tracker",type=Path,default=TRACKER); sub=parser.add_subparsers(dest="command",required=True)
    s=sub.add_parser("summary"); s.add_argument("--as-of",type=dt.date.fromisoformat,default=dt.date.today())
    o=sub.add_parser("outcome"); o.add_argument("job_id"); o.add_argument("status",choices=sorted(ALLOWED)); o.add_argument("--date",type=dt.date.fromisoformat,default=dt.date.today()); o.add_argument("--note",default="")
    f=sub.add_parser("followup"); f.add_argument("job_id"); f.add_argument("--date",type=dt.date.fromisoformat,default=dt.date.today())
    a=sub.add_parser("archive"); a.add_argument("job_id")
    d=sub.add_parser("dashboard"); d.add_argument("--output",type=Path,default=ROOT/"reports"/"pipeline.html")
    args=parser.parse_args(); fields,rows=read_tracker(args.tracker)
    if args.command=="summary":
        states,quiet=summary(rows,args.as_of); print(json.dumps({"statuses":states,"followup_due":quiet},indent=2))
    elif args.command=="outcome":
        row=find(rows,args.job_id); row["application_status"]=args.status
        if args.status in SUBMITTED and not row["submitted_date"]: row["submitted_date"]=args.date.isoformat()
        if args.note: row["gaps"]=(row["gaps"]+"; " if row["gaps"] else "")+args.note
        write_tracker(fields,rows,args.tracker); print(f"Updated {row['id']} to {args.status}")
    elif args.command=="followup":
        row=find(rows,args.job_id)
        if row["application_status"] not in SUBMITTED: raise SystemExit("Follow-up requires a submitted/open application")
        row["followup_date"]=args.date.isoformat(); write_tracker(fields,rows,args.tracker); print(f"Recorded follow-up for {row['id']}; no message was sent")
    elif args.command=="archive": print(archive(find(rows,args.job_id)))
    else: dashboard(rows,args.output); print(args.output)

if __name__=="__main__": main()

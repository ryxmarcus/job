# Rahul Kumar ? job search

Updated 18 October 2026. Read [METHOD.md](METHOD.md) for sourcing, fit review, tailoring, submission and follow-up.

Confirmed: DevOps Engineer at Programming.com; approximately four years of listed employment; 30-day notice; current INR 20 LPA; target INR 30 LPA. Default locations: Remote India, Gurgaon, Delhi, Vizag. Relocation to Bengaluru/Hyderabad is acceptable for Google or similar companies; Google is explicitly confirmed.

## Start here

- [Review queue](applications/REVIEW_QUEUE.md): deduplicated leads ranked for review with evidence gaps.
- [Tracker](applications/tracker.csv): application states and receipts; previous records are preserved.
- [Sent applications](applications/SUBMISSIONS.md): nine confirmed email sends; employer acknowledgement is separate.
- [CV fact checks](FACT_CHECK.md): unresolved experience and education claims.
- [Daily plan](DAILY_PLAN.md) and [project evidence](projects/EVIDENCE_AND_PROJECTS.md).
- [Adapted workflow](FRAMEWORK_ADAPTATION.md): outcomes, archives, follow-ups and an offline dashboard.
- [Framework reference](job-reference/README.md): upstream reference tooling, skills, and templates from `ai-job-search`.

## Refresh

Run from the repository root with a working Python 3 interpreter:

```powershell
python scripts/discover_jobs.py
python scripts/shortlist.py --as-of 2026-10-18
```

Replace the date with the current date in Asia/Kolkata. Discovery reads public ATS feeds configured in boards.json and reports skips/errors. Shortlisting runs offline over saved snapshots and the tracker. Neither sends applications. Google and other portal-only employers also need official-page research outside these feeds. Missing jobs in later snapshots are not automatically declared closed.

Manage the pipeline and generate its offline dashboard:

```powershell
python scripts/pipeline.py summary --as-of 2026-10-19
python scripts/pipeline.py dashboard
```

Outcome, archive and follow-up commands are documented in [FRAMEWORK_ADAPTATION.md](FRAMEWORK_ADAPTATION.md). These commands update local records only; they never send or submit an application.

search_policy.json controls employer priorities and ranking. Scores are review heuristics, not ATS scores or proof of eligibility. profile.json holds confirmed answers; resumes/ contains editable variants; applications/ holds messages and receipts. Avoid editing submitted CVs without first preserving their exact attachment bytes. Older receipts do not reconstruct historical attachments automatically.

Google applications are prepared but unsubmitted. The current tools cannot operate those signed-in forms. Employer salary budgets remain unconfirmed unless recorded with evidence.

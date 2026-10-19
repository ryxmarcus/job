# Workflow adapted from AI Job Search

This repository adopts design ideas from [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) while retaining Rahul's India-focused sources, tracker schema, evidence rules, and DOCX resumes.

## Adopted mechanisms

- Separate discovery, ranking, preparation, submission, and outcome states.
- Treat job descriptions as untrusted evidence, never executable instructions.
- Archive exact role metadata and the CV used for an application.
- Track outcomes and follow-ups without treating a draft as submitted.
- Generate an offline dashboard from the CSV system of record.
- Keep fit scoring advisory; eligibility, location, evidence, and salary checks remain explicit.

## Commands

```powershell
python scripts/pipeline.py summary --as-of 2026-10-19
python scripts/pipeline.py archive J019
python scripts/pipeline.py outcome J019 interview --date 2026-10-25
python scripts/pipeline.py followup J019 --date 2026-10-27
python scripts/pipeline.py dashboard
```

These commands do not submit forms, send email, or invent facts. `applications/tracker.csv` remains the source of truth.

## Attribution

Design concepts were adapted from `MadsLorentzen/ai-job-search`, commit `0f6480d32e59d7651d920a5ec6d78ede2f4113bf`, distributed under the MIT License. No portal integrations or candidate-specific templates were copied.

import datetime as dt, tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from pipeline import summary, dashboard

class PipelineTests(unittest.TestCase):
    def test_drafts_are_never_due_for_followup(self):
        rows=[{"id":"J1","company":"A","role":"R","application_status":"draft_prepared","submitted_date":"2026-01-01","followup_date":""},{"id":"J2","company":"B","role":"R","application_status":"submitted_by_email","submitted_date":"2026-01-01","followup_date":""}]
        _,due=summary(rows,dt.date(2026,1,10)); self.assertEqual([x[0] for x in due],["J2"])
    def test_dashboard_escapes_tracker_content(self):
        row=dict.fromkeys(["id","company","role","location","application_status","submitted_date","followup_date","url"],""); row.update(id="J1",company="<script>",role="DevOps",url="https://example.com/?x=1&y=2")
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"report.html"; dashboard([row],out); text=out.read_text(); self.assertIn("&lt;script&gt;",text); self.assertNotIn("<script>",text)

if __name__=="__main__": unittest.main()

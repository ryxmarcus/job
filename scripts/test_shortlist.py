import datetime as dt
import unittest
from shortlist import identity, minimum_years, location_check, evaluate

POLICY = {'preferred_companies':['Google','MongoDB'], 'confirmed_relocation_companies':['Google'],
          'experience_years_approx':4, 'recheck_after_days':7, 'core_skill_terms':['python','aws']}

class RankingTests(unittest.TestCase):
    def test_duplicate_mongodb_urls(self):
        self.assertEqual(identity('https://www.mongodb.com/careers/jobs/8051379'),
                         identity('https://www.mongodb.com/careers/job/?gh_jid=8051379'))
        self.assertEqual(identity('https://job-boards.greenhouse.io/mongodb/jobs/8051379'),
                         identity('https://www.mongodb.com/careers/jobs/8051379'))

    def test_different_jobs_on_same_careers_page(self):
        self.assertNotEqual(identity('https://example.com/careers','Acme','SRE'),
                            identity('https://example.com/careers','Acme','MLOps'))

    def test_lever_apply_duplicate(self):
        url='https://jobs.lever.co/acme/12345678-1234-1234-1234-123456789abc'
        self.assertEqual(identity(url),identity(url+'/apply?source=linkedin'))

    def test_year_ranges(self):
        self.assertEqual(minimum_years('6–8 years of experience'),6)
        self.assertEqual(minimum_years('3+ years experience; 5 years of professional experience'),5)
        self.assertEqual(minimum_years('5+ years of hands-on backend engineering experience'),5)
        self.assertEqual(minimum_years('6+ years building and operating distributed systems'),6)
        self.assertIsNone(minimum_years('Founded 12 years ago'))

    def test_remote_restrictions(self):
        self.assertEqual(location_check('Remote (India - Bangalore ONLY)','Acme',POLICY)[0],'confirm_remote_scope')
        self.assertEqual(location_check('US Remote','Acme',POLICY)[1],0)
        self.assertEqual(location_check('Bengaluru','Google',POLICY)[0],'relocation_confirmed')
        self.assertEqual(location_check('Bengaluru','MongoDB',POLICY)[0],'assess_similar_company_relocation')

    def test_sent_not_in_review_queue_and_stale_flag(self):
        row={'title':'DevOps','company':'Google','location':'Bengaluru','description':'AWS Python; 6+ years of experience',
             'checked_date':'2026-10-01','application_status':'submitted_by_email','verification':'page_checked'}
        result=evaluate(row,POLICY,dt.date(2026,10,18))
        self.assertEqual(result['lane'],'already_submitted')
        self.assertIn('source_needs_recheck',result['review_flags'])
        self.assertTrue(any(f.startswith('experience_gap') for f in result['review_flags']))

if __name__=='__main__':
    unittest.main()

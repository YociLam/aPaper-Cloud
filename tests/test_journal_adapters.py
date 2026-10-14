import importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('journal',ROOT/'skills/manage-apaper-cloud-metadata/scripts/fetch_journal_collection.py')
j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
class JournalAdapterTests(unittest.TestCase):
    def fixture(self):
        c=json.loads((ROOT/'skills/manage-apaper-cloud-metadata/scripts/journal_sources.json').read_text())['jlb']
        r={'DOI':'10.1/example','URL':'https://doi.org/10.1/example','type':'journal-article','title':['Legal scholarship'], 'author':[{'given':'A','family':'Author'}], 'abstract':'<jats:p>Actual licensed abstract.</jats:p>', 'published-online':{'date-parts':[[2026,2,4]]},'published-print':{'date-parts':[[2026,6]]}, 'license':[{'URL':'https://creativecommons.org/licenses/by/4.0/','start':{'date-parts':[[2026,2,4]]}}]}
        return c,r
    def normalize(self,r):
        c,_=self.fixture()
        return j.normalize('10.1/example',r,None,c,'jlb',2026,'2026-10-14T15:44:19Z',Path('/tmp'))
    def test_dates_abstract_author_order_and_issue_precision(self):
        _,r=self.fixture();record,status,_=self.normalize(r)
        self.assertEqual(status,'admitted');self.assertEqual(record['published_at'],'2026-02-04')
        self.assertEqual(record['journal']['issue_published_at'],'2026-06');self.assertEqual(record['abstract'],'Actual licensed abstract.')
        self.assertEqual(record['authors'],['A Author']);self.assertIsNone(record['journal']['article_number'])
    def test_missing_abstract_and_license_are_unresolved(self):
        _,r=self.fixture();r.pop('abstract');self.assertEqual(self.normalize(r)[1],'unresolved')
        _,r=self.fixture();r['license'][0]['URL']='https://creativecommons.org/licenses/by-nc/4.0/';self.assertEqual(self.normalize(r)[1],'excluded')
    def test_publication_updates_and_retractions(self):
        _,r=self.fixture();r['update-to']=[{'DOI':'10.1/example','type':'new_version','updated':{'date-parts':[[2026,3]]}}]
        record,status,_=self.normalize(r);self.assertEqual(status,'admitted');self.assertEqual(record['journal']['publication_updates'][0]['published_at'],'2026-03')
        r['update-to'][0]['type']='retraction';self.assertEqual(self.normalize(r)[1],'excluded')
    def test_future_and_corrections_are_excluded(self):
        _,r=self.fixture();r['published-online']={'date-parts':[[2026,12,1]]};self.assertEqual(self.normalize(r)[1],'excluded')
        _,r=self.fixture();r['title']=['Correction: Legal scholarship'];self.assertEqual(self.normalize(r)[1],'excluded')
    def test_incomplete_and_repeated_pagination_fail(self):
        c,_=self.fixture()
        response={'message':{'total-results':2,'items':[]}}
        with patch.object(j,'acquire',return_value=json.dumps(response).encode()):
            with self.assertRaisesRegex(ValueError,'incomplete pagination'):j.crossref(c,2026,'2026-10-14T15:44:19Z',Path('/tmp'))
        response={'message':{'total-results':2,'items':[{'DOI':'10.1/a'}],'next-cursor':'repeat'}}
        with patch.object(j,'acquire',return_value=json.dumps(response).encode()):
            with self.assertRaisesRegex(ValueError,'repeated nonterminal'):j.crossref(c,2026,'2026-10-14T15:44:19Z',Path('/tmp'))
    def test_truncated_json_is_rejected(self):
        c,_=self.fixture()
        with patch.object(j,'acquire',return_value=b'{"message":'):
            with self.assertRaises(json.JSONDecodeError):j.crossref(c,2026,'2026-10-14T15:44:19Z',Path('/tmp'))
    def test_cached_byte_ceiling_and_empty_response_fail(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            raw=Path(directory);url='https://publisher.example/metadata'
            path=raw/(hashlib.sha256(url.encode()).hexdigest()+'.input')
            with patch.object(j,'LIMIT',8):
                path.write_bytes(b'12345678')
                with self.assertRaisesRegex(ValueError,'byte ceiling'):j.acquire(url,raw)
                path.write_bytes(b'')
                with self.assertRaisesRegex(ValueError,'empty'):j.acquire(url,raw)

if __name__=='__main__':unittest.main()

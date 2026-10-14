import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/manage-apaper-cloud-metadata/scripts'))
import fetch_pmlr_volume as pmlr
import fetch_ijcai_proceedings as ijcai
import fetch_cvf_openaccess as cvf
import tempfile
import shutil

class PublisherAdapterTests(unittest.TestCase):
    def test_required_venues_preserve_ordered_metadata_from_official_posts(self):
        for venue,volume,year,fragment in [
            ('midl','v315',2026,'Medical Imaging with Deep Learning'),
            ('mlhc','v340',2026,'Machine Learning for Healthcare'),
            ('chil','v333',2026,'Health, Inference, and Learning'),
            ('mlcb','v311',2025,'Machine Learning in Computational Biology'),
            ('l4dc','v331',2026,'Learning for Dynamics and Control')]:
            with self.subTest(venue=venue):
                source=(Path(__file__).parent/'fixtures/pmlr'/f'{venue}.md').read_text()
                record=pmlr.parse_record(source,volume=volume,venue=venue,year=year,expected_title_fragment=fragment)
                self.assertTrue(record['title']);self.assertTrue(record['abstract'])
                self.assertEqual(record['authors'],pmlr.authors(pmlr.frontmatter(source)))
                self.assertEqual(record['categories'],[])
                self.assertTrue(record['link'].startswith(f'https://proceedings.mlr.press/{volume}/'))
                self.assertTrue(record['pdf_url'].startswith('https://'))
    def test_wrong_collection_and_missing_date_fail_instead_of_guessing(self):
        source=(Path(__file__).parent/'fixtures/pmlr/midl.md').read_text()
        with self.assertRaises(ValueError):pmlr.parse_record(source,volume='v315',venue='midl',year=2026,expected_title_fragment='Wrong collection')
        with self.assertRaises(ValueError):pmlr.iso_date('',2026)
    def test_frontmatter_author_order_and_preface_exclusion(self):
        source="---\nid: editorial\ntitle: Preface\nsection: Preface\ncontainer-title: Test\ndate: 2026-01-01\n---\n"
        self.assertIsNone(pmlr.parse_record(source,volume='v1',venue='test',year=2026,expected_title_fragment='Test'))
    def test_ijcai_keeps_publisher_subjects_and_stable_identity(self):
        source=(Path(__file__).parent/'fixtures/ijcai-detail.html').read_text()
        record=ijcai.parse_detail(source,'1','Agent-based and Multi-agent Systems',2026)
        self.assertEqual(record['source_paper_id'],'ijcai-2026-1')
        self.assertEqual(record['authors'][0],'Alessandro Abate')
        self.assertEqual(record['doi'],'10.24963/ijcai.2026/1')
        self.assertEqual(record['source_group']['kind'],'subject_area')
        self.assertEqual(len(record['categories']),5)
        self.assertTrue(record['abstract'].startswith('We study multi-task'))
    def test_cvf_retains_year_precision_without_inventing_a_day(self):
        filename = "Fang_Unfolding-Associative_Encoder-Decoder_Network_with_Progressive_Alignment_for_Pansharpening_ICCV_2025_paper.html"
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            shutil.copy2(Path(__file__).parent/'fixtures/iccv-detail.html', cache/filename)
            record = cvf.fetch_paper('https://openaccess.thecvf.com/content/ICCV2025/html/'+filename,
                conference='ICCV', year=2025, cache_dir=cache, timeout=1, retries=1)
            self.assertEqual(record['published'], '2025')
            self.assertEqual(record['categories'], [])
            self.assertTrue(record['authors'])

    def test_ijcai_index_preserves_track_when_subject_heading_is_absent(self):
        html='<div class="section"><div class="section_title">Demonstrations</div><div class="subsection"><div class="paper_wrapper" id="paper1"></div></div></div>'
        self.assertEqual(ijcai.parse_index(html,2026), [('1','Demonstrations','track')])

    def test_ijcai_index_duplicate_identity_is_rejected(self):
        row='<div class="paper_wrapper" id="paper1"></div>'
        with self.assertRaises(ValueError):ijcai.parse_index(row+row,2026)

if __name__=='__main__':unittest.main()

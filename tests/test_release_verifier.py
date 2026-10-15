"""The publication verifier must cover real journal packs, including partials."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'release_verifier', ROOT / 'skills/manage-apaper-cloud-metadata/scripts/verify_published_release.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ReleaseVerifierTests(unittest.TestCase):
    def setUp(self):
        self.public = ROOT / 'public'
        self.manifest = json.loads((self.public / 'v1/conferences/manifest.json').read_text())

    def test_real_conference_and_journal_collections_are_resolved(self):
        for source_id, section in [('icml', 'venues'), ('glj', 'journals'), ('jlb', 'journals')]:
            source = next(s for s in self.manifest[section] if s['id'] == source_id)
            edition = next(e for e in source['editions'] if e['id'] == source_id + ':2026')
            self.assertEqual(v.edition_pack(self.manifest, edition['id']), edition['pack'])

    def test_journal_verification_rejects_bad_bytes_and_hash(self):
        pack = v.edition_pack(self.manifest, 'glj:2026')
        payload = (self.public / 'v1/conferences' / pack['path']).read_bytes()
        for corrupt, reason in [(b'bad', 'byte count'),
                                (bytes([payload[0] ^ 1]) + payload[1:], 'SHA-256')]:
            with self.subTest(reason=reason), patch.object(v, 'fetch', return_value=corrupt):
                with self.assertRaisesRegex(RuntimeError, reason):
                    v.verify_pack(self.public, 'https://cloud.apaper.ai', self.manifest, 'glj:2026', 1)
        with patch.object(v, 'fetch', return_value=payload), contextlib.redirect_stdout(io.StringIO()) as output:
            v.verify_pack(self.public, 'https://cloud.apaper.ai', self.manifest, 'glj:2026', 1)
        self.assertIn('verified pack glj:2026', output.getvalue())

    def test_unavailable_and_unknown_editions_are_not_published(self):
        for edition_id in ['ieee_sp:2026', 'does-not-exist:2026']:
            with self.subTest(edition_id=edition_id), self.assertRaises(RuntimeError):
                v.edition_pack(self.manifest, edition_id)

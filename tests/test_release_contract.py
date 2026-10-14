"""Exercise the real release validator with checksummed malformed candidates."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class ReleaseContractTests(unittest.TestCase):
    def test_real_validator_rejects_invalid_checksummed_release_metadata(self):
        original=json.loads((ROOT/'public/v1/conferences/manifest.json').read_text())
        mutations=[
            lambda m:m['disciplines'].append(m['disciplines'][0].copy()),
            lambda m:m['venues'][0].update(discipline_ids=['undefined']),
            lambda m:m['venues'][0].update(discipline_ids=[m['venues'][0]['discipline_ids'][0]]*2),
            lambda m:m['disciplines'][0].update(display_order='first'),
            lambda m:m['disciplines'][0].update(localized_names={'en':'Computing'}),
            lambda m:m.pop('discipline_taxonomy'),
            lambda m:m.pop('generated_at'),
            lambda m:m['venues'][0].update(discipline_ids=[]),
            lambda m:m['venues'][0].update(source_kind='journal'),
            lambda m:m['journals'][0].update(source_kind='conference'),
            lambda m:m['journals'][0].update(source_kind='unknown'),
            lambda m:m['journals'][0].pop('journal'),
            lambda m:m['journals'][0]['editions'][0].pop('coverage'),
            lambda m:m['journals'][0]['editions'][0]['coverage'].update(admitted=0),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)),tempfile.TemporaryDirectory() as directory:
                manifest=json.loads(json.dumps(original));mutation(manifest)
                folder=Path(directory)/'v1/conferences';folder.mkdir(parents=True)
                data=(json.dumps(manifest)+'\n').encode();(folder/'manifest.json').write_bytes(data)
                version={'schema_version':1,'dataset':'apaper.conferences','manifest_version':manifest['manifest_version'],
                    'updated_at':manifest.get('generated_at',''),'manifest_sha256':hashlib.sha256(data).hexdigest()}
                (folder/'version.json').write_text(json.dumps(version))
                result=subprocess.run([str(ROOT/'target/debug/apaper-cloud'),'validate-site',directory],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertNotIn('missing pack',result.stderr,'Metadata validation must reject before pack IO')

if __name__=='__main__':unittest.main()

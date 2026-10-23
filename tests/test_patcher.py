import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('patcher', Path(__file__).parents[1] / 'patch_monsgeek.py')
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)


def fixture():
    readers = ';'.join(f'new DataView({v}.buffer,{v}.byteOffset,{v}.byteLength).getUint32(1,!0)' for v in ('i', 't'))
    return readers + ';whoAmI=async()=>{for(let t=0;t<3;t++){for(;!this.isOnline;)await Je(100);await Je(500)}};destory=()=>{}'


class PatchTests(unittest.TestCase):
    def test_identity_and_retry_changes(self):
        output = patcher.transform(fixture())
        self.assertEqual(output.count('===75?2381:'), 2)
        self.assertIn('?15:3', output)
        self.assertIn('?100:500', output)

    def test_idempotent(self):
        output = patcher.transform(fixture())
        self.assertEqual(patcher.transform(output), output)

    def test_unknown_bundle(self):
        with self.assertRaises(ValueError):
            patcher.transform('unrecognized app bundle')

    def test_ambiguous_reader(self):
        with self.assertRaises(ValueError):
            patcher.transform(fixture() + ';new DataView(i.buffer,i.byteOffset,i.byteLength).getUint32(1,!0)')

    def test_legacy_handshake(self):
        with self.assertRaises(ValueError):
            patcher.transform('__fun60Share;' + fixture())


if __name__ == '__main__':
    unittest.main()

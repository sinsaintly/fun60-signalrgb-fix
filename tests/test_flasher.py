"""Read-only preflight tests with fake HID; never contacts real hardware."""
import contextlib
import io
import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / 'firmware' / 'flash-2381.py'


class FlasherTests(unittest.TestCase):
    def run_fake(self, model=2381, boot=False, extra=()):
        sent = []
        class Device:
            def open_path(self, path): pass
            def close(self): pass
            def send_feature_report(self, frame):
                sent.append(frame[1])
                if frame[1] != 0x8f:
                    raise AssertionError('Test attempted a non-identity command')
                return 65
            def get_feature_report(self, report, size):
                return bytes([0, 0x8f, model & 255, model >> 8, 0, 0, 0, 0, 4, 3] + [0]*55)
        def enumerate_devices(vid, pid):
            if (boot and pid == 0x502a) or (not boot and pid == 0x502d):
                return [dict(path=b'test', usage_page=0xff01 if boot else 0xffff, usage=2)]
            return []
        fake = types.SimpleNamespace(device=Device, enumerate=enumerate_devices)
        with patch.dict(sys.modules, hid=fake), patch.object(sys, 'argv', [str(SCRIPT), *extra]), \
             patch('subprocess.run', return_value=types.SimpleNamespace(stdout='')), \
             patch('time.sleep'), patch.object(Path, 'write_text'), contextlib.redirect_stdout(io.StringIO()):
            try:
                runpy.run_path(str(SCRIPT), run_name='__main__')
            except SystemExit as error:
                return error.code, sent
        return None, sent

    def test_default_is_read_only(self):
        code, sent = self.run_fake()
        self.assertEqual(code, 0)
        self.assertEqual(sent, [0x8f])

    def test_wrong_model_rejected_even_when_armed(self):
        with self.assertRaisesRegex(AssertionError, 'Wrong model'):
            self.run_fake(model=2307, extra=('--arm',))

    def test_bootloader_needs_explicit_model_confirmation(self):
        code, sent = self.run_fake(boot=True)
        self.assertIn('model cannot be identified', code)
        self.assertEqual(sent, [])

    def test_stock_plan_read_only(self):
        code, sent = self.run_fake(extra=('--stock',))
        self.assertEqual(code, 0)
        self.assertEqual(sent, [0x8f])


if __name__ == '__main__':
    unittest.main()

"""Ensure command/result failures cannot be reported as successful comparison."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('integrity_runner', ROOT / 'tools/usb_integrity/run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def valid_manifest():
    return {'schema': 1, 'channels': 24, 'rotation': 0, 'rate_hz': 96000,
            'frames': '48', 'first_frame': '0', 'seed': '0', 'pattern': 'identity'}


class IntegrityRunner(unittest.TestCase):
    def test_bad_manifests_rejected(self):
        for value in ([], None, {**valid_manifest(), 'schema': True},
                      {**valid_manifest(), 'channels': True},
                      {**valid_manifest(), 'frames': 12},
                      {**valid_manifest(), 'seed': '-1'},
                      {**valid_manifest(), 'first_frame': str(1 << 64)},
                      {**valid_manifest(), 'rotation': 24},
                      {**valid_manifest(), 'pattern': 'unknown'}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                runner.validate(value)

    def test_checker_exit_and_result_must_agree(self):
        for code, status in ((1, 'PASS'), (0, 'FAIL')):
            completed = subprocess.CompletedProcess([], code, json.dumps({'status': status}), '')
            with patch.object(runner.subprocess, 'run', return_value=completed), \
                 self.assertRaisesRegex(RuntimeError, 'disagreement'):
                runner.check(Path('/fake/check'), valid_manifest(), io.BytesIO())

    def test_missing_terminal_result_is_error(self):
        completed = subprocess.CompletedProcess([], -9, '', '')
        with patch.object(runner.subprocess, 'run', return_value=completed), \
             self.assertRaisesRegex(RuntimeError, 'no valid terminal result'):
            runner.check(Path('/fake/check'), valid_manifest(), io.BytesIO())

    def test_malformed_or_abnormal_checker_result_is_error(self):
        for code, value in ((0, []), (0, None), (1, {}), (-9, {'status': 'FAIL'})):
            completed = subprocess.CompletedProcess([], code, json.dumps(value), '')
            with self.subTest(code=code, value=value), \
                 patch.object(runner.subprocess, 'run', return_value=completed), \
                 self.assertRaises(RuntimeError):
                runner.check(Path('/fake/check'), valid_manifest(), io.BytesIO())

    def test_manifest_decimal_strings_are_normalized_for_native_cli(self):
        config = {**valid_manifest(), 'frames': '00048', 'seed': '08'}
        runner.validate(config)
        options = runner.options(config)
        self.assertEqual(options[options.index('--seed') + 1], '8')
        self.assertEqual(options[options.index('--frames') + 1], '48')

    def test_unbounded_exclusions_rejected(self):
        for lead, tail in ((-1, 0), (192001, 0), (0, 192001)):
            with self.assertRaises(ValueError):
                runner.check(Path('/fake/check'), valid_manifest(), io.BytesIO(), lead, tail)

    def test_real_generate_check_and_corruption_reports(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            output = Path(temporary)
            self.assertEqual(runner.main(['generate', '--output-dir', str(output),
                                          '--frames', '48', '--seed', '0']), 0)
            created = Path(json.loads((output / 'latest.json').read_text())['result']).parent
            pcm = created / 'signal.pcm'
            original = pcm.read_bytes()
            self.assertEqual(runner.main(['check', '--output-dir', str(output),
                                          '--manifest', str(created / 'manifest.json'),
                                          '--input', str(pcm)]), 0)
            result = json.loads(Path(json.loads((output / 'latest.json').read_text())['result']).read_text())
            self.assertFalse(result['hardware_verified'])
            self.assertEqual(result['scope'], 'offline_capture_comparison')
            self.assertEqual(pcm.read_bytes(), original)
            corrupt = bytearray(original)
            corrupt[4 * 72 + 9] ^= 1
            pcm.write_bytes(corrupt)
            self.assertEqual(runner.main(['check', '--output-dir', str(output),
                                          '--manifest', str(created / 'manifest.json'),
                                          '--input', str(pcm)]), 1)
            result = json.loads(Path(json.loads((output / 'latest.json').read_text())['result']).read_text())
            self.assertEqual(result['status'], 'FAIL')
            self.assertEqual(result['comparison']['reason'], 'sample_mismatch')

    def test_compiler_failure_has_persisted_error(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            output = Path(temporary)
            self.assertEqual(runner.main(['build', '--output-dir', str(output), '--cc', '/bin/false']), 1)
            result = json.loads(Path(json.loads((output / 'latest.json').read_text())['result']).read_text())
            self.assertEqual(result['status'], 'ERROR')

    def test_changed_input_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            recording = directory / 'capture.pcm'
            recording.write_bytes(bytes(100))
            definition = directory / 'definition.json'
            definition.write_text(json.dumps(valid_manifest()))
            args = argparse.Namespace(command='check', manifest=definition,
                                      input=recording, max_leading_frames=0,
                                      max_trailing_frames=0)
            def changed(*unused):
                recording.write_bytes(bytes(101))
                return {'status': 'PASS'}, 0
            with patch.object(runner, 'check', side_effect=changed), \
                 self.assertRaisesRegex(RuntimeError, 'changed during comparison'):
                runner.execute(args, directory, directory)


if __name__ == '__main__':
    unittest.main()

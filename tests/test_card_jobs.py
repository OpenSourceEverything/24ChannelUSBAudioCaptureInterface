"""Check job outcomes and selection failures without touching real disks."""
import contextlib
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

loader = importlib.machinery.SourceFileLoader('device_jobs', str(Path(__file__).parents[1] / 'device'))
spec = importlib.util.spec_from_loader(loader.name, loader)
device = importlib.util.module_from_spec(spec)
loader.exec_module(device)


class CardJobs(unittest.TestCase):
    def job(self, root):
        job = {'job_id': 'a' * 32, 'selection': {'path': '/dev/card', 'diskseq': 12, 'size': 8000},
               'image': {'path': '/image.wic', 'sha256': 'b' * 64, 'size': 1000},
               'verify_only': True, 'log': str(root / 'job.log')}
        path = root / 'job.json'
        path.write_text(json.dumps(job))
        return path, job

    def test_readonly_card_stops_before_unmount_or_worker_launch(self):
        inventory = {'blockdevices': [{'path': '/dev/card', 'type': 'disk', 'rm': True,
                                      'ro': True, 'size': 8000, 'mountpoints': [None]}]}
        with patch.object(device.subprocess, 'check_output', return_value=json.dumps(inventory)), \
             patch.object(device, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'LOCK switch'):
                device.card_selection('/dev/card', 1000)
            run.assert_not_called()

    def test_old_live_install_prevents_starting_another_job(self):
        state = {'stage': 'VERIFYING', 'process': device.process_identity(os.getpid())}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'install-status.json').write_text(json.dumps(state))
            with patch.object(device, 'LOCAL', root), patch.object(device, 'run') as run:
                with self.assertRaisesRegex(RuntimeError, 'already running'):
                    device.start_card_job('/dev/card')
                run.assert_not_called()

    def test_dead_flush_or_verify_worker_is_never_reported_as_live(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for stage in ('FLUSHING', 'VERIFYING'):
                (root / 'install-status.json').write_text(json.dumps({'stage': stage, 'process': None}))
                with patch.object(device, 'LOCAL', root):
                    self.assertEqual(device.installation_status()['stage'], 'STOPPED')

    def test_failed_transfer_saves_failure_even_when_notifications_are_unavailable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, job = self.job(root)
            with patch.object(device, 'LOCAL', root), \
                 patch.object(device, 'flash', side_effect=RuntimeError('Read-back checksum failed')), \
                 patch.object(device, 'notify_card_result', return_value=False):
                self.assertEqual(device.card_worker(path), 1)
            receipt = json.loads(path.with_suffix('.result.json').read_text())
            self.assertEqual(receipt['stage'], 'ERROR')
            self.assertIn('checksum failed', receipt['message'])
            self.assertFalse(receipt['notification_sent'])
            self.assertEqual(json.loads((root / 'install-status.json').read_text())['stage'], 'ERROR')

    def test_success_receipt_is_created_after_transfer_returns(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, job = self.job(root)
            def transfer(*args, **kwargs):
                self.assertFalse(path.with_suffix('.result.json').exists())
                kwargs['progress']({'stage': 'VERIFYING', 'bytes_done': 500, 'bytes_total': 1000})
                state = json.loads((root / 'install-status.json').read_text())
                self.assertEqual(state['stage'], 'VERIFYING')
                return {'sha256': job['image']['sha256'], 'verified_bytes': 1000, 'wrote_image': False}
            with patch.object(device, 'LOCAL', root), patch.object(device, 'flash', side_effect=transfer), \
                 patch.object(device, 'notify_card_result', return_value=True):
                self.assertEqual(device.card_worker(path), 0)
            receipt = json.loads(path.with_suffix('.result.json').read_text())
            self.assertEqual(receipt['stage'], 'READY')
            self.assertEqual(receipt['verified_bytes'], 1000)

    def test_changed_selection_never_launches_a_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder) / 'image.wic'
            image.write_bytes(b'known image')
            record = {'path': str(image), 'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                      'size': image.stat().st_size}
            selected = {'path': '/dev/card', 'diskseq': 11, 'size': 8000}
            current = {**selected, 'diskseq': 12}
            with patch.object(device, 'card_selection', return_value=({}, current)), \
                 patch.object(device.subprocess, 'Popen') as popen:
                with self.assertRaisesRegex(RuntimeError, 'Card changed'):
                    device.flash('/dev/card', selection=selected, image_record=record)
                popen.assert_not_called()

    def test_interrupted_job_cleanup_records_failure_and_notifies_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, job = self.job(root)
            with patch.object(device, 'LOCAL', root), patch.object(device.subprocess, 'run'), \
                 patch.object(device, 'notify_card_result', return_value=True) as notify:
                self.assertEqual(device.card_stopped(path), 0)
                self.assertEqual(device.card_stopped(path), 0)
                notify.assert_called_once()
            receipt = json.loads(path.with_suffix('.result.json').read_text())
            self.assertEqual(receipt['stage'], 'ERROR')
            self.assertNotIn('verified_bytes', receipt)

    def test_interruption_still_reports_failure_if_container_cleanup_times_out(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, job = self.job(root)
            with patch.object(device, 'LOCAL', root), \
                 patch.object(device.subprocess, 'run', side_effect=device.subprocess.TimeoutExpired('docker', 10)), \
                 patch.object(device, 'notify_card_result', return_value=False):
                self.assertEqual(device.card_stopped(path), 0)
            receipt = json.loads(path.with_suffix('.result.json').read_text())
            self.assertEqual(receipt['stage'], 'ERROR')
            self.assertIn('cleanup could not be confirmed', receipt['message'])

    def test_zero_exit_without_complete_matching_verification_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            image = Path(folder) / 'image.wic'
            image.write_bytes(b'known image')
            record = {'path': str(image), 'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                      'size': image.stat().st_size}
            selected = {'path': '/dev/card', 'diskseq': 11, 'size': 8000}
            for event in (None, {'stage': 'VERIFIED', 'sha256': '0' * 64,
                                 'verified_bytes': record['size']}):
                child = MagicMock()
                child.stdout = io.StringIO(json.dumps(event) + '\n' if event else '')
                child.wait.return_value = 0
                child.poll.return_value = 0
                context = MagicMock()
                context.__enter__.return_value = child
                with patch.object(device, 'card_selection', return_value=({'mountpoints': [None]}, selected)), \
                     patch.object(device.subprocess, 'Popen', return_value=context), \
                     contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(RuntimeError, 'Card job failed|Incomplete card verification'):
                        device.flash('/dev/card', selection=selected, image_record=record)


if __name__ == '__main__':
    unittest.main()

"""Real process failures must leave a retained, non-PASS terminal result."""
import importlib.util
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/usb_integrity/run.py'
spec = importlib.util.spec_from_file_location('lifecycle_runner', SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def wait_for(read, predicate, seconds=8):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            value = read()
            if predicate(value):
                return value
        except (OSError, ValueError):
            pass
        time.sleep(0.02)
    raise AssertionError('Timed out waiting for fixture state')


class IntegrityLifecycle(unittest.TestCase):
    def interrupted_run(self, victim, timeout=30):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            compiler = output / 'blocked_compiler.py'
            compiler.write_text('''import os, sys, time
from pathlib import Path
if '--version' in sys.argv:
    print('fixture compiler')
else:
    Path(sys.argv[-1]).with_name('compiler.pid').write_text(str(os.getpid()))
    time.sleep(60)
''')
            command = [sys.executable, str(SCRIPT), 'build', '--output-dir', str(output),
                       '--timeout-seconds', str(timeout), '--cc',
                       shlex.join([sys.executable, str(compiler)])]
            with (output / 'owner.log').open('w') as log:
                owner = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                try:
                    latest = wait_for(lambda: json.loads((output / 'latest.json').read_text()), bool)
                    result_path = Path(latest['result'])
                    result = wait_for(lambda: json.loads(result_path.read_text()),
                                      lambda r: r.get('phase') == 'EXECUTING' and r.get('watchdog'))
                    compiler_pid = int(wait_for(lambda: (result_path.parent / 'bin/compiler.pid').read_text(), bool))
                    if victim != 'timeout':
                        pid = owner.pid if victim == 'owner' else result[victim]['pid']
                        os.kill(pid, signal.SIGKILL)
                    self.assertNotEqual(owner.wait(timeout=10), 0)
                    final = wait_for(lambda: json.loads(result_path.read_text()),
                                     lambda r: r['status'] == 'INTERRUPTED' and 'cleanup' in r)
                    self.assertFalse(final['hardware_verified'])
                    wait_for(lambda: runner.process_identity(compiler_pid, live=True), lambda x: x is None)
                    return final
                finally:
                    if owner.poll() is None:
                        owner.kill()
                        owner.wait(timeout=5)

    def test_killed_owner_is_finalized_without_owner_polling(self):
        self.assertEqual(self.interrupted_run('owner')['reason'], 'owner_died_or_identity_changed')

    def test_killed_worker_cannot_pass(self):
        self.assertIn(self.interrupted_run('worker')['reason'],
                      ('worker_died_or_identity_changed', 'worker_exited_without_terminal_result'))

    def test_killed_watchdog_cannot_pass(self):
        self.assertEqual(self.interrupted_run('watchdog')['reason'], 'watchdog_died')

    def test_timeout_is_terminal_and_kills_owned_compiler(self):
        self.assertEqual(self.interrupted_run('timeout', timeout=1)['reason'], 'wall_time_limit_exceeded')

    def test_failed_cleanup_is_retained_and_late_pass_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            identity = runner.process_identity(os.getpid())
            runner.write_json(directory / 'result.json', {'status': 'RUNNING', 'worker': identity})
            with patch.object(runner.os, 'getpgid', return_value=os.getpid()), \
                 patch.object(runner.os, 'getsid', return_value=os.getpid()), \
                 patch.object(runner.os, 'killpg', side_effect=PermissionError('fixture denial')):
                runner.interrupt_job(directory, 'fixture interruption')
            result = json.loads((directory / 'result.json').read_text())
            self.assertEqual(result['status'], 'INTERRUPTED')
            self.assertIn('fixture denial', result['cleanup'])
            self.assertFalse(runner.update_running(directory, {'status': 'PASS'}))

    def test_reused_pid_never_signals_an_unrelated_group(self):
        identity = {**runner.process_identity(os.getpid()), 'start_ticks': 'different'}
        with patch.object(runner.os, 'killpg') as kill:
            self.assertIn('UNVERIFIED', runner.cleanup_worker(identity))
        kill.assert_not_called()

    def test_legacy_abandoned_running_becomes_interrupted(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            directory = output / 'run-old'
            directory.mkdir()
            runner.write_json(directory / 'result.json', {'status': 'RUNNING'})
            runner.write_json(output / 'latest.json', {'result': str(directory / 'result.json')})
            self.assertEqual(runner.status(output)['status'], 'INTERRUPTED')

    def test_status_during_startup_does_not_interrupt_a_live_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            directory = output / 'run-starting'
            directory.mkdir()
            runner.write_json(directory / 'result.json',
                              {'status': 'RUNNING', 'phase': 'STARTING',
                               'owner': runner.process_identity(os.getpid()),
                               'deadline_monotonic': time.monotonic() + 10})
            runner.write_json(output / 'latest.json', {'result': str(directory / 'result.json')})
            self.assertEqual(runner.status(output)['status'], 'RUNNING')


if __name__ == '__main__':
    unittest.main()

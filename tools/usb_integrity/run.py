#!/usr/bin/env python3
"""Bounded, host-only entry point. Never configures USB or opens an audio device."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import signal
import shlex
import shutil
import stat
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().parent
PATTERNS = ('identity', 'edges', 'walking', 'alternating')
MAX64 = (1 << 64) - 1
FLAGS = ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-Wconversion', '-pedantic']


def process_identity(pid, *, live=False):
    """Linux PID identity survives neither PID reuse nor reboot; zombies aren't live."""
    try:
        pid = int(pid)
        if pid <= 0:
            return None
        fields = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
        if live and fields[0] in ('Z', 'X'):
            return None
        return {'pid': pid, 'start_ticks': fields[19],
                'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    except (OSError, ValueError, TypeError, IndexError):
        return None


def alive(identity):
    return bool(identity and process_identity(identity.get('pid'), live=True) == identity)


@contextlib.contextmanager
def result_lock(directory):
    with (directory / 'result.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def update_running(directory, fields):
    """Watchdog interruption wins over a later worker attempting to commit PASS."""
    with result_lock(directory):
        path = directory / 'result.json'
        result = json.loads(path.read_text())
        if result['status'] != 'RUNNING':
            return False
        result.update(fields)
        write_json(path, result)
        return True


def cleanup_worker(identity):
    # Each worker creates its own session before publishing worker-ready.json.
    # Refuse to signal any group whose leader's identity has changed/disappeared.
    if not identity or process_identity(identity.get('pid')) != identity:
        return 'UNVERIFIED: worker identity unavailable; no unrelated group signalled'
    pid = identity['pid']
    try:
        if os.getpgid(pid) != pid or os.getsid(pid) != pid:
            return 'UNVERIFIED: worker is not the recorded session/group leader'
        os.killpg(pid, signal.SIGTERM)
        time.sleep(0.1)
        if process_identity(pid) == identity:
            os.killpg(pid, signal.SIGKILL)
        return 'TERM/KILL sent to identified worker session; descendants need final audit'
    except ProcessLookupError:
        return 'Worker group already absent'
    except OSError as error:
        return 'UNVERIFIED cleanup: ' + str(error)


def interrupt_job(directory, reason):
    if update_running(directory, {'status': 'INTERRUPTED', 'reason': reason,
                                  'hardware_verified': False}):
        result = json.loads((directory / 'result.json').read_text())
        cleanup = cleanup_worker(result.get('worker'))
        with result_lock(directory):
            path = directory / 'result.json'
            result = json.loads(path.read_text())
            result['cleanup'] = cleanup
            write_json(path, result)


def watchdog(directory):
    while True:
        result = json.loads((directory / 'result.json').read_text())
        if result['status'] != 'RUNNING':
            return
        reason = None
        if not alive(result.get('owner')):
            reason = 'owner_died_or_identity_changed'
        elif not alive(result.get('worker')):
            reason = 'worker_died_or_identity_changed'
        elif time.monotonic() >= result['deadline_monotonic']:
            reason = 'wall_time_limit_exceeded'
        if reason:
            interrupt_job(directory, reason)
            return
        time.sleep(0.1)


def worker(args, directory):
    os.setsid()
    write_json(directory / 'worker-ready.json', process_identity(os.getpid()))
    # Parent must install an independent watchdog before work may begin.
    while True:
        result = json.loads((directory / 'result.json').read_text())
        if result['status'] != 'RUNNING' or not alive(result.get('owner')):
            return
        if alive(result.get('watchdog')):
            break
        if time.monotonic() >= result['deadline_monotonic']:
            return
        time.sleep(0.01)
    started = time.monotonic()
    fields = {}
    try:
        fields['build'] = build(directory / 'bin', args.cc)
        fields.update({'status': 'PASS', 'scope': 'compilation_only'} if args.command == 'build'
                      else execute(args, directory, directory / 'bin'))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        fields.update(status='ERROR', error=str(error)[:1500])
    fields['total_elapsed_seconds'] = time.monotonic() - started
    current = json.loads((directory / 'result.json').read_text())
    if not alive(current.get('owner')) or not alive(current.get('watchdog')):
        interrupt_job(directory, 'supervisor_missing_at_completion')
    else:
        update_running(directory, fields)


def supervised(args, directory):
    worker_pid = os.fork()
    if worker_pid == 0:
        try:
            worker(args, directory)
        finally:
            os._exit(0)
    ready = directory / 'worker-ready.json'
    deadline = time.monotonic() + min(5, args.timeout_seconds)
    while not ready.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    if not ready.exists():
        update_running(directory, {'status': 'INTERRUPTED', 'reason': 'worker_startup_incomplete'})
        # PID still owned by this parent; terminate only this unreaped child.
        os.kill(worker_pid, signal.SIGKILL)
        os.waitpid(worker_pid, 0)
        return
    update_running(directory, {'worker': json.loads(ready.read_text())})
    guard_pid = os.fork()
    if guard_pid == 0:
        try:
            os.setsid()
            watchdog(directory)
        finally:
            os._exit(0)
    update_running(directory, {'watchdog': process_identity(guard_pid), 'phase': 'EXECUTING'})
    try:
        # WNOWAIT retains the worker identity until cleanup is complete.
        while not os.waitid(os.P_PID, worker_pid, os.WEXITED | os.WNOHANG | os.WNOWAIT):
            current = json.loads((directory / 'result.json').read_text())
            if current['status'] == 'RUNNING' and not alive(current.get('watchdog')):
                interrupt_job(directory, 'watchdog_died')
            time.sleep(0.02)
        interrupt_job(directory, 'worker_exited_without_terminal_result')
    except KeyboardInterrupt:
        interrupt_job(directory, 'owner_interrupted')
    finally:
        _, worker_status = os.waitpid(worker_pid, 0)
        _, guard_status = os.waitpid(guard_pid, 0)
        with result_lock(directory):
            path = directory / 'result.json'
            result = json.loads(path.read_text())
            result.update(worker_exit_code=os.waitstatus_to_exitcode(worker_status),
                          watchdog_exit_code=os.waitstatus_to_exitcode(guard_status))
            write_json(path, result)


def status(output):
    latest = json.loads((output / 'latest.json').read_text())
    directory = Path(latest['result']).parent
    result = json.loads((directory / 'result.json').read_text())
    if result['status'] == 'RUNNING':
        # Conservative fallback also handles an older run lacking supervision.
        keys = ('owner',) if result.get('phase') == 'STARTING' else ('owner', 'worker', 'watchdog')
        if not all(alive(result.get(key)) for key in keys):
            interrupt_job(directory, 'abandoned_or_unsupervised_run')
        elif time.monotonic() >= result['deadline_monotonic']:
            interrupt_job(directory, 'wall_time_limit_exceeded')
        result = json.loads((directory / 'result.json').read_text())
    return result


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, data):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def build(output, compiler):
    command = shlex.split(compiler)
    if not command or not shutil.which(command[0]):
        raise RuntimeError('C compiler unavailable: ' + (command[0] if command else '(empty)'))
    output.mkdir(parents=True, exist_ok=True)
    info = {'flags': FLAGS, 'compiler': command,
            'compiler_version': subprocess.check_output([*command, '--version'], text=True).splitlines()[0],
            'source_sha256': {}, 'binary_sha256': {}}
    for name in ('generate', 'check'):
        source, target = SOURCE / (name + '.c'), output / name
        temporary = output / (name + '.building')
        with (output / (name + '.build.log')).open('w') as log:
            subprocess.run([*command, *FLAGS, str(source), '-o', str(temporary)],
                           check=True, stdout=log, stderr=subprocess.STDOUT, timeout=120)
        temporary.replace(target)
        info['source_sha256'][name] = sha(source)
        info['binary_sha256'][name] = sha(target)
    write_json(output / 'build.json', info)
    return info


def manifest(args):
    frames = args.frames if args.frames is not None else args.seconds * args.rate
    config = {'schema': 1, 'channels': args.channels, 'frames': str(frames),
              'first_frame': str(args.first_frame), 'seed': str(args.seed),
              'rotation': args.rotation, 'pattern': args.pattern, 'rate_hz': args.rate}
    validate(config)
    return config


def validate(config):
    if not isinstance(config, dict) or type(config.get('schema')) is not int or \
       config.get('schema') != 1 or config.get('pattern') not in PATTERNS:
        raise ValueError('Unknown manifest schema or pattern')
    for name in ('channels', 'rotation', 'rate_hz'):
        if type(config.get(name)) is not int:
            raise ValueError('Invalid manifest integer: ' + name)
    for name in ('frames', 'first_frame', 'seed'):
        value = config.get(name)
        if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
            raise ValueError('Expected decimal string: ' + name)
        if not 0 <= int(value) <= MAX64:
            raise ValueError('Unsigned 64-bit overflow: ' + name)
    n, frames, first = config['channels'], int(config['frames']), int(config['first_frame'])
    if not 1 <= n <= 24 or not 0 <= config['rotation'] < n:
        raise ValueError('Invalid channels/rotation')
    if not frames or first + frames - 1 > MAX64 or frames > MAX64 // (n * 3) - 8:
        raise ValueError('Invalid frame range or byte count')
    if config['rate_hz'] not in (48000, 96000):
        raise ValueError('This stage supports only 48000/96000-Hz profiles')


def options(config):
    return [part for key in ('channels', 'frames', 'first_frame', 'seed', 'rotation', 'pattern')
            for part in ('--' + key.replace('_', '-'),
                         str(config[key]) if key == 'pattern' else str(int(config[key])))]


def check(binary, config, stream, lead=0, tail=0, timeout=300):
    validate(config)
    limit = 2 * config['rate_hz']
    if not 0 <= lead <= limit or not 0 <= tail <= limit:
        raise ValueError('Boundary exclusions may not exceed two seconds each')
    process = subprocess.run([str(binary), *options(config), '--max-leading-frames', str(lead),
                              '--max-trailing-frames', str(tail)], stdin=stream,
                             capture_output=True, text=True, timeout=timeout)
    try:
        data = json.loads(process.stdout)
    except (ValueError, TypeError) as error:
        raise RuntimeError('Checker returned no valid terminal result: ' + process.stderr[:500]) from error
    if not isinstance(data, dict) or data.get('status') not in ('PASS', 'FAIL'):
        raise RuntimeError('Checker returned no valid terminal result')
    if process.returncode not in (0, 1):
        raise RuntimeError('Checker did not complete normally: ' + str(process.returncode))
    if (process.returncode == 0) != (data.get('status') == 'PASS'):
        raise RuntimeError('Checker exit/result disagreement')
    return data, process.returncode


def execute(args, directory, binary):
    if args.command == 'selftest':
        with (directory / 'selftest.log').open('w') as log:
            process = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                      '-s', str(ROOT / 'tests'), '-p', 'test_usb_integrity*.py', '-v'],
                                     cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=120)
        return {'status': 'PASS' if process.returncode == 0 else 'FAIL',
                'scope': 'host_detector_qualification', 'exit_code': process.returncode,
                'log': 'selftest.log'}
    if args.command == 'check':
        config = json.loads(args.manifest.read_text())
        validate(config)
        write_json(directory / 'manifest.json', config)
        # Read-only: the input recording is never modified or silently converted.
        with args.input.open('rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('Check only a closed regular PCM recording, not a device or pipe')
            data, code = check(binary / 'check', config, stream,
                               args.max_leading_frames, args.max_trailing_frames)
            stream.seek(0)
            fingerprint = hashlib.file_digest(stream, 'sha256').hexdigest()
            after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != \
               (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise RuntimeError('Recording changed during comparison; no stable result')
        return {'status': data['status'], 'scope': 'offline_capture_comparison',
                'exit_code': code, 'input_sha256': fingerprint, 'comparison': data}
    config = manifest(args)
    write_json(directory / 'manifest.json', config)
    if args.command == 'generate':
        size = (int(config['frames']) + 8) * config['channels'] * 3
        if size * 1.2 > shutil.disk_usage(directory).free:
            raise RuntimeError('Insufficient free space for the bounded fixture plus 20% allowance')
        path = directory / 'signal.pcm'
        with path.open('xb') as stream:
            subprocess.run([str(binary / 'generate'), *options(config)], stdout=stream,
                           stderr=subprocess.PIPE, check=True, timeout=300)
            stream.flush()
            os.fsync(stream.fileno())
        with path.open('rb') as stream:
            data, code = check(binary / 'check', config, stream)
        return {'status': data['status'], 'scope': 'host_generated_fixture',
                'exit_code': code, 'pcm': 'signal.pcm', 'sha256': sha(path),
                'comparison': data}
    # A finite host pipe benchmark: no pacing, recording disk, USB or board.
    started = time.monotonic()
    with (directory / 'generator.log').open('w') as log:
        producer = subprocess.Popen([str(binary / 'generate'), *options(config)],
                                    stdout=subprocess.PIPE, stderr=log)
        try:
            data, code = check(binary / 'check', config, producer.stdout)
            producer.stdout.close()
            producer_code = producer.wait(timeout=10)
        finally:
            if producer.stdout is not None:
                producer.stdout.close()
            if producer.poll() is None:
                producer.terminate()
                try:
                    producer.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    producer.kill()
                    producer.wait()
    elapsed = time.monotonic() - started
    return {'status': 'PASS' if code == 0 and producer_code == 0 else 'FAIL',
            'scope': 'host_pipe_capacity_only', 'comparison': data,
            'producer_exit': producer_code, 'checker_exit': code,
            'elapsed_seconds': elapsed,
            'audio_seconds': int(config['frames']) / config['rate_hz'],
            'combined_realtime_multiple': int(config['frames']) / config['rate_hz'] / elapsed,
            'payload_bytes_per_second': int(config['frames']) * config['channels'] * 3 / elapsed}


def parse(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'selftest', 'generate', 'check', 'benchmark', 'status'))
    parser.add_argument('--output-dir', type=Path, default=ROOT / '.local/usb-integrity')
    parser.add_argument('--cc', default=os.environ.get('CC', 'cc'), help='Compiler plus optional flags; no shell evaluation')
    parser.add_argument('--channels', type=int, default=24)
    frames = parser.add_mutually_exclusive_group()
    frames.add_argument('--frames', type=int)
    frames.add_argument('--seconds', type=int, default=1)
    parser.add_argument('--rate', type=int, choices=(48000, 96000), default=96000)
    parser.add_argument('--seed', type=lambda v: int(v, 0), default=secrets.randbits(64))
    parser.add_argument('--first-frame', type=int, default=0)
    parser.add_argument('--rotation', type=int, default=0)
    parser.add_argument('--pattern', choices=PATTERNS, default='identity')
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--max-leading-frames', type=int, default=0)
    parser.add_argument('--max-trailing-frames', type=int, default=0)
    parser.add_argument('--timeout-seconds', type=int, default=600,
                        help='Independent wall-time limit for the complete host job')
    args = parser.parse_args(argv)
    if args.command == 'check' and (args.manifest is None or args.input is None):
        parser.error('check requires --manifest and --input')
    if args.seconds <= 0 or args.seconds > 3600:
        parser.error('--seconds must be 1..3600')
    if not 1 <= args.timeout_seconds <= 7200:
        parser.error('--timeout-seconds must be 1..7200')
    return args


def main(argv=None):
    args = parse(argv)
    if args.command == 'status':
        result = status(args.output_dir)
        print(json.dumps(result))
        return 0 if result['status'] == 'PASS' else 1
    args.output_dir.mkdir(parents=True, exist_ok=True)
    directory = args.output_dir / ('run-' + uuid.uuid4().hex)
    directory.mkdir()
    result_path = directory / 'result.json'
    result = {'status': 'RUNNING', 'command': args.command, 'run_id': directory.name,
              'pid': os.getpid(),
              'owner': process_identity(os.getpid()),
              'phase': 'STARTING',
              'deadline_monotonic': time.monotonic() + args.timeout_seconds,
              'hardware_verified': False, 'g1': 'HOLD', 'contract': 1}
    write_json(result_path, result)
    write_json(args.output_dir / 'latest.json', {'result': str(result_path)})
    try:
        supervised(args, directory)
    except (OSError, ValueError, RuntimeError) as error:
        interrupt_job(directory, 'supervision_error: ' + str(error))
    result = json.loads(result_path.read_text())
    print(json.dumps({'status': result['status'], 'scope': result.get('scope'),
                      'result': str(result_path), 'error': result.get('error')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())

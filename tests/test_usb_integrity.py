"""Qualify native tools against independent bytes and deliberate failures."""
import json
import os
from pathlib import Path
import random
import shlex
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MASK = (1 << 64) - 1
NAMES = ('identity', 'edges', 'walking', 'alternating')


def reference_mix(value):
    value = (value + 0x9e3779b97f4a7c15) & MASK
    value = ((value ^ (value >> 30)) * 0xbf58476d1ce4e5b9) & MASK
    value = ((value ^ (value >> 27)) * 0x94d049bb133111eb) & MASK
    return value ^ (value >> 31)


def reference_code(frame, channel, channels, pattern, seed, rotation):
    if pattern == 'edges':
        return (0, 0xffffff, 1, 0xfffffe, 0x7fffff, 0x800000,
                0xff, 0x100, 0xffff, 0x10000, 0x555555, 0xaaaaaa)[(frame + channel) % 12]
    if pattern == 'walking':
        k = (frame + channel) % 48
        return (1 << k) if k < 24 else (0xffffff ^ (1 << (k - 24)))
    if pattern == 'alternating':
        return 0xaaaaaa if (frame + channel) & 1 else 0x555555
    role = (channel - rotation) % channels
    if channels >= 3 and role < 3:
        return ((frame & 0xffffff), ((frame >> 24) & 0xffffff),
                (0xa50000 | (frame >> 48)))[role]
    return reference_mix(frame ^ ((seed + (channel + 1) * 0x9e3779b97f4a7c15) & MASK)) & 0xffffff


def reference_stream(channels=24, frames=96, first=0, seed=0,
                     rotation=0, pattern='identity'):
    def marker(domain):
        return b''.join((reference_mix(seed ^ domain ^ i) & 0xffffff).to_bytes(3, 'little')
                        for i in range(4 * channels))
    body = b''.join(reference_code(f, c, channels, pattern, seed, rotation).to_bytes(3, 'little')
                    for f in range(first, first + frames) for c in range(channels))
    return marker(0x5354415254303031) + body + marker(0x454e442d30303031)


class IntegrityTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.bin = Path(cls.directory.name)
        cls.executor = shlex.split(os.environ.get('USB_INTEGRITY_EXECUTOR', ''))
        cc = shlex.split(os.environ.get('CC', 'cc'))
        if not cc or not shutil.which(cc[0]):
            raise RuntimeError('A native C compiler is required to qualify the checker')
        for name in ('generate', 'check'):
            subprocess.run([*cc, '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                            '-Wconversion', '-pedantic',
                            str(ROOT / 'tools/usb_integrity' / (name + '.c')),
                            '-o', str(cls.bin / name)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def args(self, channels=24, frames=96, first=0, seed=0,
             rotation=0, pattern='identity'):
        return ['--channels', str(channels), '--frames', str(frames),
                '--first-frame', str(first), '--seed', str(seed),
                '--rotation', str(rotation), '--pattern', pattern]

    def program(self, name):
        return [*self.executor, str(self.bin / name)]

    def compare(self, data, config=None, extra=()):
        return subprocess.run([*self.program('check'),
                               *(self.args(**(config or {}))), *extra],
                              input=data, capture_output=True, timeout=10)

    def assert_bad(self, data, config=None, extra=()):
        result = self.compare(data, config, extra)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'FAIL')
        return json.loads(result.stdout)

    def test_mix_known_constants(self):
        self.assertEqual(reference_mix(0), 0xe220a8397b1dcdaf)
        self.assertEqual(reference_mix(1), 0x910a2dec89025cc1)

    def test_literal_body_vectors(self):
        cases = [({'channels': 3, 'frames': 1, 'first': 0x123456789abcdef0},
                  'f0debc9a78563412a5'),
                 ({'channels': 4, 'frames': 1, 'pattern': 'walking'},
                  '010000020000040000080000'),
                 ({'channels': 4, 'frames': 1, 'pattern': 'alternating'},
                  '555555aaaaaa555555aaaaaa'),
                 ({'channels': 1, 'frames': 1}, 'f465b9'),
                 ({'channels': 12, 'frames': 1, 'pattern': 'edges'},
                  '000000ffffff010000feffffffff7f000080ff0000000100ffff00000001555555aaaaaa')]
        for config, literal in cases:
            with self.subTest(config=config):
                generated = subprocess.check_output([*self.program('generate'), *self.args(**config)])
                n = config['channels'] * 3
                self.assertEqual(generated[n * 4:-n * 4], bytes.fromhex(literal))
                independent = reference_stream(**config)
                self.assertEqual(generated, independent)
                self.assertEqual(self.compare(independent, config).returncode, 0)

    def test_boundaries_channels_rotations_seeds(self):
        starts = [0, 255, 256, (1 << 24) - 2, (1 << 32) - 2,
                  (1 << 48) - 2, MASK - 3]
        rng = random.Random(7321)
        for channels in (1, 2, 3, 8, 24):
            for first in starts:
                for pattern in NAMES:
                    config = dict(channels=channels, frames=4, first=first,
                                  seed=rng.getrandbits(64), rotation=rng.randrange(channels),
                                  pattern=pattern)
                    with self.subTest(config=config):
                        data = reference_stream(**config)
                        generated = subprocess.check_output([*self.program('generate'), *self.args(**config)])
                        self.assertEqual(generated, data)
                        self.assertEqual(self.compare(data, config).returncode, 0)

    def test_every_channel_rotation(self):
        for rotation in range(24):
            config = dict(rotation=rotation)
            data = reference_stream(**config)
            self.assertEqual(subprocess.check_output([*self.program('generate'), *self.args(**config)]), data)
            self.assertEqual(self.compare(data, config).returncode, 0)

    def test_early_bank_covers_all_bits_and_changing_channels(self):
        # Qualify the revised hardware bank using actual native producer bytes.
        data = subprocess.check_output([*self.program('generate'),
                                        *self.args(frames=48, pattern='walking')])[4 * 72:-4 * 72]
        for channel in range(24):
            values = [int.from_bytes(data[f * 72 + channel * 3:f * 72 + channel * 3 + 3],
                                     'little') for f in range(48)]
            for bit in range(24):
                self.assertEqual({(value >> bit) & 1 for value in values}, {0, 1})
        changing = set()
        for rotation in (0, 3):
            data = subprocess.check_output([*self.program('generate'),
                                            *self.args(frames=16, rotation=rotation)])[4 * 72:-4 * 72]
            for channel in range(24):
                values = {data[f * 72 + channel * 3:f * 72 + channel * 3 + 3] for f in range(16)}
                if len(values) > 1:
                    changing.add(channel)
        self.assertEqual(changing, set(range(24)))

    def test_error_at_stdio_chunk_boundary_is_observed(self):
        config = dict(frames=2000)
        clean = reference_stream(**config)
        for offset in (65535, 65536, 65537):
            corrupt = bytearray(clean)
            corrupt[offset] ^= 1
            result = self.assert_bad(corrupt, config)
            self.assertEqual((int(result['frame']), result['channel']),
                             (offset // 72 - 4, (offset % 72) // 3))

    def test_every_bit_in_every_channel_is_observed(self):
        clean = reference_stream()
        position = (4 + 17) * 72
        for channel in range(24):
            for bit in range(24):
                corrupt = bytearray(clean)
                corrupt[position + channel * 3 + bit // 8] ^= 1 << (bit % 8)
                result = self.assert_bad(corrupt)
                self.assertEqual((result['frame'], result['channel']), ('17', channel))

    def test_lost_and_duplicated_sample_or_frame(self):
        clean = reference_stream()
        position = (4 + 17) * 72
        for size in (3, 72):
            self.assert_bad(clean[:position] + clean[position + size:])
            self.assert_bad(clean[:position] + clean[position:position + size] + clean[position:])

    def test_channel_swap_duplicate_endian_shift_and_zero_fill(self):
        clean = reference_stream()
        position = (4 + 17) * 72
        variants = []
        swap = bytearray(clean)
        swap[position:position + 3], swap[position + 9:position + 12] = \
            swap[position + 9:position + 12], swap[position:position + 3]
        variants.append(swap)
        duplicate = bytearray(clean)
        duplicate[position + 9:position + 12] = duplicate[position:position + 3]
        variants.append(duplicate)
        endian = bytearray(clean)
        endian[position + 9:position + 12] = endian[position + 9:position + 12][::-1]
        variants.append(endian)
        zero = bytearray(clean)
        zero[position:position + 72] = bytes(72)
        variants.append(zero)
        variants.append(clean[:position] + b'\0' + clean[position:])
        for data in variants:
            self.assert_bad(data)

    def test_stuck_bits_are_observed_with_walking_pattern(self):
        config = dict(pattern='walking')
        original = reference_stream(**config)
        for bit in range(24):
            corrupt = bytearray(original)
            for f in range(96):
                for channel in range(24):
                    offset = (f + 4) * 72 + channel * 3 + bit // 8
                    corrupt[offset] &= 255 ^ (1 << (bit % 8))
            self.assert_bad(corrupt, config)

    def test_sequence_reset_and_wrap_regression(self):
        clean = reference_stream()
        position = (4 + 48) * 72
        self.assert_bad(clean[:position] + clean[4 * 72:(4 + 48) * 72] + clean[-4 * 72:])
        config = dict(first=(1 << 24) - 48)
        original = reference_stream(**config)
        wrong = reference_stream(first=0, frames=48)
        self.assert_bad(original[:position] + wrong[4 * 72:-4 * 72] + original[-4 * 72:], config)

    def test_truncation_extra_data_and_missing_markers_fail(self):
        clean = reference_stream()
        for data in (b'', clean[:-1], clean[:-72], clean[:-4 * 72], clean[72:],
                     clean[4 * 72:], clean + bytes(72), clean[:400]):
            self.assert_bad(data)

    def test_declared_boundary_windows_only(self):
        clean = reference_stream()
        data = bytes(3 * 72) + clean + bytes(2 * 72)
        self.assert_bad(data)
        extra = ['--max-leading-frames', '3', '--max-trailing-frames', '2']
        result = self.compare(data, extra=extra)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)['leading_frames_excluded'], '3')
        self.assertEqual(json.loads(result.stdout)['trailing_frames_excluded'], '2')
        self.assert_bad(bytes(4 * 72) + clean, extra=extra)
        self.assert_bad(clean + bytes(3 * 72), extra=extra)
        self.assert_bad(b'\0' + clean, extra=extra)
        self.assert_bad(data + b'\0', extra=extra)

    def test_interior_marker_does_not_restart_comparison(self):
        clean = reference_stream()
        offset = (4 + 17) * 72
        self.assert_bad(clean[:offset] + clean[:4 * 72] + clean[offset:],
                        extra=['--max-leading-frames', '192000'])

    def test_wrong_seed_length_mapping_and_pattern_fail(self):
        clean = reference_stream()
        for config in (dict(seed=1), dict(frames=95), dict(frames=97),
                       dict(channels=8), dict(rotation=1), dict(pattern='edges')):
            self.assert_bad(clean, config)

    def test_invalid_arguments_fail_before_output(self):
        cases = [[], ['--frames', '0'], ['--frames', '-1'], ['--frames', '2', '--channels', '25'],
                 ['--frames', '2', '--first-frame', str(MASK)],
                 ['--frames', '2', '--rotation', '24'], ['--frames', '2', '--seed', str(MASK + 1)],
                 ['--frames', '1', '--pattern', 'bogus'], ['--frames'],
                 ['--frames', '1', '--seed', ' -1'], ['--frames', '1', '--seed', '+1']]
        for program in ('generate', 'check'):
            for args in cases:
                result = subprocess.run([*self.program(program), *args], input=b'', capture_output=True)
                self.assertEqual(result.returncode, 2, (program, args, result.stdout))
                self.assertEqual(result.stdout, b'')


if __name__ == '__main__':
    unittest.main()

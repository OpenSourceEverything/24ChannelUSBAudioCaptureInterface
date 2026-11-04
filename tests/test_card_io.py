"""Exercise actual byte transfer, corruption detection and opened-device binding."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('card_io', Path(__file__).parents[1] / 'tools/card_io.py')
card_io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(card_io)


class CardTransfer(unittest.TestCase):
    def fixture(self, folder):
        image = Path(folder) / 'image.wic'
        card = Path(folder) / 'card.fixture'
        payload = bytes(range(256)) * 4101
        image.write_bytes(payload)
        return image, card, payload, hashlib.sha256(payload).hexdigest()

    def test_write_verifies_exact_image_and_preserves_bytes_beyond_it(self):
        with tempfile.TemporaryDirectory() as folder:
            image, card, payload, expected = self.fixture(folder)
            card.write_bytes(b'\0' * len(payload) + b'outside image')
            events = []
            result = card_io.transfer(image, card, expected, report=events.append)
            self.assertEqual(card.read_bytes(), payload + b'outside image')
            self.assertEqual(result['sha256'], expected)
            self.assertEqual(result['verified_bytes'], len(payload))
            self.assertTrue(result['wrote_image'])
            self.assertIn('FLUSHING', [e['stage'] for e in events])
            self.assertEqual(events[-1]['bytes_done'], len(payload))

    def test_verify_only_preserves_the_entire_target(self):
        with tempfile.TemporaryDirectory() as folder:
            image, card, payload, expected = self.fixture(folder)
            card.write_bytes(payload + b'unchanged tail')
            before = card.read_bytes()
            result = card_io.transfer(image, card, expected, verify_only=True)
            self.assertFalse(result['wrote_image'])
            self.assertEqual(card.read_bytes(), before)

    def test_one_corrupted_byte_fails_with_correct_image_size(self):
        with tempfile.TemporaryDirectory() as folder:
            image, card, payload, expected = self.fixture(folder)
            damaged = bytearray(payload)
            damaged[len(damaged) // 2] ^= 1
            card.write_bytes(damaged)
            with self.assertRaisesRegex(RuntimeError, 'checksum failed'):
                card_io.transfer(image, card, expected, verify_only=True)

    def test_truncated_readback_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            image, card, payload, expected = self.fixture(folder)
            card.write_bytes(payload[:-1])
            with self.assertRaisesRegex(RuntimeError, 'ended early'):
                card_io.transfer(image, card, expected, verify_only=True)

    def test_device_replacement_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as folder:
            image, card, payload, expected = self.fixture(folder)
            card.write_bytes(b'preserve selected device')
            with patch.object(card_io.fcntl, 'ioctl', return_value=struct.pack('Q', 12)):
                with self.assertRaisesRegex(RuntimeError, 'Card changed'):
                    card_io.transfer(image, card, expected, diskseq=11)
            self.assertEqual(card.read_bytes(), b'preserve selected device')


if __name__ == '__main__':
    unittest.main()

"""Protect device selection and verified-image boundaries without bench writes."""
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
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('device', str(Path(__file__).parents[1] / 'device'))
spec = importlib.util.spec_from_loader(loader.name, loader)
device = importlib.util.module_from_spec(spec)
loader.exec_module(device)


class DeviceBoundaries(unittest.TestCase):
    def test_stale_build_status_is_reported_as_stopped(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'install-status.json').write_text(json.dumps({
                'stage': 'BUILDING', 'message': 'Old build record'}))
            with patch.object(device, 'LOCAL', root):
                self.assertEqual(device.installation_status()['stage'], 'STOPPED')

    def test_live_build_status_remains_building(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'install-status.json').write_text(json.dumps({
                'stage': 'BUILDING', 'message': 'Live build',
                'process': device.process_identity(os.getpid())}))
            with patch.object(device, 'LOCAL', root):
                self.assertEqual(device.installation_status()['stage'], 'BUILDING')

    def test_reused_process_id_does_not_keep_old_build_alive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            identity = {**device.process_identity(os.getpid()), 'start_ticks': 'wrong'}
            (root / 'install-status.json').write_text(json.dumps({
                'stage': 'WRITING', 'message': 'Old writer', 'process': identity}))
            with patch.object(device, 'LOCAL', root):
                self.assertEqual(device.installation_status()['stage'], 'STOPPED')

    def test_install_preserves_an_unrelated_command(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            command = home / '.local/bin/bbb'
            command.parent.mkdir(parents=True)
            command.write_text('existing command')
            with patch.object(device.Path, 'home', return_value=home):
                with self.assertRaisesRegex(RuntimeError, 'unrelated command'):
                    device.install_cli()
            self.assertEqual(command.read_text(), 'existing command')

    def test_install_shortcut_is_repeatable(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(device.Path, 'home', return_value=Path(folder)), \
                 contextlib.redirect_stdout(io.StringIO()):
                command = device.install_cli()
                device.install_cli()
                self.assertEqual(command.resolve(), device.ROOT / 'device')

    def card_inventory(self, removable=True, mount='/media/user/project', size=8000):
        return {'blockdevices': [{'path': '/dev/card', 'type': 'disk', 'rm': removable,
            'size': size, 'mountpoints': [None], 'children': [
                {'path': '/dev/card1', 'type': 'part', 'mountpoints': [mount]}]}]}

    def test_host_disk_is_rejected_even_if_marked_removable(self):
        for mount in ['/', '/home', '/home/user', '/boot', '/boot/efi', '/usr', '/var/lib']:
            with self.subTest(mount=mount), self.assertRaisesRegex(RuntimeError, 'host filesystem'):
                device.removable_card('/dev/card', self.card_inventory(mount=mount), 1000)

    def test_fixed_disk_and_partition_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'whole removable'):
            device.removable_card('/dev/card', self.card_inventory(removable=False), 1000)
        with self.assertRaisesRegex(RuntimeError, 'whole removable'):
            device.removable_card('/dev/card1', self.card_inventory(), 1000)

    def test_undersized_card_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'too small'):
            device.removable_card('/dev/card', self.card_inventory(size=999), 1000)

    def test_explicit_removable_card_is_accepted(self):
        card = device.removable_card('/dev/card', self.card_inventory(), 1000)
        self.assertEqual(card['path'], '/dev/card')

    def test_sd_reader_without_removable_flag_is_accepted(self):
        inventory = self.card_inventory(removable=False)
        inventory['blockdevices'][0]['path'] = '/dev/mmcblk0'
        with patch.object(device.Path, 'read_text', return_value='SD\n'):
            card = device.removable_card('/dev/mmcblk0', inventory, 1000)
        self.assertEqual(card['path'], '/dev/mmcblk0')

    def test_emmc_is_rejected_even_with_removable_flag(self):
        inventory = self.card_inventory()
        inventory['blockdevices'][0]['path'] = '/dev/mmcblk0'
        with patch.object(device.Path, 'read_text', return_value='MMC\n'):
            with self.assertRaisesRegex(RuntimeError, 'whole removable'):
                device.removable_card('/dev/mmcblk0', inventory, 1000)

    def test_unreadable_mmc_type_is_rejected(self):
        inventory = self.card_inventory()
        inventory['blockdevices'][0]['path'] = '/dev/mmcblk0'
        with patch.object(device.Path, 'read_text', side_effect=OSError('unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'whole removable'):
                device.removable_card('/dev/mmcblk0', inventory, 1000)

    def test_remote_host_cannot_add_ssh_options_or_shell_commands(self):
        for host in ['-oProxyCommand=bad', 'host;bad', 'root@host', 'host\nother', '$(bad)']:
            with self.subTest(host=host), self.assertRaisesRegex(RuntimeError, 'board IP'):
                device.ssh_command(host)

    def test_development_flash_does_not_fall_back_to_reference_image(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(device, 'LOCAL', Path(folder)), patch.object(device, 'fetch_image') as fetch:
                with self.assertRaisesRegex(RuntimeError, 'No completed development image'):
                    device.flash('/dev/card')
                fetch.assert_not_called()

    def test_development_image_must_still_match_build_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = root / 'built.wic'
            image.write_bytes(b'corrupt')
            (root / 'image-ready.json').write_text(json.dumps({
                'path': str(image), 'sha256': hashlib.sha256(b'original').hexdigest()}))
            with patch.object(device, 'LOCAL', root):
                with self.assertRaisesRegex(RuntimeError, 'checksum changed'):
                    device.development_image()

    def test_multiple_adapters_need_an_explicit_choice(self):
        with patch.object(device.glob, 'glob', return_value=['/dev/one', '/dev/two']):
            with self.assertRaisesRegex(RuntimeError, 'Found 2'):
                device.serial_port()
            self.assertEqual(device.serial_port('/dev/selected'), '/dev/selected')

    def test_missing_adapter_is_reported(self):
        with patch.object(device.glob, 'glob', return_value=[]):
            with self.assertRaisesRegex(RuntimeError, 'Found 0'):
                device.serial_port()

    def image_environment(self, folder):
        payload = b'known image bytes\x00\xff'
        root = Path(folder)
        lock = root / 'sources.json'
        lock.write_text(json.dumps({'bootstrap_image': {
            'filename': 'board.wic', 'url': 'https://example.invalid/board.wic',
            'sha256': hashlib.sha256(payload).hexdigest()}}))
        return payload, root, lock

    def test_download_is_published_only_after_hash_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            payload, root, lock = self.image_environment(folder)
            with patch.object(device, 'LOCAL', root), patch.object(device, 'LOCK', lock), \
                 patch.object(device.urllib.request, 'urlopen', return_value=io.BytesIO(payload)), \
                 contextlib.redirect_stdout(io.StringIO()):
                image = device.fetch_image()
                self.assertEqual(image.read_bytes(), payload)

    def test_corrupt_download_never_becomes_a_flash_image(self):
        with tempfile.TemporaryDirectory() as folder:
            _, root, lock = self.image_environment(folder)
            with patch.object(device, 'LOCAL', root), patch.object(device, 'LOCK', lock), \
                 patch.object(device.urllib.request, 'urlopen', return_value=io.BytesIO(b'corrupt')), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, 'Checksum failed'):
                    device.fetch_image()
                self.assertFalse((root / 'images/board.wic').exists())

    def test_corrupt_cached_image_is_not_silently_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            _, root, lock = self.image_environment(folder)
            (root / 'images').mkdir()
            (root / 'images/board.wic').write_bytes(b'corrupt')
            with patch.object(device, 'LOCAL', root), patch.object(device, 'LOCK', lock):
                with self.assertRaisesRegex(RuntimeError, 'wrong checksum'):
                    device.fetch_image()


if __name__ == '__main__':
    unittest.main()

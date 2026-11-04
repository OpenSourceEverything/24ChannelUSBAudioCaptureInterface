#!/usr/bin/env python3
"""Bounded image write/read-back with machine-readable progress."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import time

CHUNK = 1024 * 1024


def transfer(image, target, expected, *, verify_only=False, report=lambda event: None,
             diskseq=None):
    size = Path(image).stat().st_size
    if size <= 0 or len(expected) != 64:
        raise ValueError('Select a nonempty image and its SHA-256 checksum.')
    started = time.monotonic()
    last_report = 0

    def progress(stage, count, force=False):
        nonlocal last_report
        now = time.monotonic()
        if force or now - last_report >= 1:
            report({'stage': stage, 'bytes_done': count, 'bytes_total': size,
                    'elapsed_seconds': round(now - started, 1)})
            last_report = now

    with open(target, 'rb' if verify_only else 'r+b', buffering=0) as card:
        if diskseq is not None:
            # BLKGETDISKSEQ binds the opened device, including hotplug/reuse.
            actual = struct.unpack('Q', fcntl.ioctl(card.fileno(), 0x80081280, b'\0' * 8))[0]
            if actual != int(diskseq):
                raise RuntimeError('Card changed after selection. No write attempted.')
        if not verify_only:
            progress('WRITING', 0, True)
            copied = 0
            with open(image, 'rb') as source:
                while copied < size:
                    chunk = source.read(min(CHUNK, size - copied))
                    if not chunk:
                        raise RuntimeError('Image ended early. Do not boot this card.')
                    view = memoryview(chunk)
                    while view:
                        written = card.write(view)
                        if not written:
                            raise RuntimeError('Card write stopped. Do not boot this card.')
                        view = view[written:]
                    copied += len(chunk)
                    progress('WRITING', copied)
            progress('FLUSHING', copied, True)
            os.fsync(card.fileno())
        # Request fresh reads without dropping unrelated host caches.
        if hasattr(os, 'posix_fadvise'):
            try:
                os.posix_fadvise(card.fileno(), 0, size, os.POSIX_FADV_DONTNEED)
            except OSError:
                pass  # fsync + read-back still runs if cache advice is unsupported.
        card.seek(0)
        progress('VERIFYING', 0, True)
        checked = 0
        digest = hashlib.sha256()
        while checked < size:
            chunk = card.read(min(CHUNK, size - checked))
            if not chunk:
                raise RuntimeError('Read-back ended early. Do not boot this card.')
            digest.update(chunk)
            checked += len(chunk)
            progress('VERIFYING', checked)
        actual = digest.hexdigest()
        if actual != expected:
            raise RuntimeError('Read-back checksum failed. Do not boot this card.')
        progress('VERIFYING', checked, True)
        return {'sha256': actual, 'verified_bytes': checked, 'wrote_image': not verify_only}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    parser.add_argument('target')
    parser.add_argument('expected')
    parser.add_argument('--diskseq', required=True, type=int)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    try:
        if not stat.S_ISBLK(os.stat(args.target).st_mode):
            raise RuntimeError('The selected target is not a block device.')
        result = transfer(args.image, args.target, args.expected,
                          verify_only=args.verify_only, diskseq=args.diskseq,
                          report=lambda event: print(json.dumps(event), flush=True))
        print(json.dumps({'stage': 'VERIFIED', **result}), flush=True)
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({'stage': 'ERROR', 'message': str(error)}), flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build userspace tools from an existing Yocto recipe sysroot; never deploy."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe-work', type=Path, default=ROOT /
                        '.local/build/tmp/work/cortexa8hf-neon-poky-linux-gnueabi/alsa-utils/1.2.11')
    parser.add_argument('--output-dir', type=Path, default=ROOT / '.local/usb-integrity-arm')
    parser.add_argument('--emulate-tests', action='store_true',
                        help='Run the detector fixtures under existing host QEMU user emulation')
    args = parser.parse_args()
    work = args.recipe_work.resolve()
    native = work / 'recipe-sysroot-native'
    compiler = native / 'usr/bin/arm-poky-linux-gnueabi/arm-poky-linux-gnueabi-gcc'
    assembler = native / 'usr/bin/arm-poky-linux-gnueabi/arm-poky-linux-gnueabi-as'
    sysroot = work / 'recipe-sysroot'
    for required in (compiler, assembler, sysroot / 'usr/include/stdio.h'):
        if not required.is_file():
            parser.error('Matching cached Yocto toolchain/sysroot is incomplete: ' + str(required))
    command = [str(compiler), '--sysroot=' + str(sysroot), '-mcpu=cortex-a8',
               '-mfpu=neon', '-mfloat-abi=hard']
    output = args.output_dir.resolve()
    code = subprocess.call([sys.executable, str(Path(__file__).with_name('run.py')),
                            'build', '--output-dir', str(output), '--cc', shlex.join(command)])
    if code or not args.emulate_tests:
        return code
    emulator = ROOT / '.local/build/tmp/sysroots-components/x86_64/qemu-native/usr/bin/qemu-arm'
    if not emulator.is_file():
        parser.error('Cached host QEMU user emulator is unavailable: ' + str(emulator))
    directory = Path(json.loads((output / 'latest.json').read_text())['result']).parent
    environment = os.environ.copy()
    environment.update(CC=shlex.join(command),
                       USB_INTEGRITY_EXECUTOR=shlex.join([str(emulator), '-L', str(sysroot)]))
    result = {'status': 'RUNNING', 'scope': 'arm_user_emulation_only', 'hardware_verified': False}
    result_path = directory / 'emulated-result.json'
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    try:
        with (directory / 'emulated-selftest.log').open('w') as log:
            process = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                                      '-s', str(ROOT / 'tests'), '-p', 'test_usb_integrity.py', '-v'],
                                     cwd=ROOT, env=environment, stdout=log,
                                     stderr=subprocess.STDOUT, timeout=180)
        code = process.returncode
        result.update(status='PASS' if code == 0 else 'FAIL', exit_code=code)
    except (OSError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        code = 1
        result.update(status='ERROR', error=str(error))
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({**result, 'result': str(result_path)}))
    return code


if __name__ == '__main__':
    sys.exit(main())

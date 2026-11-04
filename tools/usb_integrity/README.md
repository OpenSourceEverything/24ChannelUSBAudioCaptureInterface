# USB integrity tools

Host-only preparation for TEST-008. The [version 1 PCM contract](../../docs/design/usb-test-pattern.md)
defines all bytes. These tools never configure USB, contact the board or open
an audio device. A successful comparison is a software result; G1 and all
physical tests remain open.

Requires Python 3.11+ and a native C11 compiler. From the repository root:

```sh
python3 tools/usb_integrity/run.py selftest
python3 tools/usb_integrity/run.py generate --seconds 1 --seed 0
python3 tools/usb_integrity/run.py benchmark --seconds 60 --seed 0
python3 -m unittest discover -s tests -v
```

Each command creates a unique run directory under ignored .local/usb-integrity,
with result.json, native binaries, compiler logs and source/binary hashes.
latest.json points to the newest run. Generate additionally saves manifest.json
and signal.pcm; check reads a closed, stable recording without changing it:

```sh
python3 tools/usb_integrity/run.py check --manifest RUN/manifest.json --input RUN/signal.pcm
```

Replace RUN with the actual run directory. Check rejects a missing END marker,
partial frame or interior mismatch; it never resynchronizes after START.
Only explicit --max-leading-frames / --max-trailing-frames permit exclusions,
at most two seconds each. Default is zero. Reports retain first bad frame,
channel and expected/actual codes. Every completed non-PASS command exits
nonzero. A compiler failure, timeout or abnormal checker termination is ERROR.
RUNNING is never a pass: this synchronous host utility has no independent
supervisor, periodic capture checker or desktop notifier. After a forced kill,
its unfinished result can remain RUNNING. Task 004 must supply those lifecycle
features before unattended hardware runs; do not use this runner alone as
their supervisor.

Options: --channels 1..24, --rate 48000/96000, --pattern
identity/edges/walking/alternating, --rotation 0..channels-1,
--first-frame, --seed, and --frames or --seconds (1..3600). Counts and seeds
are unsigned 64-bit; overflowing ranges fail. Default is 24 channels/96 kHz,
one second, identity, rotation zero and a new random seed. Explicit seed zero
is for reproducible fixtures, not the next hardware run. Raw data is always
packed three-byte little-endian PCM. Sample-rate options label the data;
output is unpaced. Never route these high-level code patterns to speakers.

The C executables accept --option value pairs for channels, frames, first-frame,
seed, rotation and pattern. Generate writes raw PCM to stdout; check reads
stdin and writes one terminal JSON result. Native check also accepts boundary
frame limits; only the Python wrapper enforces the two-second policy.

The benchmark transfers a finite generated stream through a host pipe without
disk recording, USB or pacing. --seconds 60 means 60 seconds of audio data,
not 60 seconds of elapsed benchmarking. The reported combined throughput
does not separately qualify generator/checker processing, board scheduling,
recording storage or TEST-008's full component-margin procedure.

## ARM build without an image rebuild

Use the matching cached Yocto recipe sysroot from the pinned baseline:

```sh
python3 tools/usb_integrity/build-yocto.py
python3 tools/usb_integrity/build-yocto.py --emulate-tests
```

This performs two userspace compilations only; it never builds an image,
installs a package, reflashes SD or contacts the BBB. --recipe-work selects an
explicit existing matching recipe work directory if the local build layout
differs. Missing compiler/assembler/headers stop with an error; the helper
does not download or construct a new toolchain. Prefer the populated
recipe-sysroot-native over isolated sysroots-components: the latter's linker/
assembler links can be unresolved and accidentally invoke host tools.

The result under .local/usb-integrity-arm records compiler/version, Cortex-A8/
NEON/hard-float flags and exact source/binary hashes. Inspect both executables
with readelf -h -A -l -d before deployment. The current build requests
/usr/lib/ld-linux-armhf.so.3 and libc.so.6; check both on the actual board
after G1. No ARM execution or sustained target generation result follows from
compilation. A retained SDK is the later portable build route; this helper
depends on an existing local build cache.
The optional emulation command uses the existing cached host qemu-arm and the
same target sysroot to run all 15 detector methods against newly compiled ARM
executables. It writes separate emulated-result.json and emulated-selftest.log
files. Check that result and the command's exit code separately from the
compilation result. QEMU here emulates userspace instructions/libraries on the
host; it does not emulate the BBB's USB controller, real-time scheduling or
board I/O, and is not a target throughput benchmark.

Review handoff and staged hardware instructions:
[preparation review](../../docs/reviews/usb-tools-preparation-2026-11-04.md),
[task 003](../../docs/tasks/003-board-preparation.md).

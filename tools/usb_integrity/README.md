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
Host jobs now execute in a separate worker session with an independent watchdog.
The watchdog checks owner/worker PID, process start time, boot identity and a
wall-time deadline; owner or worker SIGKILL produces a retained INTERRUPTED
result without owner polling. Loss of the watchdog also interrupts the job.
Cleanup attempts and uncertain/failed cleanup are retained, and an interrupted
job cannot later commit PASS. --timeout-seconds (default 600, range 1..7200)
sets the full-job bound. This lifecycle support is Linux-specific.

```sh
python3 tools/usb_integrity/run.py status
```

Status reads the result referenced by latest.json, and conservatively marks
legacy abandoned/unsupervised RUNNING results INTERRUPTED. latest.json is a
pointer, not a second status authority. Per-run result.json is authoritative.
PID reuse cannot authorize signalling an unrelated process group. If the
recorded group leader has disappeared, cleanup is explicitly UNVERIFIED;
this host utility is not cgroup containment of arbitrary remote descendants.
Live PCM readiness/capture orchestration, bounded live comparison, remote
worker containment and desktop notification remain [task 006](../../docs/tasks/006-capture-runner.md).
Do not use the host utility alone as an unattended hardware capture supervisor.

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

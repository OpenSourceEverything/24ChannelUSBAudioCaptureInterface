# 003 — Prepare the board experiment

State: READY_FOR_REVIEW. Depends on [002](002-host-tools.md); execution waits
for G1. This is deployment/trial preparation for TEST-008, not another test
procedure or an execution approval.

Prepare a reproducible ARM build using the pinned Yocto compiler, plus a
reviewable manifest and recovery instructions for the first target-format
trial. Record the pinned gadget ring/period constraints and the actual error
observation needed; source limits are not runtime measurements.

Do not change live USB profiles, clocks, pinmux or firmware while G1 is open.
Do not rebuild or reflash the base image just to stage a userspace tool.

Exit: reviewable software artifacts and explicit trial/recovery steps are
ready. Unavailable compiler/runtime validation is stated rather than guessed.

## Build artifacts

[Build helper and commands](../../tools/usb_integrity/README.md) use the
populated cached Yocto ALSA recipe sysroots, GCC 13.5.0 and Cortex-A8/NEON/
hard-float flags. Both C executables compile without warnings. ELF inspection
identifies ARMv7 hard-float, libc.so.6 and /usr/lib/ld-linux-armhf.so.3.
The cached image contains those runtime files; the physical board's files
and execution remain to be checked after G1. Host ARM emulation qualifies
sample logic only, not the BBB CPU, scheduler, ALSA or USB controller.

No image rebuild, package install, SD write or board access was needed.
Build output, source/binary hashes and compiler logs are retained under ignored
.local/usb-integrity-arm. Copy matching artifacts over USB SSH only after G1,
verify SHA-256 at both ends and keep them in a dedicated temporary trial
directory. Do not replace audioctl or the working boot/service configuration.

## Staged first-trial configuration

Freeze a fresh run ID and seed in manifest.json: schema 1, channels 24,
rate_hz 96000, pattern identity, rotation 0, first_frame "0", frames
"5760000" (60 seconds of data), plus the seed as a decimal string. The
producer also sends four START and four END frames: 414,720,576 total bytes.
Retain this manifest independently of captured samples. Prepare bounded host
storage for a 62-second raw capture (428,544,000 bytes), logs and analysis
copies, with at least the documented 20% allowance. Final SATA qualification
is still required by the unchanged procedures unless G1 explicitly disposes
the proposal to defer it. Never select, format or write an unknown disk.

After G1, from the retained UART console: save the current UDC and all gadget
attributes; stop producers; unbind the gadget; set p_chmask=16777215,
p_srate=96000 and p_ssize=3; rebind the same controller. This deliberately
disconnects composite USB audio/SSH. Retain host enumeration, high-speed
state, descriptors, card IDs and native format/channel/rate capabilities.
Do not assume old ALSA card numbers survive reconnect. Unsupported native
format is a failure to investigate, never permission to use conversion.

Command templates for review, not commands already executed:

```sh
# Host: HOST_PCM is the explicitly identified native hw:CARD=...,DEV=0 PCM.
# RUN is a new, approved recording directory; preserve both streams' logs/status.
arecord -D "$HOST_PCM" -t raw -f S24_3LE -r 96000 -c 24 -d 62 \
  --disable-resample --disable-channels --disable-format --disable-softvol \
  --fatal-errors --dump-hw-params -v "$RUN/capture.pcm" 2>"$RUN/arecord.log"

# Board: BOARD_PCM is the freshly identified native gadget playback PCM.
# Use Bash with pipefail; take seed/count/map from the frozen manifest.
set +e
set -o pipefail
./generate --channels 24 --frames 5760000 --first-frame 0 \
  --seed "$RUN_SEED" --rotation 0 --pattern identity 2>generator.log |
  aplay -D "$BOARD_PCM" -t raw -f S24_3LE -r 96000 -c 24 \
    --disable-resample --disable-channels --disable-format --disable-softvol \
    --fatal-errors --dump-hw-params -v 2>aplay.log
# Save PIPESTATUS immediately, before another command changes it.
trial_status=("${PIPESTATUS[@]}")
printf '%s\n' "${trial_status[@]}" > pipeline-exit-codes.txt

# Host: compare the complete CLOSED recording after both processes finish.
python3 tools/usb_integrity/run.py check --manifest "$RUN/manifest.json" \
  --input "$RUN/capture.pcm" --max-leading-frames 192000 \
  --max-trailing-frames 192000
```

Start host capture first and confirm its PCM is RUNNING with the expected
parameters before starting the producer within the permitted lead interval.
Do not manually guess a sleep interval as the final automation. The finite
producer drains before the host's bounded recording ends. Log any padding
after END as tail exclusion; no interior samples may be excluded. A missing
marker, nonzero exit, xrun or time overrun cannot become a shortened PASS.
Retain /proc/asound card/PCM hw_params and sw_params while active on both
ends. Templates do not yet provide live checking, independent supervision,
timeout cleanup or notification; those are explicit task 004 prerequisites.

## Buffer and error observations

Pinned u_audio.c limits the ring to 16 x 4096 bytes and each period to 4096
bytes. At 72 bytes/frame and 96 kHz, these are at most about 9.481 ms of
ring data and 56 whole frames / 0.583 ms per period. Actual negotiated
settings may be smaller. Retain them; no average throughput benchmark proves
these short service deadlines are met.

The source's nonzero isochronous completion status is a pr_debug site.
The cached built kernel has CONFIG_DYNAMIC_DEBUG and CONFIG_DYNAMIC_DEBUG_CORE
disabled. Quiet dmesg and writing a dynamic-debug selector cannot establish
zero errors on that configuration. CONFIG_KPROBES/KPROBE_EVENTS are enabled;
a narrow counter is a candidate only after symbol/ABI/field-offset validation
and an observation-loss check. If that route is unavailable, review a minimal
counter/config change and its separate kernel build. Do not enable every
packet's logging or claim the criterion has passed without an observation
point. Retain exact-data results separately from lower-level error counts.

## Recovery and handoff

Keep UART available throughout. Stop producer/playback first, then recording;
save failures before cleanup. Via UART, restart ose-audio-usb: its ExecStop
removes the experimental gadget and ExecStart recreates the known mono
48-kHz/S16_LE profile. Recheck attributes, USB SSH and a fresh bounded nonzero
tone recording. An unresponsive controller requires a separately recorded
recovery; the earlier rebind success is not an automatic production policy.
No reboot, eMMC change or pinmux alteration is part of this trial preparation.

Next: resolve external G1 findings, then complete task 004's runner/error
instrumentation and execute only the accepted plan. [Review entry point](../reviews/usb-tools-preparation-2026-11-04.md).

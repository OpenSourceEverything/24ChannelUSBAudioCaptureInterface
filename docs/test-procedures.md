# Test Procedures

Status: initial engineering procedures. The [requirements](requirements.md)
own the targets; these procedures define how to measure them. Provisional
limits are not production claims. No analog, synchronization or endurance
result is implied by this document. Record unexecuted tests as NOT_RUN.

## Common setup and result rules

- Identify hardware/PCB revisions, channel map, input mode/gain, firmware and
  kernel commits, device tree, host OS, application/version and USB descriptors.
- Default analog setup: complete external LINE connector to host recording,
  all 24 channels powered/active, native 96-kHz capture with 24 valid bits,
  documented line gain, phantom off, 100-Ω differential source impedance and
  ambient 23 ±5 °C. Calibrate stimulus level at the DUT connector under load.
  DUT means the complete device under test. State exceptions explicitly.
- Equipment: characterized low-distortion balanced generator/audio analyzer,
  calibrated level meter, source-equivalent terminations, suitable clock/
  logic probes, Linux recording host and external SATA recording drive.
  Oscilloscope/logic checks establish levels and timing, not -100-dB audio
  performance. Identify instrument model, calibration date and uncertainty.
- Characterize generator, fixtures and analyzer noise/distortion/crosstalk
  floors using the same levels and bandwidth. Repeat sensitive tests three
  times. A measurement floor that cannot resolve the target is INCONCLUSIVE,
  not PASS. Do not subtract unrelated noise floors to manufacture a pass.
- Reference dBFS to a full-scale sine RMS value. Use the same normalization
  for stimulus, residual noise and host analysis. Preserve raw samples;
  disable AGC, normalization, mixing, effects and sample-rate conversion.
- PASS: the measured result, including the relevant uncertainty bound, meets
  the target. FAIL: demonstrated violation. BLOCKED: a prerequisite/limit is
  missing. INCONCLUSIVE: measurement cannot resolve the limit. NOT_RUN: no
  execution. N/A requires a documented scope/feature reason. A provisional
  engineering PASS does not promote a requirement or certify production.
- Retain commands/instrument settings, raw or losslessly retained recordings,
  sample counts, analysis version/configuration, result values, uncertainty,
  logs/error counters and checksum manifest. Do not record only screenshots.

## TEST-001: Channel count and format

Equipment: configured full-channel DUT, known analog source(s), Linux host,
ALSA native recorder and a recorder such as Audacity for application proof.

1. Inspect hardware parameters and USB descriptors. Record the actual ADC
   output width, serial slot width, memory format, USB subslot width and
   file format. Identify unused/padding bits independently of valid bits.
2. Record all 24 channels simultaneously at the target format for 60 seconds.
   Drive distinguishable signals on the inputs, or move one known -12-dBFS
   tone through all 24 inputs in documented time windows while capture of
   every channel continues. Check that changing one physical input changes
   its intended recorded channel. Identical fan-out tones alone cannot prove
   independence or rule out duplication.
3. Inspect the native capture rather than an application's floating-point
   export alone. Confirm negotiated 96 kHz, channel count, native 24 valid
   bits and ordering against the hardware map. Check serial data/mode or a
   known digital test pattern when validating padding/sign extension.
4. Repeat the physical-input change in the host application. For the first
   one-input milestone, retain the same evidence but label it a partial test.

PASS: ADC-001/002 and CAP-001/002/004 are met for all channels and the
recording corresponds to physical input. A 24-bit file header does not prove
24 effective analog bits, nor does a generated USB tone pass analog capture.

## TEST-002: Crosstalk

Equipment: low-crosstalk source/fixtures, 100-Ω differential source-equivalent
terminations, analyzer capable of resolving the proposed limit.

1. Terminate every unused input with a documented balanced 100-Ω
   source-equivalent network; document each leg's connection to reference.
2. Drive input 1 with a calibrated 1-kHz sine producing -1.0 ±0.1 dBFS.
   Record every channel for at least 10 seconds after a 2-second settling time.
3. Measure each channel's fundamental amplitude with the same coherent FFT
   or tone-fitting method. Report window, length, normalization, bins and
   effective analysis bandwidth, no greater than 10 Hz around the actual tone.
   Include analysis uncertainty and the independently measured fixture floor.
4. Calculate each victim result as 20 log10(V_victim,1k / V_driven,1k).
   Repeat with each input driven: retain all 24 × 23 = 552 directed pairs.

PASS: every pair meets ADC-003. At a -1-dBFS driven level, -100-dBFS leakage
is only -99 dB relative and fails the -100-dB target. A noise-floor-limited
estimate is a bound; do not claim an exact crosstalk value below that floor.

## TEST-003: Dynamic range

Equipment: calibrated source/attenuator and audio analyzer with validated
fundamental removal, 20-Hz–20-kHz filtering and A-weighting.

1. Establish full-scale reference from the documented analog transfer gain;
   do not run the converter into clipping merely to obtain a reference.
2. Set a 1-kHz tone to produce -60.0 ±0.1 dBFS, keeping the signal present
   during the noise measurement. Capture at least 10 seconds per channel.
3. Remove the fundamental with the characterized notch/tone-removal method.
   Measure residual RMS over 20 Hz–20 kHz with A-weighting. Record filter
   response, equivalent noise bandwidth and any notch-bandwidth correction.
4. Refer the residual to the full-scale sine. With a measured low-level
   signal-to-residual ratio R and actual tone level L dBFS, dynamic range is
   R - L; for exactly -60 dBFS, add 60 dB. Also retain unweighted results.
5. Repeat every input and include source/analyzer/attenuator uncertainty.

PASS: every complete LINE channel meets ADC-004. Silence/auto-mute and an
ADC datasheet number are insufficient evidence. This is an AES17-style
engineering procedure; verify filters and definitions against the selected
normative edition before claiming AES17 conformance. References:
[Audio Precision's method explanation](https://www.audioprecision.com/news/more-about-signal-to-noise-ratio-and-dynamic-range),
[AES17-2020 description](https://aes.org/publications/standards-store/?id=21).

## TEST-004: Distortion

Equipment: characterized low-distortion generator and analyzer capable of
resolving the proposed THD+N limit at the actual connector voltage.

1. Drive a 1-kHz sine producing -1.0 ±0.1 dBFS. Verify source and receiver
   remain unclipped, with the required input bias/common-mode conditions.
2. Capture at least 10 seconds. Remove the fundamental and measure residual
   noise plus harmonics from 20 Hz to 20 kHz, unweighted. State the removal
   filter/bins and integration bandwidth; do not use an unspecified FFT floor.
3. Compute THD+N = 20 log10(V_residual / V_fundamental). Repeat every channel
   with all converters active, then characterize lower levels and supported
   gains separately. Additional characterization does not change the named
   -1-dBFS acceptance point.

PASS: every complete LINE path meets ADC-005, with uncertainty accounted for.
MIC/INSTRUMENT distortion limits at other gains remain separate design gates.

## TEST-005: Channel synchronization

Equipment: matched distribution fixture, common band-limited broadband/MLS
or marked waveform, clock probes and repeatable time/phase analysis. MLS is
a known pseudorandom sequence useful for finding time shifts by correlation.

1. Calibrate fixture path delay and loading. Feed the same -12-dBFS nominal
   waveform to all inputs in the same mode/gain. Avoid an uncharacterized
   passive fan-out whose loading/phase errors dominate the result.
2. Measure common clocks and frame/reset sequence. Record all channels and
   determine pairwise delay with correlation and fractional-sample analysis.
   A 1-kHz phase comparison alone is ambiguous by whole tone periods.
3. Repeat at least three starts, including a power cycle. Repeat analysis at
   the beginning, during and at the end of TEST-006; retain offsets versus time.
   Do not remove measured DUT delay by aligning channels in postprocessing.

PASS: ADC-006's provisional one-sample bound is met, including fixture/
analysis uncertainty, with no relative drift or frame slips in the 24-hour
run. A shared oscillator alone does not demonstrate deterministic alignment.

## TEST-006: Continuous recording

Equipment: full-channel DUT, known/marked analog signals or a qualified
deterministic serial-audio stimulus, external SATA drive on the Linux host,
sample-integrity checker and CPU/buffer/error monitoring.

### Storage and resource preflight

The recording target is the host's external SATA drive, not the BeagleBone
microSD. Identify its actual device, mounted path, filesystem, free space and
host connection. Do not infer it from a changing /dev/sdX name or format an
unidentified disk. Use a dedicated test directory on the selected volume.
If connected through a USB–SATA bridge, record USB topology and test
drive/audio traffic together.

| Stored representation | Audio write rate | Raw bytes for 24 hours | Free-space target with 20% allowance |
| --- | --- | --- | --- |
| Packed 24-bit, 3 bytes/value | 6,912,000 B/s | 597,196,800,000 | 716,636,160,000 bytes |
| 32-bit container, 4 bytes/value | 9,216,000 B/s | 796,262,400,000 | 955,514,880,000 bytes |

These are payload calculations; include headers, manifests and retained
comparison copies separately. A 16-GB boot card cannot store this run. Check
actual free space rather than assuming a nominal drive capacity is sufficient.
Use RF64/W64 or contiguous split files; ordinary RIFF WAV has a 32-bit size
limit. Five-minute packed chunks contain 2,073,600,000 audio bytes each;
retain exact first-frame indices/counts and prove gap-free file boundaries.

Before the long run, test a bounded temporary-file write on this specific
volume while USB capture/checking runs, using a dataset larger than the
reported host RAM and including flush completion. Record sustained throughput,
worst stalls and minimum buffer headroom. A cache-only speed result is not a
drive test. Start with a conservative engineering goal of twice the required
write rate; actual uninterrupted capture remains the acceptance evidence.

### Integrity and execution

1. Progress through 1-minute, 30-minute and 1-hour runs before the 24-hour run.
   A shorter successful run is partial evidence, not a 24-hour PASS.
2. Supply a known stimulus capable of exposing loss/duplication. A constant
   tone alone can hide whole-period drops. For deterministic TDM/USB test
   patterns, include channel identity and a monotonically advancing frame
   sequence and compare every received sample against the expected value.
3. For the complete analog run, compare normalized ADC-capture sample-block
   hashes/frame counts against host-recorded blocks, using the same 24 valid
   bits, channel order and frame boundaries. Send or retain the small digest/
   index manifest separately; a checksum of the final file alone cannot
   detect an error that occurred before that file was written. Measure the
   overhead on both board and host. This comparison facility is not yet
   implemented; without it or an equivalent independent check, mark the
   corruption criterion BLOCKED instead of claiming a bit-exact analog oracle.
4. Check known analog markers/time alignment as well: a digest comparison
   beginning after DMA cannot detect samples lost before its observation
   point. Document stimulus coverage, detector thresholds and limitations.
5. Record all 24 channels continuously for 24 hours. Monitor device/host xruns,
   USB errors, buffer occupancy, sample counts, clock state, CPU, temperature
   and storage stalls. Preserve periodic status independent of the recorder.
6. Close/flush files, validate every chunk boundary and compare all manifests.
   Keep 64-bit counters: at exactly 96 kHz, 24 hours is 8,294,400,000 frames
   per channel, beyond a 32-bit frame counter. Account for measured clock
   accuracy and test duration rather than treating the nominal count alone
   as a continuity proof.

PASS: ADC-007 and the long-duration portion of ADC-006 meet their limits with
complete stated integrity coverage. Any detected lost/duplicated/corrupted
sample, silent discontinuity, transport xrun or storage interruption fails.
An unobservable corruption path prevents PASS. Analyze crosstalk/distortion
on suitable retained windows afterward; continuous FFT of all samples is not
required for transport-integrity checking. A faster PC is a profiling decision
after this workload is measured, not a prerequisite inferred from data volume.

## TEST-007: Input compatibility and front-end controls

Equipment: calibrated source, 100-Ω LINE/150-Ω MIC/10-kΩ resistive INSTRUMENT
fixtures, impedance/capacitance measurement tools, level meter, scope and
appropriate dummy microphone-power loads. Use one front-end prototype first.

1. For each claimed connector/mode, verify pinout, polarity, shield/reference,
   balanced XLR/TRS and unbalanced TS behavior. One socket/input records one
   mono source. Never infer source voltage from connector shape.
2. Measure input impedance across 20 Hz–20 kHz in LINE/MIC. In INSTRUMENT,
   separate input resistance and capacitance, and report complex impedance at
   1 kHz rather than confusing the resistor value with total AC impedance.
   Measure jack input capacitance with the cable contribution removed;
   retain the fixture calibration and frequency.
3. Measure gain at minimum, maximum and named intermediate settings. Apply
   the specified source maximum at minimum gain and inspect clipping. Check
   LINE +4/+24-dBu behavior, MIC 0-dBu minimum-gain headroom, INSTRUMENT
   2-V RMS headroom, and each mode's frequency response versus 1 kHz.
4. For MIC EIN, use the 150-Ω source at 60-dB preamp gain, unweighted
   20 Hz–20 kHz; refer output noise through the measured complete path gain.
   State source-resistor noise separately. Check ADC-004/005 only in their
   named LINE configuration, not as an assertion about other gains.
5. Apply common-mode stimulus on matched 100-Ω legs at 50/60 Hz and 20 kHz;
   calculate common-mode rejection from measured differential gain and
   common-mode transfer. Repeat with documented source-impedance imbalance
   for characterization, not a different hidden acceptance condition.
6. Verify visible mode/gain/clip/power state and muted switching. If phantom
   is fitted, first review numeric voltage/current/discharge/fault limits,
   then use dummy loads to check boot-off, independent enables, MIC exit,
   and no power transfer to jack contacts. Undefined limits block the
   relevant test; source scopes/ratings come from the approved circuit.

PASS: the applicable IN/ANA requirements are met with measured values and
uncertainty recorded. Missing per-mode/protection limits remain explicit
BLOCKED gates, not guessed thresholds or evidence of feature completion.

## TEST-008: USB path, packet budget and clock-rate handling

1. Inspect negotiated high-speed UAC2 descriptors and Linux driver binding.
   Start a mono generated tone in matched ALSA formats, record on the host,
   and verify frequency/amplitude/physical device routing and error logs.
2. Before selecting an ADC board, exercise a generated 24-channel/96-kHz
   stream with known channel/frame patterns in the actual target USB packing.
   For 3-byte subslots, 12 frames require 864 bytes and 13 require 936 bytes
   per high-speed microframe. A four-byte subslot needs 1152 bytes for 12
   frames and exceeds the reviewed 1024-byte implementation cap.
3. Verify actual descriptor capacity, controller behavior and packet contents,
   not just nominal bus bandwidth. Initially run 30 minutes, logging pattern
   mismatches and buffers. Exercise clock tolerance/USB scheduling variation
   within the documented supported range; inspect bounded occupancy and
   absence of hidden sample deletion/resampling. Undefined clock limits
   block the tolerance subtest.

PASS: the named USB requirements hold for the advertised configuration.
Generated samples prove the USB path only; they bypass ADC, McASP and capture
DMA and cannot satisfy the complete analog/digital-front-end tests.

## TEST-009: Board interface, clocks, power and capture DMA

1. Record the exact board identity/revision, schematics, mux table, device
   tree, driver source/config and proposed converter interface. Resolve every
   used pin and shared net; assign one driver per clock/data signal.
2. Calculate serial clocks, timing margins, voltage/startup limits, FIFO/DMA
   layout and available buffers. Review the chosen kernel's CPU and codec
   DAI constraints; CPU-side channel capacity alone is insufficient.
3. Review paper compatibility before purchase. With qualified test hardware,
   measure rails/clock duty/setup/hold/reset, bind the actual sound card and
   run known patterns through the full receive-serializer/DMA arrangement.
   Start with a representative bank and then all required lanes. Inspect
   channel order, sample packing, error counters, buffer headroom and CPU.
4. Measure simultaneous-channel power and supported power/cable conditions;
   include startup/unpowered cases and specified protection tests. Do not
   execute fault injection while the applicable circuit limits are undefined.

PASS: the documented interface and the hardware checks meet CAP-006/ELE
requirements and support the target full-channel stream. Label source-review
findings separately from physical PASS. The [initial audit](research/beaglebone-multichannel-feasibility.md)
records candidate pins and remaining gates, not a completed capture test.

## TEST-010: Errors, interruption and recovery

During known-pattern capture, deliberately stop the source, overload the
bridge, unplug/replug USB, terminate/restart recording and restart the board.
Retain errors/counters and the resulting files. After each case restore the
documented setup and repeat the short known-pattern check.

PASS: failures are visible, affected samples/files are identified, and capture
recovers using the documented procedure without silently claiming continuity.

## TEST-011: Yocto baseline, access and updates

From the pinned sources/configuration, build the image and inspect kernel,
bootloader/rootfs identity. Boot on the actual board; record UART access,
key-based SSH, board menu and USB tone. Verify remote password access is
disabled according to the development policy without publishing credentials.
Deploy a menu edit, then a versioned application package over SSH with the
card left in place. Observe the changed program and package version. Check
applicable microphone-power defaults after boot.
Verify the provisioning key is installed under the actual root account home.
On a legacy-loader BBB, verify automatic SD boot through uEnv.txt as well as
the first manual boot. Reboot and recheck USB SSH, menu and a nonzero host
tone recording. A warm reboot is not a cold power-cycle qualification.

PASS: the named FW requirements work on hardware with source/artifact/log
evidence. Metadata parsing or successful compilation alone is insufficient.

## TEST-012: Development turnaround and build independence

Time an actual menu deployment and warm application build/deploy/result,
with the matching SDK/dependencies present. Keep build, transfer, restart,
human editing and recording outage times separate. Repeat three warm runs.
Exercise background platform building while the board runs its last working
system; verify live status and failure reporting. Retain downloads/sstate/SDK
and show task reuse without destructive cleaning. Record builder configuration
and portable pinned inputs for a separate build host.

PASS: the scenarios meet the [turnaround targets](requirements.md#development-turnaround),
and routine userspace changes require no card removal or full-image write.
Do not substitute the earlier tiny freestanding probe for this real workload.

## TEST-013: Product evidence and release gates

Review the actual design/BOM/revision against connectors, power, schematics,
firmware pins, build/install/recovery procedures, measured test reports and
exact manufacturer parts. Confirm claims do not exceed test evidence.
Record licenses/USB IDs/manufacturing test and applicable market compliance
scope, owner and evidence. Missing limits, approvals or certification evidence
remain BLOCKED before release; this review does not itself confer compliance.

## TEST-014: Windows 7 stretch investigation

After Linux acceptance, identify a lawful supported driver/application/OS
combination and document signing, licensing and redistribution conditions.
Test enumeration, channel count, actual format, recording and recovery on
that exact host. Label any reduced UAC1 mode separately. PASS only for the
demonstrated combination; this test does not gate Linux development.

## TEST-015: Unattended card installation

Equipment: Linux build host, completed checked image, explicitly identified
spare card/reader and the host-side test suite. Use temporary regular-file
fixtures for deliberate corruption/truncation tests, never a live boot disk.

1. Run the host suite. Verify corruption, short read-back, target replacement,
   write protection, interrupted workers and missing/wrong success records
   cannot produce READY. Confirm verify-only leaves fixture bytes unchanged.
2. Start bbb flash CARD. Observe saved progress through write, flush and verify;
   the command returns while the systemd job continues. Leave the terminal
   closed during the job; keep the host awake and user session logged in.
3. Inspect the saved result/log and desktop completion notification. Verify
   exact image byte count/SHA-256 and card identity. Notification availability
   is reported separately; a missing notification must not hide the result.
4. Use --wait for an exit-code-driven script, and --verify-only to exercise
   the actual read-back path without another write or image build. With a
   disposable fixture/job, stop the worker and verify cleanup and failure.

PASS: FW-008 holds, with no assistant status polling or new image build needed
to complete the job. Host fixtures and read-only hardware checks are partial
evidence for the background write path; record each executed scenario.

## Requirement coverage

The table below maps every requirement ID to repeatable verification. Each
procedure includes the equipment/conditions above. No row is marked executed
solely because its procedure exists. Results belong in a dated bench report.

| Requirement | Repeatable procedure |
| --- | --- |
| CAP-001 | [TEST-001](#test-001-channel-count-and-format), [TEST-006](#test-006-continuous-recording) |
| CAP-002 | [TEST-001](#test-001-channel-count-and-format), [TEST-002](#test-002-crosstalk) |
| CAP-003 | [TEST-005](#test-005-channel-synchronization), [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| CAP-004 | [TEST-001](#test-001-channel-count-and-format) |
| CAP-005 | [TEST-006](#test-006-continuous-recording), [TEST-010](#test-010-errors-interruption-and-recovery) |
| CAP-006 | [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma), [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-001 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-002 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-003 | [TEST-001](#test-001-channel-count-and-format) |
| USB-004 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-005 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling), [TEST-006](#test-006-continuous-recording) |
| ADC-001 | [TEST-001](#test-001-channel-count-and-format) |
| ADC-002 | [TEST-001](#test-001-channel-count-and-format) |
| ADC-003 | [TEST-002](#test-002-crosstalk) |
| ADC-004 | [TEST-003](#test-003-dynamic-range) |
| ADC-005 | [TEST-004](#test-004-distortion) |
| ADC-006 | [TEST-005](#test-005-channel-synchronization), [TEST-006](#test-006-continuous-recording) |
| ADC-007 | [TEST-006](#test-006-continuous-recording) |
| ANA-001 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| ANA-002 | [TEST-007](#test-007-input-compatibility-and-front-end-controls), [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| ANA-003 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| ANA-004 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| ELE-001 | [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| ELE-002 | [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| ELE-003 | [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| ELE-004 | [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| FW-001 | [TEST-011](#test-011-yocto-baseline-access-and-updates) |
| FW-002 | [TEST-011](#test-011-yocto-baseline-access-and-updates) |
| FW-003 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling), [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| FW-004 | [TEST-011](#test-011-yocto-baseline-access-and-updates), [TEST-012](#test-012-development-turnaround-and-build-independence) |
| FW-005 | [TEST-012](#test-012-development-turnaround-and-build-independence) |
| FW-006 | [TEST-012](#test-012-development-turnaround-and-build-independence) |
| FW-007 | [TEST-006](#test-006-continuous-recording) |
| FW-008 | [TEST-015](#test-015-unattended-card-installation) |
| PRD-001 | [TEST-013](#test-013-product-evidence-and-release-gates) |
| PRD-002 | [TEST-010](#test-010-errors-interruption-and-recovery) |
| PRD-003 | [TEST-013](#test-013-product-evidence-and-release-gates) |
| PRD-004 | [TEST-013](#test-013-product-evidence-and-release-gates) |
| WIN-001 | [TEST-014](#test-014-windows-7-stretch-investigation) |
| WIN-002 | [TEST-014](#test-014-windows-7-stretch-investigation) |
| WIN-003 | [TEST-014](#test-014-windows-7-stretch-investigation) |
| IN-001 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-002 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-003 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-004 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-005 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-006 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-007 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-008 | [TEST-003](#test-003-dynamic-range), [TEST-004](#test-004-distortion) |
| IN-009 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-010 | [TEST-007](#test-007-input-compatibility-and-front-end-controls), [TEST-002](#test-002-crosstalk) |
| IN-011 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-012 | [TEST-007](#test-007-input-compatibility-and-front-end-controls), [TEST-011](#test-011-yocto-baseline-access-and-updates) |
| IN-013 | [TEST-007](#test-007-input-compatibility-and-front-end-controls) |
| IN-014 | [TEST-007](#test-007-input-compatibility-and-front-end-controls), [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma) |
| IN-015 | [TEST-009](#test-009-board-interface-clocks-power-and-capture-dma), [TEST-013](#test-013-product-evidence-and-release-gates) |

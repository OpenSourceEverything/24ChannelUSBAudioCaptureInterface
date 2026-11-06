# Test Procedures

Status: engineering procedures, G1-B revision 2026-11-06. The [requirements](requirements.md)
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
- Equipment for analog/full-product tests: characterized low-distortion
  balanced generator/audio analyzer,
  calibrated level meter, source-equivalent terminations, suitable clock/
  logic probes, Linux recording host and external SATA recording drive.
  TEST-008's early generated-USB stage uses its own identified-host-storage
  preflight and needs no new ADC/analyzer. Oscilloscope/logic checks establish
  levels and timing, not -100-dB audio
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
  missing. INCONCLUSIVE: measurement cannot resolve the limit. INTERRUPTED:
  stopped/abandoned job or incomplete comparison, never continuous PASS.
  NOT_RUN: no execution. N/A requires a documented scope/feature reason. A provisional
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

Scope: generated samples in BeagleBone userspace -> ALSA gadget playback ->
USB -> native Linux host capture -> saved recording and independent checker.
External review has returned; G1 remains HOLD until the execution
prerequisites in the [disposition](reviews/g1-disposition-2026-11-06.md) close.
No board configuration or test is performed by revising this document. No new ADC, preamp or analyzer is needed for
this stage. All new scenarios remain NOT_RUN until their evidence is retained.
Thresholds below implement the G1-B
[USB-stage profile](requirements.md#generated-usb-stage-test-profile);
that requirements section owns their values and review status.

### Configuration and packet preflight

1. Preserve the working mono configuration and a UART recovery path. Record
   kernel/source revisions, gadget settings, channel-position/mapping metadata,
   descriptors, native PCM formats, host controller/topology and recorder.
   Retain a high-speed UAC2 enumeration and mono tone/application check.
2. Qualify 24 simultaneous channels at 96 kHz with 24 valid bits and three-byte
   USB subslots. Confirm native sample packing rather than inferring it from
   an editor export. Disable sample-rate conversion, gain, mute, dither and
   other transformations on the comparison path; use unity or absent gadget
   volume controls. Record processor-memory and stored-file widths separately.
3. Calculate endpoint service interval/capacity with the actual driver:
   require high-speed bInterval=1 (125 us), 24 channels and three-byte USB
   subslots. Record p_hs_bint, fb_max and the descriptor's wMaxPacketSize,
   transaction multiplier and bBitResolution/bSubslotSize. At 125 us,
   12 frames x 24 x 3 = 864 bytes; a 13-frame packet is 936 bytes. With the
   pinned default fb_max=5, require at least 936 bytes and no high-bandwidth
   transaction multiplier. Calculate any changed feedback reserve from the
   pinned source, rather than assuming 936 bytes covers every setting.
   Four-byte subslots already need 1152 bytes for 12 frames, beyond the
   reviewed driver's 1024-byte cap. Inspect actual descriptors and bounded
   packet traces for lengths/frame alignment and extra-frame handling. Do not
   advertise or run an over-capacity configuration as a valid stream. Reject
   the driver's "may drop data" sizing/clamping warning. Bounded traces must
   identify the correct device/endpoint and iso packet lengths (not whole-URB
   lengths); successful audio packets contain complete 72-byte frames within
   advertised capacity. Retain trace-loss evidence. A nominal-clock trace need
   not contain a 13-frame packet; descriptor/source reserve and observed packet
   correctness are separate checks. No packets or a lossy trace is INCONCLUSIVE.

The cap is a finding about the inspected implementation, not all USB 2.0
isochronous endpoints. Source baseline: Linux 6.6.21 Yocto commit
06644f0d7193d7ec39d7fe41939a21953e7a0c65, functions
get_max_bw_for_bint/set_ep_max_packet_size_bint in
drivers/usb/gadget/function/f_uac2.c and packet accumulation in u_audio.c.
[Kernel UAC2 interface documentation](https://www.kernel.org/doc/html/latest/usb/gadget-testing.html#uac2-function)
describes configuration attributes; verify their presence in the pinned build.

### Exact-data oracle and detector qualification

An oracle is the independently defined expected sample stream. Freeze its
algorithm, seeds, channel order, unsigned 24-bit code representation,
little-endian byte encoding and reference vectors before running hardware.
Keep 64-bit frame indices and a unique run identifier in the run manifest.
For the long identity pattern, encode the frame index across multiple sample
words or use an equivalently unambiguous long-period construction; a lone
24-bit counter wraps after about 175 seconds at 96 kHz and is insufficient.
Every channel also needs identifiable, changing data. Rotate counter/marker
roles through channels so no channel or bit is checked only with a constant.

The host checker compares every captured 24-bit value against the frozen
definition. It must not obtain its expectation by copying the board's output
or importing the same untested packing routine. Independently specified byte
vectors must cover sign and byte boundaries. Retain implementation revisions,
first failing frame/channel/expected/actual values and total checked counts.

Before trusting PASS, demonstrate each detector with corrupted host fixtures:
one-bit changes in every bit position/channel, missing/duplicated sample and
whole frame, channel swap/duplication, byte-order/subslot shift, stuck bit,
zero-filled block, truncation and an error at a recording-chunk boundary.
Also deliberately reset/wrap the generator's sequence state. Each must FAIL;
an intact reference must PASS. These software fixtures do not inject voltage
faults into the board. Test detection during recording as well as final-file
validation; record the checker interval and failure-notification delay.

Start capture before the generator. Use unique start/end markers and a
predeclared alignment method. Report startup/shutdown samples excluded from
comparison and their maximum permitted duration, proposed at two seconds per
end. Start the timed valid-data window only after the start marker. No silent
resynchronization, dropped tail or exclusion of an interior mismatch is allowed.
A missing end marker or incomplete comparison is FAIL, not a shorter PASS.

### Early-stage patterns, runs and storage

PCM contents change coverage, not the constant byte rate. Use the frozen
[contract v1](design/usb-test-pattern.md) and independently tested native tools.
Preserve the mono bootstrap, then attempt 24/96k directly. Lower channel/rate
profiles are diagnostics when needed. They are not additional mandatory modes.

| Early run | Exact stimulus and evidence |
| --- | --- |
| Identity | At least 60 s at rotation 0; new seed/run identity, native all-channel comparison. |
| Coverage bank | 60 s total: 19 s edges, 19 s walking, 19 s alternating and 3 s identity at rotation 3, each with complete markers and a separate manifest. Every channel is mixed/changing in either identity rotation; retain bit/channel coverage and software corruption-fixture results. |
| Nominal | At least 10 min long identity, no unexplained loss, duplication, xrun, USB error or interruption. |
| Loaded | At least 15 min long identity with the exact predefined board/host/storage load below. Same zero-error acceptance and complete final validation. |
| Application | Record all 24 channels in an ordinary Linux application at target rate; verify the map using known data. Keep native exact-data recording separate from editor/export representation. |

Extra channel-active epochs and tone/sweep/burst families are deferred unless
an uncovered failure justifies them. The original corruption-fixture suite
still applies; periodic patterns alone cannot establish continuity.

Use an explicitly identified existing mounted host recording volume; record
mount/device identity, filesystem, topology, free space and directory. Require
120% of all planned retained data plus logs/analysis copies. Never select or
format an unknown disk. At 6,912,000 B/s, 10 and 15 minutes contain
4,147,200,000 and 6,220,800,000 payload bytes respectively; include markers
and capture boundary allowances. Use raw PCM, RF64/W64 or proven contiguous
chunks; the loaded file exceeds ordinary RIFF WAV's 32-bit size limit.

Qualify bounded writes/flush completion on that directory, retain actual
write timing and concurrent capture/checking stalls, and fsync completed
recordings before final comparison/checksum and PASS. A successful flush
is not a power-loss durability qualification. Require no storage loss during
the tested load; explicitly leave unmeasured physical-write/2× margin
unqualified. TEST-006/FW-007 retain final external-SATA qualification and the
larger-than-RAM flushed benchmark for the later endurance gate.

### Readiness, supervision, load and error observation

Before hardware execution, freeze exact command argv, native PCM names,
clock/feedback settings, recorder/checker versions, expected counts/durations,
timeouts, selected paths and load/resource caps in the run manifest.
Readiness must observe the actual native capture PCM RUNNING at the correct
format/channel/rate before starting generation; a PID or guessed sleep is
insufficient. The permitted leading interval still applies.

Supervise generator, recorder and checker with retained independent process
identity/exit evidence, live comparison, bounded failure-detection delay,
wall-time limits and cleanup. An independent watchdog/service must mark a
dead/reused worker or expired deadline INTERRUPTED/INCONCLUSIVE, retain failed
cleanup and notify without assistant polling. Neither SIGKILL nor stale
RUNNING may turn an incomplete comparison into PASS. Qualify clean, killed,
stalled, timed-out and cleanup-failure paths with host fixtures first.

For the 15-minute load, prescribe one named, bounded CPU workload on the BBB,
one on the host, ECM/SSH polling cadence and an explicitly capped concurrent
write workload on the selected volume. Record exact commands, process count,
nice/affinity, byte rates, output limits and stop deadline before starting.
Measure board generation separately from host checking (at least 60 s elapsed
after warm-up where practical), including owned copies/conversion and actual
build flags. The diagnostic 2× processing goal is 13.824 MB/s for packed data;
a miss needs an explicit risk disposition with successful sustained target
capture, rather than automatic rejection. Failure to sustain realtime blocks
advancement. Host pipe/QEMU results cannot substitute for BBB measurements.

Retain one-second CPU/RAM/temperature/error summaries, actual ALSA period/ring
parameters and available queue observations; define their sampling bounds.
Observed exhaustion, unbounded growth or undocumented discontinuity fails.
Sampled occupancy cannot prove a continuous minimum or a formal worst-gap
reserve. Record missing/unresolvable observations as INCONCLUSIVE. The formal
2× worst-combined-gap proof is deferred, not claimed by sampled measurements.

Qualify a completion-error observation at u_audio_iso_complete **entry** or an
equivalent point that covers all completions, including early returns and
-ESHUTDOWN. The old pr_debug site skips some of these paths. Quiet logs with
DEBUG/DYNAMIC_DEBUG disabled are insufficient. Prefer existing tracing if
symbol, ABI, field offsets, stream/endpoint attribution and observation-loss
accounting can be validated. A known/synthetic event must exercise the actual
observation path; testing only an offline parser does not qualify a live
counter. Prove monitoring is active using successful-completion liveness as
well as zero unexpected errors. Missing/lost observations block that claim.
Bracket expected disruption windows by event/time; an -ESHUTDOWN inside an
otherwise valid recording is unexpected, regardless of its errno name.
Preserve both board and host errors. A kernel change is a fallback if the
existing mechanism cannot meet these requirements, not a prerequisite by fiat.

### Recovery, decision and deferred integration

Run three cold starts and three USB reconnects. Also run one producer stop,
one host stop and one warm restart. Retain every failed attempt, explicitly
mark each affected recording interrupted, and perform a fresh 60-s identity
capture after **each** recovery. An unexplained startup failure blocks an
unqualified stage PASS; successful retries do not erase it. Restore the known
mono profile and verify recovery at the end.

PASS applies only to this generated USB path when native configuration,
qualified checker, every compared value/count/marker, completed early run
set, visible errors, storage completion, application mapping and recovered
startups meet the early profile. Retain manifests, all exit/status evidence,
native samples/lossless chunks, hashes, packet traces and resource/error logs.
A margin diagnosis or interrupted file receives its own disposition; it is
not relabeled uninterrupted success.

Before an exact ADC recommendation, complete TEST-009's paper interface
review, including the [clock-domain plan](design/architecture.md#adc-clock-to-usb-rate-reconciliation).
The initial proposed scheme uses shared ADC audio clocks and a bounded bridge
controlling the gadget's qualified Playback Pitch; it is not implemented or
measured. Buffering alone cannot reconcile independent average rates.
Defer -100/0/+100-ppm software characterization and formal reserve tests to
bridge/ADC integration, retaining their earlier 10-minute-per-offset proposal
for review against real tolerances. Physical clock/drift/jitter tests require
representative hardware. Keep later 30-minute/one-hour engineering runs,
FW-007 external-SATA preflight and full-device 24-hour/analog/physical timing
acceptance separate and unpassed. Deliberate overload beyond the declared
operating envelope remains a later TEST-010 characterization.

## TEST-009: Board interface, clocks, power and capture DMA

1. Record the exact board identity/revision, schematics, mux table, device
   tree, driver source/config and proposed converter interface. Resolve every
   used pin and shared net; assign one driver per clock/data signal.
2. Calculate serial clocks, timing margins, voltage/startup limits, FIFO/DMA
   layout and available buffers. Review the chosen kernel's CPU and codec
   DAI constraints; CPU-side channel capacity alone is insufficient.
   Define worst-case supply/temperature, clock tolerances, output delay,
   input setup/hold, duty cycle, skew, wiring/load and simultaneous-lane
   switching within component ratings. Patterned USB audio does not measure
   these electrical margins; do not substitute doubled voltage/clock tests.
3. Review paper compatibility before an exact ADC recommendation; this paper
   check does not block the generated USB experiment. With qualified test hardware,
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

For the early USB stage, use TEST-008's three cold starts/three reconnects
plus one source stop, host stop and warm restart. For later integration,
add bounded bridge overload and extend the cases to the physical ADC path.
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
scope, owner and evidence. Check PRD-005's customer, feature mix, price/volume,
complete cost and differentiation against the [product-definition worksheet](research/product-definition.md).
Customer/economics sign-off precedes production analog/PCB commitment; full
release qualification does not precede one experimental ADC bank.
Missing limits, approvals or certification evidence
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
| USB-006 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-007 | [TEST-008](#test-008-usb-path-packet-budget-and-clock-rate-handling), [TEST-006](#test-006-continuous-recording) |
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
| PRD-005 | [TEST-013](#test-013-product-evidence-and-release-gates) |
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

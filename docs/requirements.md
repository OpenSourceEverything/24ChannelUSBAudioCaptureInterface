# Product Requirements

These requirements define the intended product and its staged acceptance.
This is the single requirements document for the product, analog inputs and
development workflow. Numeric analog limits are proposed engineering targets.
Requirements do not certify the proposed processor, ADCs, or software implementation.
The [architecture](design/architecture.md) identifies feasibility constraints.
[Repeatable test procedures](test-procedures.md) define setup, measurements,
pass/fail rules and requirement coverage. A written procedure is not a test result.

## Purpose and boundary

The product receives analog audio, converts it into synchronized digital
samples, and exposes independent recording channels to a Linux USB host.
The first bench milestone starts at a known line source. The proposed product
boundary also includes analog microphones and raw passive guitars through
per-channel MIC/LINE/INSTRUMENT conditioning and an XLR/quarter-inch combo
socket. See the [input requirements](#analog-input-requirements) for source-facing
targets and their status. A preamp/buffer may become a reusable module with
a documented electrical interface; separate repository packaging is deferred
until that interface is defined.

## Functional requirements

| ID | Requirement | Verification |
| --- | --- | --- |
| CAP-001 | The full configuration shall capture 24 independent analog channels simultaneously at 96,000 samples/second/channel with 24 valid sample bits. | Record distinguishable inputs on all channels and inspect rate, format, channel ordering, and sample continuity. [TEST-001](test-procedures.md#test-001-channel-count-and-format), [TEST-006](test-procedures.md#test-006-continuous-recording) |
| CAP-002 | The host shall receive channels separately, without summing, duplication, or an undocumented channel reorder. | Inject identifiable signals into individual inputs and compare the host recording with the documented map. [TEST-001](test-procedures.md#test-001-channel-count-and-format), [TEST-002](test-procedures.md#test-002-crosstalk) |
| CAP-003 | All ADC channels shall share a coherent sampling clock and a documented frame/reset alignment method. | Measure clocks and record a common signal to check fixed channel alignment and drift. [TEST-005](test-procedures.md#test-005-channel-synchronization), [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |
| CAP-004 | ADC resolution, serial slot width, USB subslot width, and host file format shall be documented separately. | Inspect datasheets, hardware configuration, USB descriptors, and recorded samples. [TEST-001](test-procedures.md#test-001-channel-count-and-format) |
| CAP-005 | Buffer overruns, underruns, dropped samples, and device disconnects shall be observable. Capture software shall not silently report uninterrupted success after an error. | Exercise overload and disconnect recovery and inspect counters/logs and recording behavior. [TEST-006](test-procedures.md#test-006-continuous-recording), [TEST-010](test-procedures.md#test-010-errors-interruption-and-recovery) |
| CAP-006 | The reference implementation shall use external audio ADCs feeding BeagleBone McASP with DMA and Linux ALSA. Retaining the BeagleBone at full scale requires demonstrated serial and USB feasibility. | Inspect the signal path and validate sustained capture on the selected board/kernel. [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma), [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling) |

Here, McASP is the processor's multichannel audio serial port; DMA transfers
samples between that peripheral and memory; ALSA is Linux's audio interface.

## USB and recording requirements

| ID | Requirement | Verification |
| --- | --- | --- |
| USB-001 | The primary host interface shall be USB Audio Class 2.0 (UAC2) over a USB 2.0 high-speed device connection. | Inspect descriptors, negotiated speed, and Linux host driver binding. [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-002 | A supported Linux host shall record through its standard USB audio driver without a proprietary host driver. | Enumerate the device and record using ALSA and a recording application. [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-003 | One analog input shall be recordable in Audacity or an equivalent Linux application as the first end-to-end milestone. | Record an externally supplied tone and speech/music where appropriate; verify the file is non-silent and matches the physical input. [TEST-001](test-procedures.md#test-001-channel-count-and-format) |
| USB-004 | Firmware shall advertise only configurations that fit its actual endpoint, controller, FIFO, and clock-handling capabilities. Nominal bus speed alone is insufficient. | Audit packet calculations/descriptors and sustain the advertised stream without loss. [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-005 | The implementation shall manage the rate difference between the audio clock and USB host timing without unbounded buffer growth or hidden sample deletion. | Monitor buffer occupancy and sample continuity during extended capture. [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling), [TEST-006](test-procedures.md#test-006-continuous-recording) |
| USB-006 | Before an analog hardware buying recommendation, the generated 24-channel/96-kHz/24-valid-bit USB path shall preserve every compared sample and channel identity through the host recording. Validate the checker using independently specified reference vectors and deliberate corruption. Explicitly bound startup/shutdown exclusions; counters, a file checksum or tone frequency alone do not establish integrity. | [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling) |
| USB-007 | Characterize throughput, buffer reserve and load limits at the intended USB format against the proposed [stage profile](#generated-usb-stage-test-profile), plus FW-007's storage preflight. Report each boundary separately; no 2× USB capacity or analog-voltage requirement is implied. | [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling), [TEST-006](test-procedures.md#test-006-continuous-recording) |

A generated digital tone can verify the USB/software path. It does not satisfy
USB-003 or prove analog capture.

### Generated USB-stage test profile

The following USB-006/007 thresholds are proposed for G1 peer review. They
are neither measured capacity nor final product guarantees. TEST-008 supplies
the execution and evidence method; changes to targets belong here.

| Check | Proposed engineering threshold |
| --- | --- |
| Format ramp | Known-data runs of at least 60 s each at 1 channel/96 kHz, 8/96 kHz, 24/48 kHz and 24/96 kHz, all with 24 valid bits and three-byte USB subslots. Only the final setting qualifies the target. |
| Pattern bank | Every TEST-008 pattern family at 24/96k for at least 60 s; every compared value correct, with documented bit/channel coverage. |
| Nominal / loaded capture | At least 30 min nominal and 60 min with the predefined concurrent board/host/drive workload; all 24 channels compared throughout. |
| Software rate variation | At least 10 min each at -100/0/+100 ppm using a qualified mechanism; this provisional range must be reviewed against the eventual clock tolerance. |
| Component processing margin | Board pattern generation and host unpack/checking each achieve at least 2× realtime in separate bounded component benchmarks of at least 60 s after warm-up. This excludes USB and disk performance. |
| Buffer reserve | At each critical-path service-gap entry, the relevant queued/free reserve covers at least twice the worst measured combined gap for that path. Record instrumentation bounds and queue direction; sampled occupancy alone is insufficient. |
| Comparison boundaries | Explicit start/end markers, no interior exclusions; proposed maximum unverified startup and shutdown intervals are 2 s each. Timed run durations count only compared data. |
| Recovery | At least three executions per TEST-008 recovery case, each followed by a fresh 60-s identity check; expected disruption is labeled and does not count as continuous operation. |

Load commands/rates, supported clock control, exact pattern definition,
reference vectors and reliable buffer instrumentation are execution
prerequisites, not values to invent during a run. Missing prerequisites block
their subtests. A reviewer may reject or revise these proposals with reasons;
any failure/inconclusive margin result needs a recorded disposition before
advancing. No 24-hour run is required to complete this early USB-only gate;
the full-device 24-hour target remains ADC-007.

## Provisional capture performance targets

ADC-001 through ADC-007 describe the complete input-to-host capture chain,
not an IC purchase specification. They do not mandate a manufacturer, chip
channel count or serializer topology. The 24-channel/24-bit/96-kHz goals trace
to CAP-001; the analog performance, timing and 24-hour limits remain provisional
until their cost, measurement capability and feasibility are reviewed.

Unless stated otherwise, test every channel in LINE mode at 96 kHz, with all
24 channels powered and active, the documented fixed line gain, a 100-Ω
balanced source impedance, and 23 ±5 °C ambient. Measure from the external
analog connector through the final host recording. MIC/INSTRUMENT modes have
their own gain/loading/noise targets below; LINE results do not certify them.

| ID | Provisional target | Repeatable verification |
| --- | --- | --- |
| ADC-001 | Capture 24 independent analog channels simultaneously, preserving their identity and ordering. | [TEST-001](test-procedures.md#test-001-channel-count-and-format) |
| ADC-002 | Capture at 96,000 samples/s/channel with 24 valid sample bits; document serial slots, memory containers, USB subslots and recorded format separately. Sample bits do not imply 24 effective analog bits. | [TEST-001](test-procedures.md#test-001-channel-count-and-format) |
| ADC-003 | At 1 kHz and -1.0 ±0.1 dBFS on each driven LINE input, leakage into every other channel is at most -100 dB relative to the driven channel's fundamental amplitude. Measure the 1-kHz component with effective analysis bandwidth no greater than 10 Hz; terminate unused inputs as specified by TEST-002. | [TEST-002](test-procedures.md#test-002-crosstalk) |
| ADC-004 | Complete LINE-path dynamic range is at least 110 dB(A), using a -60.0 ±0.1-dBFS low-level tone, fundamental removal, 20-Hz–20-kHz measurement bandwidth and A-weighting. | [TEST-003](test-procedures.md#test-003-dynamic-range) |
| ADC-005 | Complete LINE-path THD+N is at most -100 dB relative to a calibrated 1-kHz fundamental at -1.0 ±0.1 dBFS, measured over 20 Hz–20 kHz without A-weighting. | [TEST-004](test-procedures.md#test-004-distortion) |
| ADC-006 | Channels use coherent sampling clocks with deterministic frame alignment. Provisional maximum pairwise timing offset is one sample (10.417 µs at 96 kHz), with zero accumulated relative sample drift or frame slips over 24 hours. Document measurement uncertainty and fixed analog/filter delay. | [TEST-005](test-procedures.md#test-005-channel-synchronization), [TEST-006](test-procedures.md#test-006-continuous-recording) |
| ADC-007 | Sustain simultaneous 24-channel/96-kHz/24-valid-bit recording for 24 hours with zero dropped, duplicated or transport-corrupted sample frames and no reported capture/bridge/USB xruns. Use known signals plus independent sample-integrity checks; counters alone are insufficient. | [TEST-006](test-procedures.md#test-006-continuous-recording) |

Crosstalk is a ratio between channels, expressed in dB. For example, a
-1-dBFS driven tone and -101-dBFS leakage correspond to -100 dB of crosstalk.
Do not substitute a -100-dBFS absolute threshold. Dynamic-range and distortion
measurements require a characterized source/analyzer path with a sufficient
measurement floor; an oscilloscope alone cannot establish these targets.

## Analog input requirements

Status: proposed engineering baseline, researched 2026-11-03. The requested
source coverage is raw guitar, XLR and balanced/unbalanced connections. Numeric
limits below are design targets, not measured performance or release claims.
They guide circuit and ADC selection; revise them explicitly when measurements
or cost justify a change.

### Recommended channel

Use one XLR/6.35-mm combo receptacle and selectable MIC, LINE and INSTRUMENT
modes per channel. Plan this capability for all 24 channels as the working
product scope. One socket accepts one plug and records one mono channel at a
time. A balanced TRS cable uses three contacts for one channel, not stereo.

| Mode | Intended source and connection | Required input circuitry |
| --- | --- | --- |
| MIC | Analog microphone, balanced XLR | Low-noise adjustable-gain preamp, interference rejection and input protection. |
| LINE | External preamp, mixer or other line output; balanced XLR/TRS or unbalanced TS with documented wiring | Balanced receiver/driver, attenuation or gain as needed, filtering and ADC level/bias matching. |
| INSTRUMENT | Raw passive guitar/bass pickup on a TS cable | High-impedance buffer with adjustable gain, followed by ADC level/bias matching. Active instruments/pedals may instead use LINE according to their output level. |

XLR is a connector, not a voltage specification. An XLR line output still
needs LINE mode. Do not infer source type or enable microphone power just
because an XLR plug is present.

The [Neutrik Combo FAQ](https://www.neutrik.us/en-us/neutrik/faq/combo) confirms
that XLR and jack contacts are separate; the connector does not join them
automatically. Keep the paths separate where required for gain and power
control. [NCJ6FI-S](https://www.neutrik.com/en/product/ncj6fi-s) illustrates
a solder-cup combo receptacle, not a selected production part. Exact footprint,
switch contacts, voltage rating and panel mounting require qualification.

### Source-facing targets

Unless stated otherwise, characterize at 96 kHz with the final 24-channel
configuration powered and active. Measure at the input connector, not just
at the converter IC.

| ID | Proposed target | Selection consequence / verification |
| --- | --- | --- |
| IN-001 | Each channel supports the three modes above, selected explicitly. XLR pins 2/3 are positive/negative; pin 1 is shield. Balanced jack tip/ring are positive/negative; sleeve is shield/reference. Document actual chassis/signal-ground connections and unbalanced cable wiring. | Review connector drawing and schematic; test each plug/mode combination. Never sum the two paths or tie separate source outputs together. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-002 | LINE nominal level +4 dBu; supported maximum +24 dBu, differential for a balanced source. Also accept lower-level unbalanced sources within the selected range. | Design the receiver/pad for the external voltage, not the ADC pin voltage. Test balanced and unbalanced operation separately. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-003 | Set nominal LINE conversion full scale at +25 dBu, reserving 1 dB for tolerance. +4 dBu maps to -21 ±0.5 dBFS; +24 dBu shall remain unclipped. | Verify gain and overload across component/supply/temperature tolerances. A digital gain reduction cannot repair analog clipping. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-004 | LINE input impedance nominal 20 kΩ differential, at least 10 kΩ across 20 Hz–20 kHz; document impedance from each leg to reference and in unbalanced mode. | Receiver/pad must not load the source excessively. Measure complex impedance rather than equating it to the chip's input resistance. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-005 | MIC input impedance at least 2 kΩ differential; preamp gain covers nominal 0–60 dB before ADC level matching, with ±1-dB accuracy at named calibrated settings; accept at least 0 dBu at minimum gain without clipping. | Evaluate with a 150-Ω balanced source. Establish gain accuracy, overload at every gain setting and actual ADC drive. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-006 | INSTRUMENT input resistance nominal 1 MΩ, at least 900 kΩ, measured separately from reactive loading; report complex impedance at 1 kHz. Input capacitance target no more than 150 pF excluding the cable; gain covers nominal 0–30 dB before ADC level matching, with ±1-dB accuracy at named calibrated settings; accept a 2-V RMS sine at minimum gain. | Use a low-input-current buffer. Measure loading and transient headroom; a low-impedance line input is not a substitute. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-007 | Frequency response within ±0.5 dB from 20 Hz–20 kHz relative to 1 kHz, in each supported mode. | Measure with documented source impedances: 100 Ω LINE, 150 Ω MIC, 10 kΩ resistive INSTRUMENT. Also characterize a pickup/cable model for guitar tone. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-008 | The complete LINE circuit shall be evaluated against provisional ADC-004/ADC-005, including its receiver, attenuation, driver and power/reference noise. | Budget the receiver, resistors, ADC driver, converter, reference and power noise together. Evaluate at 96 kHz; headline 48-kHz figures alone are insufficient. [TEST-003](test-procedures.md#test-003-dynamic-range), [TEST-004](test-procedures.md#test-004-distortion) |
| IN-009 | MIC equivalent input noise no greater than -125 dBu, unweighted 20 Hz–20 kHz, at 60-dB preamp gain with a 150-Ω source. Publish the source-resistor noise contribution. | Measure complete path noise, refer it back through measured gain, and identify the analyzer/source floor. Do not apply LINE dynamic-range claims to a high-gain microphone mode. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-010 | LINE common-mode rejection at least 60 dB at 50/60 Hz and 40 dB at 20 kHz with a 1-V RMS common-mode signal and matched 100-Ω source legs. Crosstalk uses the provisional ADC-003 target and measurement definition. | Test assembled channels and repeat with source-impedance imbalance. Publish the bandwidth, driven/victim channels and input terminations. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls), [TEST-002](test-procedures.md#test-002-crosstalk) |
| IN-011 | Mode, gain, channel number, signal/clip state and microphone-power state are visible to the user. Mode changes start muted and do not silently resume a different channel/gain. | Bench controls may be jumpers/manual controls initially. Define final controls and switching transients before release. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |

dBu expresses RMS voltage relative to 0.775 V. dBFS expresses level relative
to the digital full-scale sine. A-weighting reduces the contribution of some
frequencies in a noise measurement; weighted and unweighted results are not
interchangeable. Dynamic range describes the span down to the noise floor;
THD+N measures distortion plus noise relative to a test tone.

The +24-dBu range is a proposed compatibility target with 20 dB of peak room
above +4 dBu. It is not mandatory for all audio equipment. As a real-world
reference, [RME's ADI-8 QS manual, section 16.1](https://rme-audio.de/downloads/adi8qs_e.pdf)
specifies +24-dBu sensitivity and 10-kΩ line inputs. Its published performance
does not establish this project's performance.

### Microphone power and faults

Phantom power is a proposed production feature; it stays off in the first
analog prototype. Its implementation adds supply, protection and control work
beyond the combo connector. The requested MIC/LINE/INSTRUMENT coverage remains
product scope; build and characterize one front-end channel before replication.

| ID | Provisional requirement | Verification |
| --- | --- | --- |
| IN-012 | If 48-V phantom power is implemented, it shall be individually enabled, visible to the user and off at boot and on the initial LINE test path. | [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls), [TEST-011](test-procedures.md#test-011-yocto-baseline-access-and-updates) |
| IN-013 | Phantom power shall only reach intended XLR microphone contacts, never jack/guitar contacts. Leaving MIC mode disables/discharges it before reconnection; quantify and validate discharge/mute timing. | [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| IN-014 | Before phantom operation, specify voltage/current limits, matched feed resistors, capacitor ratings, transient/short protection and simultaneous-channel power budget. | [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls), [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |
| IN-015 | Before a production circuit is approved, specify and test operating common-mode/DC limits, external phantom faults, ESD and unpowered-input protection. Audio overload level is distinct from damage tolerance. | [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma), [TEST-013](test-procedures.md#test-013-product-evidence-and-release-gates) |

Do not assume the existing BeagleBone USB supply can power 24 front ends and
microphone loads. [TI's phantom-power application report](https://www.ti.com/lit/an/sboa320a/sboa320a.pdf)
explains the supply function; final limits and protection remain design gates.

MIC distortion versus gain, INSTRUMENT noise/distortion, full common-mode
range, gain-control details and protection limits remain characterization/
design gates. Do not advertise broad "high quality in every mode" claims
from the LINE targets alone. Class A/B/AB describes circuit operation, not a
required quality grade; select topology using the measured limits above.

### Derive the ADC requirements

```text
source type + source impedance + loudest input + noise target
  -> connector / mode / gain or attenuation / input protection
  -> ADC drive voltage, common-mode bias and filter
  -> ADC performance, clock/serial interface and power requirements
```

An external preamp can use the LINE connector contract. An internal reusable
MIC/INSTRUMENT module should feed a documented ADC-ready interface; do not
force it to generate a +24-dBu output merely to attenuate that signal again.
Freeze its voltage, bias, load, power, control and grounding contract after
choosing the converter circuit, before creating a dependency/submodule.

The [ADC selection research](research/adc-selection.md) maps these targets
to converter candidates and separates the inexpensive first test from the
production converter.

### Immediate bench milestone

Keep the first test in LINE mode: one assembled, documented ADC board and a
known low-level tone. Start around 0.5 V peak-to-peak at 1 kHz, measured with
the oscilloscope at the qualified board input. Its schematic must permit this
source/coupling arrangement. This does not test the +24-dBu receiver, a raw
guitar or a microphone preamp. The existing staged USB-tone/analog acceptance
sequence still applies; no preamp purchase is necessary for this milestone.

## Analog and electrical requirements

| ID | Requirement | Verification |
| --- | --- | --- |
| ANA-001 | Every analog input shall have a documented connector, pinout, signal type, impedance, maximum level, common-mode/bias requirement, and ground reference. | Review the input specification and measure the assembled circuit. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| ANA-002 | Input conditioning shall supply the coupling, bias, attenuation, filtering, and protection required by the selected ADC and source. | Review the ADC reference circuit and verify levels and clipping on hardware. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls), [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |
| ANA-003 | Mic, line, instrument, and digital sources shall not be treated as electrically interchangeable. Phantom power shall not be present on the initial line-input path. | Inspect source/interface specifications and measure input voltages. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| ANA-004 | The production input design shall provide MIC, LINE and INSTRUMENT modes for the requested microphone, balanced/unbalanced line and raw-guitar coverage. Use the proposed [input targets](#analog-input-requirements) to drive analog circuit and ADC selection. | Review per-mode impedance, gain, headroom, connector wiring and measured performance; distinguish proposed limits from demonstrated results. [TEST-007](test-procedures.md#test-007-input-compatibility-and-front-end-controls) |
| ELE-001 | Digital connections shall respect BeagleBone and ADC I/O voltage limits, including startup and unpowered conditions. | Review rail sequencing and measure interface levels. [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |
| ELE-002 | The design shall document power consumption, supply rails, grounding, decoupling, and the supported cable/power arrangement. | Measure the prototype and review the schematic and BOM. [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |
| ELE-003 | Shared header functions, including HDMI/eMMC conflicts, shall be resolved for the exact board and device-tree configuration before wiring McASP. | Compare schematic, pinmux, active drivers, and measured pins. [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |
| ELE-004 | Development hardware shall expose labeled, probe-accessible power rails, ground, analog input, serial data, bit clock, frame sync and required master-clock signals through test points or documented headers. | Verify physical probe clearance, signal identity and accessible ground references on the prototype. [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma) |

The first ADC shall be an assembled breakout or evaluation board with its
required support circuitry and a documented integration interface. A bare
converter IC alone does not meet the initial bench requirement. Keep serial
clock wiring short and provide nearby ground access for probing.

## Staged acceptance

Initial engineering acceptance targets below are requirements for development;
they are not existing test results or final product performance claims.

### Current review gate: G1

Before further BeagleBone configuration/bench experiments or an equipment
buying recommendation, obtain an external review of the current USB-stage
requirements and TEST-008, TEST-010 and TEST-009's paper-interface portion.
Use the [focused review addendum](reviews/usb-stage-review.md) with this file
and the single test-procedures document. Record the reviewed revisions,
findings, resolutions and the owner's acceptance of the review disposition.
Unresolved blocking findings keep G1 on HOLD. Preparing documents and host-only
test fixtures does not close this gate or authorize a purchase.

After G1 closes, complete the generated-channel tests below. Their USB-stage
PASS and the paper ADC/interface review permit a concrete bench-equipment
recommendation; purchase remains a separate owner decision. A review is not
a substitute for those physical tests. Any failed/inconclusive margin target
needs an explicit review disposition before advancing.

### Execution sequence after review

1. USB path: a generated tone reaches a Linux recorder through the BeagleBone
   USB audio device. A 48-kHz/16-bit bootstrap is permitted.
2. Architecture gate before purchase: document exact board pins, shared-pin
   conflicts, clock ownership/timing budget, serial format, pinned-kernel
   channel/DMA constraints and ADC electrical compatibility. After the first
   USB tone, test a generated 24-channel USB stream at the target format,
   including the checked patterns, staged runs and resource margins in
   TEST-008. All 24 generated channels must be active together. This stage
   does not require buying 24 analog front ends or precision audio instruments.
   Source review is not sustained-capture validation. Prefer a representative
   multichannel converter bank when qualified test hardware is available;
   a stereo converter is only an optional diagnostic purchase.
3. One analog input: external ADC capture reaches the host application. Progress
   from a supported bootstrap mode to 96 kHz with 24 valid bits. A stereo ADC
   may transport an unused second channel, with its termination documented.
4. One-channel endurance: record for at least 30 minutes at the target format
   with no reported capture/bridge/USB overruns or underruns and no detected
   sample discontinuities. Document the clock and continuity measurement method.
5. Representative multichannel bank: satisfy format, mapping, synchronization
   and endurance checks with a topology that can scale to the full product.
   Eight channels is a useful experiment, not a required chip package size.
6. Full product: first run a one-hour engineering check, then the provisional
   24-hour ADC-007 endurance procedure at 96 kHz/24 valid bits. Measure and
   publish channel alignment, sample-integrity coverage and uncertainty.
   The one-hour check does not pass the 24-hour target.

Record the board revision, ADC/module revision, firmware/kernel, host OS,
application, negotiated formats, duration, errors, and signal evidence with
each result. Measure latency, noise, clipping, distortion, and crosstalk before
setting saleable product limits. The [analog input document](#analog-input-requirements)
sets proposed numeric design targets; those are not verified product claims.
No numeric end-to-end latency promise is established. A 24-bit sample format
does not imply 24 effective bits of analog performance.

## Development turnaround

These are initial acceptance targets, not measured performance claims. Measure them
after the first source-built image boots and network access works.

| Scenario | Goal | Measurement boundary |
| --- | --- | --- |
| One menu-message edit | At most 60 seconds | Start deployment through observing the changed menu on the board; no image write or reboot. |
| Small application edit with dependencies and SDK already present | At most 120 seconds | Start incremental compilation through observing the updated application on the board; no complete image rebuild. |
| Incremental driver/kernel change | Establish a measured baseline before setting a limit | Record build, transfer and restart/reboot separately. |
| Full image/SDK build | Background operation with visible live/error status | Record elapsed time, changed baseline, cache reuse and host resources. |

For each run record the source and baseline commits, host CPU/RAM/storage,
cold or warm cache, exact command, elapsed build/transfer/restart time and
seconds the board or recording was unavailable. Repeat a representative warm
edit to distinguish a slow first setup from the normal development loop.

The acceptance check must exercise the real board. An empty compiler benchmark
or a successful file upload alone does not prove the updated program runs.

## Productization

- FW-001: Maintain a pinned Yocto source baseline and product layer that builds
  the kernel, bootloader and root filesystem for the selected BeagleBone.
  Verification: [TEST-011](test-procedures.md#test-011-yocto-baseline-access-and-updates).

- FW-002: Provide documented UART login, key-based SSH access and a simple
  board menu for status and the USB test tone. Keep private keys and local
  provisioning configuration out of the public repository.
  Verification: [TEST-011](test-procedures.md#test-011-yocto-baseline-access-and-updates).

- FW-003: Validate board boot, login and a board-generated USB tone, then
  close review gate G1 and validate the generated full-channel USB path and
  paper pin/clock/driver/exact-ADC interface before recommending an analog
  hardware purchase. Prove sustained capture
  with representative test hardware afterward; source review is not a pass.
  Retain source/build/kernel evidence separately from physical observations.
  Verification: [TEST-008](test-procedures.md#test-008-usb-path-packet-budget-and-clock-rate-handling), [TEST-009](test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma).

- FW-004: Provide a development workflow that writes the complete SD image
  initially, then deploys ordinary application changes over SSH with the card
  left in the board. Document package/dependency updates, reboot requirements
  and recovery separately. Routine application work shall not require reflashing.
  Verification: [TEST-011](test-procedures.md#test-011-yocto-baseline-access-and-updates), [TEST-012](test-procedures.md#test-012-development-turnaround-and-build-independence).

- FW-005: Ordinary application edits shall have a documented incremental
  compile/deploy/test path independent of a complete image or SDK rebuild.
  Measure edit-to-result time and recording/board downtime separately, using
  the [development turnaround targets](#development-turnaround).
  Verification: [TEST-012](test-procedures.md#test-012-development-turnaround-and-build-independence).

- FW-006: Preserve reusable downloads, compiled-task cache and matching SDKs.
  Full platform builds shall run independently of the last working board
  system and report live completion/failure state. Support a separate build
  host through pinned sources/configuration and versioned artifacts.
  Verification: [TEST-012](test-procedures.md#test-012-development-turnaround-and-build-independence).

- FW-007: The reference endurance setup shall record onto an external SATA
  drive attached to the Linux recording host. Identify its actual connection,
  filesystem and free space. Initial preflight targets are free space at least
  120% of calculated payload and sustained flushed write throughput at least
  twice the stored audio rate under concurrent capture/checking. Actual
  uninterrupted recording remains the acceptance evidence; SATA is not a
  new interface requirement on the BeagleBone.
  Verification: [TEST-006](test-procedures.md#test-006-continuous-recording).

- FW-008: Initial card installation shall reuse the completed image and run
  writing, flushing and read-back verification without assistant polling.
  Preserve progress, logs and a terminal result; notify the desktop when
  available. Require an explicitly selected card, bind its identity, reject
  write protection and report interruption/failure. READY requires a complete
  matching image checksum; routine application deployment still avoids flashing.
  Verification: [TEST-015](test-procedures.md#test-015-unattended-card-installation).

- PRD-001: Maintain reproducible hardware sources, firmware configuration,
  build/install instructions, schematics, connector definitions, and a BOM
  with exact approved manufacturer parts or module revisions.
  Verification: [TEST-013](test-procedures.md#test-013-product-evidence-and-release-gates).

- PRD-002: Document recovery from interrupted recording, USB reconnect, and
  restart without leaving the device in an unexplained state.
  Verification: [TEST-010](test-procedures.md#test-010-errors-interruption-and-recovery).

- PRD-003: Record measured power, thermal behavior, audio performance, and
  endurance before advertising the corresponding product capabilities.
  Verification: [TEST-013](test-procedures.md#test-013-product-evidence-and-release-gates).

- PRD-004: Establish firmware/hardware licensing, USB identification rights,
  manufacturing tests, enclosure/connector requirements, and applicable market
  compliance requirements before product release. No certification or license
  choice is implied by repository visibility.
  Verification: [TEST-013](test-procedures.md#test-013-product-evidence-and-release-gates).

## Compatibility stretch goal

- WIN-001: Investigate Windows 7 operation after the Linux path works, without
  changing the primary architecture or reducing its 24-channel target.
  Verification: [TEST-014](test-procedures.md#test-014-windows-7-stretch-investigation).

- WIN-002: Treat Windows 7 UAC2 driver availability, redistribution/licensing,
  signing, host architecture, and recording-application support as separate
  qualification requirements. Do not promise driverless UAC2 on Windows 7.
  Verification: [TEST-014](test-procedures.md#test-014-windows-7-stretch-investigation).

- WIN-003: A reduced UAC1 diagnostic mode, if later justified, shall be clearly
  distinguished from full-product compatibility and shall not gate Linux work.
  Verification: [TEST-014](test-procedures.md#test-014-windows-7-stretch-investigation).

Microsoft's in-box UAC2 driver starts with Windows 10 version 1703; Windows 7
therefore needs a separately established solution. See
[Microsoft's UAC2 driver documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/usb-2-0-audio-drivers).

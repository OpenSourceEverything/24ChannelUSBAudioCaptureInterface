# External review addendum: generated 24-channel USB stage

Review package: G1 draft A, 2026-11-04. Review status: **HOLD — awaiting
external findings and owner disposition**. This addendum scopes the review;
it adds no requirements or competing test procedures.

Supply the complete text of these two files with this addendum:

- [docs/requirements.md](../requirements.md): the single requirements document.
- [docs/test-procedures.md](../test-procedures.md): the single procedures document.

The review must work from those supplied texts without repository access.
The source findings below are review inputs, not independently verified
hardware results. Request missing evidence rather than assuming a pass.

## Request to the reviewer

Review whether the proposed **next USB-only engineering stage** is sufficient,
repeatable and proportionate before changing the BeagleBone again or choosing
analog test equipment. Challenge unsupported assumptions and unnecessary work.
Do not review the entire finished product as though all its future tests must
pass before the next experiment.

Focus on USB-001/002/004–007, CAP-002/004/005, FW-003/007; the generated
USB-stage profile and G1 staged-acceptance gate; TEST-008; TEST-010 recovery;
and TEST-009's paper pin/clock/interface prerequisites for buying advice.
Use CAP-001/003/006 and ADC-001/002/006/007 to check that this stage does not
make unsupported claims about analog conversion, clocks or 24-hour operation.
Other analog, microphone-power, product-release and Windows 7 requirements
are context only unless they directly prevent a suitable first ADC experiment.

## Observed baseline and limits

- Intended product: 24 independent analog inputs, 24 valid bits, 96 kHz,
  USB Audio Class 2.0 to Linux. MIC/LINE/INSTRUMENT are eventual input modes.
- Reported bench evidence: source-built Yocto/Poky 5.0.21 with Linux 6.6.21
  boots a physical BeagleBone Black from SD; UART, key-based USB SSH and the
  board menu work. USB networking and audio share the composite connection.
- Actual live Audacity 3.7.9 recording: 568,560 mono frames at 48 kHz,
  11.845 s; native S16_LE observed; exported WAV contains a generated 1-kHz
  tone. This establishes a small live USB path, not 24-channel performance.
- Initial boot previously enumerated but produced silence and stalled USB
  networking; rebinding the USB controller restored transfers with DMA still
  enabled. A later warm reboot worked without that intervention. Root cause
  and repeated cold-start reliability are unqualified.
- Stopping host recording before the board tone producer was followed by a
  producer I/O error. The future tests must distinguish expected shutdown
  from faults during compared recording and retain both outcomes.
- No external ADC, analog capture, McASP receive configuration, full-channel
  generator/checker, rate-variation test or long-run integrity PASS exists.
  Pattern algorithms, independent vectors, load profiles and instrumentation
  described in TEST-008 are planned prerequisites, not implemented evidence.
- Available: the board, Linux computer, 16-GB boot SD, UART/USB cables,
  soldering bench and oscilloscope. No ADC board or precision audio analyzer
  is identified. A future external SATA recording volume is not yet identified.

## Technical assumptions to challenge

At 24 x 96,000, three-byte PCM requires 6.912 MB/s. With 125-us service
intervals, 12 frames need 864 bytes and 13 need 936 bytes. Four-byte USB
subslots need 1152 bytes for 12 frames; the inspected pinned gadget driver
caps the endpoint at 1024 bytes. Verify descriptors, extra-frame reserve,
controller behavior and the actual implementation. USB's headline bandwidth
alone does not close the gate. The cap is not asserted for all USB endpoints.

Pinned source: Yocto kernel commit
06644f0d7193d7ec39d7fe41939a21953e7a0c65,
drivers/usb/gadget/function/f_uac2.c (get_max_bw_for_bint and
set_ep_max_packet_size_bint) and u_audio.c (packet accumulation).
The [kernel UAC2 configuration documentation](https://www.kernel.org/doc/html/latest/usb/gadget-testing.html#uac2-function)
is an interface reference, not proof of this build or physical throughput.

Preliminary McASP source/pin review suggests three receive lanes, each with
eight 32-bit slots, at 24.576-MHz BCLK. Candidate lanes P9.30/P9.41/P9.28
include a shared-pad issue and HDMI ownership conflict. Codec/machine mapping,
clock/reset alignment and sustained receive DMA are unproven. This is a
future integration risk; generated USB patterns bypass that entire path.

“2x” is proposed only for separately measured generator/checker throughput,
flushed storage throughput and defined buffer reserve. It is not a demand
for 48 inputs, 192-kHz operation, doubled voltage or twice the USB payload.
Data values do not increase constant-rate PCM traffic. Alternating sample
bits are useful data coverage, not proof of worst-case USB electrical signaling.

## Questions the review must resolve

1. Is exercising all 24 generated channels before buying an ADC the right
   stopping point? Which proposed checks are essential before buying advice,
   and which can wait for a representative converter bank or full product?
2. Can the proposed patterns and independent expected-data checker expose
   every listed drop, duplicate, channel-map, bit/byte, reset/wrap and chunk
   fault? Identify false-pass paths, including common bugs in generator and
   checker, marker ambiguity and unverified startup/shutdown exclusions.
3. Are the proposed 60-s pattern/ramp tests, 30-min nominal, 60-min loaded,
   rate offsets, recovery repetitions and 2x margins justified for this stage?
   Supply concrete replacements where they are excessive or insufficient.
4. Are clock-variation and buffer-reserve checks observable and implementable
   on this kernel? State where simulation ends and physical ADC clock testing
   must begin. Check packet reserve against the full proposed rate range.
5. Are load, storage and error-reporting definitions enough to prevent a
   misleading pass? Name execution prerequisites still missing; distinguish
   fatal planning defects from details to freeze before the relevant run.
6. Does the stage meaningfully reduce BeagleBone feasibility risk without
   pretending to validate McASP/DMA or analog signal integrity? What exact
   pin/clock/logic/module evidence must precede a bench-hardware recommendation?

## Required response and gate decision

Return a concise engineering review with:

- Verdict: READY FOR THE USB EXPERIMENTS, REVISE BEFORE EXPERIMENTS, or
  INSUFFICIENT EVIDENCE. This is a plan review, never a hardware PASS.
- Findings ranked blocking / major / minor; each names the requirement/test
  section, a concrete failure or unnecessary cost, and the smallest correction.
- A minimum sufficient pre-purchase test set, exact acceptance criteria and
  explicitly deferred physical/analog/full-product tests.
- Equipment needed now versus after USB qualification. Do not select an exact
  ADC from headline specifications or approve an order without interface proof.
- Sources for technical objections, and a clear distinction between reported
  observations, calculations, source review and assumptions.

No further board experiment or buying recommendation proceeds while G1 is
open. After findings are resolved and the owner accepts the disposition,
execute the agreed generated USB tests and paper interface review. Only their
qualified results support a concrete equipment recommendation; purchasing
still requires the owner's separate decision. Keep all source changes local
unless the owner authorizes a push.

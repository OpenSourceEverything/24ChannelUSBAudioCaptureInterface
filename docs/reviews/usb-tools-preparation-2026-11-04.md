# USB-stage preparation: software results and next review

Date: 2026-11-04. Status: **software ready for review; G1 remains HOLD**.
This is an implementation/status supplement to G1 draft A, not a returned
external review, owner disposition or hardware PASS. The owner authorized
committing/pushing the prepared work and continuing host preparation.

## Recommendation

Keep all 24 generated channels at 96 kHz/S24_3LE as the next transport goal.
Finish external plan review before another BBB experiment or an ADC/equipment
recommendation. Generated channels bypass ADCs, McASP and the analog inputs;
24 physical analog inputs are a later qualification stage.

After accepted review, begin with the agreed short native-format identity
trial, then the agreed pattern, duration/load and startup/recovery checks.
Use a smaller configuration to diagnose a failure. Exact data comparison and
repeatable startup reduce the relevant uncertainty more directly than adding
arbitrary extreme waveforms. Measure 2x reserve at named components; there is
no absolute worst-case waveform or 2x USB-payload proof in this preparation.

## What is complete

- [Contract v1](../design/usb-test-pattern.md): packed 24-bit PCM, 64-bit frame
  identity, seeded start/end markers, all-channel role rotation and four
  exact-code patterns: identity, edges, walking and alternating.
- [Host tools](../../tools/usb_integrity/README.md): independently implemented
  C generator/checker, a third Python reference, literal vectors, deliberate
  corruption fixtures and bounded host commands with retained results.
- Native qualification: 24 USB-tool test methods pass, including all 576
  channel/bit flips, sample/frame loss and duplication, channel swap/duplicate,
  endian/byte shifts, stuck bits, zero fill, truncation, marker violations,
  reset/wrap and 64-KiB I/O-boundary damage. The whole project has 59 passing
  host test methods. An intact reference passes; each specified corruption
  fixture fails. This is tested coverage, not a proof of every possible fault.
- Host pipe observation: 5,760,000 data frames / 414,720,000 compared bytes,
  zero mismatches, 2.0544 seconds elapsed, about 29.21x real time. This is
  60 seconds of audio data processed unpaced, not a 60-second wall-time test.
  It combines generator and checker on this host, excluding USB and disk.
  It does not pass the separate component-margin requirement or establish
  BBB scheduling headroom.
- ARM preparation: both executables compile with cached Yocto GCC 13.5.0,
  strict warnings and Cortex-A8/NEON/hard-float flags. ELF inspection confirms
  ARMv7 hard-float and the matching cached runtime loader/libc. All 15 native
  detector test methods also pass under host QEMU ARM user emulation
  (45.850 seconds). This tests ARM sample logic; it exercises no BBB hardware.
- [Task 003](../tasks/003-board-preparation.md) records the staged manifest,
  native ALSA command templates, format/descriptor observations, buffer limits
  and return to the existing mono profile. No template has been executed on
  the board. No base-image build or SD write was needed.

Sanitized counts, hashes and build/result provenance are in
[the evidence summary](usb-tools-evidence-2026-11-04.json). Raw run reports,
logs and binaries remain in ignored local output. No secret, local account
path or recording is required to read this review.

## Findings still requiring disposition or implementation

1. **USB error observation is unresolved.** Pinned u_audio.c reports nonzero
   isochronous completion status through pr_debug. The cached built kernel
   disables CONFIG_DYNAMIC_DEBUG and CONFIG_DYNAMIC_DEBUG_CORE. A quiet log
   cannot establish zero completion errors, and a runtime dynamic-debug
   selector cannot enable a site omitted by that configuration. Kprobes and
   Kprobe events are enabled; a narrow counter needs symbol/ABI/field-offset
   qualification and evidence that observations are not lost. If unavailable,
   review a minimal counter/config change and separate kernel build. Exact
   PCM matches and lower-level error counts remain separate evidence.
2. **Real-time deadlines remain unmeasured.** The pinned gadget ring is at
   most 65,536 bytes, about 9.481 ms at target payload. Its maximum 4096-byte
   period fits only 56 whole frames / 0.583 ms. Actual ALSA negotiation may
   be smaller. Average host throughput does not prove these deadlines on BBB.
3. **The capture runner is still a task 004 prerequisite.** Add an actual PCM
   readiness barrier, live comparison and notification interval, independent
   supervision, timeout/cleanup and killed-worker tests before unattended
   hardware runs. The present host runner is synchronous; after SIGKILL it
   can leave RUNNING, which must never be interpreted as PASS.
4. **The full waveform bank is unfinished.** Channel-active marker epochs
   and distinct per-channel tone/sweep/marked-burst vectors remain to be
   implemented and independently qualified. Four exact-code tools do not
   close the whole TEST-008 pattern bank or application proof.
5. **Early-gate scope proposals remain proposals.** Recommend deferring final
   external-SATA qualification and formal 2x worst-gap reserve/clock-offset
   characterization from the first experimental ADC buying decision, while
   preserving their later acceptance. The current requirements/procedures
   still require them. No implicit waiver has been made. Freeze actual
   bounded load commands, error observations and recording volume before
   their applicable tests; no unidentified disk has been selected.
6. **Startup repeatability deserves direct testing.** Propose three cold
   starts and three reconnects, each followed by a fresh 60-second target
   identity run, retaining failures and recovery logs. This responds to the
   earlier silence/network-stall observation. It is a plan proposal, not
   reliability evidence or permission to alter the existing thresholds.

Source findings refer to Linux 6.6.21 kernel commit
06644f0d7193d7ec39d7fe41939a21953e7a0c65, u_audio.c buffer constants and
u_audio_iso_complete, ARM PAGE_SHIFT=12, and the retained cached build config.
Those source/configuration observations do not verify the live board state.

## Files to print or share

Supply the complete text of:

1. [docs/requirements.md](../requirements.md): one requirements file.
2. [docs/test-procedures.md](../test-procedures.md): one procedures file.
3. [G1 draft A addendum](usb-stage-review.md): the original focused review
   request and baseline. Its implementation status is historical; the
   software results above supersede only those status statements.
4. This preparation supplement. For code-level review, additionally supply
   the linked pattern contract, task 003 and tools/tests.

The original three G1 draft A files are unchanged byte-for-byte from their
review snapshot at product commit 7c11cc2. No requirement, test limit or
gate was relaxed to make these software results pass.

## Focused reviewer prompt

Review only the proposed next generated-USB stage and its prerequisites for
one representative ADC/equipment recommendation. Use the supplied requirements,
procedures, G1 draft A and this newer implementation supplement. Review the
contract/code if supplied; otherwise identify what source evidence you lack.

Return READY FOR EXPERIMENTS, REVISE BEFORE EXPERIMENTS or INSUFFICIENT
EVIDENCE, with blocking/major/minor findings. For each, name the relevant
requirement/test, concrete failure mode and smallest correction. Specify the
minimum sufficient test set, measurable acceptance, prerequisites and explicitly
deferred work. Resolve whether final SATA, formal timing reserve and clock
simulation belong before the first experimental ADC buying recommendation.
Challenge checker false passes, marker/exclusion assumptions, error
observability, startup/recovery and the unfinished live-checker/waveform work.
Distinguish source calculations, host software tests, emulation and physical
measurements. Do not grant a hardware PASS, choose an exact ADC without
pin/voltage/clock/driver evidence, or authorize an order.

## Next checkpoint

Record external findings and the owner's accepted disposition in
[task 004](../tasks/004-usb-trials.md). Complete its remaining orchestration
and error-observation work, then execute only the accepted plan. Task 005
remains the separate exact-interface and equipment recommendation checkpoint.
No new board access/change, analog experiment, supplier contact or purchase
occurred during this preparation.

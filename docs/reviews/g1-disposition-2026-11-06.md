# G1 external review: scrutiny and implemented disposition

Date: 2026-11-06. Reviewed baseline: 6305834. Authoritative documents are now
**G1-B**. Overall: **agree with REVISE BEFORE EXPERIMENTS; G1 remains HOLD for
execution prerequisites**. No physical USB/ADC result or purchase approval.

The owner supplied the review and directed scrutiny and implementation of
agreed findings. This authorizes the plan edits below without another approval
request. The review itself supplies no operating/purchase authority. Reviewer
identity/credentials and independent reproduction were not supplied; no
certification or independently reproduced tool result is inferred.

Original received text is retained locally, unchanged, with its SHA-256 in
the [receipt/evidence record](g1-evidence-2026-11-06.json). The November 6
Desktop packet and November 4 evidence remain historical snapshots; current
requirements/procedures supersede their proposed early thresholds.

## Finding-by-finding disposition

| Finding | Assessment | Implemented decision / remaining evidence |
| --- | --- | --- |
| B1 packet capacity | AGREE, with reserve qualification | Require high speed, bInterval=1, native three-byte subslots and actual endpoint/packet evidence. Default fb_max=5 gives 936 bytes; recompute any changed setting. Nominal traffic need not emit a 13-frame packet. Reject clamp warnings, wrong-interval/format and capacity shortfall. Actual descriptors/traces: NOT_RUN. |
| B2 error observability | AGREE; strengthen coverage | Observe completion entry/equivalent, including early-return and -ESHUTDOWN cases; classify expected disruptions by the window, not by errno alone. Require liveness, endpoint attribution, a known event through the actual observation path and loss accounting. Quiet logs or parser-only fixtures cannot qualify it. Live instrumentation remains unqualified. |
| B3 runner | AGREE; host lifecycle correction implemented | Host jobs now have a separate worker/session and independent watchdog, PID/start-time/boot identity, wall-time bound and atomic interruption winning over late PASS. SIGKILL/timeout/cleanup fixtures are tested. Native PCM readiness, live recording orchestration/checking, remote-process containment and desktop notification remain capture-runner work; B3 is not declared fully closed. |
| B4 paper McASP/ADC feasibility | AGREE | Exact board/pins/shared nets/HDMI, three RX lanes, clocks/reset, voltage, DAI/DMA/channel map and bridge plan are mandatory before an exact ADC recommendation. They do not block generated USB diagnosis. Existing paper candidates remain unqualified. |
| M1 all-channel analog scope | AGREE with cost/demand warning; no automatic scope reduction | Preserve the requested all-24-channel provisional modes. Add PRD-005, a product-definition/economics worksheet and a pre-production analog/PCB gate. Buyer, price, volume and complete cost remain UNKNOWN. Correct comparator interpretation below. |
| M2 early qualification | AGREE as an engineering judgment, not a proven optimal duration | Adopt 10-min nominal/15-min defined-load runs and identified existing host storage. Defer final SATA/2× physical-write, formal reserve and clock-offset work to their named later gates. Zero data loss and visible errors stay mandatory. Longer tests may be warranted by actual faults. |
| M3 clocks | AGREE | Add a concrete paper proposal: coherent shared ADC audio clock domain, bounded queues and qualified gadget Playback Pitch control for USB pacing. It is not an implemented bridge; real module clock/pin/driver and closed-loop stability evidence remain required. |
| M4 processing margin | AGREE, qualified | Measure BBB generation and host checking separately, actual buffers and sustained loaded behavior. A 2× miss receives a risk disposition rather than automatic rejection. Failure to sustain realtime, exhaustion or hidden corruption still blocks advancement. |
| M5 startup | AGREE; stronger failure rule | Three cold starts and three reconnects, every attempt retained; any unexplained startup failure prevents an unqualified stage PASS. One successful retry cannot erase a failure. |
| N1 intermediate formats | AGREE | Diagnostic only when target format fails; no mandatory full format ramp. |
| N2 extra waveforms | AGREE with explicit coverage replacement | Keep four implemented patterns. Use a 60-s identity plus a 60-s coverage bank: edges/walking/alternating 19 s each, identity rotation 3 for 3 s. The extra rotation makes every metadata channel carry changing mixed data in another run. Defer extra sweep/burst/channel-marker work unless a named uncovered fault requires it. |
| N3 two-second boundaries | AGREE | Retain exact markers/counts and <=2 s per end; no interior exclusion or silent resynchronization. |
| N4 controlled stops | AGREE | One producer stop, host stop and warm restart each for this early gate; each recovery gets a fresh 60-s identity run. Full integration/overload tests remain later. |
| N5 production qualification | AGREE | PRD-001–004 release/manufacturing work is not a first experimental ADC gate. PRD-005's customer/economics decision precedes expensive production analog/PCB work. |

## Qualifications and disagreements

1. **936 bytes is conditional, not a universal reserve.** In the pinned
   source, asynchronous playback sizing uses the highest advertised sample
   rate, actual fb_max and interval. At the default 5, 96000 x 1.005 / 8000
   rounds up to 13 frames, or 936 bytes. Larger headroom can require more.
   Source/descriptor reserve is distinct from observing an extra frame on a
   short nominal trace. Inspect per-iso-packet lengths, not just URB totals.
2. **A quiet or selective counter can falsely pass.** The existing pr_debug
   site is after ep_enabled/-ESHUTDOWN returns. Counting only that site misses
   paths. Count at entry/equivalent and retain expected-stop windows explicitly;
   a shutdown event during a claimed continuous window is still a fault.
3. **A useful comparison is not a direct equivalent.** The Scarlett 18i20
   headline includes digital expansion and rate-dependent ADAT capacity; its
   eight mic/line inputs and two instrument inputs are a shared analog bank.
   HARMAN documents Ui24R DAW operation at 48 kHz. Neither headline validates
   a 24-local-analog/96-kHz product or proves buyers want fewer modes.
   [Primary-source details and limits](../research/product-definition.md#comparator-corrections).
4. **Shorter tests do not establish reliability.** Accept 10/15 minutes as
   proportionate risk reduction for one experimental ADC decision, not as a
   statistical reliability guarantee or a replacement for later endurance.
5. **The source of this text is an evidence limit.** Agree with the critique
   that code and raw results were absent from the original four-document
   packet. Code/reference tests can now accompany the disposition. Separate
   implementations and fault fixtures reduce common errors; no independent
   software certification is claimed.

## Implementation and stage boundaries

- Updated the single requirements/procedures files together: native profile,
  10/15-min acceptance, 60-s coverage bank, existing storage, recovery matrix,
  clock/error prerequisites and explicitly deferred later work.
- Added the clock-domain proposal and product-definition/PRD-005 gate.
- Corrected host job abandonment; clean and killed-worker evidence remains
  software-only. Source/data contracts are unchanged.
- Split remaining work into capture orchestration, live instrumentation and
  commercial definition checkpoints under [docs/tasks](../tasks/README.md).

**G1 is not waiting for the owner to approve these same edits again.** It
remains HOLD until capture/readiness/error-observation/workload prerequisites
are actually qualified and their exact evidence/revisions recorded. That
bounded readiness work may inspect the board and exercise the existing mono
setup under a recorded qualification/recovery protocol. Full target-format
acceptance stays blocked until it succeeds. Readiness qualification is not a
claim that the target-format experiment has passed.
No board configuration/access, ADC choice, supplier message or purchase was
performed while implementing this disposition.

After readiness: run the revised USB stage; record every failure; complete the
paper exact-module interface gate; then prepare one experimental ADC
recommendation. Customer/economics definition can proceed in parallel before
production analog/PCB commitment. Purchasing remains separate.

## Technical sources

- Actual pinned kernel 06644f0d7193d7ec39d7fe41939a21953e7a0c65:
  f_uac2.c get_max_bw_for_bint/set_ep_max_packet_size_bint; u_audio.c
  u_audio_iso_complete/u_audio_pitch_info/u_audio_pitch_put; u_audio.h
  FBACK_FAST_MAX. Local source is authoritative for this build; live behavior
  remains unmeasured. Upstream comparison:
  [f_uac2.c v6.6.21](https://github.com/gregkh/linux/blob/v6.6.21/drivers/usb/gadget/function/f_uac2.c),
  [u_audio.c v6.6.21](https://github.com/gregkh/linux/blob/v6.6.21/drivers/usb/gadget/function/u_audio.c).
- [BeagleBoard cape interface](https://docs.beagle.cc/boards/capes/cape-interface-spec.html)
  and the [existing pinned pin/driver audit](../research/beaglebone-multichannel-feasibility.md).
  A pin-function listing is not a completed board-revision/net/clock review.

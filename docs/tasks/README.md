# Engineering checkpoints

This directory tracks bounded work and its evidence. Product limits remain
in [requirements](../requirements.md); execution methods remain in
[test procedures](../test-procedures.md). A completed software task is not a
hardware PASS or acceptance of external review gate G1.

| Checkpoint | State | Exit evidence / next dependency |
| --- | --- | --- |
| [001: Pattern contract](001-pattern-contract.md) | COMPLETE_SOFTWARE | Frozen packed-PCM pattern, markers, long frame identity and independent byte vectors. |
| [002: Host tools](002-host-tools.md) | COMPLETE_SOFTWARE | Generator/checker and host watchdog/kill/timeout fixtures; hardware orchestration is task 006. |
| [003: Board preparation](003-board-preparation.md) | REVISED_G1_B | ARM artifacts and revised trial/recovery commands; hardware readiness remains open. |
| [004: USB trials](004-usb-trials.md) | HOLD_READINESS | Revised 10/15-min gate; depends on qualified tasks 006/007 and frozen workload. |
| [005: ADC decision](005-adc-decision.md) | DEPENDS_004 | Exact module/pin/voltage/clock compatibility and one concrete bench-hardware recommendation. |
| [006: Capture runner](006-capture-runner.md) | PREPARED | Native PCM readiness, live comparison, containment/notification and failure fixtures. |
| [007: USB error observation](007-usb-error-observation.md) | PREPARED | Qualified completion-entry counter, attribution, known-event/liveness/loss tests. |
| [008: Product definition](008-product-definition.md) | OPEN | Buyer/input mix, price/volume, complete costs and differentiation before production analog/PCB. |

Current review entry: [November 6 scrutiny and disposition](../reviews/g1-disposition-2026-11-06.md).
External review returned REVISE BEFORE EXPERIMENTS. The owner directed scrutiny
and implementation of agreed changes; G1-B updates are authorized. G1 remains
HOLD for execution readiness, not another approval of the same document edits.
No physical 24-channel PASS exists. Keep task completion, plan disposition and
measured results separate. No image rebuild or SD write was needed.

Each checkpoint records scope, deliverables, validation, unresolved limits and
the exact next action. Preserve a result when it fails; update this table when
a checkpoint changes state.

# Engineering checkpoints

This directory tracks bounded work and its evidence. Product limits remain
in [requirements](../requirements.md); execution methods remain in
[test procedures](../test-procedures.md). A completed software task is not a
hardware PASS or acceptance of external review gate G1.

| Checkpoint | State | Exit evidence / next dependency |
| --- | --- | --- |
| [001: Pattern contract](001-pattern-contract.md) | COMPLETE_SOFTWARE | Frozen packed-PCM pattern, markers, long frame identity and independent byte vectors. |
| [002: Host tools](002-host-tools.md) | COMPLETE_SOFTWARE | Generator/checker, deliberate-fault tests and bounded host results; live capture supervision remains in 004. |
| [003: Board preparation](003-board-preparation.md) | READY_FOR_REVIEW | ARM artifacts and staged trial/recovery commands; instrumentation gaps are explicit. |
| [004: USB trials](004-usb-trials.md) | HOLD_G1 | Target-format smoke, pattern, duration/load/startup/recovery results. |
| [005: ADC decision](005-adc-decision.md) | DEPENDS_004 | Exact module/pin/voltage/clock compatibility and one concrete bench-hardware recommendation. |

Review entry point: [USB tools preparation and remaining decisions](../reviews/usb-tools-preparation-2026-11-04.md).
Checkpoints 001–003 are prepared for review. The owner authorized committing/pushing
the prepared project work and continuing preparation until it is reviewable.
No external review has been returned; G1 remains open. Keep approval and test
results separate from task completion. Ordinary changes use file/package
deployment later; preparing these tools requires no image build or SD write.

Each checkpoint records scope, deliverables, validation, unresolved limits and
the exact next action. Preserve a result when it fails; update this table when
a checkpoint changes state.

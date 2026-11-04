# Engineering checkpoints

This directory tracks bounded work and its evidence. Product limits remain
in [requirements](../requirements.md); execution methods remain in
[test procedures](../test-procedures.md). A completed software task is not a
hardware PASS or acceptance of external review gate G1.

| Checkpoint | State | Exit evidence / next dependency |
| --- | --- | --- |
| [001: Pattern contract](001-pattern-contract.md) | IN_PROGRESS | Frozen packed-PCM pattern, markers, long frame identity and independent byte vectors. |
| [002: Host tools](002-host-tools.md) | PLANNED | Generator/checker, deliberate-fault tests, bounded runner and reviewable results. |
| [003: Board preparation](003-board-preparation.md) | PLANNED | Reproducible ARM build and exact staged trial instructions; no board change before G1. |
| [004: USB trials](004-usb-trials.md) | HOLD_G1 | Target-format smoke, pattern, duration/load/startup/recovery results. |
| [005: ADC decision](005-adc-decision.md) | DEPENDS_004 | Exact module/pin/voltage/clock compatibility and one concrete bench-hardware recommendation. |

Current independent work: 001–003. The owner authorized committing/pushing
the prepared project work and continuing preparation until it is reviewable.
No external review has been returned; G1 remains open. Keep approval and test
results separate from task completion. Ordinary changes use file/package
deployment later; preparing these tools requires no image build or SD write.

Each checkpoint records scope, deliverables, validation, unresolved limits and
the exact next action. Preserve a result when it fails; update this table when
a checkpoint changes state.

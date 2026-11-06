# 002 — Implement and qualify host tools

State: COMPLETE_SOFTWARE. Depends on [001](001-pattern-contract.md).

Deliver separately implemented compiled generator and checker, a small Python
entry point, independent reference tests and deliberate corruption fixtures.
Reject bit/sample/frame/channel/byte errors, zero-fill, sequence reset,
truncation and incomplete markers. Save bounded progress/terminal JSON and
first-mismatch details; process failure must never become PASS.

Validate clean vectors and every detector with real native executables.
Measure host generation/checking throughput separately from board and disk
performance. Keep recordings/results in ignored local output directories;
publish only sanitized, reproducible summaries.

Exit: software self-tests and detector fixtures pass; commands and limits are
documented. This does not pass TEST-008 on a physical USB connection.

Delivered: [tools and commands](../../tools/usb_integrity/README.md), separate
compiled implementations and explicit RUNNING/PASS/FAIL/ERROR reports. Native
builds use strict compiler warnings. November 6 adds independent host watchdog,
PID/boot/start-time identity, deadline/INTERRUPTED results, kill/timeout/cleanup
fixtures and the revised bit/channel bank check: 33 USB-tool methods and 68
whole-project methods pass. No hardware test is implied.

The host pipe benchmark compares 5,760,000 data frames / 414,720,000 bytes
without a mismatch. It is a short throughput observation, not TEST-008's
separate 60-second component-margin measurement or board/USB/storage evidence.
Exact values and provenance: [preparation review](../reviews/usb-tools-preparation-2026-11-04.md).

Remaining hardware orchestration is [006](006-capture-runner.md), including
native readiness, live comparison, remote containment and notification;
qualified error observation is [007](007-usb-error-observation.md). G1-B
defers extra waveform families while retaining the four-pattern bank. The
host utility must not supervise unattended hardware capture by itself.

Next: [ARM build and trial preparation](003-board-preparation.md).

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
compiled implementations, 24 USB-tool test methods including deliberate
faults, and explicit RUNNING/PASS/FAIL/ERROR reports. Native builds use strict
compiler warnings. Complete project suite: 59 test methods pass.

The host pipe benchmark compares 5,760,000 data frames / 414,720,000 bytes
without a mismatch. It is a short throughput observation, not TEST-008's
separate 60-second component-margin measurement or board/USB/storage evidence.
Exact values and provenance: [preparation review](../reviews/usb-tools-preparation-2026-11-04.md).

Remaining implementation belongs to 004: live capture comparison/notification,
independent supervision and stopped-worker detection, waveform bank and
qualified instrumentation. The synchronous host utility does not supply these
features and must not supervise an unattended hardware run by itself.

Next: [ARM build and trial preparation](003-board-preparation.md).

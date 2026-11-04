# 002 — Implement and qualify host tools

State: PLANNED. Depends on [001](001-pattern-contract.md).

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

Next: [ARM build and trial preparation](003-board-preparation.md).

# 001 — Freeze the generated-data contract

State: COMPLETE_SOFTWARE. Supports USB-006 and TEST-008; no hardware execution.

Deliver a versioned specification for signed 24-bit little-endian PCM,
channel order, run seed, 64-bit frame indices, start/end markers and bounded
capture alignment. Include identity, edge-code, walking-bit and alternating
patterns. Freeze independently stated byte vectors around sign, byte and
counter boundaries. Define exactly what each pattern cannot detect alone.

Exit: both generator and checker can be assessed against the same written
contract without sharing an untested encoder. Missing/duplicated data cannot
be hidden by resynchronizing the valid-data window.

Delivered: [packed PCM contract v1](../design/usb-test-pattern.md), separate C
producer/comparator and a third Python reference with literal byte vectors.
Counter boundaries include 24/32/48/64-bit transitions; all 24 role rotations
are tested. Periodic patterns explicitly require the separate identity run.

Validation and limits: [preparation review](../reviews/usb-tools-preparation-2026-11-04.md).
The frozen contract covers four exact-code patterns. It does not yet implement
TEST-008's distinct tone/sweep/burst bank or channel-active marker epochs.

Next: [host qualification](002-host-tools.md), then external G1 disposition.

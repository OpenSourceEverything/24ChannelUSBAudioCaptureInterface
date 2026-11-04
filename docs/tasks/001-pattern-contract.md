# 001 — Freeze the generated-data contract

State: IN_PROGRESS. Supports USB-006 and TEST-008; no hardware execution.

Deliver a versioned specification for signed 24-bit little-endian PCM,
channel order, run seed, 64-bit frame indices, start/end markers and bounded
capture alignment. Include identity, edge-code, walking-bit and alternating
patterns. Freeze independently stated byte vectors around sign, byte and
counter boundaries. Define exactly what each pattern cannot detect alone.

Exit: both generator and checker can be assessed against the same written
contract without sharing an untested encoder. Missing/duplicated data cannot
be hidden by resynchronizing the valid-data window.

Next: [host implementation and detector qualification](002-host-tools.md).

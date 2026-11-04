# 004 — Execute generated 24-channel USB trials

State: HOLD_G1. No full-channel hardware test has run.

Prerequisites: external G1 findings resolved and owner disposition recorded;
qualified tools from [002](002-host-tools.md); reviewed configuration,
recording directory, error observations and recovery path from
[003](003-board-preparation.md).

Use TEST-008's agreed configuration and thresholds. Start with a reversible
60-second target-format trial and stop at the first mismatch. Retain actual
native formats, descriptors, period/buffer settings and compared frame counts.
Use lower-count/rate diagnostics when a failure needs isolation.

Then execute the agreed pattern bank, nominal/loaded runs and startup/reconnect
checks. Keep every failure and expected shutdown separate. Long runs must
save status/results and notify without assistant polling. Return to the known
mono profile. ADC/McASP/analog and 24-hour acceptance stay unpassed.

Review proposals still unresolved: whether final SATA qualification and formal
2x reserve/rate simulation should be deferred from this early buying gate.
Do not silently adopt those scope changes. Follow the accepted disposition.

Exit: reviewable measured results for the exact generated USB path, including
limits and any failures; no blanket platform or product PASS.

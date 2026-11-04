# 004 — Execute generated 24-channel USB trials

State: HOLD_G1. No full-channel hardware test has run.

Implementation checkpoints, to complete before unattended execution:

1. Record accepted G1 disposition, exact artifact hashes and authorized scope.
2. Finish capture orchestration: fresh manifest, native PCM readiness barrier,
   bounded recording/free-space checks, live comparison, independent worker
   supervision, timeouts, persisted progress/terminal results and notification.
   Qualify killed/stalled producer/recorder/checker and cleanup fixtures.
3. Qualify an observable USB completion-status counter and loss detection;
   retain actual period/ring sizes and xruns. Dynamic debug is disabled in the
   cached build; quiet logs do not close this item.
4. Complete the remaining channel-active marker and exact tone/sweep/burst
   vectors before claiming the whole TEST-008 pattern bank is implemented.
5. Execute the agreed smoke/matrix, then pattern/duration/load and
   startup/reconnect/recovery subtests, updating this task after each chunk.

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

# 004 — Execute generated 24-channel USB trials

State: HOLD_READINESS, G1-B 2026-11-06. External review and agreed document
edits are recorded in the [disposition](../reviews/g1-disposition-2026-11-06.md).
The owner's implementation request authorizes the agreed edits. No full-channel
hardware test has run; live readiness/error qualification remains open.

Implementation checkpoints, to complete before unattended execution:

1. Record accepted G1 disposition, exact artifact hashes and authorized scope.
2. Complete [task 006](006-capture-runner.md): fresh manifest, native PCM readiness barrier,
   bounded recording/free-space checks, live comparison, independent worker
   supervision, timeouts, persisted progress/terminal results and notification.
   Qualify killed/stalled producer/recorder/checker and cleanup fixtures.
3. Complete [task 007](007-usb-error-observation.md): USB completion-status/loss observation;
   retain actual period/ring sizes and xruns. Dynamic debug is disabled in the
   cached build; quiet logs do not close this item.
4. Use the revised frozen four-pattern/rotation coverage bank. Additional
   channel-active/tone/sweep/burst families are deferred unless a named fault
   needs them. Retain source/reference and all checker corruption fixtures.
5. Execute target-format smoke/coverage, 10-min nominal, 15-min loaded and
   startup/reconnect/recovery subtests, updating this task after each chunk.

Prerequisites: G1-B implementation/readiness evidence recorded;
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

Agreed scope: identified existing storage at this gate; final SATA/physical-write
2×, formal reserve/clock-offset and longer endurance remain later, unpassed work.
Three cold starts/three reconnects plus one producer-stop/host-stop/warm-restart
each, with fresh identity after every recovery. Application proof stays required.

Exit: reviewable measured results for the exact generated USB path, including
limits and any failures; no blanket platform or product PASS.

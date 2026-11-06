# 006 — Qualify live capture orchestration

State: PREPARED, G1-B B3. Host lifecycle foundation is implemented/tested in
run.py; this task is the separate hardware-capture prerequisite. No hardware
run is authorized by marking host software complete.

1. Freeze native PCM identities, manifest, fresh seed, paths, counts, exact
   argv/timeouts, error-monitor identity and workload limits. Persist the
   reviewed artifact hashes and actual board/host versions.
2. Supervise recorder, producer/SSH process and live checker independently.
   Read actual /proc/asound PCM status and hw_params: RUNNING at 24/96k and
   correct native format before generation; record readiness time and bounded
   leading frames. A PID or sleep alone cannot release the barrier.
3. Preserve raw samples while comparing live, bound queue/memory/write sizes
   and first-fault notification latency. Retain exact exit codes, marker/
   frame counts, resource/error evidence and final flushed-file comparison.
4. Use an independent service/watchdog with containment of local **and remote**
   workers. Host run.py isolates its own worker session; it does not guarantee
   cleanup of a reparented remote generator or uninterruptible storage I/O.
   A killed watchdog, stalled/timeout worker or uncertain cleanup cannot PASS.
5. Qualify success, recorder-before-ready, wrong-format readiness, killed/
   stalled owner/producer/recorder/checker, disk-full/flush failure and failed
   remote cleanup. Retain terminal INTERRUPTED/INCONCLUSIVE results and notify
   without assistant polling; killed runs are not shorter successes.

Exit: complete host-fixture evidence for orchestration plus actual native
readiness/worker/error-monitor preflight. Record unresolved observations
explicitly. Then task 004 can execute the revised TEST-008 profile after task
007 is also qualified. Existing C data contract and detector fixtures remain
the exact oracle; a new orchestration layer must not bypass them.

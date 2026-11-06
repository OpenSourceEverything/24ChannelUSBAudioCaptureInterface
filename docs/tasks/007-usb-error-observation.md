# 007 — Qualify USB completion/error observation

State: PREPARED, G1-B B2. No live counter is qualified. Cached kernel has
KPROBES/KPROBE_EVENTS but no DEBUG/DYNAMIC_DEBUG path for the old pr_debug site.

1. Inspect the actual running kernel/module, available symbols, ABI and
   debug/trace facilities. Check matching type/field offsets from exact build
   evidence; never guess a usb_request offset from another kernel.
2. Prefer a narrow completion-entry/equivalent observation using the existing
   tracing mechanism if reliable. Attribute the active audio endpoint/direction
   and status; include ep-disabled and -ESHUTDOWN early-return paths omitted by
   the old debug site. Record successful-completion liveness as well as errors.
3. Define observation-loss accounting (probe misses, event-buffer loss and
   consumer gaps) and start/stop windows. A zero error value with no active
   observation or lost events is INCONCLUSIVE. Do not enable every packet's
   text logging for the complete run as a substitute for a bounded counter.
4. Exercise a known controlled shutdown/event through the actual installed
   observation path, bracket its expected window and retain host/board evidence.
   A parser-only synthetic fixture cannot prove the live probe is attached.
   Any shutdown/error inside a claimed continuous valid window is unexpected.
5. If existing tracing cannot satisfy coverage/loss requirements, prepare a
   minimal counter/config change and a separately reviewed kernel deployment/
   recovery path. No kernel/image rebuild is mandatory merely because tracing
   was not previously attempted.

Exit: known-event, liveness, coverage/attribution and no-loss evidence on the
actual board with measurement overhead documented. Then supply the observation
to task 006/004. This prerequisite does not pass full-channel USB transport.

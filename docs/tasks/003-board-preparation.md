# 003 — Prepare the board experiment

State: PLANNED. Depends on [002](002-host-tools.md); execution waits for G1.

Prepare a reproducible ARM build using the pinned Yocto compiler, plus a
reviewable manifest and recovery instructions for the first target-format
trial. Record the pinned gadget ring/period constraints and the actual error
observation needed; source limits are not runtime measurements.

Do not change live USB profiles, clocks, pinmux or firmware while G1 is open.
Do not rebuild or reflash the base image just to stage a userspace tool.

Exit: reviewable software artifacts and explicit trial/recovery steps are
ready. Unavailable compiler/runtime validation is stated rather than guessed.

Next: close external review G1, then [004](004-usb-trials.md).

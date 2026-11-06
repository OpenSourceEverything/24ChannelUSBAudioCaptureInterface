# 005 — Qualify one bench ADC purchase

State: DEPENDS_004. No exact ADC board is approved for purchase.

B4 paper interface work may proceed before the USB trial; it does not block
generated USB diagnosis. An exact ADC recommendation still needs both its
qualified interface and the measured task 004 result. Use the
[clock-domain proposal](../design/architecture.md#adc-clock-to-usb-rate-reconciliation)
as a candidate to verify, not an implemented rate-matching bridge.

After the agreed USB gate and paper full-channel interface review, compare
assembled, documented, probe-accessible converter boards. Check exact module
revision/schematic, logic and supply limits, input conditioning, clock/reset
ownership and timing, lane/slot format, exposed pins and pinned codec/machine
driver compatibility. A cheap stereo board does not establish 24-channel
feasibility; prefer a representative bank when its interface is qualified.

Generate a precise one-board bench BOM, then use the existing marketplace
automation sourcing path for exact offers and complete cost. Recommend one
option with documented gaps. A recommendation is not authorization to order.

First analog trial: one known low-level line signal, measured at the qualified
board input; local ADC capture before USB application capture. Preamp design,
24 physical front ends and precision audio equipment remain later decisions.
Commercial input-mix and complete-cost decisions are [task 008](008-product-definition.md);
they precede production analog/PCB commitment, not the bounded USB experiment.

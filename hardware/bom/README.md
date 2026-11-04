# Single-Channel Prototype BOM

[single-channel.csv](single-channel.csv) is the initial functional BOM. It
defines quantities and qualification criteria; it is not a purchase-approved
manufacturer BOM. Exact part numbers and module revisions must replace generic
descriptions after technical qualification. A cheap module with the right chip
name can still have an unsuitable clock or input circuit.

Purchase status: HOLD until the USB baseline and full-channel interface review
are complete. Compare candidate converter banks against the complete-input
performance targets, clock alignment, board pin/driver support and total cost.
Prefer representative multichannel test hardware when practical; no converter
manufacturer or chip channel count is required by the product specification.
See the [feasibility review](../../docs/research/beaglebone-multichannel-feasibility.md).

TI PCM1808EVM remains an optional two-channel diagnostic candidate, not a
recommended purchase at this stage and not evidence for 24-channel capture.
Its manufacturer guide [SBAU349](https://www.ti.com/lit/pdf/SBAU349) supplies
schematics and bench access, but its analog performance falls short of the
provisional production targets. See [requirements](../../docs/requirements.md)
and [ADC selection evidence](../../docs/research/adc-selection.md).
The chip supports 24-bit conversion at up to 96 kHz;
the complete module must separately meet all of the following:

- A published schematic, connector pinout and identifiable hardware revision.
- Compatible 3.3-V digital I/O and documented analog/digital supply rails.
- Accessible mode settings for the selected I2S format, master/slave role,
  sample rate and master-clock relationship.
- An identified oscillator or an accessible external master-clock input.
- A defined input full scale, coupling, bias, impedance and unused-input
  termination. Include any required attenuation, buffer or filter components.
- Exposed serial data, bit clock, frame sync and master clock where required.
- Labeled headers or test points with room for scope probes and nearby ground
  connections; accessible power rails and analog input for level checks.
- Assembled support circuitry and mechanically secure bench connections.
  A bare IC or a board requiring probes directly on fine-pitch IC legs does
  not meet the initial development requirement.

Reference: [TI PCM1808 product documentation](https://www.ti.com/product/PCM1808).
An evaluation board with a complete schematic may reduce integration uncertainty
even if its initial cost is higher. No module is approved by chip-name matching.
The documented PCM1808EVM's fitted crystal is 12.288 MHz, supporting the
48-kHz/256-fs first test without another clock purchase. The 96-kHz/256-fs
configuration needs a 24.576-MHz source through its external-clock selection.
CLK-001 is deferred. Check whether the BeagleBone board clock can supply the
qualified reference before adding a separate oscillator to an order.

The initial analog source is a known low-level line output or signal generator.
A separate microphone preamp is optional. If used, its maximum output must fit
the input circuit; a raw microphone or an instrument is not a line source.
See [analog front ends and build-versus-buy evaluation](../../docs/design/analog-front-end.md)
for the difference between an input buffer, a microphone preamp and an ADC.

The production combo socket, MIC preamp, INSTRUMENT buffer and any phantom
power circuit are deliberately outside this one-LINE-channel BOM. Their
required functions are recorded in the input contract. Generate their exact
design BOM after the source interface and converter circuit are qualified.

## Sourcing workflow

Generate or revise this BOM before searching. Use the separate
OpenSourceEverything/marketplace-automation repository for read-only searches
and inspection; keep its implementation there. Example queries:

```sh
node scripts/marketplace-research.mjs batch amazon 'PCM1808 I2S ADC module' 1 5
node scripts/marketplace-research.mjs search alibaba 'PCM1808 I2S ADC module'
node scripts/marketplace-research.mjs inspect '<exact listing URL>'
```

Run these from marketplace-automation using its documented runtime. An
unavailable/blocked marketplace is an unknown result, not evidence of supply.
Inspect exact product pages after search; search cards are leads.

For every candidate, retain the BOM line ID, exact URL/model/revision, seller,
selected variant and quantity, observed price/currency/time, minimum order,
shipping/tax/duty visibility, lead time, returns/warranty information, schematic
evidence, technical pass/hold/reject reason, and remaining unknowns. Match the
exact board to manufacturer data. Keep dated offers and bench-specific shopping
decisions in project coordination notes, rather than treating them as durable
product specifications.

This sourcing process covers research. Supplier contact, carts and purchases
require separate owner authorization.

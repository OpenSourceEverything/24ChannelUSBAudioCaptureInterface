# Product definition and commercial evidence

Updated: 2026-11-06. Status: decisions/evidence missing; no validated business
case, price or manufacturing margin. Supports PRD-005 and TEST-013. These
questions precede production analog/PCB commitment; they do not block the
bounded generated-USB experiment or a qualified representative ADC bank.

The objective is a viable product to sell. The current requested capability
remains 24 analog channels, 96 kHz, 24 valid sample bits and Linux/UAC2, with
MIC/LINE/INSTRUMENT modes provisionally on every channel. No scope reduction,
manufacturer, production processor or selling price is selected by this review.

## Decisions to support with evidence

| Decision | Current evidence/status | Required next record |
| --- | --- | --- |
| Buyer and recording use case | UNKNOWN | Specific buyer, session/source counts and current workaround; interviews or observed workflow, with evidence date. |
| Input mix | Owner-requested all-24-channel mode coverage; customer demand unvalidated | Count simultaneous MIC/LINE/INSTRUMENT sources and needed gains/phantom/control workflow; compare a fully interchangeable bank with a justified mixed bank. |
| 96-kHz benefit | Product target; buyer value unvalidated | Explain the use case, alternatives and value relative to cost/host load; retain the target until a deliberate product decision changes it. |
| Linux-first market | Technical direction chosen; commercial fit unvalidated | Target supported systems/DAWs and buyer expectations, monitoring/output/latency needs and support matrix. Capture-only capability is not assumed to satisfy every buyer. |
| Differentiation | UNKNOWN | Explain why a buyer chooses this over an existing interface/mixer and what measurable advantage supports the claim. |
| Selling price and volume | UNKNOWN | Target market/currency/channel, customer price, expected first-batch volume and confidence; no fabricated target. |
| Complete unit economics | UNKNOWN | Exact BOM/revisions, labor/yield, assembly, test/calibration time, enclosure/PSU, packaging/freight, fees, returns/warranty and support/update labor at that volume. |
| Availability and maintenance | No production parts approved | Lifecycle and revision control, qualified substitutes, supply continuity, reproducible firmware and a supported update/recovery policy. |
| Release evidence | Unqualified | Audio/full-channel/clock/endurance results, traceability, licensing/USB IDs and applicable qualification scope under PRD-001–004. |

These are evidence fields, not permission to contact customers/suppliers or
place orders. Compile the owner's available use-case and price assumptions
first; preserve UNKNOWN where none were supplied.

## Comparator corrections

The review's input-mix warning is sound. Headline channel counts need rate,
physical connector, shared-mode and digital-expansion context:

- Focusrite's **Scarlett 18i20 4th Generation** publishes eight microphone
  preamps, eight line inputs sharing that analog bank and two instrument
  inputs. Its 26-input headline includes digital expansion; ADAT capacity
  falls from 16 channels at 44.1/48 kHz to eight at 96 kHz. These figures do
  not describe 26 physical analog inputs or prove equivalence to our proposed
  24-analog-channel/96-kHz device. [Manufacturer specifications](https://focusrite.com/products/scarlett-18i20).
- Soundcraft's **Ui24R** is useful input-mix/workflow context. HARMAN's DAW
  instructions specify a 48-kHz session. Treating its advertised channel count
  as evidence of 24 analog channels at 96 kHz would be unsupported.
  [Manufacturer DAW instructions](https://help.harmanpro.com/en_US/ui24r-multitrack-recording-with-a-daw).

These are limited primary-source observations checked November 6, not a
competitive price study, Linux support proof or a demand signal. Verify exact
generation, simultaneous local analog channels, rate-dependent digital I/O,
required expansion hardware and complete customer cost before comparing.

## Exit

Before production analog/PCB commitment, record the justified product scope,
customer evidence, price/volume and complete-cost assumptions, major risks and
the owner's product decision. Preserve the full requested capability while
evaluating a smaller commercial variant; a review comment alone does not
authorize deleting channels or modes. PRD-004's later release qualification
and TEST-006's physical endurance remain separate gates.

# Input-Driven ADC Selection

Research date: 2026-11-03. Recommendation: establish the
[MIC/LINE/INSTRUMENT input contract](../requirements/analog-inputs.md) first.
Use a documented PCM1808 board only to prove one analog channel; evaluate
AK5558VN first for the production eight-channel bank. No exact module or
production converter is approved by this research.

## Translate the input contract

| Input requirement | Derived converter/circuit requirement |
| --- | --- |
| MIC, LINE and raw passive guitar | Different input impedance and gain circuits can feed one ADC family. Connector shape and amplifier class do not select the ADC. |
| +24-dBu supported LINE maximum | Attenuation and balanced reception before the chip. Check every amplifier/input pin at maximum differential and common-mode voltage. |
| 110-dBA LINE dynamic range | Prefer at least 115-dBA converter performance under comparable conditions, leaving some noise budget for the analog circuit. Chip typical performance is not a system guarantee. |
| -100-dB LINE THD+N | Screen converters at 96 kHz, near full scale, with documented measurement bandwidth. Prefer at least 6 dB of chip margin; test the complete chain. |
| 24 independent channels | No channel summing to achieve a better headline noise number. Three eight-channel banks remain provisional, subject to McASP pin/driver validation. |
| 24 valid bits at 96 kHz | Accept a converter with 24/32-bit serial output, documenting valid bits, slot packing and later conversion to USB's independently chosen subslot width. |
| Coherent capture | One clock domain, documented multi-chip reset/alignment, accessible clock controls, compatible 3.3-V I/O. Do not combine unrelated module oscillators. |
| Fast bench progress | Assembled board, schematic/revision, labeled headers/test points, safe analog input, supply/mode documentation and an explicit clock source. |

## Voltage calculation

These are calculations, not measurements:

```text
V_RMS = 0.775 × 10^(dBu / 20)
V_peak-to-peak = 2 × sqrt(2) × V_RMS       [sine wave]

 +4 dBu =  1.228 V RMS =  3.474 V peak-to-peak
+24 dBu = 12.283 V RMS = 34.741 V peak-to-peak
+25 dBu = 13.782 V RMS = 38.980 V peak-to-peak
```

For a balanced input, these voltages are measured between hot and cold.
For a symmetrical source each leg has half the differential swing; real
sources need not be symmetrical. Check leg-to-ground limits separately.

The PCM1808 chip's 3-V peak-to-peak full scale therefore needs a nominal
voltage ratio of 3/38.980 = 0.07696 (-22.27 dB) to implement the proposed
+25-dBu LINE full-scale mapping. It also requires its own DC bias. This is
a gain calculation, not a resistor-divider schematic or permission to connect
a professional line output directly to an unknown module.

At +25-dBu reference full scale, 110 dB of dynamic range corresponds to about
43.6 µV RMS of input-referred weighted noise. Independent noise contributions
add by root-sum-square, not by adding their dB ratings. Equal 115-dB ADC and
analog-stage contributions would combine to about 112 dB, before other losses.
Distortion products need a separate budget and can add coherently.

## Candidate screen

| Candidate | Interface / analog input | Manufacturer evidence | Decision |
| --- | --- | --- | --- |
| TI PCM1808 | Two channels; 24-bit I2S/LJ; single-ended 3-V peak-to-peak chip input at 5-V analog supply | At 96 kHz: typical 101-dBA dynamic range and -87-dB THD+N; the latter measured at -0.5 dBFS with 400-Hz HPF/20-kHz LPF. | Integration prototype only. Fails the proposed production LINE quality targets even before adding analog circuitry. |
| AKM AK5558VN | Eight differential channels; 24/32-bit PCM including TDM256 at 96 kHz | 115-dBA typical dynamic range in unsummed mode under default 48-kHz conditions. At 96 kHz, typical S/(N+D) 106 dB at -1 dBFS, 40-Hz–40-kHz bandwidth. | First production candidate to evaluate: matches the provisional eight-channel-bank topology. Need 96-kHz noise characterization and complete input-stage budget. |
| AKM AK5578EN | Eight differential channels; AKM describes pin/register compatibility with AK5558VN | 121-dBA typical unsummed dynamic range under default 48-kHz conditions. At 96 kHz, typical S/(N+D) 110 dB at -1 dBFS, 40-Hz–40-kHz bandwidth. | Higher-margin alternative if complete-bank cost and availability justify it. Still needs board-level qualification. |

S/(N+D) is signal relative to noise plus distortion; the table's positive
106/110-dB ratios correspond to negative THD+N dB ratios. The measurement
bandwidths differ, so this screen is not a lab comparison. Neither AKM's
48-kHz noise specifications nor a 32-bit output establishes 96-kHz effective
resolution. Do not use summed-channel performance for this product.

Sources: [PCM1808 datasheet, sections 6.5 and 7](https://www.ti.com/lit/ds/symlink/pcm1808.pdf),
[AK5558 datasheet 015099850-E-02, sections 8 and 13](https://www.akm.com/content/dam/documents/products/audio/audio-adc/ak5558vn/ak5558vn-en-datasheet.pdf),
[AK5578 datasheet 015016736-E-03, section 8](https://www.akm.com/content/dam/documents/products/audio/audio-adc/ak5578en/ak5578en-en-datasheet.pdf).
Lifecycle pages checked on the research date list
[PCM1808 as ACTIVE](https://www.ti.com/product/PCM1808),
[AK5558VN as MP](https://www.akm.com/us/en/products/audio/audio-adc/ak5558vn/) and
[AK5578EN as MP](https://www.akm.com/us/en/products/audio/audio-adc/ak5578en/).
These labels do not establish module stock, distributor lead time or a
production supply commitment. Recheck at procurement.

## Clock and board traps

The [PCM1808EVM guide, SBAU349](https://www.ti.com/lit/pdf/SBAU349) provides a
schematic, 5-V board input with onboard 3.3-V regulation, hardware mode
controls, RCA analog inputs and digital signal/ground headers. Its fitted
12.288-MHz crystal is suitable for a 48-kHz/256-fs bootstrap. For the
datasheet's 96-kHz/256-fs mode, provide 24.576 MHz through the documented
external-clock selection; include that source in the BOM. Do not assume the
EVM runs 96 kHz with its fitted crystal. Price/availability and physical
revision remain unqualified.

PCM1808 stereo 32-bit slots at 96 kHz need 6.144-MHz bit clock. AK5558's
eight-slot TDM256 bank needs 24.576 MHz and supports a 24.576-MHz master clock
at that rate. Its datasheet defines multi-chip synchronization using reset,
configuration and the same system clock. Driver timing and exact board pins
still require validation; this does not establish 24-channel feasibility.

Generic low-cost PCM1808 boards remain on hold without their exact schematic,
input circuit, clock/revision and mode access. Buying the chip name is not
enough. Do not buy a USB-only sound dongle as a substitute for exposing the
ADC's serial audio interface to the BeagleBone.

## Next engineering gate

1. Finish the Yocto/USB generated-tone baseline.
2. Qualify one exact assembled PCM1808 board and its clock arrangement against
   [ADC-001/CLK-001 in the prototype BOM](../../hardware/bom/single-channel.csv).
   Record landed price, lead time and missing circuitry before recommending
   an order. A cheaper unsupported board is still an unqualified board.
3. Capture a scope-checked 1-kHz line tone locally, then in the Linux host
   recorder; change its physical frequency/level and repeat at 96 kHz.
4. Develop one reusable MIC/LINE/INSTRUMENT front-end channel, measuring
   loading, gain, clipping and noise before replicating it. Freeze its
   electrical interface before making a separate repository a dependency.
5. Qualify an eight-channel production converter bank and its synchronization,
   analog quality, power and cost before extending to 24 channels.

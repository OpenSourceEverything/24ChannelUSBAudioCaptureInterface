# Analog Front Ends and Prototype Hardware

## Functions and boundaries

The [proposed input contract](../requirements.md#analog-input-requirements) now calls for
one combo socket with MIC, LINE and INSTRUMENT modes per channel. It defines
the source impedance, gain, headroom and quality targets that drive this
circuit. Keep the first bench milestone to one known LINE tone. The
[ADC review](../research/adc-selection.md) distinguishes that prototype from
production quality and identifies the evaluation board's clock limitation.

An analog-to-digital converter (ADC) produces numeric samples from analog
voltage. The IC is one component. A usable ADC board also needs power
decoupling, clocking, configuration and input conditioning appropriate to the
chip. A breakout makes the signals accessible; an evaluation board generally
adds circuitry and documentation for evaluating a manufacturer's device.
Verify what is actually included rather than relying on either label.

```text
microphone -> microphone preamp --------------------+
passive guitar pickup -> high-impedance buffer -----+-> ADC input conditioning
known line output ---------------------------------+   -> ADC board
                                                        -> BeagleBone
```

- A microphone preamp supplies gain for a low-level source and may need a
  balanced input, interference rejection and optional controlled phantom power.
- A passive guitar pickup normally needs a high-impedance input to avoid
  loading the pickup and changing its response. This may be a buffer with
  modest gain. Active pickups, pedals and other outputs require their own
  source specifications rather than an automatic passive-pickup assumption.
- A line source may need attenuation, buffering or balance conversion before
  the ADC. Its connector shape does not establish its electrical level.
- Cables and XLR/quarter-inch adapters change connections, not the required
  gain, impedance or conversion function. An isolation transformer can provide
  galvanic isolation or impedance transformation within its specified loading
  and frequency range; it does not digitize audio or provide active gain.

For a first controlled test, use a known analog tone or line output within
the ADC circuit's input limits. Add the source-specific preamp/buffer after
conversion and USB delivery can be measured independently.

## Amplifier operating classes

Classes A, B, AB and C describe how amplification devices conduct during a
signal cycle. They are not recording-quality grades or input categories.

- Class A keeps the relevant devices conducting throughout the cycle and
  incurs continuous bias power.
- Class B uses half-cycle conduction; crossover behavior matters when the
  halves are combined.
- Class AB overlaps conduction around that transition, trading bias power
  against crossover behavior.
- Class C uses less than half-cycle conduction and is unsuitable as the
  ordinary linear, broadband audio preamp stage in this signal path.

A complete preamp can contain stages with different operating classes.
Compare the complete circuit at the intended gain, source impedance, output
load and supplies. Class A labeling alone establishes neither lower noise
nor lower distortion. [Analog Devices' amplifier-class definitions](https://www.analog.com/en/resources/glossary/power-amplifier.html)
explain the conduction-angle distinction.

## Building and buying

Buying one documented ADC board separates converter/clock debugging from
designing a new analog PCB. Custom preamps can reuse a proven low-noise IC
application circuit, with product-specific gain control, connectors, protection
and ADC output interface. A discrete transistor design is not required to
make a reusable preamp product.

Examples of distinct design building blocks are the
[TI INA217 microphone preamp IC](https://www.ti.com/product/INA217)
for suitable low-impedance sources, and a FET-input audio op amp such as
[TI OPA1656](https://www.ti.com/product/OPA1656) for a suitable instrument-buffer
circuit. These are examples, not selected BOM parts or complete drop-in
modules. Check lifecycle, supplies, stability and the exact application
circuit before selection.

Compare an assembled purchased preamp with the complete custom assembly:

- Amplifier ICs and passives, input protection, gain controls and connectors.
- PCB fabrication, assembly, inspection, calibration and audio testing.
- Shared power supply and any phantom-power supply, grounding and enclosure.
- Design effort, prototype revisions, yield, repair and replacement costs.

Compare the same input functions and measured performance at one prototype
and the intended channel count. Spreading shared costs across 24 channels
can change the result; savings cannot be established from the amplifier IC
price alone.

## Quality and measurement

Specify input impedance, gain range, overload level, frequency response,
noise, distortion, interference rejection where applicable, channel crosstalk,
and power consumption. Match the preamp output range and common-mode voltage
to the ADC circuit's actual input contract.

An oscilloscope establishes clocks, gross waveform shape, levels and clipping.
Low-noise and low-distortion claims need a characterized source/measurement
path with a known noise and distortion floor. Document bandwidth, weighting,
gain, source impedance, load and uncertainty alongside each result.

## Bench access

Use an assembled ADC board with a schematic, accessible mode controls,
documented clock ownership and labeled signal connections. Provide secure
headers and test points for analog input, each supply, data and clocks, with
nearby ground points for probing. Mechanical probe access must not require
touching adjacent fine-pitch IC pins. Avoid routing high-speed audio clocks
through long loose leads or treating a solderless breadboard as a production
audio layout.

[TI PCM1808EVM](https://www.ti.com/tool/PCM1808EVM) is an example of a manufacturer
evaluation platform exposing digital audio and control signals. Its full
schematic, clock options, required accessories, actual availability and price
must be reviewed before selection. No specific evaluation board is mandated.

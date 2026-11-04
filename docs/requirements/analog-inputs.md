# Analog Input Requirements

Status: proposed engineering baseline, researched 2026-11-03. The requested
source coverage is raw guitar, XLR and balanced/unbalanced connections. Numeric
limits below are design targets, not measured performance or release claims.
They guide circuit and ADC selection; revise them explicitly when measurements
or cost justify a change.

## Recommended channel

Use one XLR/6.35-mm combo receptacle and selectable MIC, LINE and INSTRUMENT
modes per channel. Plan this capability for all 24 channels as the working
product scope. One socket accepts one plug and records one mono channel at a
time. A balanced TRS cable uses three contacts for one channel, not stereo.

| Mode | Intended source and connection | Required input circuitry |
| --- | --- | --- |
| MIC | Analog microphone, balanced XLR | Low-noise adjustable-gain preamp, interference rejection and input protection. |
| LINE | External preamp, mixer or other line output; balanced XLR/TRS or unbalanced TS with documented wiring | Balanced receiver/driver, attenuation or gain as needed, filtering and ADC level/bias matching. |
| INSTRUMENT | Raw passive guitar/bass pickup on a TS cable | High-impedance buffer with adjustable gain, followed by ADC level/bias matching. Active instruments/pedals may instead use LINE according to their output level. |

XLR is a connector, not a voltage specification. An XLR line output still
needs LINE mode. Do not infer source type or enable microphone power just
because an XLR plug is present.

The [Neutrik Combo FAQ](https://www.neutrik.us/en-us/neutrik/faq/combo) confirms
that XLR and jack contacts are separate; the connector does not join them
automatically. Keep the paths separate where required for gain and power
control. [NCJ6FI-S](https://www.neutrik.com/en/product/ncj6fi-s) illustrates
a solder-cup combo receptacle, not a selected production part. Exact footprint,
switch contacts, voltage rating and panel mounting require qualification.

## Source-facing targets

Unless stated otherwise, characterize at 96 kHz with the final 24-channel
configuration powered and active. Measure at the input connector, not just
at the converter IC.

| ID | Proposed target | Selection consequence / verification |
| --- | --- | --- |
| IN-001 | Each channel supports the three modes above, selected explicitly. XLR pins 2/3 are positive/negative; pin 1 is shield. Balanced jack tip/ring are positive/negative; sleeve is shield/reference. Document actual chassis/signal-ground connections and unbalanced cable wiring. | Review connector drawing and schematic; test each plug/mode combination. Never sum the two paths or tie separate source outputs together. |
| IN-002 | LINE nominal level +4 dBu; supported maximum +24 dBu, differential for a balanced source. Also accept lower-level unbalanced sources within the selected range. | Design the receiver/pad for the external voltage, not the ADC pin voltage. Test balanced and unbalanced operation separately. |
| IN-003 | Set nominal LINE conversion full scale at +25 dBu, reserving 1 dB for tolerance. +4 dBu maps to approximately -21 dBFS; +24 dBu shall remain unclipped. | Verify gain and overload across component/supply/temperature tolerances. A digital gain reduction cannot repair analog clipping. |
| IN-004 | LINE input impedance nominal 20 kΩ differential, at least 10 kΩ across 20 Hz–20 kHz; document impedance from each leg to reference and in unbalanced mode. | Receiver/pad must not load the source excessively. Measure complex impedance rather than equating it to the chip's input resistance. |
| IN-005 | MIC input impedance at least 2 kΩ differential; preamp gain covers 0–60 dB before ADC level matching; accept at least 0 dBu at minimum gain without clipping. | Evaluate with a 150-Ω balanced source. Establish gain accuracy, overload at every gain setting and actual ADC drive. |
| IN-006 | INSTRUMENT impedance nominal 1 MΩ, at least 900 kΩ at 1 kHz; input capacitance target no more than 150 pF excluding the cable; gain covers 0–30 dB before ADC level matching; accept a 2-V RMS sine at minimum gain. | Use a low-input-current buffer. Measure loading and transient headroom; a low-impedance line input is not a substitute. |
| IN-007 | Frequency response within ±0.5 dB from 20 Hz–20 kHz relative to 1 kHz, in each supported mode. | Measure with documented source impedances: 100 Ω LINE, 150 Ω MIC, 10 kΩ resistive INSTRUMENT. Also characterize a pickup/cable model for guitar tone. |
| IN-008 | LINE dynamic range at least 110 dB A-weighted; THD+N no worse than -100 dB at 1 kHz/-1 dBFS over 20 Hz–20 kHz, with weighting disabled for THD+N. | Budget the receiver, resistors, ADC driver, converter, reference and power noise together. Evaluate at 96 kHz; headline 48-kHz figures alone are insufficient. |
| IN-009 | MIC equivalent input noise no greater than -125 dBu, unweighted 20 Hz–20 kHz, at 60-dB preamp gain with a 150-Ω source. Publish the source-resistor noise contribution. | Measure complete path noise, refer it back through measured gain, and identify the analyzer/source floor. Do not apply LINE dynamic-range claims to a high-gain microphone mode. |
| IN-010 | LINE common-mode rejection at least 60 dB at 50/60 Hz and 40 dB at 20 kHz with a 1-V RMS common-mode signal and matched 100-Ω source legs. Channel crosstalk no greater than -90 dB at 1 kHz. | Test assembled channels and repeat with source-impedance imbalance. Publish the bandwidth, driven/victim channels and input terminations. |
| IN-011 | Mode, gain, channel number, signal/clip state and microphone-power state are visible to the user. Mode changes start muted and do not silently resume a different channel/gain. | Bench controls may be jumpers/manual controls initially. Define final controls and switching transients before release. |

dBu expresses RMS voltage relative to 0.775 V. dBFS expresses level relative
to the digital full-scale sine. A-weighting reduces the contribution of some
frequencies in a noise measurement; weighted and unweighted results are not
interchangeable. Dynamic range describes the span down to the noise floor;
THD+N measures distortion plus noise relative to a test tone.

The +24-dBu range is a proposed compatibility target with 20 dB of peak room
above +4 dBu. It is not mandatory for all audio equipment. As a real-world
reference, [RME's ADI-8 QS manual, section 16.1](https://rme-audio.de/downloads/adi8qs_e.pdf)
specifies +24-dBu sensitivity and 10-kΩ line inputs. Its published performance
does not establish this project's performance.

## Microphone power and faults

- Recommend individually enabled 48-V phantom power for condenser microphones
  as a production feature; this is an added proposed capability, not something
  established by the request for an XLR connector alone. It stays off in the
  first analog prototype and defaults off at boot.
- Phantom power shall only reach the intended XLR microphone contacts, never
  the jack/guitar path. Leaving MIC mode disables it and discharges the path
  before reconnection. Select discharge/mute timing from measured hardware.
- Before enabling phantom power, define supply voltage/current capability,
  feed-resistor matching, capacitor ratings, hot-plug/short protection and
  simultaneous-channel power budget. Test with suitable dummy loads first.
  Do not assume the existing BeagleBone USB supply can power 24 front ends
  and their microphone loads.
  [TI's phantom-power application report](https://www.ti.com/lit/an/sboa320a/sboa320a.pdf)
  explains the supply function; it is not a complete product protection design.
- LINE and INSTRUMENT accept audio, not speaker-amplifier outputs. Define
  operating common-mode/DC limits, external phantom-power faults, ESD and
  unpowered-input protection before approving a production schematic. A
  maximum unclipped audio level is not a damage threshold.

MIC distortion versus gain, INSTRUMENT noise/distortion, full common-mode
range, gain-control details and protection limits remain characterization/
design gates. Do not advertise broad "high quality in every mode" claims
from the LINE targets alone. Class A/B/AB describes circuit operation, not a
required quality grade; select topology using the measured limits above.

## Derive the ADC requirements

```text
source type + source impedance + loudest input + noise target
  -> connector / mode / gain or attenuation / input protection
  -> ADC drive voltage, common-mode bias and filter
  -> ADC performance, clock/serial interface and power requirements
```

An external preamp can use the LINE connector contract. An internal reusable
MIC/INSTRUMENT module should feed a documented ADC-ready interface; do not
force it to generate a +24-dBu output merely to attenuate that signal again.
Freeze its voltage, bias, load, power, control and grounding contract after
choosing the converter circuit, before creating a dependency/submodule.

The [ADC selection research](../research/adc-selection.md) maps these targets
to converter candidates and separates the inexpensive first test from the
production converter.

## Immediate bench milestone

Keep the first test in LINE mode: one assembled, documented ADC board and a
known low-level tone. Start around 0.5 V peak-to-peak at 1 kHz, measured with
the oscilloscope at the qualified board input. Its schematic must permit this
source/coupling arrangement. This does not test the +24-dBu receiver, a raw
guitar or a microphone preamp. The existing staged USB-tone/analog acceptance
sequence still applies; no preamp purchase is necessary for this milestone.

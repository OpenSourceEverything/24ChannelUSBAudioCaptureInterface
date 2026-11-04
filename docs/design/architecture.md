# Architecture and Feasibility Constraints

## Signal path

```text
24 MIC / LINE / INSTRUMENT inputs, one source per combo socket
  -> mode-specific preamp / line receiver / high-impedance guitar buffer
  -> ADC level/bias conditioning, filtering and protection
  -> 24 audio ADC channels, provisionally three eight-channel devices
  -> synchronized serial audio data lanes
  -> BeagleBone McASP + DMA
  -> ALSA capture + bounded audio bridge
  -> USB audio gadget ALSA playback
  -> USB device IN endpoint, UAC2
  -> Linux USB host audio capture
  -> Audacity or another recording application
```

The first prototype exercises only a known line source. Full source coverage
requires the [input requirements](../requirements.md#analog-input-requirements), including
separate microphone and guitar conditioning. A combo connector alone does
not supply these functions. The reusable front-end module boundary remains
to be defined; external preamps can feed LINE mode.

The Linux USB gadget is a USB peripheral implemented by the BeagleBone.
ALSA capture hardware and a UAC2 gadget are separate endpoints; merely enabling
both does not route audio between them. The bridge must preserve channel order,
sample representation, and timing, and expose buffer errors.

## Clock and serial topology

All converters need a common sample-clock domain and deterministic frame
alignment. Define one owner for master clock, serial bit clock, frame sync,
and reset; never connect competing clock outputs.

An initial full-scale topology to evaluate is one eight-channel TDM stream
per ADC on three receive serializers, with common clock/frame signals.
TDM means time-division multiplexing: channels occupy successive slots on a
serial data wire. At eight 32-bit slots and 96 kHz, each lane needs a
24.576-MHz bit clock. A single 24-slot lane needs 73.728 MHz; padding to 32
slots needs 98.304 MHz. A single full-rate combined lane exceeds the AM335x clock limit; any
daisy-chain alternative requires a separate supported timing/topology review.

The [source-level feasibility review](../research/beaglebone-multichannel-feasibility.md)
identifies a candidate three-lane pin map, HDMI/shared-pin conflicts, the
pinned driver limits and remaining runtime checks. It is not physical proof.

The exact board must expose the required McASP signals, and its kernel driver
must support the selected serializer/slot arrangement. HDMI shares audio
resources on BeagleBone Black and requires an explicit pin/resource decision.
[TI's McASP/ALSA documentation](https://software-dl.ti.com/processor-sdk-linux/esd/AM335X/latest/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/Audio.html)
describes the separate peripheral, DMA, device-tree and sound-card layers.

AK5558VN is a candidate eight-channel converter, not a selected production
part. See the [input-driven ADC review](../research/adc-selection.md) for
manufacturer evidence, 96-kHz measurement conditions and remaining analog
qualification. Three chips do not
automatically form a 24-channel serial bus. See
[AKM's ADC catalog](https://www.akm.com/us/en/products/audio/audio-adc/).

For the first input, a documented PCM1808 stereo module is a lower-complexity
candidate. Use one analog channel, terminating the other as its circuit
requires. The [TI PCM1808](https://www.ti.com/product/PCM1808) supports 24-bit
conversion up to 96 kHz and I2S/left-justified serial output; it is not a
drop-in eight-channel TDM design. Its documented analog performance falls
short of the proposed production LINE targets; it can still prove integration.

## USB bandwidth is an endpoint constraint

Decimal payload rates, excluding protocol overhead:

| Configuration | Bytes/second | Bytes per 125-us interval at 96 kHz |
| --- | --- | --- |
| 24 channels, four bytes/sample | 9,216,000 | 1,152 |
| 24 channels, packed three bytes/sample | 6,912,000 | 864 |
| Eight channels, four bytes/sample | 3,072,000 | 384 |

At 96 kHz, one high-speed microframe nominally contains 12 sample frames.
Clock tolerance and packet scheduling need additional capacity. Thirteen
frames of 24 packed samples require 936 bytes; the four-byte equivalent is
1,248 bytes.

A single USB high-speed isochronous transaction carries at most 1,024 payload
bytes. Higher-bandwidth endpoints require multiple transactions per interval
and matching gadget/controller/driver support. The bus's 480-Mbit/s nominal
speed does not establish that support. See
[USB 2.0 specification, section 5.9](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/2656.usb_5F00_20.pdf).

The upstream Linux UAC2 implementation inspected at commit
6628e7d4c6b25c8d18f1345e3a20d21829aae7e4 caps high-speed endpoint sizing at
1,024 bytes in set_ep_max_packet_size_bint. Consequently, 24 channels at
96 kHz in four-byte USB subslots do not fit that implementation's endpoint.
This source review does not establish the behavior of a vendor kernel.
See the [pinned UAC2 implementation](https://github.com/torvalds/linux/blob/6628e7d4c6b25c8d18f1345e3a20d21829aae7e4/drivers/usb/gadget/function/f_uac2.c#L702).

Evaluate packed 24-bit USB samples while retaining 32-bit McASP/ALSA storage
as needed. Packing belongs in the bridge and must preserve all valid bits.
Packed transport fits the basic packet calculation; sustained BeagleBone
operation, descriptor support, clock tracking, and 24-channel labeling still
need hardware validation. A four-byte USB format instead requires a verified
alternative endpoint implementation. Neither route is a demonstrated result.

## USB direction naming

For Linux's UAC2 gadget, playback/capture names are from the gadget ALSA side:

```text
ADC -> board ALSA capture -> bridge -> gadget ALSA playback
    -> USB IN -> computer ALSA capture
```

The p_chmask, p_srate and p_ssize settings control board-to-host audio in the
referenced driver. The c_* settings describe host-to-board audio. Verify the
actual kernel implementation before configuring it; names alone can reverse
the intended direction. See the
[legacy UAC2 topology and parameters](https://github.com/torvalds/linux/blob/v3.8/drivers/usb/gadget/f_uac2.c#L20)
and [configfs UAC2 attributes](https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/configfs-usb-gadget-uac2).

## Reusable preamp boundary

Start with a line-level input. Input classes describe the source interface:

- Microphone: low-level balanced sources, selectable gain, impedance and
  optionally controlled phantom power; electret bias is a separate requirement.
- Line: higher-level balanced or unbalanced outputs; ADC headroom, attenuation
  and bias still require a defined circuit.
- Instrument: high-impedance sources needing a suitable input buffer.
- Digital: a protocol receiver for S/PDIF, ADAT, AES3 or the actual source
  protocol; an analog preamp/ADC path is not interchangeable with it.

Amplifier classes A, AB and D describe circuit operation rather than these
source interfaces. See [analog front ends](analog-front-end.md) for quality
criteria, bench access and build-versus-buy evaluation.

A companion preamp can become a separate reusable repository once its analog
output level, impedance, balance, connector, power, grounding and channel
contract are defined. Integrate it as an optional version-pinned submodule
only when product builds consume its design files. Do not make initial
line-level capture depend on designing a microphone preamp.

# 24-Channel USB Audio Capture Interface

A product project for recording 24 independent analog audio channels at
24-bit resolution and 96 kHz through USB Audio Class 2.0 on a Linux computer.
The reference platform is a BeagleBone with external audio ADCs. Full-scale
operation is a design target, not a demonstrated capability.

Classification: object > electronic device > audio equipment > audio interface
> multichannel audio interface > 24-channel USB audio capture interface.

Start with one analog channel recorded in Audacity or another Linux recording
application. Establish the USB path with a generated tone separately, then
validate the external ADC path before expanding to eight and 24 channels.

## Start here

Run ./device install-cli once, then type bbb to open the BeagleBone terminal.
Press Enter; at a login
prompt, enter root. See the [Yocto baseline and board controls](firmware/README.md)
for the pinned build, initial SD installation, USB SSH access and the on-board
audio menu. After installation, use bbb deploy to update the menu without
removing the card.
Establish this firmware baseline and its USB tone before wiring the ADC.
Review the full-channel pin/clock/driver/USB path before any analog purchase.
The first analog test uses a known line source; representative multichannel
hardware is preferred once its interface is qualified.

## Product documents

- [Product requirements](docs/requirements.md)
- [Repeatable test procedures and requirement coverage](docs/test-procedures.md)
- [BeagleBone pin/clock/driver feasibility review](docs/research/beaglebone-multichannel-feasibility.md)
- [Input-driven ADC selection research](docs/research/adc-selection.md)
- [Architecture and bandwidth constraints](docs/design/architecture.md)
- [Single-channel integration procedure](docs/bring-up/single-channel.md)
- [Prototype BOM and sourcing criteria](hardware/bom/README.md)
- [Initial prototype BOM](hardware/bom/single-channel.csv)

The proposed product has one XLR/quarter-inch combo socket per channel with
MIC, LINE and INSTRUMENT modes, supporting microphones, balanced/unbalanced
line sources and raw passive guitars. Each source needs its appropriate
preamp, receiver or buffer before the ADC. First prove a known line tone;
the complete multi-mode front end is a later hardware milestone.

The BeagleBone does not replace audio ADCs. Its general-purpose analog inputs
are not the proposed audio converters.
The UART debug cable provides console access. USB audio uses the board's
separate USB device connection.

Windows 7 compatibility is a stretch goal and must not drive the primary
Linux/UAC2 architecture.

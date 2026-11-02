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
for the pinned build, first-boot image, SSH access and the on-board audio menu.
Establish this firmware baseline and its USB tone before buying analog parts.

## Product documents

- [Product requirements](docs/requirements/README.md)
- [Architecture and bandwidth constraints](docs/design/architecture.md)
- [Single-channel integration procedure](docs/bring-up/single-channel.md)
- [Prototype BOM and sourcing criteria](hardware/bom/README.md)
- [Initial prototype BOM](hardware/bom/single-channel.csv)

External preamps provide analog signals; the BeagleBone does not replace audio
ADCs. Its general-purpose analog inputs are not the proposed audio converters.
The UART debug cable provides console access. USB audio uses the board's
separate USB device connection.

Windows 7 compatibility is a stretch goal and must not drive the primary
Linux/UAC2 architecture.

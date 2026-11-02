# Single-Channel Integration

The first analog result is a known external signal recorded on a Linux host
through the BeagleBone's USB audio connection. A synthetic tone is a separate
diagnostic result.

## Connections

```text
USB-to-UART adapter -> debug header -> console only
Linux computer USB -> BeagleBone USB device port -> audio data
source -> conditioning -> external audio ADC -> McASP pins
```

Use the exact board reference manual for connector type and pin mapping.
BeagleBone Black uses a mini-USB client port; its USB-A port is the host port.
See [board connectors](https://docs.beagleboard.org/boards/beaglebone/black/ch07.html).
The debug interface is 3.3-V TTL, normally 115200 baud, eight data bits,
no parity, one stop bit and no flow control. Do not use RS-232 voltage levels.

## Inspect before configuring

On the board, inspect the kernel, active audio devices, and gadget support:

```sh
uname -a
cat /proc/asound/cards
arecord -l
aplay -l
lsmod
ls /sys/class/udc
modinfo g_audio
```

An HDMI playback card is not an ADC capture device. A sound-card device-tree
definition and supported ADC/codec driver are needed for the selected McASP
capture circuit.

Use a maintained board image for a reproducible product baseline, normally
first on removable media while preserving the existing installation. A
legacy image may already provide g_audio without configfs. Do not assume
modern configfs instructions apply to an older vendor kernel, or that the
presence of g_audio proves it has been successfully used.

## Establish USB audio independently

Keep the UART console available while configuring USB. Record the active
gadget driver and its configuration before replacing it; unloading a composite
gadget can disconnect networking and storage. Preserve mounted storage and
provide a tested restoration path.

Configure a small supported UAC2 stream, starting with one or two channels
at 48 kHz if necessary. Match the board's actual API: legacy g_audio module
parameters or a supported configfs uac2 function. Board-to-host audio uses
the gadget's playback side; see the [direction map](../design/architecture.md#usb-direction-naming).

On the host:

```sh
lsusb -t
arecord -l
```

Confirm the new capture device and negotiated high-speed connection. Play a
generated tone into the board's gadget ALSA playback device and record from
the corresponding host capture device. Use explicit ALSA hardware devices
and matched formats; do not assume card numbers. Keep playback/recording
errors visible. Inspect the tone recording before proceeding.

## Add one analog input

1. Qualify an ADC module using the [BOM criteria](../../hardware/bom/README.md).
   Confirm its schematic, exposed mode pins, oscillator, clock ownership,
   sample format and input circuit before wiring.
2. Assign the exact McASP header pins and remove conflicting HDMI/pinmux
   ownership in the chosen image. Check that all digital signals are at
   compatible levels. Do not connect analog audio to McASP or GPIO.
3. Establish one clock domain. Measure master clock where required, bit clock
   and frame sync. For stereo 32-bit slots at 96 kHz, bit clock is 6.144 MHz;
   the ADC's required master-clock ratio is a separate constraint.
4. Create the ALSA capture card configuration for the actual ADC and clock
   mode. Record locally on the board first and inspect the waveform, format,
   clipping and noise. This isolates ADC/McASP issues from USB issues.
5. Bridge board capture to gadget playback with a bounded, format-aware audio
   path. Account for clock drift explicitly. A raw arecord-to-aplay pipe may
   help diagnose routing but is not evidence of production clock stability.
6. On the host, select the USB capture device in Audacity, enable one recording
   channel where available, set the matching rate, and record the known input.
   If the ADC transport is stereo, identify the active input and unused channel.
7. Repeat at 96 kHz with 24 valid bits. Capture native PCM with ALSA to verify
   the transport format separately from Audacity's internal/export format.

For a known hardware format, a host-side native recording can use:

```sh
arecord -D hw:CARD=<capture-card>,DEV=0 --dump-hw-params -d 1 /dev/null
arecord -D hw:CARD=<capture-card>,DEV=0 -r 96000 -c <channels> -f <native-format> -d 60 capture.wav
```

Replace placeholders from actual device capabilities. Packed three-byte
24-bit audio commonly uses S24_3LE; 24 valid bits in a larger container need
the driver's actual format. Do not claim bit depth merely from a WAV filename
or an editor setting.

## Evidence to retain

For analog acceptance, retain the circuit/module revision, clock measurements,
ALSA hardware parameters, USB descriptors and speed, mapping, recording length,
error counts, and waveform/spectrum observations. Test source on/off and a
frequency or level change so a synthetic or unrelated host source cannot be
mistaken for the analog input. Follow the staged endurance requirements in
[Product Requirements](../requirements/README.md#staged-acceptance).

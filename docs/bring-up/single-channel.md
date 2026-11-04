# Single-Channel Integration

The first analog result is a known external signal recorded on a Linux host
through the BeagleBone's USB audio connection. A synthetic tone is a separate
diagnostic result.

## Initial configuration

Use a computer headphone output playing a 1-kHz sine wave as the first analog
source. Use one channel of a documented ADC board selected after the
full-channel interface review and qualified before purchase. Keep
microphone preamp design and guitar input buffering outside this first test.

1. Play the tone through a headphone output, starting with output volume low.
2. Probe one output channel against its signal ground. Adjust for approximately
   0.5 V peak-to-peak and confirm a clean 1-kHz waveform without clipping.
3. Feed that channel into the ADC board's documented AC-coupled line input,
   within the board's rated input range. Preserve the required ADC input bias;
   this instruction does not authorize connecting to an unconditioned IC pin.
4. Configure ADC-to-McASP capture and confirm the tone locally on the board.
5. Forward capture through USB and record it in Audacity on the host.
6. Stop/restart the source and change its frequency; verify the recorded
   signal follows those changes.

The 0.5-V peak-to-peak level is a conservative initial test setting, not a
product full-scale specification. A headphone-derived signal is sufficient
for routing verification; it is not a calibrated distortion/noise reference.
Amplifier operating class is not an initial capture requirement.

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

### Record the bootstrap tone in Audacity

For the current mono bootstrap, select ALSA as the host, OSE Audio Bench as
the recording device, one mono channel and a 48000-Hz project sample rate.
Use the displayed device name; its numeric card index can change.

If Audacity is installed as a Snap, grant its recording/device connections:

```sh
sudo snap connect audacity:audio-record
sudo snap connect audacity:alsa
```

Close and reopen Audacity afterward. If it still lists only a default device,
check the Snap launcher's saved preference at
~/snap/audacity/common/Always use PulseAudio. If that file contains
ALWAYS_USE_PULSEAUDIO=1, change it to ALWAYS_USE_PULSEAUDIO=0 and restart
Audacity. Then use Transport > Rescan Audio Devices if needed.

Start recording in Audacity. In a separate terminal, run bbb ssh, then
audioctl tone on the board. After about ten seconds, stop the tone with
Ctrl+C before stopping Audacity. Export a mono 48000-Hz signed 16-bit PCM WAV
and inspect its nonzero signal and frequency. Closing the host stream while
speaker-test is still writing can produce a board-side I/O error; retain
errors and their timing rather than treating every disconnect as sample loss.

This generated-tone test bypasses the ADC and McASP. Audacity's internal
floating-point track format does not increase the bootstrap's 16-bit USB
resolution. Analog input and 24-channel/24-bit/96-kHz operation need their
own tests.

## Add one analog input

1. Qualify an ADC module using the [BOM criteria](../../hardware/bom/README.md).
   Confirm its schematic, exposed mode pins, oscillator, clock ownership,
   sample format and input circuit before wiring. Start with a known line
   source, around 0.5 V peak-to-peak at 1 kHz after checking the circuit's
   input limits and measuring the voltage. The future combo-socket
   MIC/INSTRUMENT circuits are not required for this first test. A PCM1808EVM
   with its fitted 12.288-MHz crystal needs an external clock arrangement
   for the documented 96-kHz/256-fs mode; see the
   [ADC review](../research/adc-selection.md#clock-and-board-traps).
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
[Product Requirements](../requirements.md#staged-acceptance).

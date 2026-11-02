# Product Requirements

These requirements define the intended product and its staged acceptance.
They do not certify the proposed processor, ADCs, or software implementation.
The [architecture](../design/architecture.md) identifies feasibility constraints.

## Purpose and boundary

The product receives analog audio, converts it into synchronized digital
samples, and exposes independent recording channels to a Linux USB host.
The initial product boundary starts at external preamp/line outputs. A
microphone preamp may become a reusable companion product with a documented
electrical interface.

## Functional requirements

| ID | Requirement | Verification |
| --- | --- | --- |
| CAP-001 | The full configuration shall capture 24 independent analog channels simultaneously at 96,000 samples/second/channel with 24 valid sample bits. | Record distinguishable inputs on all channels and inspect rate, format, channel ordering, and sample continuity. |
| CAP-002 | The host shall receive channels separately, without summing, duplication, or an undocumented channel reorder. | Inject identifiable signals into individual inputs and compare the host recording with the documented map. |
| CAP-003 | All ADC channels shall share a coherent sampling clock and a documented frame/reset alignment method. | Measure clocks and record a common signal to check fixed channel alignment and drift. |
| CAP-004 | ADC resolution, serial slot width, USB subslot width, and host file format shall be documented separately. | Inspect datasheets, hardware configuration, USB descriptors, and recorded samples. |
| CAP-005 | Buffer overruns, underruns, dropped samples, and device disconnects shall be observable. Capture software shall not silently report uninterrupted success after an error. | Exercise overload and disconnect recovery and inspect counters/logs and recording behavior. |
| CAP-006 | The reference implementation shall use external audio ADCs feeding BeagleBone McASP with DMA and Linux ALSA. Retaining the BeagleBone at full scale requires demonstrated serial and USB feasibility. | Inspect the signal path and validate sustained capture on the selected board/kernel. |

Here, McASP is the processor's multichannel audio serial port; DMA transfers
samples between that peripheral and memory; ALSA is Linux's audio interface.

## USB and recording requirements

| ID | Requirement | Verification |
| --- | --- | --- |
| USB-001 | The primary host interface shall be USB Audio Class 2.0 (UAC2) over a USB 2.0 high-speed device connection. | Inspect descriptors, negotiated speed, and Linux host driver binding. |
| USB-002 | A supported Linux host shall record through its standard USB audio driver without a proprietary host driver. | Enumerate the device and record using ALSA and a recording application. |
| USB-003 | One analog input shall be recordable in Audacity or an equivalent Linux application as the first end-to-end milestone. | Record an externally supplied tone and speech/music where appropriate; verify the file is non-silent and matches the physical input. |
| USB-004 | Firmware shall advertise only configurations that fit its actual endpoint, controller, FIFO, and clock-handling capabilities. Nominal bus speed alone is insufficient. | Audit packet calculations/descriptors and sustain the advertised stream without loss. |
| USB-005 | The implementation shall manage the rate difference between the audio clock and USB host timing without unbounded buffer growth or hidden sample deletion. | Monitor buffer occupancy and sample continuity during extended capture. |

A generated digital tone can verify the USB/software path. It does not satisfy
USB-003 or prove analog capture.

## Analog and electrical requirements

| ID | Requirement | Verification |
| --- | --- | --- |
| ANA-001 | Every analog input shall have a documented connector, pinout, signal type, impedance, maximum level, common-mode/bias requirement, and ground reference. | Review the input specification and measure the assembled circuit. |
| ANA-002 | Input conditioning shall supply the coupling, bias, attenuation, filtering, and protection required by the selected ADC and source. | Review the ADC reference circuit and verify levels and clipping on hardware. |
| ANA-003 | Mic, line, instrument, and digital sources shall not be treated as electrically interchangeable. Phantom power shall not be present on the initial line-input path. | Inspect source/interface specifications and measure input voltages. |
| ELE-001 | Digital connections shall respect BeagleBone and ADC I/O voltage limits, including startup and unpowered conditions. | Review rail sequencing and measure interface levels. |
| ELE-002 | The design shall document power consumption, supply rails, grounding, decoupling, and the supported cable/power arrangement. | Measure the prototype and review the schematic and BOM. |
| ELE-003 | Shared header functions, including HDMI/eMMC conflicts, shall be resolved for the exact board and device-tree configuration before wiring McASP. | Compare schematic, pinmux, active drivers, and measured pins. |
| ELE-004 | Development hardware shall expose labeled, probe-accessible power rails, ground, analog input, serial data, bit clock, frame sync and required master-clock signals through test points or documented headers. | Verify physical probe clearance, signal identity and accessible ground references on the prototype. |

The first ADC shall be an assembled breakout or evaluation board with its
required support circuitry and a documented integration interface. A bare
converter IC alone does not meet the initial bench requirement. Keep serial
clock wiring short and provide nearby ground access for probing.

## Staged acceptance

Initial engineering acceptance targets below are requirements for development;
they are not existing test results or final product performance claims.

1. USB path: a generated tone reaches a Linux recorder through the BeagleBone
   USB audio device. A 48-kHz/16-bit bootstrap is permitted.
2. One analog input: external ADC capture reaches the host application. Progress
   from a supported bootstrap mode to 96 kHz with 24 valid bits. A stereo ADC
   may transport an unused second channel, with its termination documented.
3. One-channel endurance: record for at least 30 minutes at the target format
   with no reported capture/bridge/USB overruns or underruns and no detected
   sample discontinuities. Document the clock and continuity measurement method.
4. Eight channels: satisfy the format, mapping, synchronization, and endurance
   requirements for one eight-channel converter bank.
5. Full product: record all 24 channels for at least one hour at 96 kHz/24 valid
   bits without reported transport errors or detected discontinuities. Measure
   and publish channel alignment and the measurement uncertainty.

Record the board revision, ADC/module revision, firmware/kernel, host OS,
application, negotiated formats, duration, errors, and signal evidence with
each result. Measure latency, noise, clipping, distortion, and crosstalk before
setting saleable product limits; no numeric audio-quality or latency promise
is established here. A 24-bit sample format does not imply 24 effective bits
of analog performance.

## Productization

- FW-001: Maintain a pinned Yocto source baseline and product layer that builds
  the kernel, bootloader and root filesystem for the selected BeagleBone.
- FW-002: Provide documented UART login, key-based SSH access and a simple
  board menu for status and the USB test tone. Keep private keys and local
  provisioning configuration out of the public repository.
- FW-003: Validate board boot, login and a board-generated USB tone before
  selecting additional analog hardware. Retain source/build/kernel evidence
  separately from hardware observations.
- FW-004: Provide a development workflow that writes the complete SD image
  initially, then deploys ordinary application changes over SSH with the card
  left in the board. Document package/dependency updates, reboot requirements
  and recovery separately. Routine application work shall not require reflashing.
- PRD-001: Maintain reproducible hardware sources, firmware configuration,
  build/install instructions, schematics, connector definitions, and a BOM
  with exact approved manufacturer parts or module revisions.
- PRD-002: Document recovery from interrupted recording, USB reconnect, and
  restart without leaving the device in an unexplained state.
- PRD-003: Record measured power, thermal behavior, audio performance, and
  endurance before advertising the corresponding product capabilities.
- PRD-004: Establish firmware/hardware licensing, USB identification rights,
  manufacturing tests, enclosure/connector requirements, and applicable market
  compliance requirements before product release. No certification or license
  choice is implied by repository visibility.

## Compatibility stretch goal

- WIN-001: Investigate Windows 7 operation after the Linux path works, without
  changing the primary architecture or reducing its 24-channel target.
- WIN-002: Treat Windows 7 UAC2 driver availability, redistribution/licensing,
  signing, host architecture, and recording-application support as separate
  qualification requirements. Do not promise driverless UAC2 on Windows 7.
- WIN-003: A reduced UAC1 diagnostic mode, if later justified, shall be clearly
  distinguished from full-product compatibility and shall not gate Linux work.

Microsoft's in-box UAC2 driver starts with Windows 10 version 1703; Windows 7
therefore needs a separately established solution. See
[Microsoft's UAC2 driver documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/usb-2-0-audio-drivers).

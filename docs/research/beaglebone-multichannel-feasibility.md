# BeagleBone Multichannel Feasibility Review

Status: source-level findings, not a physical 24-channel capture result.
Purchase remains on hold. Requirements are in [one document](../requirements.md);
[TEST-008/009](../test-procedures.md#test-009-board-interface-clocks-power-and-capture-dma)
separate USB, pin/clock review and sustained DMA validation.

## Candidate interface

Three receive serializers carrying eight 32-bit slots each would carry
24 independent channels at 96 kHz with a shared 24.576-MHz bit clock.
This is a topology to validate, not a requirement to buy eight-channel chips.

| Proposed role | Header / SoC pad | Mux / issue |
| --- | --- | --- |
| Receive lane 0 | P9.30 / D12, MCASP0_AXR0, pad offset 0x998 | Mode 0, input. |
| Receive lane 1 | P9.41 / D13, MCASP0_AXR1, pad offset 0x9a8 | Mode 0, input; shares header net with D14/XDMA_EVENT_INTR1 (0x9b4). Keep the other pad from driving this net. |
| Receive lane 2 | P9.28 / C12, MCASP0_AHCLKR, pad offset 0x99c | Mode 2 selects AXR2; stock HDMI uses this as TX. |
| Serial bit clock | P9.31 / A13, MCASP0_ACLKX, offset 0x990 | Mode 0; direction/clock ownership still to be chosen. |
| Frame sync | P9.29 / B13, MCASP0_FSX, offset 0x994 | Mode 0; synchronized TX/RX clock routing must match the DAI format. |
| Master-clock route | P9.25 / A14, MCASP0_AHCLKX, offset 0x9ac | Mode 0 candidate; stock DT declares a gated 24.576-MHz board reference. Verify actual schematic, enable path and loading before relying on it. |

Source mapping: [BeagleBoard's pinmux source](https://github.com/beagleboard/bb.org-overlays/blob/master/tools/pinmux-generator/BeagleBone_Black.dts)
identifies P9.41's second pad as P9_91/P9_41.1, not another physical connector.
Cross-check with the exact board schematic before wiring. This candidate
avoids the P8 LCD/eMMC alternatives; it still requires HDMI audio ownership
to be removed and both P9.41 pads to be configured deliberately.

## Clock limits

[AM335x datasheet SPRS717L, section 7.11](https://www.ti.com/lit/ds/symlink/am3358.pdf)
describes four serializers per McASP and 256-byte FIFOs. Its timing tables
specify minimum clock periods of 20 ns at OPP100 and 40 ns at OPP50.

- 24.576 MHz has a 40.690-ns period: plausible for the proposed lanes, but
  ADC output delay, input setup/hold, edge selection, duty cycle, voltage,
  clock skew and loaded rise/fall times still need a complete timing budget.
- A single 24-slot/32-bit lane would require 73.728 MHz. Padding to 32 slots
  requires 98.304 MHz. Both exceed the stated 50-MHz maximum; do not use
  these as AM335x full-rate candidates.
- Define one owner per clock. Shared frequency alone does not demonstrate
  frame/reset alignment. Measure representative multi-chip starts early.
- The stock board DT's fixed/gated clock is a potential existing resource,
  not proof of a free usable clock output. Check schematic routing, clock
  consumers, enable control and fan-out before purchasing another oscillator.

## Pinned Linux source findings

Inspected kernel commit: 06644f0d7193d7ec39d7fe41939a21953e7a0c65,
Linux 6.6.21 Yocto source. Paths below are relative to that kernel tree.

| Source | Finding | What it does not prove |
| --- | --- | --- |
| sound/soc/ti/davinci-mcasp.c, davinci_mcasp_startup | Capture channel constraint is configured RX serializer count × TDM slots. Three RX serializers and eight slots permit 24 on the CPU side. | Sound-card/codec constraints, DMA order or physical throughput. |
| Same file, mcasp_i2s_hw_param / mcasp_common_hw_param | Activates multiple serializers, configures shared slot masks and receive DMA events. | All required lanes work with the selected ADC format/clock phase. |
| sound/soc/ti/edma-pcm.c | 128-KiB maximum buffer, 64-KiB maximum period, 2–19 periods. | Reliable scheduling at the target rate. |
| sound/soc/codecs/ak5558.c | Existing codec DAI exposes at most eight channels per chip. | A single codec link can expose the complete 24-channel system. |
| sound/soc/soc-pcm.c | Multiple-codec links can retain CPU channel limits and fix per-codec parameters using slot masks. | The required three-lane mapping is already implemented or its order is known. |
| arch/arm/boot/dts/ti/omap/am335x-boneblack-hdmi.dtsi | Stock card has two slots and serial-dir = 0 0 1 0: HDMI playback, no RX serializers. Declares a 24.576-MHz fixed/gated reference. | The baseline image contains a 24-channel capture card. It does not. |

At 24 × 96 kHz × four memory bytes, 128 KiB represents only about 14.22 ms
of audio. An illustrative four-period buffer of 256 frames/period occupies
98,304 bytes and spans 10.667 ms. These are calculations, not a chosen latency
or a demonstrated stable buffer configuration. Profile scheduling and the
USB bridge; avoid recording full-rate data onto the BeagleBone boot card.

The inspected image configuration includes McASP, TI EDMA PCM and the simple
sound-card framework as modules. CONFIG_SND_SOC_AK5558 is not enabled in this
baseline. Selecting that converter would require its driver/configuration
and an actual multiple-codec machine/DT design. Do not change the in-progress
baseline build merely to add an unselected codec.

## Required experiments before product claims

1. Boot the commissioned image, verify USB networking/login and the generated
   mono tone. Then test generated 24-channel target-format USB data and packet
   packing independently of ADC hardware.
2. Review the exact candidate board, supply/logic levels, clock timing,
   existing clock resource and pin ownership. Prepare a reviewable sound-card/
   device-tree configuration with a recovery path, without changing live pins.
3. Choose test hardware that exercises a representative multichannel bank
   and the intended clock/reset arrangement. Review exact manufacturer board
   documentation and complete cost before recommending purchase. A stereo
   board can debug one signal path but cannot close this architecture gate.
4. With known serial patterns, exercise all required RX lanes, validate channel
   interleaving and data bits, measure buffer headroom/error counters and CPU.
   Then integrate actual analog capture and multi-chip reset/phase tests.
5. Run staged endurance on the external SATA host drive. The full 24-hour
   acceptance also needs independent sample-integrity and timing checks.

Conclusion: three receive lanes are plausible from pin/driver source review;
the stock image is not configured for them, and sustained 24-channel DMA,
clock alignment and USB streaming remain unproven. No converter purchase or
platform-feasibility PASS follows from this review.

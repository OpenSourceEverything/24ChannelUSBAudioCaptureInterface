# Yocto Development Baseline

The firmware baseline is Yocto Project 5.0.21 (Scarthgap LTS), using the upstream
beaglebone-yocto board support and the product's meta-ose-audio layer.
[sources.json](sources.json) pins the source commit and the official reference
image checksum. Local sources, build output and provisioning files stay in
the ignored .local directory.

## Talk to the board

From the repository root:

```sh
./device install-cli
bbb
```

The shortcut opens the same terminal as ./device console and can be used from
any directory when ~/.local/bin is on PATH.

Press Enter. At a login prompt, enter root and press Enter. The development
image permits a local UART root login without a password. Exit the host
terminal with Ctrl+]. Automatic adapter selection requires exactly one
candidate; use --port PATH when multiple adapters are connected.

In the custom image, enter audioctl for a numbered menu:

1. Board status, including the network address and audio devices.
2. Enable the initial one-channel 48-kHz/16-bit USB audio device.
3. Send a 1-kHz test tone to the USB host; stop with Ctrl+C.

For Ethernet access, use the IP address shown by board status:

```sh
./device ssh <board-ip>
```

SSH accepts the public key selected during setup. SSH password authentication
is disabled. This is a root-access development image for board bring-up;
production access policy is a separate product configuration.

## Fast first boot

```sh
./device fetch-image
```

This downloads the official core-image-minimal reference image and verifies
its pinned SHA-256. It establishes the boot/UART baseline. It does not contain
our audio menu, SSH configuration or UAC2 kernel additions. Those are supplied
by the source-built ose-audio-image below. Do not report the reference image
as a completed custom firmware build.

After identifying the project card, write it with:

```sh
./device flash /dev/<project-card>
```

This erases that card. The helper requires Linux, Docker and udisksctl, rejects
fixed disks, partitions and mounted host filesystems, and verifies the written
bytes against the image checksum. Select the whole removable card, not a
partition or the host disk. Boot the BeagleBone from the card; the board's boot button
can force the SD bootloader when the eMMC bootloader otherwise takes precedence.

## Build the product development image

Use a supported Linux host with the prerequisites in the
[Yocto system requirements](https://docs.yoctoproject.org/5.0.21/ref-manual/system-requirements.html).
The host helper uses Python 3.11 or newer, Git, Bash, OpenSSH and pyserial.
Builds use two jobs by default.

```sh
./device setup
./device build --parse-only
./device build
```

Setup checks out the exact pinned Poky release and creates build configuration.
It uses ~/.ssh/id_ed25519.pub by default; --public-key PATH selects another
public key. If the default key is absent, setup creates a project key under
.local/ssh. Private keys never enter the layer or Git.

The custom image contains the board menu, ALSA tools, key-based OpenSSH access,
systemd and a kernel configuration fragment for USB UAC2 and McASP.
Built disk images appear under:

```text
.local/build/tmp/deploy/images/beaglebone-yocto/
```

To build the cross-development SDK:

```sh
./device sdk
```

Changing a kernel fragment still requires a built-kernel configuration check
and a hardware boot test. A parsed recipe or generated image alone is not
proof of working USB audio or ADC capture.

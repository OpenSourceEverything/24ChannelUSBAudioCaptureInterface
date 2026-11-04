# Yocto Development Baseline

Install the complete development image once. Leave the microSD in the board
for ordinary code changes: log in and send updates over USB networking or
Ethernet. A 16 GB card is sufficient. The large compiler build runs on the
computer, not the BeagleBone.

The [development turnaround requirements](../docs/requirements.md#development-turnaround) define
the normal edit/test path, initial timing targets, cache retention and when
a separate faster builder is justified.

The baseline is Yocto Project 5.0.21 (Scarthgap LTS), using upstream
beaglebone-yocto support and the product's meta-ose-audio layer.
[sources.json](sources.json) pins the source commit and optional reference
image checksum. Sources, caches, images and provisioning files stay in the
ignored .local directory.

## Board controls

Run ./device install-cli once from the repository. Then use these from any
directory when ~/.local/bin is on PATH:

| Command | Purpose |
| --- | --- |
| bbb | Open UART. Press Enter, then log in as root if asked. Exit with Ctrl+]. |
| bbb ssh | Log in over the USB device cable at 192.168.7.2. |
| bbb ssh BOARD_IP | Log in over Ethernet at the address shown by board status. |
| bbb deploy | Send the current audioctl script over SSH without flashing or rebooting. |
| bbb build | Build the complete development image on the computer. |
| bbb status | Show board/build information and any active card-installation status. |
| bbb flash CARD | Start background image writing and read-back verification on the explicitly selected card. |

Active installation status is checked against the running process. A stopped
job is reported as STOPPED rather than retaining an old BUILDING/WRITING label.

The UART adapter and USB device cable are separate connections. Use the small
mini-USB device socket for the computer connection; the full-size USB-A socket
is the board's host port. UART remains usable if USB networking fails. Use
bbb console --port PATH when multiple UART adapters are connected.

In the new image, audioctl opens a menu for status, USB setup and a 1-kHz test
tone. The initial USB stream is one channel at 48 kHz, 16 bits. Ctrl+C stops the
tone. This tests the USB path and does not demonstrate an external ADC.

The image starts ECM USB networking and UAC2 audio together. The board uses
192.168.7.2/30 and offers the computer 192.168.7.1 through DHCP, without an
Internet gateway or DNS server. Enable automatic IPv4 on the computer's USB
network connection. Use UART or Ethernet to diagnose a conflicting subnet.
Composite operation and available endpoints require a built-kernel hardware
test before this configuration can be called working.

SSH accepts the public key selected during setup; password authentication is
disabled. UART root login has no password in this development image. This is
a bench access policy. Production credentials and USB IDs need a separate
configuration; the current Linux Foundation VID/PID is for local development.

## Build and install once

Use a supported Linux host with the prerequisites in the
[Yocto system requirements](https://docs.yoctoproject.org/5.0.21/ref-manual/system-requirements.html).
The helper uses Python 3.11 or newer, Git, Bash, OpenSSH and pyserial. Builds
use two jobs by default and reuse downloaded sources and compiled cache entries.

```sh
bbb setup
bbb build --parse-only
bbb build
bbb flash /dev/PROJECT_CARD
```

Setup checks out pinned Poky sources and generates build configuration. It
uses ~/.ssh/id_ed25519.pub by default; --public-key PATH selects another key.
If absent, setup creates a project key under .local/ssh. Private keys never
enter the layer or Git. A successful build records its image path and checksum
in .local/image-ready.json; flash selects that completed image.

Flash erases the selected card. It requires a Linux host with disk-sequence
support, a running systemd user session, Docker and udisksctl,
rejects partitions, fixed disks/eMMC and mounted host filesystems, and verifies
the written image by reading it back. It reuses the completed image without a
build, runs independently of the terminal/chat, and saves CHECKING, WRITING,
FLUSHING, VERIFYING and READY/error states. Run bbb status for progress; a
desktop notification reports the outcome when notifications are available.
The saved result remains available even if desktop notification is unavailable.
Keep the computer awake and your user session logged in until completion.

Each run retains its selected image checksum, card identity, log and result
under .local/card-jobs/. Replacing/reinserting a card after job selection aborts
the job; an opened-device sequence check runs before writing. Write-protected
cards stop with an unlock/reinsert instruction. A stopped worker cannot count
as successful verification; its container is stopped and failure is recorded.
READY requires a complete matching SHA-256 read-back, after writes are flushed.
Use bbb flash CARD --wait for scripts that need a success/failure exit code;
bbb flash CARD --verify-only checks an existing card without writing it.
Neither command rebuilds the image. Do not start a second job on the same card.

Native SD readers may report removable=0;
they are accepted only when the kernel identifies their media as SD. Select
the whole card, not a partition. No card is selected automatically.

After verification, power off the board, insert the card and boot. If the old
eMMC bootloader takes precedence, hold the boot button while applying power
to select SD boot. Capture the UART boot log and confirm the new OS before
using network/audio commands. Routine development then keeps the card in place.

The image includes OpenSSH, ALSA tools, systemd, the audio menu, UAC2/ECM kernel
configuration, opkg package management and 1 GiB of extra root filesystem space.
Images appear under .local/build/tmp/deploy/images/beaglebone-yocto/.

## Normal update loop

Edit meta-ose-audio/recipes-core/ose-audio-tools/files/audioctl, then run:

```sh
bbb deploy
bbb ssh
audioctl
```

Deploy validates shell syntax and replaces /usr/bin/audioctl atomically. It
does not update dependencies, keys, services or the kernel. To apply changes
to an already configured USB device, stop the tone, then run
systemctl restart ose-audio-usb from UART; this disconnects USB SSH. Keep
script changes in the recipe so the next clean image includes them.

For packages and new dependencies:

```sh
bbb yocto bitbake RECIPE
bbb install-package PATH_TO_BUILT_PACKAGE.ipk
```

Packages appear under .local/build/tmp/deploy/ipk/. Install packages and any
new dependencies from this same build configuration. opkg reports missing
dependencies; no public package feed is configured. A local package revision
service increments revisions when rebuilt content changes. Preserve its local
database while maintaining an existing package stream. Do not install packages
from an unrelated distribution.

Yocto's application development workflow is also available:

```sh
bbb yocto devtool modify RECIPE
bbb yocto devtool build RECIPE
bbb yocto devtool deploy-target RECIPE root@192.168.7.2
```

Use devtool for recipes in its workspace. It deploys files for development,
bypassing the package manager; dependencies must already be installed. Avoid
mixing devtool and opkg updates for the same files. See the
[deployment reference](https://docs.yoctoproject.org/5.0.21/ref-manual/devtool-reference.html#deploying-your-software-on-the-target-machine).
If setup generated a project key, configure devtool's SSH identity for it;
bbb ssh/deploy/install-package select it automatically.

| Change | Typical action |
| --- | --- |
| Application/menu | Deploy over SSH; restart its process if necessary. |
| New userspace dependency | Build/install matching packages. |
| Service/network configuration | Update its package and reload/restart; retain UART access. |
| Kernel/driver/device tree | Rebuild and validate matching kernel, modules and boot files; transfer over the network and reboot using a board-specific update procedure. |
| Partition layout or unbootable storage | Reinstall/recover the SD image when required. |

Ordinary code work requires no reflash. A tested kernel/boot update procedure
is still needed; installing a kernel IPK alone is not a complete boot update.
A production updater with interruption recovery is future work.

## Platform and product boundaries

Upstream Poky owns the toolchain and board support. The product layer owns its
image, kernel fragment, access configuration, USB service and audio tools.
Keep upstream sources clean; put changes in recipes or narrow append files.
This keeps the build understandable and makes another supported board possible
without rewriting application logic. Clocks, pinmux and peripheral support
still require board-specific validation.

Build the cross-development SDK with bbb sdk. Use bbb yocto bitbake ... for
other tasks in the pinned environment. Recipe parsing, a compiled image,
a hardware boot and a successful recording are separate results. Inspect the
built kernel configuration and test hardware before claiming audio works.

## Optional minimal reference image

bbb fetch-image verifies the pinned official core-image-minimal WIC for boot
diagnosis. Only bbb flash /dev/PROJECT_CARD --bootstrap selects it. It lacks
the custom SSH/menu/UAC2 additions and is not the normal first installation.
Using it would require another custom image installation later.

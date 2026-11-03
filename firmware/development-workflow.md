# Development turnaround and board availability

The normal edit/test loop must update only the changed program. Full image
builds run separately, while an already commissioned board keeps its last
working system. Record build time and board downtime separately: a long
compiler run does not require taking the board out of service for that time.

## Choose the smallest update

| Change | Working path | Board impact |
| --- | --- | --- |
| Audio menu or setup script | Edit source, then bbb deploy. | File replacement needs no reboot. Applying changed USB settings disconnects USB and must be done with UART available. |
| Application logic | Build the changed application with the matching SDK or devtool; deploy its binary/package over SSH. | Restart the affected process when necessary; measure any recording interruption. |
| Added application dependency | Build/install matching packages from this Yocto baseline. | Restart only affected processes; preserve package/version compatibility. |
| Driver, kernel or device tree | Build the affected component using saved build state. | Use a validated module reload or matched boot-file update/reboot procedure. |
| Toolchain, distribution or major image change | Build and validate the image/SDK in the background. | Apply only when ready; retain a recovery route and the last working artifact. |

The first complete image and SDK can require substantial build time. Later
toolchain, distribution or widely shared library changes can also invalidate
many cached tasks. Keep these operations out of the ordinary application
edit loop. They remain part of integration and release validation.

bbb build builds the whole image. For one package, use
bbb yocto bitbake RECIPE. For an application in the devtool workspace, use
bbb yocto devtool build RECIPE and its deploy-target command. See the
[existing update commands](README.md#normal-update-loop).

Build the SDK once for a selected baseline with bbb sdk, then use its
environment-setup script and the application's normal build tool. The SDK
provides a cross-compiler: it runs on the computer and produces programs for
the BeagleBone. Updating application source does not require rebuilding that
SDK. Update it when the target toolchain or required development libraries
change. Keep an application recipe so a clean image can reproduce the same
software; an SDK-only local change must not become an undocumented dependency.

## Initial acceptance targets

These are development goals, not measured performance claims. Measure them
after the first source-built image boots and network access works.

| Scenario | Goal | Measurement boundary |
| --- | --- | --- |
| One menu-message edit | At most 60 seconds | Start deployment through observing the changed menu on the board; no image write or reboot. |
| Small application edit with dependencies and SDK already present | At most 120 seconds | Start incremental compilation through observing the updated application on the board; no complete image rebuild. |
| Incremental driver/kernel change | Establish a measured baseline before setting a limit | Record build, transfer and restart/reboot separately. |
| Full image/SDK build | Background operation with visible live/error status | Record elapsed time, changed baseline, cache reuse and host resources. |

For each run record the source and baseline commits, host CPU/RAM/storage,
cold or warm cache, exact command, elapsed build/transfer/restart time and
seconds the board or recording was unavailable. Repeat a representative warm
edit to distinguish a slow first setup from the normal development loop.

The acceptance check must exercise the real board. An empty compiler benchmark
or a successful file upload alone does not prove the updated program runs.

## Preserve and narrow the build

- Retain source downloads, sstate compiled-task cache, SDK and package revision
  database. The current setup configures DL_DIR, SSTATE_DIR and PRSERV_HOST.
- Use incremental builds during development. Broad clean/cleansstate operations
  require a diagnosed reason because they discard reusable work.
- Keep the product layer and application recipes separate from upstream board
  support, so an application change does not deliberately rebuild the platform.
- Review image dependencies before the next baseline revision. The current
  upstream defaults enable X11; systemd selects libxkbcommon, whose feature
  defaults add X11/Wayland dependencies. This console/audio device should have
  an explicitly reviewed headless configuration, while retaining ALSA, USB,
  networking, login and required board support. Compare task/dependency graphs
  and test the resulting image before adopting the smaller baseline.
- Keep the current first build progressing; make platform feature reductions
  as a separate measured baseline change rather than repeatedly restarting
  bring-up to tune build options.

## Faster builder decision

Profile the missed target first: source downloads, compilation, packaging,
storage and deployment have different remedies. Use a faster Linux builder
when compute/storage time or the frequency of full builds justifies it.
Application iteration and board availability must still have their own fast
path after a builder upgrade.

A separate build host must use the same source pins and reviewed configuration.
Transfer versioned images, packages and the matching SDK back to the bench.
Reuse compatible download/sstate caches; avoid treating a copied temporary
build tree with host-specific paths as the portable development interface.
Keep private SSH keys and local provisioning out of shared caches/repositories.

## Primary references

- [Using the SDK toolchain directly](https://docs.yoctoproject.org/5.0.21/sdk-manual/working-projects.html)
- [Yocto build speed controls and feature reduction](https://docs.yoctoproject.org/5.0.21/dev-manual/speeding-up-build.html)
- [devtool build and deployment](https://docs.yoctoproject.org/5.0.21/ref-manual/devtool-reference.html)

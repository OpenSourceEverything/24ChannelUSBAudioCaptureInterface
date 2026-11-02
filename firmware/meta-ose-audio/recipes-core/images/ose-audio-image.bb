SUMMARY = "BeagleBone audio development image"
LICENSE = "MIT"

inherit core-image

IMAGE_INSTALL = "packagegroup-core-boot os-release openssh alsa-utils kernel-modules ose-audio-tools"
IMAGE_LINGUAS = "en-us"
IMAGE_ROOTFS_EXTRA_SPACE = "131072"

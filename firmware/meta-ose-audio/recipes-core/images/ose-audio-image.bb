SUMMARY = "BeagleBone audio development image"
LICENSE = "MIT"

inherit core-image

IMAGE_FEATURES += "package-management"
IMAGE_INSTALL = "packagegroup-core-boot os-release openssh alsa-utils kernel-modules ose-audio-tools"
IMAGE_LINGUAS = "en-us"
IMAGE_BOOT_FILES:append = " uEnv.txt"
do_image_wic[depends] += "ose-audio-bootfiles:do_deploy"
# Leave 1 GiB for packages and bench development without replacing the image.
IMAGE_ROOTFS_EXTRA_SPACE = "1048576"

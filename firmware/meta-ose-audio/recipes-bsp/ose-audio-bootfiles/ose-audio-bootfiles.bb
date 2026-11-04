SUMMARY = "SD boot bridge for BeagleBone Black with legacy eMMC U-Boot"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit allarch deploy nopackages

SRC_URI = "file://uEnv.txt"
INHIBIT_DEFAULT_DEPS = "1"

do_deploy() {
    install -d ${DEPLOYDIR}
    install -m 0644 ${WORKDIR}/uEnv.txt ${DEPLOYDIR}/uEnv.txt
}
addtask deploy after do_install before do_build

SUMMARY = "Audio bench menu, USB gadget and key-based development login"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302e"

inherit allarch

FILESEXTRAPATHS:prepend := "${AUDIO_PROVISION_DIR}:"
SRC_URI = "file://audioctl file://motd file://authorized_keys"
RDEPENDS:${PN} = "alsa-utils-speakertest alsa-utils-aplay kmod openssh"

do_install() {
    install -D -m 0755 ${WORKDIR}/audioctl ${D}${bindir}/audioctl
    install -D -m 0644 ${WORKDIR}/motd ${D}${sysconfdir}/motd
    install -D -m 0600 ${WORKDIR}/authorized_keys ${D}/home/root/.ssh/authorized_keys
    chmod 0700 ${D}/home/root/.ssh
}

FILES:${PN} += "/home/root/.ssh"

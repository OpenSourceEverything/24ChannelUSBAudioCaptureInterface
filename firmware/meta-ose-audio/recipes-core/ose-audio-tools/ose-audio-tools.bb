SUMMARY = "Audio bench menu, USB gadget and key-based development login"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit allarch systemd

FILESEXTRAPATHS:prepend := "${AUDIO_PROVISION_DIR}:"
SRC_URI = "file://audioctl file://motd file://authorized_keys file://ose-audio-usb.service file://20-ose-usb.network"
RDEPENDS:${PN} = "alsa-utils-speakertest alsa-utils-aplay kmod openssh systemd"
SYSTEMD_SERVICE:${PN} = "ose-audio-usb.service"

do_install() {
    install -D -m 0755 ${WORKDIR}/audioctl ${D}${bindir}/audioctl
    install -D -m 0644 ${WORKDIR}/motd ${D}${sysconfdir}/motd
    install -D -m 0600 ${WORKDIR}/authorized_keys ${D}/home/root/.ssh/authorized_keys
    chmod 0700 ${D}/home/root/.ssh
    install -D -m 0644 ${WORKDIR}/ose-audio-usb.service ${D}${systemd_system_unitdir}/ose-audio-usb.service
    install -D -m 0644 ${WORKDIR}/20-ose-usb.network ${D}${sysconfdir}/systemd/network/20-ose-usb.network
}

FILES:${PN} += "/home/root/.ssh"

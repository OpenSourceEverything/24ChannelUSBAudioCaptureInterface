# Customize the login message through the recipe that owns /etc/motd.
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://ose-audio-motd"

do_install:append() {
    install -m 0644 ${WORKDIR}/ose-audio-motd ${D}${sysconfdir}/motd
}

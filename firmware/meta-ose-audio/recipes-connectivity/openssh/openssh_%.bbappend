FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://ose-sshd-config"

do_install:append() {
    install -m 0600 ${WORKDIR}/ose-sshd-config ${D}${sysconfdir}/ssh/sshd_config
    install -m 0600 ${WORKDIR}/ose-sshd-config ${D}${sysconfdir}/ssh/sshd_config_readonly
}

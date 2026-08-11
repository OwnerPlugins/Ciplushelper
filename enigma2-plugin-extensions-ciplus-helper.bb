SUMMARY = "CI+ Helper Plugin for Enigma2"
MAINTAINER = "Lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "GPLv2"

inherit gitpkgv

SRCREV = "${AUTOREV}"
PV = "6.0+git${SRCPV}"
PKGV = "6.0+git${GITPKGV}"
VER = "6.0"
PR = "r0"

S = "${WORKDIR}/git"
SRC_URI = "git://github.com/Belfagor2005/ciplushelper-8.4.git;protocol=https;branch=master"

PLUGIN_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"

# Must declare ALL files that end up in the package
FILES:${PN} = "${PLUGIN_DIR}/* /etc/enigma2/*"

RDEPENDS:${PN} = "enigma2"

do_install() {
    # 1. Copy ONLY the usr/ directory (plugin + binaries + locale)
    if [ -d "${S}/usr" ]; then
        cp -rp ${S}/usr/* ${D}/usr/
    fi

    # 2. Copy ONLY etc/enigma2/ from the repo into /etc/enigma2/ on the box
    if [ -d "${S}/etc/enigma2" ]; then
        install -d ${D}/etc/enigma2
        cp -rp ${S}/etc/enigma2/* ${D}/etc/enigma2/
    fi

    # 3. Set execute permissions on binaries and scripts
    find ${D}${PLUGIN_DIR} -name "ciplushelper" -exec chmod 755 {} \;
    chmod +x ${D}${PLUGIN_DIR}/plugin.py
    chmod +x ${D}${PLUGIN_DIR}/translate_utils.py
    chmod +x ${D}${PLUGIN_DIR}/update_translations.py
    chmod +x ${D}${PLUGIN_DIR}/ciplushelper.sh 2>/dev/null || true
    chmod +x ${D}${PLUGIN_DIR}/stop_oscam.sh 2>/dev/null || true
}

do_install[cleandirs] = "${D}${PLUGIN_DIR}"ipped)
INSANE_SKIP:${PN} += "already-stripped"

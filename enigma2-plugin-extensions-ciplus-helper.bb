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

# Plugin path
PLUGIN_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"

# Binaries are in the plugin folder, installed by postinst
FILES:${PN} = "${PLUGIN_DIR}/*"

# Dependencies (if needed)
RDEPENDS:${PN} = "enigma2"

do_install() {
    # Create plugin directory
    install -d ${D}${PLUGIN_DIR}

    # Copy entire plugin folder
    cp -rp ${S}/* ${D}${PLUGIN_DIR}/

    # Remove .git if present
    rm -rf ${D}${PLUGIN_DIR}/.git 2>/dev/null || true

    # Remove unwanted files (if any)
    rm -f ${D}${PLUGIN_DIR}/.gitignore 2>/dev/null || true

    # Ensure all binaries are executable
    find ${D}${PLUGIN_DIR} -name "ciplushelper" -exec chmod 755 {} \;

    chmod +x ${D}${PLUGIN_DIR}/plugin.py
    chmod +x ${D}${PLUGIN_DIR}/translate_utils.py
    chmod +x ${D}${PLUGIN_DIR}/update_translations.py
}

do_install[cleandirs] = "${D}${PLUGIN_DIR}"

# No need to strip binaries (they're already stripped)
INSANE_SKIP:${PN} += "already-stripped"

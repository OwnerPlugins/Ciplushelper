#!/bin/bash
## command line == wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash

version='7.1'
changelog='
**Version 7.1 - Init script fix**
- Fixed: init script detected itself as the running daemon (never started it)
- Fixed: stop/restart killed the init script itself
- Fixed: plugin status line always showed "Not running"
- Fixed: "Install WORKING binary" now stops the daemon before copying
- Fixed: no more nested /etc/ciplus/ciplus on repeated install
- Fixed: autostart is preserved when the plugin is updated
- Installer: postinst is now also looked up in CONTROL/, CRLF stripped from scripts
'

TMPPATH=/tmp/Ciplushelper-install
FILEPATH=/tmp/Ciplushelper-main.tar.gz

# Plugin paths
if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/Ciplushelper
fi

echo "========================================="
echo "  CI+ Helper Plugin Installer v$version"
echo "========================================="
echo ""

cleanup() {
    echo "Cleaning up temporary files..."
    [ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
    [ -f "$FILEPATH" ] && rm -f "$FILEPATH"
}

detect_os() {
    if [ -f /var/lib/dpkg/status ]; then
        OSTYPE="DreamOs"
        STATUS="/var/lib/dpkg/status"
    elif [ -f /etc/opkg/opkg.conf ] || [ -f /var/lib/opkg/status ]; then
        OSTYPE="OE"
        STATUS="/var/lib/opkg/status"
    elif [ -f /etc/debian_version ]; then
        OSTYPE="Debian"
        STATUS="/var/lib/dpkg/status"
    else
        OSTYPE="Unknown"
        STATUS=""
    fi
    echo "Detected OS type: $OSTYPE"
}

detect_os

if ! command -v wget >/dev/null 2>&1; then
    echo "Installing wget..."
    case "$OSTYPE" in
        "DreamOs"|"Debian")
            apt-get update && apt-get install -y wget || { echo "Failed to install wget"; exit 1; }
            ;;
        "OE")
            opkg update && opkg install wget || { echo "Failed to install wget"; exit 1; }
            ;;
        *)
            echo "Unsupported OS type. Cannot install wget."
            exit 1
            ;;
    esac
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "Python3 image detected"
    PYTHON="PY3"
else
    echo "Python2 image detected"
    PYTHON="PY2"
fi

install_pkg() {
    local pkg=$1
    if [ -z "$STATUS" ] || ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "Installing $pkg..."
        case "$OSTYPE" in
            "DreamOs"|"Debian")
                apt-get update && apt-get install -y "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            "OE")
                opkg update && opkg install "$pkg" || { echo "Could not install $pkg, continuing anyway..."; }
                ;;
            *)
                echo "Cannot install $pkg on unknown OS type, continuing..."
                ;;
        esac
    else
        echo "$pkg already installed"
    fi
}

# Install dependencies
install_pkg "tar"

cleanup
mkdir -p "$TMPPATH"

echo "Downloading CI+ Helper v$version..."
wget --no-check-certificate 'https://github.com/OwnerPlugins/Ciplushelper/archive/refs/heads/main.tar.gz' -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "Failed to download CI+ Helper package!"
    cleanup
    exit 1
fi

echo "Extracting package..."
tar -xzf "$FILEPATH" -C "$TMPPATH"
if [ $? -ne 0 ]; then
    echo "Failed to extract CI+ Helper package!"
    cleanup
    exit 1
fi

echo "Installing plugin files..."
mkdir -p "$PLUGINPATH"

# Find the extracted directory
EXTRACTED_DIR=$(find "$TMPPATH" -type d -name "Ciplushelper*" -o -name "ciplushelper*" | head -1 2>/dev/null)

if [ -z "$EXTRACTED_DIR" ] || [ ! -d "$EXTRACTED_DIR" ]; then
    echo "Could not find extracted plugin directory!"
    cleanup
    exit 1
fi

echo "Found extracted directory: $EXTRACTED_DIR"

# Copy only the usr/ directory structure
if [ -d "$EXTRACTED_DIR/usr" ]; then
    echo "Copying usr/ to / ..."
    cp -r "$EXTRACTED_DIR/usr"/* / 2>/dev/null
    echo "Plugin files copied to system"
else
    # Fallback: find plugin.py and copy that directory
    PLUGIN_SRC=$(find "$EXTRACTED_DIR" -type f -name "plugin.py" -exec dirname {} \; | head -1 2>/dev/null)
    if [ -n "$PLUGIN_SRC" ] && [ -d "$PLUGIN_SRC" ]; then
        echo "Found plugin source: $PLUGIN_SRC"
        cp -r "$PLUGIN_SRC"/* "$PLUGINPATH/" 2>/dev/null
        echo "Plugin files copied to $PLUGINPATH"
    else
        echo "ERROR: Could not find plugin files!"
        echo "Available directories:"
        find "$EXTRACTED_DIR" -type d | head -20
        cleanup
        exit 1
    fi
fi

# Strip CRLF from shell scripts (a CRLF shebang makes them unexecutable)
sed -i 's/\r$//' "$PLUGINPATH/ciplushelper.sh" 2>/dev/null
POSTINST=""
for f in "$PLUGINPATH/postinst" "$EXTRACTED_DIR/CONTROL/postinst"; do
    [ -f "$f" ] && { POSTINST="$f"; break; }
done
[ -n "$POSTINST" ] && sed -i 's/\r$//' "$POSTINST" 2>/dev/null

# Ensure all binaries are executable
find "$PLUGINPATH" -name "ciplushelper" -exec chmod 755 {} \;
chmod 755 "$PLUGINPATH/ciplushelper.sh" 2>/dev/null
chmod 755 "$PLUGINPATH/postinst" 2>/dev/null
chmod 755 "$PLUGINPATH/prerm" 2>/dev/null
chmod 755 "$PLUGINPATH/postrm" 2>/dev/null
chmod 755 "$PLUGINPATH/plugin.py" 2>/dev/null
chmod 755 "$PLUGINPATH/__init__.py" 2>/dev/null

# Run postinst manually (it writes info.txt, installs binary, init script and certificates)
if [ -n "$POSTINST" ]; then
    echo "Running postinst ($POSTINST)..."
    sh "$POSTINST"
else
    echo "WARNING: postinst not found - info.txt, binary and init script were NOT installed."
    echo "         Open the plugin and use 'Install WORKING binary' to complete the setup."
fi

# FORCE plugin cache rebuild (fix for DM8000/OpenPLi)
echo "Rebuilding plugin cache..."
rm -f /tmp/plugin_list*
rm -f /tmp/epgcache*

sync

# Detection info - use head -1 for BusyBox compatibility
if [ -f /etc/hostname ]; then
    box_type=$(head -1 /etc/hostname 2>/dev/null || cat /etc/hostname 2>/dev/null || echo "Unknown")
else
    box_type="Unknown"
fi

if [ -f /usr/lib/enigma.info ]; then
    distro_value=$(grep '^distro=' /usr/lib/enigma.info 2>/dev/null | awk -F '=' '{print $2}')
    distro_version=$(grep '^imageversion=' /usr/lib/enigma.info 2>/dev/null | awk -F '=' '{print $2}')
elif [ -f /etc/image-version ]; then
    distro_value=$(grep '^distro=' /etc/image-version 2>/dev/null | awk -F '=' '{print $2}')
    distro_version=$(grep '^version=' /etc/image-version 2>/dev/null | awk -F '=' '{print $2}')
else
    distro_value="Unknown"
    distro_version="Unknown"
fi

python_vers=$(python --version 2>&1 2>/dev/null || echo "Python not found")
arch=$(uname -m)

cat <<EOF

#########################################################
#               INSTALLED SUCCESSFULLY                  #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
#########################################################
#                                                       #
#  Test from telnet:                                    #
#    /etc/init.d/ciplushelper start                     #
#  Check a CI+ channel, then open the plugin and        #
#  enable autostart if everything works.                #
#  (Only if the daemon is missing, use the plugin       #
#   entry "Install WORKING binary")                     #
#                                                       #
#  Check debug log: /home/root/ciplus_debug.log        #
#                                                       #
#########################################################
#           Please REBOOT your device to apply          #
#########################################################
^^^^^^^^^^Debug information:
BOX MODEL: $box_type
ARCHITECTURE: $arch
OS SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: ${distro_value:-Unknown}
IMAGE VERSION: ${distro_version:-Unknown}
PLUGIN VERSION: $version
PLUGIN PATH: $PLUGINPATH
CHANGELOG:
$changelog
EOF

cleanup
exit 0
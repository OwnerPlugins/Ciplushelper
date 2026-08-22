#!/bin/bash
## command line == wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash

version='7.0'
changelog='
**Version 7.0 - Major Update**
- Unified ConfigListScreen interface - all settings and actions in one list
- Real-time daemon status display (Running/Not running)
- Automatic init script copying with CRLF fix
- Certificate sync to /etc/ssl/certs/
- Install WORKING binary (hd51/6.new - 1010KB)
- CI modules detection with slot status
- ConfigAction class for menu commands
- All code comments and debug messages in English
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

# Install dependencies (skip tar if already installed)
if ! command -v tar >/dev/null 2>&1; then
    install_pkg "tar"
fi

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

# Find the extracted directory - more robust search
EXTRACTED_DIR=""
if [ -d "$TMPPATH/Ciplushelper-main" ]; then
    EXTRACTED_DIR="$TMPPATH/Ciplushelper-main"
elif [ -d "$TMPPATH/ciplushelper-main" ]; then
    EXTRACTED_DIR="$TMPPATH/ciplushelper-main"
else
    # Try to find any directory containing plugin.py
    EXTRACTED_DIR=$(find "$TMPPATH" -type f -name "plugin.py" -exec dirname {} \; | head -1)
fi

if [ -z "$EXTRACTED_DIR" ] || [ ! -d "$EXTRACTED_DIR" ]; then
    echo "Could not find extracted plugin directory!"
    echo "Available directories in $TMPPATH:"
    ls -la "$TMPPATH"
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
    PLUGIN_SRC=$(find "$EXTRACTED_DIR" -type f -name "plugin.py" -exec dirname {} \; | head -1)
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

# Ensure all binaries are executable
find "$PLUGINPATH" -name "ciplushelper" -exec chmod 755 {} \;
chmod 755 "$PLUGINPATH/ciplushelper.sh" 2>/dev/null
chmod 755 "$PLUGINPATH/postinst" 2>/dev/null
chmod 755 "$PLUGINPATH/prerm" 2>/dev/null
chmod 755 "$PLUGINPATH/postrm" 2>/dev/null
chmod 755 "$PLUGINPATH/plugin.py" 2>/dev/null
chmod 755 "$PLUGINPATH/__init__.py" 2>/dev/null

# Run postinst manually
if [ -f "$PLUGINPATH/postinst" ]; then
    echo "Running postinst..."
    sh "$PLUGINPATH/postinst"
fi

sync

# Detection info - use head -1 for BusyBox compatibility
if [ -f /etc/hostname ]; then
    box_type=$(head -1 /etc/hostname 2>/dev/null || echo "Unknown")
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
#  To complete setup, open the plugin and select:      #
#  "Install WORKING binary (recommended)"              #
#                                                       #
#  Then enable autostart if everything works.          #
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
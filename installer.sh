#!/bin/bash
## command line == wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash
version='6.1'
changelog='Unified hardware detection for ARM/MIPSEL boxes\n- WQHD (2560x1440) skin support\n- ARM/Zgemma-ARM separation with dedicated binary\n- CI+ slot management (0 and 1)\n- "Restart GUI" command\n- Faster process detection using pgrep\n- Code refactoring with commands dictionary\n- Fixed model detection for boxes without getImageVersion'

TMPPATH=/tmp/Ciplushelper-install
FILEPATH=/tmp/Ciplushelper-main.tar.gz

# Plugin paths
if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/Ciplushelper
fi

echo "Starting CI+ Helper installation..."

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

echo "Downloading CI+ Helper..."
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

# Find the extracted plugin directory
EXTRACTED_DIR=$(find "$TMPPATH" -type d -name "Ciplushelper*" -o -name "ciplushelper*" | head -1)

if [ -n "$EXTRACTED_DIR" ] && [ -d "$EXTRACTED_DIR" ]; then
    echo "Found extracted plugin in: $EXTRACTED_DIR"
    
    # Copy all files from extracted directory to plugin path
    cp -r "$EXTRACTED_DIR"/* "$PLUGINPATH/" 2>/dev/null
    
    # If the extracted directory has a different structure (e.g., Ciplushelper-main/Ciplushelper/)
    if [ ! -f "$PLUGINPATH/plugin.py" ]; then
        # Try to find plugin.py in subdirectories
        SUBDIR=$(find "$EXTRACTED_DIR" -type f -name "plugin.py" -exec dirname {} \; | head -1)
        if [ -n "$SUBDIR" ]; then
            echo "Found plugin.py in: $SUBDIR"
            cp -r "$SUBDIR"/* "$PLUGINPATH/" 2>/dev/null
        else
            echo "Could not find plugin.py in extracted archive"
            cleanup
            exit 1
        fi
    fi
else
    echo "Could not find plugin files in extracted archive"
    echo "Available directories:"
    find "$TMPPATH" -type d | head -20
    cleanup
    exit 1
fi

# Ensure all binaries are executable
find "$PLUGINPATH" -name "ciplushelper" -exec chmod 755 {} \;
chmod 755 "$PLUGINPATH/ciplushelper.sh" 2>/dev/null
chmod 755 "$PLUGINPATH/postinst" 2>/dev/null
chmod 755 "$PLUGINPATH/prerm" 2>/dev/null
chmod 755 "$PLUGINPATH/postrm" 2>/dev/null

# Run postinst manually
if [ -f "$PLUGINPATH/postinst" ]; then
    echo "Running postinst..."
    sh "$PLUGINPATH/postinst"
fi

sync

# --- Detection info ---
box_type=$(head -n 1 /etc/hostname 2>/dev/null || echo "Unknown")

# Detect image version
if [ -f /usr/lib/enigma.info ]; then
    # OpenPLi
    distro_value=$(grep '^distro=' /usr/lib/enigma.info 2>/dev/null | awk -F '=' '{print $2}')
    distro_version=$(grep '^imageversion=' /usr/lib/enigma.info 2>/dev/null | awk -F '=' '{print $2}')
elif [ -f /etc/image-version ]; then
    # OpenATV
    distro_value=$(grep '^distro=' /etc/image-version 2>/dev/null | awk -F '=' '{print $2}')
    distro_version=$(grep '^version=' /etc/image-version 2>/dev/null | awk -F '=' '{print $2}')
else
    distro_value="Unknown"
    distro_version="Unknown"
fi

python_vers=$(python --version 2>&1)
arch=$(uname -m)

cat <<EOF

#########################################################
#               INSTALLED SUCCESSFULLY                  #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
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

exit 0
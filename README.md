<h1 align="center">⚙️ CI+ Helper Plugin for Enigma2

[![Version](https://img.shields.io/badge/Version-7.0-blue.svg)](https://github.com/OwnerPlugins/Ciplushelper)
[![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg)](https://www.enigma2.net)
[![Python](https://img.shields.io/badge/Python3-only-orange.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
</h1>
<p align="center">
  <a href="https://github.com/OwnerPlugins">
    <img src="https://komarev.com/ghpvc/?username=OwnerPlugins&label=Repository%20Views&color=blueviolet" alt="Visitors">
  </a>
</p>

<p align="center">
  <a href="https://ko-fi.com/lululla">
    <img src="https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="Donate via Ko-fi">
  </a>
  <a href="https://paypal.me/OwnerPlugins">
    <img src="https://img.shields.io/badge/_-Donate-green.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="Donate via PayPal">
  </a>
</p>

---

## 📌 Description

**CI+ Helper** is a comprehensive Enigma2 plugin for managing the `ciplushelper` daemon, enabling CI+ certification across ARM and MIPSEL set-top boxes.

The plugin automatically detects your hardware architecture and installs the optimal binary for your device, ensuring maximum compatibility and performance.

---

## ✨ Features

- **Automatic Hardware Detection** – Supports ARM and MIPSEL boxes via `/proc/stb/`, `opkg`, and `uname` fallbacks
- **Multi-Architecture Support** – Separate binaries for generic ARM, Zgemma ARM, HD51 ARM, and MIPSEL
- **WQHD (2560×1440) Skin** – Optimized interface for 2K displays
- **CI+ Slot Management** – Enable/disable CI+ certification per slot (0 and 1) on ARM boxes
- **Zgemma ARM Binary** – Dedicated binary for Zgemma models (H6, H7, H9, H10) using HD51/6.new optimized build
- **Certificates Management** – Install/remove `/etc/ciplus` certificates with automatic sync to `/etc/ssl/certs/`
- **Autostart Control** – Enable/disable `ciplushelper` at boot via init script
- **Service Control** – Start/stop `ciplushelper` daemon with real-time status display
- **Init Script Management** – Automatically copies and configures `/etc/init.d/ciplushelper`
- **Open CI Assignment** – Quick access to the system plugin for mapping channels to CI slots (OpenPLi/OpenATV)
- **Update Plugin** – Update directly from the menu via `installer.sh`

---

## 📦 Supported Models

### ARM Architecture (Binary from hd51/6.new - 1010KB)
- **Zgemma:** H6, H7, H9combo(se), H9twin(se), H10
- **HD51, VS1500, Pulse 4K(mini), h17, 8100s, hd61**
- **Uclan (ustym4kpro), DM8000**

### ARM Architecture (Alternative - 1.7MB)
- **Zgemma ARM** – alternative binary for specific models

### MIPSEL Architecture
- Mutant (hd1500/hd2400)
- Xtrend (et8000/et10000)
- Formuler (f1/f3/f4)
- Triplex, Cube

---

## 📸 Screenshots

| Main Menu | About | CI+ Slot Management |
|-----------|-------|---------------------|
| ![Menu](screenshots/menu.png) | ![About](screenshots/about.png) | ![Slots](screenshots/slots.png) |

*(Screenshots coming soon)*

---

## 🔧 Installation

### Via Telnet IPK (recommended)
```bash
opkg install /tmp/enigma2-plugin-extensions-ci-plus-helper_7.0_all.ipk
```

### Via Command Line
```bash
wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash
```

### From GitHub (development)
```bash
git clone https://github.com/OwnerPlugins/Ciplushelper.git /tmp/ciplushelper
cp -r /tmp/ciplushelper/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper /usr/lib/enigma2/python/Plugins/Extensions/
```

### Post-Installation
After installation, **reboot your box**:
```bash
reboot
```

---

## 🚀 Usage

1. Open the **Plugin Browser** (Menu → Plugins)
2. Select **CI+ Helper**
3. The plugin automatically detects your model and shows:
   - **CI modules detected** – shows which CI slots are present
   - **Enable auto-check module** – toggles automatic module checking
   - **CI+ Helper status** – shows if the daemon is running
   - **Enable/Disable ciplushelper autostart** – manages boot startup
   - **Start/Stop ciplushelper** – manual service control
   - **Install WORKING binary (recommended)** – installs the correct binary for your device
   - **Install /etc/ciplus** – installs certificates (if missing)
   - **Open CI Assignment** – opens the CI assignment plugin
   - **Update plugin** – updates to the latest version
   - **Supported models** – displays compatible devices

4. For first-time setup on ARM/Zgemma boxes:
   - Select **"Install WORKING binary (recommended)"**
   - The plugin will:
     - Copy certificates to `/etc/ciplus/` and `/etc/ssl/certs/`
     - Copy the init script to `/etc/init.d/ciplushelper`
     - Install the correct binary (hd51/6.new - 1010KB)
     - Start the daemon automatically
   - Wait for confirmation that the daemon is running

---

## 🛠️ Development

### Build from source
```bash
git clone https://github.com/OwnerPlugins/Ciplushelper.git
cd ciplushelper
# Build IPK
opkg-build .
```

---

## 📋 Changelog

### v7.0 - Major Update
- **New:** Unified ConfigListScreen interface – all settings and actions in one list
- **New:** Real-time daemon status display (Running/Not running) with pgrep detection
- **New:** Automatic init script copying from `ciplushelper.sh` to `/etc/init.d/ciplushelper`
- **New:** Certificate sync to `/etc/ssl/certs/` in addition to `/etc/ciplus/`
- **New:** "Install WORKING binary (recommended)" – uses the verified hd51/6.new binary (1010KB)
- **New:** CI modules detection with slot status display
- **New:** Action keys with ConfigAction class for menu commands
- **Improved:** Better error handling with debug logging to `/home/root/ciplus_debug.log`
- **Improved:** Automatic binary selection based on hardware detection
- **Improved:** Start/Stop commands now verify daemon status
- **Improved:** Skin dimensions optimized for WQHD, FHD, and HD displays
- **Fixed:** ConfigNothing TypeError – replaced with custom ConfigAction class
- **Fixed:** ci_auto_check_module moved under config.plugins.cionoff
- **Fixed:** Certificates installation in both `/etc/ciplus/` and `/etc/ssl/certs/`
- **Fixed:** Init script not being copied correctly
- **Fixed:** Binary selection for Zgemma ARM models (uses hd51/6.new)

### v6.9
- **Changed:** All code comments and debug messages now in English
- **Changed:** Plugin now always visible in plugin list (removed SystemInfo check)

### v6.8
- **Disable autostart by default; bump to 6.8
- **Apply auto PEP8 aggressive fixes

### v6.7
- **Remove** installer, simplify plugin

### v6.6
- **Update Locale
- **Bump version to 6.6
- **Add debug logging and improve autostart/CI handling
- **Refactor Ciplushelper plugin: autostart & UI
- **Disable 'Restart GUI' and switch plugin menu
- **Add shebang and normalize encoding headers
- **Apply auto PEP8 aggressive fixes

### v6.5
- **Bump** version to 6.5 and robustness fixes
- **Apply** auto PEP8 aggressive fixes
- **Detect** CI module and conditionally register plugin
- **Apply** auto PEP8 aggressive fixes

### v6.4
- **Improved:** Oscam detection now uses `ps -A | grep -i` for universal compatibility
- **Improved:** Oscam status is now updated in real-time using `onShown` callback
- **Improved:** Toggle Oscam uses PID-based kill and binary detection via `/proc/<pid>/exe`
- **Fixed:** Oscam toggle now properly starts Oscam using the exact binary path

### v6.3
- **New:** Oscam toggle – start/stop Oscam directly from the plugin menu
- **New:** "Open CI Assignment" menu entry

### v6.2
- **New:** "Update plugin" command via `installer.sh`
- **Fixed:** `TypeError` in MessageBox caused by skin inheritance
- **Improved:** Skin dimensions for WQHD, FHD, and HD displays

### v6.1
- **Fixed:** Installer now copies only the `usr/` directory structure
- **Improved:** `postinst` script now detects `ustym4kpro`, `dm8000`, and all generic ARM/MIPSEL boxes

### v6.0
- **New:** WQHD (2560×1440) skin support
- **New:** ARM/Zgemma-ARM separation with dedicated binary
- **New:** CI+ slot management (0 and 1)
- **New:** "Restart GUI" command
- **Improved:** Unified hardware detection with multiple fallbacks
- **Improved:** Faster process detection using `pgrep`
- **Improved:** Code refactoring with `commands` dictionary
- **Fixed:** Model detection for boxes without `getImageVersion`
- **Fixed:** Skin dimensions for FHD displays
- **Fixed:** `postrm` script to properly stop service before removal

---

## ⚠️ Important Notes

### Oscam / SoftCAM Conflict
If you have **Oscam** or any other softCAM running on your box, it may conflict with the CI+ helper daemon. Both try to access the same hardware descrambler. To use CI+ helper, stop or disable Oscam temporarily:
```bash
/etc/init.d/softcam stop   # or use your softcam's stop command
```

### Daemon Status Verification
After starting the daemon, the plugin shows "Running" if the process is detected. However, if the daemon starts and then crashes, the status will show "Not running". Check the debug log for details:
```bash
cat /home/root/ciplus_debug.log
```

### Binary Selection
- **ARM/Zgemma models:** Uses `hd51/6.new/ciplushelper` (1010KB) – the verified working binary
- **Alternative:** `zgemma-arm/ciplushelper` (1.7MB) – available for specific models
- **MIPSEL models:** Uses `mipsel32/ciplushelper` (1.5MB)

### First-Time Setup
For ARM/Zgemma boxes, always run **"Install WORKING binary (recommended)"** after installation. This ensures:
1. Certificates are correctly installed
2. Init script is properly configured
3. The correct binary is installed
4. The daemon is started and verified

### Debug Logging
The plugin writes debug information to `/home/root/ciplus_debug.log`. Check this file if you encounter issues:
```bash
tail -f /home/root/ciplus_debug.log
```

---

## 🔍 Troubleshooting

### Daemon not starting
1. Check the debug log: `cat /home/root/ciplus_debug.log`
2. Verify binary exists: `ls -la /usr/bin/ciplushelper`
3. Check init script: `ls -la /etc/init.d/ciplushelper`
4. Test manually: `/usr/bin/ciplushelper`
5. Verify certificates: `ls -la /etc/ciplus/` and `ls -la /etc/ssl/certs/`

### Daemon starts but channels don't clear
1. Verify the daemon is running: `pgrep -f ciplushelper`
2. Check CI module is inserted and recognized
3. Verify CI Assignment is configured correctly
4. Check if Oscam/softCAM is conflicting: `ps -A | grep -i oscam`

### Permission issues
```bash
chmod 755 /usr/bin/ciplushelper
chmod 755 /etc/init.d/ciplushelper
chmod 755 /etc/ciplus
chmod 644 /etc/ssl/certs/*.pem
```

---

## 📝 Credits

- **Contributors:** OwnerPlugins
- **Testers:** Community

---

## 📄 License

This plugin is licensed under the **GNU General Public License v2**.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📧 Contact

- **GitHub Issues:** [https://github.com/OwnerPlugins/Ciplushelper/issues](https://github.com/OwnerPlugins/Ciplushelper/issues)
- **Forum:** [LinuxSat Support](https://www.linuxsat-support.com/thread/163204-test-ciplus-helper-all/)

---

## 📜 CI+ Helper v7.0 – Plugin History

**V.7.0 was born from 3 original plugins:**

1. `enigma2-plugin-extensions-ci_plus_helper-openpli8.x_5_all` – User Interface
2. `enigma2-plugin-systemplugins-ciplushelper_5.8-r3_all` – Daemon and binaries
3. `enigma2-plugin-systemplugins-cioffon_1.2_all` – CI auto off/on

---

### Changes and fixes applied for v7.0

- Unified `ConfigListScreen` into a single list
- Added real-time daemon status (`Running` / `Not running`)
- Added automatic CI module detection (`Slot1` / `Slot2`)
- Added `installer.sh` for GitHub installation
- Created unified `postinst` with improved detection
- CRLF fix (`sed -i 's/\r$//'` on init script)
- `pgrep -x` → `pgrep -f` for daemon detection
- Certificates copied to `/etc/ssl/certs/` in addition to `/etc/ciplus/`
- BusyBox support (`head -1` instead of `head -n 1`)
- Improved ARM/MIPSEL model detection
- Added translations (`locale/`)
- Removed `SystemInfo` to make the plugin always visible



**Enjoy your CI+ Helper!** 🎯
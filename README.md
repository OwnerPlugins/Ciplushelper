<h1 align="center">⚙️ CI+ Helper Plugin for Enigma2

[![Version](https://img.shields.io/badge/Version-6.6-blue.svg)](https://github.com/OwnerPlugins/Ciplushelper)
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

**CI+ Helper** is a plugin for Enigma2 that provides comprehensive management of the `ciplushelper` daemon, enabling CI+ certification for a wide range of ARM and MIPSEL set-top boxes.

It automatically detects your box model and architecture, installing the correct binary for optimal compatibility.

---

## ✨ Features

- **Automatic Hardware Detection** – Supports ARM and MIPSEL boxes via `/proc/stb/`, `opkg`, and `uname` fallbacks
- **Multi-Architecture Support** – Separate binaries for generic ARM, Zgemma ARM, and MIPSEL
- **WQHD (2560×1440) Skin** – Optimized interface for 2K displays
- **CI+ Slot Management** – Enable/disable CI+ certification per slot (0 and 1) on ARM boxes
- **Zgemma ARM Binary** – Dedicated binary for Zgemma models (H7, H9, H10)
<!-- - **Restart GUI** – Quick restart of Enigma2 interface directly from the plugin -->
- **Certificates Management** – Install/remove `/etc/ciplus` certificates
- **Autostart Control** – Enable/disable `ciplushelper` at boot
- **Service Control** – Start/stop `ciplushelper` daemon
- **Oscam Toggle** – Start/stop Oscam directly from the plugin menu to avoid descrambler conflicts with CI+ helper.
- **Open CI Assignment** – Quick access to the system plugin for mapping channels to CI slots (OpenPLi/OpenATV).
- **Update plugin - Command** – update the plugin directly from the menu via installer.sh.

---

## 📦 Supported Models

### ARM Architecture
- **Zgemma:** H6, H7, H9combo(se), H9twin(se), H10
- **Other:** HD51, VS1500, Pulse 4K(mini), h17, 8100s, hd61, Uclan (ustym4kpro), DM8000

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
opkg install /tmp/enigma2-plugin-extensions-ci-plus-helper_6.4_all.ipk
```

or command line

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
3. Choose from available options:
   - **Start/Stop** ciplushelper service
   - **Enable/Disable** autostart
   - **Install/Remove** `/etc/ciplus` certificates
   - **Install** Zgemma ARM binary (if applicable)
   - **Enable/Disable CI+ slots** (ARM only)
   - **Restart GUI**
   - **Update Plugin**

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

### v6.4
- **Improved:** Oscam detection now uses `ps -A | grep -i` for universal compatibility (works with `OSCam_11965-803` and all variants).
- **Improved:** Oscam status is now updated in real-time using `onShown` callback.
- **Improved:** Toggle Oscam uses PID-based kill and binary detection via `/proc/<pid>/exe` for reliable start/stop.
- **Fixed:** Oscam toggle now properly starts Oscam using the exact binary path.

### v6.3
- **New:** Oscam toggle – start/stop Oscam directly from the plugin menu to avoid descrambler conflicts with CI+ helper.
- **New:** "Open CI Assignment" menu entry – quick access to the system plugin for mapping channels to CI slots (OpenPLi/OpenATV).

### v6.2
- **New:** "Update plugin" command – update the plugin directly from the menu via `installer.sh`.
- **Fixed:** `TypeError` in MessageBox caused by skin inheritance with `getDesktop()` at class level.
- **Improved:** Skin dimensions for WQHD, FHD, and HD displays.

### v6.1
- **Fixed:** Installer now copies only the `usr/` directory structure, avoiding extra files (`.github`, `screenshots`, `CONTROL`, etc.) being copied to the plugin folder.
- **Improved:** `postinst` script now detects `ustym4kpro`, `dm8000`, and all generic ARM/MIPSEL boxes.

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
- **Fixed:** `TypeError` in MessageBox caused by skin inheritance with getDesktop() at class level.

---

## ⚠️ Important Notes

### Oscam / SoftCAM conflict

If you have **Oscam** or any other softCAM running on your box, it may conflict with the CI+ helper daemon.

- Both Oscam and `ciplushelper` try to access the same hardware descrambler.
- To use CI+ helper, **stop or disable Oscam** temporarily:
  ```bash
  /etc/init.d/softcam stop   # or use your softcam's stop command
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

**Enjoy your CI+ Helper!** 🎯



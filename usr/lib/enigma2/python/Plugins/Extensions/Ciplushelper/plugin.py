# plugin.py
# coded from lululla 20260725

from os import popen, system as os_system
from os.path import exists
from Components.ActionMap import ActionMap
from Components.config import ConfigYesNo, config
from Components.MenuList import MenuList
from enigma import eDVBCI_UI, eTimer, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop

from . import _, __version__

config.misc.ci_auto_check_module = ConfigYesNo(False)

ciplushelper = "/etc/init.d/ciplushelper"


def get_pids(process_name):
    """Return all PIDs for a process using multiple detection methods."""
    debug_file = "/tmp/ciplushelper.log"

    def debug(msg):
        try:
            with open(debug_file, "a") as f:
                f.write("[get_pids] %s\n" % msg)
        except Exception:
            pass

    debug("Searching for process: %s" % process_name)

    try:
        # Method 1: ps + grep (case-insensitive)
        cmd = "ps -A | grep -i '%s' | grep -v grep | awk '{print $1}'" % process_name
        debug("Method 1: %s" % cmd)

        result = popen(cmd).read().strip()
        debug("Method 1 result: '%s'" % result)

        if result:
            pids = result.split()
            debug("Method 1 success: %s" % pids)
            return pids
    except Exception as e:
        debug("Method 1 exception: %s" % e)

    try:
        # Method 2: ps + awk (case-insensitive)
        cmd = (
            "ps -A | awk '/[%s%s]%s/ {print $1}'"
            % (
                process_name[0].upper(),
                process_name[0].lower(),
                process_name[1:]
            )
        )
        debug("Method 2: %s" % cmd)

        result = popen(cmd).read().strip()
        debug("Method 2 result: '%s'" % result)

        if result:
            pids = result.split()
            debug("Method 2 success: %s" % pids)
            return pids
    except Exception as e:
        debug("Method 2 exception: %s" % e)

    try:
        # Method 3: pgrep fallback
        cmd = "pgrep -f -i %s" % process_name
        debug("Method 3: %s" % cmd)

        result = popen(cmd).read().strip()
        debug("Method 3 result: '%s'" % result)

        if result:
            pids = result.split()
            debug("Method 3 success: %s" % pids)
            return pids
    except Exception as e:
        debug("Method 3 exception: %s" % e)

    debug("No process found.")
    return []


class Ciplushelper(Screen):
    def __init__(self, session):
        desktop = getDesktop(0)
        if desktop:
            width = desktop.size().width()
            if width >= 2560:
                self.skin = """
                <screen position="center,center" size="1360,550" title="CI+ helper menu" >
                    <widget name="menu" position="10,10" size="1340,540" font="Regular;40" itemHeight="60" scrollbarMode="showOnDemand" />
                </screen>"""
            elif width >= 1920:
                self.skin = """
                <screen position="center,center" size="1020,420" title="CI+ helper menu" >
                    <widget name="menu" position="10,10" size="1000,400" font="Regular;30" itemHeight="50" scrollbarMode="showOnDemand" />
                </screen>"""
            else:
                self.skin = """
                <screen position="center,center" size="670,340" title="CI+ helper menu" >
                    <widget name="menu" position="10,10" size="660,320" scrollbarMode="showOnDemand" />
                </screen>"""
        else:
            self.skin = """
            <screen position="center,center" size="670,340" title="CI+ helper menu" >
                <widget name="menu" position="10,10" size="660,320" scrollbarMode="showOnDemand" />
            </screen>"""

        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("CI+ helper menu") + "  v" + __version__)

        self.model = ""
        self.ret = ""
        self.oscam_binary = ""

        self.oscam_pids = get_pids("oscam")
        self.oscam_emu_pids = get_pids("oscam-emu")

        self.onShown.append(self.update_oscam_status)
        self.build_menu()

    def build_menu(self):
        menu_list = []
        menu_list.append((_("Supported models"), "about_ciplushelper"))

        model = ""
        info_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/info.txt"
        if exists(info_path):
            try:
                with open(info_path, 'r') as f:
                    lines = f.read()
                    if "ciplushelper-arm" in lines:
                        model = "ciplushelper-arm"
                    elif "ciplushelper-mipsel32" in lines:
                        model = "ciplushelper-mipsel32"
                    elif "ciplushelper-zgemma-arm" in lines:
                        model = "ciplushelper-zgemma-arm"
            except Exception:
                pass

        self.model = model
        self.ret = popen("pgrep ciplushelper").read()

        if model:
            # Autostart
            if exists("/etc/rc2.d/S50ciplushelper"):
                menu_list.append(
                    (_("Disable ciplushelper autostart"), "disable"))
            else:
                menu_list.append(
                    (_("Enable ciplushelper autostart"), "enable"))

            # Start/Stop
            if "ciplushelper" in self.ret:
                menu_list.append((_("Stop ciplushelper"), "stop"))
            else:
                menu_list.append((_("Start ciplushelper"), "start"))

            # ARM‑specific
            if "ciplushelper-arm" in model or "ciplushelper-zgemma-arm" in model:
                if not exists("/etc/cicert.bin"):
                    menu_list.append(
                        (_("Install version from Zgemma"), "install_cicert_bin"))
                else:
                    for i in range(2):
                        enable_file = "/etc/ciplus%d_enable" % i
                        disable_file = "/etc/ciplus%d_disable" % i
                        if exists(enable_file):
                            menu_list.append(
                                (_("Disable CI+ slot") +
                                 " " +
                                 str(i),
                                    "disable_ciplus%d" %
                                    i))
                        elif exists(disable_file):
                            menu_list.append(
                                (_("Enable CI+ slot") +
                                 " " +
                                 str(i),
                                    "enable_ciplus%d" %
                                    i))
                    menu_list.append(
                        (_("Install default version"), "install_default"))

            # Update init script if needed
            try:
                copy = True
                with open('/etc/init.d/ciplushelper', 'r') as f:
                    if "VERSION=1" in f.read():
                        copy = False
                if copy:
                    cmd = "cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper.sh %s && chmod 755 %s" % (
                        ciplushelper, ciplushelper)
                    os_system(cmd)
            except Exception:
                pass

        # Certificates
        cert_paths = [
            "/etc/ciplus/customer.pem",
            "/etc/ciplus/device.pem",
            "/etc/ciplus/root.pem",
            "/etc/ciplus/param"]

        if all(exists(p) for p in cert_paths):
            menu_list.append((_("Remove") + " /etc/ciplus", "remove_sert"))
        else:
            menu_list.append((_("Install") + " /etc/ciplus", "install_sert"))

        menu_list.append((_("Open CI Assignment"), "open_ci_assignment"))

        # Stop/Start Oscam
        oscam_status = "running" if (
            self.oscam_pids or self.oscam_emu_pids) else "stopped"
        menu_list.append((_("Oscam:") + " " + oscam_status, "toggle_oscam"))

        # Update plugin
        menu_list.append((_("Update plugin"), "update_plugin"))
        menu_list.append((_("Restart GUI"), "restart_gui"))

        self["menu"] = MenuList(menu_list)
        self["actions"] = ActionMap(
            ["OkCancelActions"], {
                "ok": self.run, "cancel": self.close}, -1)

    def update_oscam_status(self):
        self.oscam_pids = get_pids("oscam")
        self.oscam_emu_pids = get_pids("oscam-emu")

        if self.oscam_pids:
            pid = self.oscam_pids[0]
            result = popen(
                "readlink -f /proc/%s/exe 2>/dev/null" % pid).read().strip()
            if result:
                self.oscam_binary = result
        else:
            if not hasattr(self, 'oscam_binary') or not self.oscam_binary:
                result = popen(
                    "find /usr/bin -name 'OSCam*' -o -name 'oscam*' 2>/dev/null | head -1").read().strip()
                if result:
                    self.oscam_binary = result
                else:
                    self.oscam_binary = "oscam"  # Fallback

        oscam_status = "running" if (
            self.oscam_pids or self.oscam_emu_pids) else "stopped"

        if hasattr(self, "menu") and self["menu"] is not None:
            menu_list = self["menu"].list
            for i, item in enumerate(menu_list):
                if item[1] == "toggle_oscam":
                    menu_list[i] = (
                        _("Oscam:") + " " + oscam_status,
                        "toggle_oscam")
                    self["menu"].setList(menu_list)
                    break

    def run(self):
        returnValue = self["menu"].l.getCurrentSelection()
        if returnValue is None:
            return
        returnValue = returnValue[1]

        plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"

        commands = {
            "enable": "%s enable_autostart" % ciplushelper,
            "disable": "%s disable_autostart" % ciplushelper,
            "start": "%s start" % ciplushelper,
            "stop": "%s stop" % ciplushelper,
            "install_sert": "cp -R %s/ciplus /etc/ciplus" % plugin_path,
            "remove_sert": "rm -rf /etc/ciplus",
            "disable_ciplus0": "mv /etc/ciplus0_enable /etc/ciplus0_disable",
            "enable_ciplus0": "mv /etc/ciplus0_disable /etc/ciplus0_enable",
            "disable_ciplus1": "mv /etc/ciplus1_enable /etc/ciplus1_disable",
            "enable_ciplus1": "mv /etc/ciplus1_disable /etc/ciplus1_enable",
        }

        if returnValue in commands:
            os_system(commands[returnValue])
            self.close()
            return

        if returnValue == "auto_check":
            config.misc.ci_auto_check_module.value = not config.misc.ci_auto_check_module.value
            config.misc.ci_auto_check_module.save()
            self.close()
            return

        if returnValue == "install_cicert_bin":
            os_system("cp %s/cicert.bin /etc/cicert.bin" % plugin_path)
            for i in range(2):
                enable_file = "/etc/ciplus%d_enable" % i
                if not exists(enable_file):

                    os_system(
                        "echo 'rename ciplus*_enable to ciplus*_disable for deactivate ciplus certification of the module.' > %s" %
                        enable_file)
            if "ciplushelper" in self.ret:
                os_system("killall ciplushelper 2>/dev/null && sleep 2")

            os_system(
                "cp %s/ciplushelper_bin/zgemma-arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper" %
                plugin_path)
            if "ciplushelper" in self.ret:
                self.session.open(
                    Console, _("Start ciplushelper"), [
                        "/etc/init.d/ciplushelper start && echo '" + _("Need restart GUI") + "'"])
            self.close()
            return

        if returnValue == "install_default":
            if "ciplushelper" in self.ret:
                os_system("killall ciplushelper 2>/dev/null && sleep 2")
            os_system(
                "cp %s/ciplushelper_bin/arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper" %
                plugin_path)
            if "ciplushelper" in self.ret:
                self.session.open(
                    Console, _("Start ciplushelper"), [
                        "/etc/init.d/ciplushelper start && echo '" + _("Need restart GUI") + "'"])
            self.close()
            return

        if returnValue == "open_ci_assignment":
            try:
                from Plugins.SystemPlugins.CommonInterfaceAssignment.plugin import CIselectMainMenu
                self.session.openWithCallback(self.close, CIselectMainMenu)
            except ImportError:
                self.session.open(
                    MessageBox,
                    _("Common Interface Assignment plugin not found. Please install it from System Plugins."),
                    MessageBox.TYPE_INFO)
                self.close()
            return

        if returnValue == "toggle_oscam":
            if self.oscam_pids or self.oscam_emu_pids:
                for pid in self.oscam_pids:
                    os_system("kill -9 %s 2>/dev/null" % pid)
                for pid in self.oscam_emu_pids:
                    os_system("kill -9 %s 2>/dev/null" % pid)
                msg = _("Oscam stopped.")
            else:
                if hasattr(self, 'oscam_binary') and self.oscam_binary:
                    os_system("%s & 2>/dev/null" % self.oscam_binary)
                    msg = _("Oscam started.")
                else:
                    msg = _("Oscam binary not found!")
                    self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                    self.close()
                    return
            self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
            self.close()
            return

        if returnValue == "update_plugin":
            cmd = "wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash"
            self.session.open(Console, _("Updating plugin..."), [cmd])
            self.close()
            return

        if returnValue == "restart_gui":
            self.session.openWithCallback(
                self.restart_gui_callback,
                MessageBox,
                _("Are you sure you want to restart the GUI?"),
                MessageBox.TYPE_YESNO
            )
            return

        if returnValue == "about_ciplushelper":
            installed = self.model if self.model else _("Unknown")
            message = _("CI+ Helper Plugin") + " v" + __version__ + "\n\n" + \
                _("Supported devices:") + "\n" + \
                "ARM: HD51 / VS1500 / Zgemma (H6/H7/H9combo(se)/H9twin(se)/H10) / Pulse 4K(mini) / h17 / 8100s / hd61\n" + \
                "MIPSEL: Mutant (hd1500/hd2400) / Xtrend (et8000/et10000) / Formuler (f1/f3/f4) / Triplex / Cube\n\n" + \
                _("Other models may need '/etc/ciplus'") + "\n\n" + \
                _("Installed:") + " " + installed
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def restart_gui_callback(self, answer):
        if answer:
            self.session.open(TryQuitMainloop)


pause_checkTimer = eTimer()


def check_cimodule():
    try:
        from Components.SystemInfo import SystemInfo
        NUM_CI = SystemInfo.get("CommonInterface", 0)
        if NUM_CI:
            change = False
            if NUM_CI == 1:
                state = eDVBCI_UI.getInstance().getState(0)
                if state == 1:
                    SystemInfo["CommonInterface"] = 0
                    change = True
            elif NUM_CI == 2:
                state = eDVBCI_UI.getInstance().getState(0)
                state1 = eDVBCI_UI.getInstance().getState(1)
                if state == 1 and state1 == 2:
                    return
                if state == 1:
                    SystemInfo["CommonInterface"] -= 1
                    change = True
                if state1 == 1:
                    SystemInfo["CommonInterface"] -= 1
                    change = True
            if change:
                try:
                    from Tools.CIHelper import cihelper
                    cihelper.load_ci_assignment(force=True)
                except Exception:
                    pass
                try:
                    if _Session and _Session.nav.getCurrentlyPlayingServiceOrGroup():
                        _Session.nav.playService(
                            _Session.nav.getCurrentlyPlayingServiceOrGroup(),
                            forceRestart=True
                        )
                except Exception:
                    pass
    except Exception:
        pass


_Session = None


def sessionstart(reason, session):
    pass


pause_checkTimer.callback.append(check_cimodule)


def main(session, **kwargs):
    session.open(Ciplushelper)


def is_module_active():
    """Check if any CI module is actually inserted and active (works on OpenPLi & OpenATV)"""
    try:
        from Components.BoxInfo import BoxInfo
        NUM_CI = BoxInfo.getItem("CommonInterface")
    except ImportError:
        try:
            from Components.SystemInfo import SystemInfo
            NUM_CI = SystemInfo.get("CommonInterface", 0)
        except Exception:
            return False

    if NUM_CI and NUM_CI > 0:
        try:

            for slot in range(NUM_CI):
                state = eDVBCI_UI.getInstance().getState(slot)
                if state > 0:
                    return True
        except Exception:
            pass
    return False


def menu(menuid, **kwargs):
    if menuid == "cicam":
        return [(_("CI+ helper"), main, "ci_helper", 30)]
    return []


def Plugins(**kwargs):
    if is_module_active():
        return [
            PluginDescriptor(
                name=_("CI+ helper") + " v" + __version__,
                description=_("CI+ helper for Enigma2"),
                icon="plugin.png",
                where=PluginDescriptor.WHERE_PLUGINMENU,
                fnc=main
            ),
            PluginDescriptor(
                name=_("CI+ helper") + " v" + __version__,
                where=PluginDescriptor.WHERE_EXTENSIONSMENU,
                fnc=main
            )
        ]
    return []


# for test no cicam
"""
def menu(menuid, **kwargs):
    if menuid == "plugin":
        return [(_("CI+ helper"), main, "ci_helper", 30)]
    return []


def Plugins(**kwargs):
    from Components.SystemInfo import SystemInfo
    return [
        PluginDescriptor(
            name=_("CI+ helper") + " v" + __version__,
            description=_("CI+ helper for Enigma2"),
            icon="plugin.png",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=main
        ),
        PluginDescriptor(
            name=_("CI+ helper") + " v" + __version__,
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            fnc=main
        )
    ]
"""
# end test

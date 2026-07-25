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

from . import _, __version__

config.misc.ci_auto_check_module = ConfigYesNo(False)

ciplushelper = "/etc/init.d/ciplushelper"


class Ciplushelper(Screen):
    if getDesktop(0).size().width() >= 2560:
        skin = """
        <screen position="center,center" size="1360,420" title="CI+ helper menu" >
            <widget name="menu" position="10,10" size="1340,400" font="Regular;40" itemHeight="60" scrollbarMode="showOnDemand" />
        </screen>"""
    elif getDesktop(0).size().width() >= 1920:
        skin = """
        <screen position="center,center" size="1020,320" title="CI+ helper menu" >
            <widget name="menu" position="10,10" size="1000,300" font="Regular;30" itemHeight="50" scrollbarMode="showOnDemand" />
        </screen>"""
    else:
        skin = """
        <screen position="center,center" size="670,220" title="CI+ helper menu" >
            <widget name="menu" position="10,10" size="660,200" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("CI+ helper menu") + "  v" + __version__)

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
                        enable_file = f"/etc/ciplus{i}_enable"
                        disable_file = f"/etc/ciplus{i}_disable"
                        if exists(enable_file):
                            menu_list.append(
                                (_("Disable CI+ slot") + " " + str(i), f"disable_ciplus{i}"))
                        elif exists(disable_file):
                            menu_list.append(
                                (_("Enable CI+ slot") + " " + str(i), f"enable_ciplus{i}"))
                    menu_list.append(
                        (_("Install default version"), "install_default"))

            # Update init script if needed
            try:
                copy = True
                with open('/etc/init.d/ciplushelper', 'r') as f:
                    if "VERSION=1" in f.read():
                        copy = False
                if copy:
                    cmd = f"cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper.sh {ciplushelper} && chmod 755 {ciplushelper}"
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

        menu_list.append((_("Restart GUI"), "restart_gui"))

        self["menu"] = MenuList(menu_list)
        self["actions"] = ActionMap(
            ["OkCancelActions"], {
                "ok": self.run, "cancel": self.close}, -1)

    def run(self):
        returnValue = self["menu"].l.getCurrentSelection()
        if returnValue is None:
            return
        returnValue = returnValue[1]

        plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"

        commands = {
            "enable": f"{ciplushelper} enable_autostart",
            "disable": f"{ciplushelper} disable_autostart",
            "start": f"{ciplushelper} start",
            "stop": f"{ciplushelper} stop",
            "install_sert": f"cp -R {plugin_path}/ciplus /etc/ciplus",
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
            os_system(f"cp {plugin_path}/cicert.bin /etc/cicert.bin")
            for i in range(2):
                enable_file = f"/etc/ciplus{i}_enable"
                if not exists(enable_file):
                    os_system(
                        f"echo 'rename ciplus*_enable to ciplus*_disable for deactivate ciplus certification of the module.' > {enable_file}")
            if "ciplushelper" in self.ret:
                os_system("killall ciplushelper 2>/dev/null && sleep 2")
            os_system(
                f"cp {plugin_path}/ciplushelper_bin/zgemma-arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper")
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
                f"cp {plugin_path}/ciplushelper_bin/arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper")
            if "ciplushelper" in self.ret:
                self.session.open(
                    Console, _("Start ciplushelper"), [
                        "/etc/init.d/ciplushelper start && echo '" + _("Need restart GUI") + "'"])
            self.close()
            return

        if returnValue == "restart_gui":
            self.session.open(
                MessageBox,
                _("Are you sure you want to restart the GUI?"),
                MessageBox.TYPE_YESNO,
                self.restart_gui)
            return

        if returnValue == "about_ciplushelper":
            installed = self.model if self.model else _("Unknown")
            message = _("CI+ Helper Plugin") + " v" + __version__ + "\n\n" + \
                _("Supported devices:") + "\n" + \
                _("ARM") + ": HD51 / VS1500 / Zgemma (H6/H7/H9combo(se)/H9twin(se)/H10) / Pulse 4K(mini) / h17 / 8100s / hd61\n" + \
                _("MIPSEL") + ": Mutant (hd1500/hd2400) / Xtrend (et8000/et10000) / Formuler (f1/f3/f4) / Triplex / Cube\n\n" + \
                _("Other models may need '/etc/ciplus'") + "\n\n" + \
                _("Installed:") + " " + installed
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def restart_gui(self, answer):
        if answer:
            os_system("killall -9 enigma2")


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
                            _Session.nav.getCurrentlyPlayingServiceOrGroup(), forceRestart=True)
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


def menu(menuid, **kwargs):
    if menuid == "cicam":
        return [(_("CI+ helper"), main, "ci_helper", 30)]
    return []


def Plugins(**kwargs):
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
